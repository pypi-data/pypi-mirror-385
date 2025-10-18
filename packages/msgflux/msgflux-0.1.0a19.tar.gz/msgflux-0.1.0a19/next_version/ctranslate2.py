import shutil
import subprocess
from pathlib import Path
from typing import List, Literal, Optional, Union

import numpy as np

try:
    import ctranslate2
    import torch
    from transformers import AutoModelForSequenceClassification, AutoProcessor
except Exception as e:
    raise ImportError(
        "`ctranslate2` not detected, please install"
        "using `pip install ctranslate2`"
    ) from e
from msgflux.models.base import BaseModel
from msgflux.models.response import ModelResponse
from msgflux.models.types import (
    TextClassifierModel,
    TextEmbedderModel,
)
from msgflux.telemetry.span import instrument
from msgflux.utils.pooling import apply_pooling


def _ct2_transformers_converter(model_id: str, output_dir: str):
    if not Path(output_dir).is_dir():
        raise ValueError(f"Invalid output_dir: {output_dir}")
    converter_path = shutil.which("ct2-transformers-converter")
    if converter_path is None:
        raise FileNotFoundError("ct2-transformers-converter not found in PATH")
    subprocess.run( # noqa: S603
        [converter_path, "--model", model_id, "--output_dir", output_dir],
        check=True,
    )


CT2_DTYPE = Literal[
    "int8",
    "int8_float32",
    "int8_float16",
    "int8_bfloat16",
    "int16",
    "float16",
    "bfloat16",
    "float32",
]


class _BaseCTranslate2(BaseModel):
    provider: str = "ctranslate2"

    def __init__(
        self,
        model_id: str,
        *,
        device: Optional[Literal["cpu", "cuda"]] = "cpu",
        dtype: Optional[CT2_DTYPE] = "float32",
        processor_id: Optional[str] = None,
        pooling_strategy: Optional[Literal["mean", "max", "cls"]] = "mean",
        trust_remote_code: Optional[bool] = False,
        flash_attn: Optional[bool] = False,
        tensor_parallel: Optional[bool] = False,
    ):
        super().__init__()
        self.processor_params = {
            "pretrained_model_name_or_path": processor_id or model_id,
            "trust_remote_code": trust_remote_code,
        }
        self.processor_run_params = {"return_tensors": "pt"}
        self.sampling_params = {
            "device": device,
            "compute_type": dtype,
            "flash_attention": flash_attn,
            "tensor_parallel": tensor_parallel,
            "trust_remote_code": trust_remote_code,
        }
        self.model_id = model_id
        self.pooling_strategy = pooling_strategy
        self._initialize()

    def _initialize(self):
        self._init_processor()
        self._convert_to_ct2()
        self._init_model()
        if self.model_type == "text_classifier":
            self._init_head_model()

    def _convert_to_ct2(self):
        self.ct2_model_id = f"{self.model_id.split('/')[1]}-ct2"
        _ct2_transformers_converter(self.model_id, self.ct2_model_id)

    def _init_processor(self):
        self.processor = AutoProcessor.from_pretrained(**self.processor_params)

    @torch.inference_mode()
    def _execute_model(self, data):
        inputs = self.processor(data, **self.processor_run_params)
        tokens = inputs.input_ids
        model_outputs = self.model.forward_batch(tokens)
        return model_outputs

    def __call__(self, data: Union[str, List[str]]) -> ModelResponse:
        if not isinstance(list):
            data = [data]
        return self._generate(data)


class CTranslate2TextEmbedder(_BaseCTranslate2, TextEmbedderModel):
    def _init_model(self):
        self.model = ctranslate2.Encoder(self.ct2_model_id, **self.sampling_params)

    def _get_embeddings(self, last_hidden_state):
        if self.sampling_params.get("device") == "cuda":
            last_hidden_state = (
                torch.as_tensor(
                    last_hidden_state, device=self.sampling_params.get("device")
                )
                .cpu()
                .numpy()
            )
        else:
            last_hidden_state = np.array(last_hidden_state)
        embeddings = apply_pooling(last_hidden_state, self.pooling_strategy)
        return embeddings

    @instrument("ctranslate2.generation", {"response.type": "text_embedder"})
    def _generate(self, data):
        response = ModelResponse()
        model_output = self._execute_model(data)

        last_hidden_state = model_output.last_hidden_state
        embeddings = self._get_embeddings(last_hidden_state)
        embeddings_list = embeddings.tolist()

        response.set_response_type("text_embedding")
        response.add(embeddings_list)

        return response


class CTranslate2TextClassifier(_BaseCTranslate2, TextClassifierModel):
    def _init_head_model(self):
        model = AutoModelForSequenceClassification(self.model_id)
        self.id2label = model.config.id2label
        self.head_model = model.classifier.eval().to(self.sampling_params.get("device"))

    def _execute_head_model(self, pooler_output) -> List[str]:
        if self.sampling_params.get("device") == "cuda":
            pooler_output = torch.as_tensor(
                pooler_output, device=self.sampling_params.get("device")
            )
        else:
            pooler_output = np.array(pooler_output)
            pooler_output = torch.as_tensor(pooler_output)
        logits = self.head_model(pooler_output)
        predicted_class_ids = logits.argmax(1)
        labels = [self.id2label[label_id] for label_id in predicted_class_ids]
        return labels

    @instrument("ctranslate2.generation", {"response.type": "text_classification"})
    def _generate(self, data):
        response = ModelResponse()
        model_output = self._execute_model(data)
        pooler_output = model_output.pooler_output
        labels = self._execute_head_model(pooler_output)
        response.set_response_type("text_classification")
        response.add(labels)
        return response
