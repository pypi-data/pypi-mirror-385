from io import BufferedReader
from typing import List, Union

import numpy as np
import torch
from PIL import Image

from msgflux.models.response import Response


class BaseVision:
    @torch.inference_mode()
    def _execute_model(self, images):
        processed_images = []
        for pixels in images:
            if isinstance(pixels, BufferedReader):
                image_pil = Image.open(pixels)
            else: # numpy
                image_pil = Image.fromarray(pixels)
            processed_images.append(self.processor(image_pil))
        inputs = torch.stack(processed_images)
        inputs = inputs.to(self.dtype).to(self.device)
        model_output = self.model(inputs)
        if isinstance(model_output, torch.Tensor):
            model_output = model_output.cpu()
        return model_output

    def __call__(
        self,
        data: Union[
            BufferedReader, np.ndarray, List[Union[BufferedReader, np.ndarray]]
        ],
    ) -> Response:
        if not isinstance(data, list):
            data = [data]
        response = self._generate(images=data)
        return response


class BaseClassifier:
    def _process_cls_output(self, logits):
        scores, cls_idxs = torch.topk(logits.softmax(dim=1), k=1)
        predictions = []
        for score, cls_idx in zip(scores, cls_idxs):
            label = self.id2label[cls_idx]
            if self.return_score:
                result = {"score": score, "label": label}
            else:
                result = label
            predictions.append(result)
        return predictions


class BaseAudioClassifier(BaseClassifier):
    def _generate(self, images):
        response = Response()
        model_output = self._execute_model(images)
        predictions = self._process_cls_output(model_output)
        response.set_response_type("audio_classification")
        response.add(predictions)
        return response


class BaseImageClassifier(BaseClassifier):
    def _generate(self, images):
        response = Response()
        model_output = self._execute_model(images)
        predictions = self._process_cls_output(model_output)
        response.set_response_type("image_classification")
        response.add(predictions)
        return response


class BaseVideoClassifier(BaseClassifier):
    def _generate(self, images):
        response = Response()
        model_output = self._execute_model(images)
        predictions = self._process_cls_output(model_output)
        response.set_response_type("video_classification")
        response.add(predictions)
        return response
