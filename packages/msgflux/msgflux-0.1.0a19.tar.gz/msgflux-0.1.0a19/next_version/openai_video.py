@register_model
class OpenAIImageTextToVideo(_BaseOpenAI, ImageTextToVideoModel):
    """OpenAI Video Generation."""

    def __init__(
        self,
        *,
        model_id: str,
        size: Optional[str] = "auto",
        quality: Optional[str] = "auto",
        background: Optional[Literal["transparent", "opaque", "auto"]] = None,
        moderation: Optional[Literal["auto", "low"]] = None,
        base_url: Optional[str] = None,
    ):
        """Args:
        model_id:
            Model ID in provider.
        size:
            The size of the generated images.
        quality:
            The quality of the image that will be generated.
        background:
            Allows to set transparency for the background of the generated image(s).
        moderation:
            Control the content-moderation level for images generated.
        base_url:
            URL to model provider.
        """
        super().__init__()
        self.model_id = model_id
        self.sampling_params = {"base_url": base_url or self._get_base_url()}
        self.sampling_run_params = dict(
            size=size, quality=quality, background=background
        )
        if moderation:
            self.sampling_run_params["moderation"] = moderation
        self._initialize()
        self._get_api_key()

    def _prepare_inputs(self, image, mask):
        inputs = {}
        if isinstance(image, str):
            image = [image]
        inputs["image"] = [encode_data_to_bytes(item) for item in image]
        if mask:
            inputs["mask"] = encode_data_to_bytes(mask)
        return inputs

    @model_retry
    def __call__(
        self,
        prompt: str,
        *,
        image: Optional[Union[str, List[str]]] = None,
        secounds: Optional[int] = None,
        response_format: Optional[Literal["url", "base64"]] = None,
        n: Optional[int] = 1,
    ) -> ModelResponse:
        """Args:
        prompt:
            A text description of the desired image(s).
        image:
            The image(s) to edit. Can be a path, an url or base64 string.
        mask:
            An additional image whose fully transparent areas
            (e.g. where alpha is zero) indicate where image
            should be edited. If there are multiple images provided,
            the mask will be applied on the first image.
        response_format:
            Format in which images are returned.
        n:
            The number of images to generate.
        """
        generation_params = dotdict(prompt=prompt, n=n, model=self.model_id)
        # input_reference

        if response_format is not None:
            if response_format == "base64":
                response_format = "b64_json"
            generation_params.response_format = response_format

        inputs = self._prepare_inputs(image, mask)
        response = self._generate(**generation_params, **inputs)
        return response        