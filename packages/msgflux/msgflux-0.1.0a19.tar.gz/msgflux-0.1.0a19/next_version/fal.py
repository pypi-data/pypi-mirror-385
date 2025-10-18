from os import getenv
from typing import (
    Any, Dict, List, Literal, Mapping, Optional, Union
)

try:
    import fal_client
except ImportError:
    fal_client = None

from msgflux.dotdict import dotdict
from msgflux.models.base import BaseModel
from msgflux.models.registry import register_model
from msgflux.models.response import ModelResponse
from msgflux.models.types import (
    ImageTextToImageModel,
    ImageTextToVideoModel,    
    TextToImageModel,
    TextToVideoModel
)
from msgflux.utils.encode import encode_data_to_bytes
from msgflux.utils.tenacity import model_retry


class _BaseFal(BaseModel):
    provider: str = "fal"

    def _initialize(self):
        """Initialize the OpenAI client with empty API key."""
        if fal_client is None:
            raise ImportError(
                "`fal_client` client is not available. "
                "Install with `pip install msgflux[fal]`."
            )
        self.client = fal_client
        return

    def _get_api_key(self):
        """Load API keys from environment variable."""
        key = getenv("FAL_KEY")
        if not key:
            raise ValueError(
                "The Fal api key is not available. Please set `FAL_KEY`"
            )
        return key

    def _execute_model(self, **kwargs):
        """Main method to execute the model."""
        model_id = f"fal-ai/{self.model_id}"
        handler = self.client.subscribe(model_id, arguments=kwargs)
        request_id = handler.request_id
        while True:
            status = self.client.status(model_id, request_id)
            if status == "...": # done
                model_output = self.client.result(model_id, request_id)
                return model_output