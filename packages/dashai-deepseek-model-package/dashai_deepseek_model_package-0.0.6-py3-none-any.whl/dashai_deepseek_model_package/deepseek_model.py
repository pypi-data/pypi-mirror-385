from typing import List

from llama_cpp import Llama

from DashAI.back.core.schema_fields import (
    BaseSchema,
    float_field,
    int_field,
    schema_field,
    enum_field,
)
from DashAI.back.models.text_to_text_generation_model import (
    TextToTextGenerationTaskModel,
)

from DashAI.back.models.hugging_face.llama_utils import is_gpu_available_for_llama_cpp

if is_gpu_available_for_llama_cpp():
    DEVICE_ENUM = ["gpu", "cpu"]
    DEVICE_PLACEHOLDER = "gpu"
else:
    DEVICE_ENUM = ["cpu"]
    DEVICE_PLACEHOLDER = "cpu"


class DeepSeekSchema(BaseSchema):
    """Schema for DeepSeek model."""

    model_name: schema_field(
        enum_field(
            enum=[
                "TheBloke/deepseek-llm-7B-chat-GGUF",
                "TheBloke/deepseek-coder-6.7B-instruct-GGUF",
            ]
        ),
        placeholder="TheBloke/deepseek-llm-7B-chat-GGUF",
        description="The specific DeepSeek model version to use.",
    )  # type: ignore

    max_tokens: schema_field(
        int_field(ge=1),
        placeholder=100,
        description="Maximum number of tokens to generate.",
    )  # type: ignore

    temperature: schema_field(
        float_field(ge=0.0, le=1.0),
        placeholder=0.7,
        description=(
            "Sampling temperature. Higher values make the output more random, "
            "while lower values make it more focused and deterministic."
        ),
    )  # type: ignore

    frequency_penalty: schema_field(
        float_field(ge=0.0, le=2.0),
        placeholder=0.1,
        description=(
            "Penalty for repeated tokens in the output. Higher values reduce the "
            "likelihood of repetition, encouraging more diverse text generation."
        ),
    )  # type: ignore

    n_ctx: schema_field(
        int_field(ge=1),
        placeholder=4096,
        description=(
            "Maximum number of tokens the model can process in a single forward pass "
            "(context window size)."
        ),
    )  # type: ignore

    device: schema_field(
        enum_field(enum=DEVICE_ENUM),
        placeholder=DEVICE_PLACEHOLDER,
        description="The device to use for model inference.",
    )  # type: ignore


class DeepSeekModel(TextToTextGenerationTaskModel):
    """DeepSeek model for text generation using llama.cpp library."""

    SCHEMA = DeepSeekSchema

    __FILENAMES_DICT = {
        "TheBloke/deepseek-llm-7B-chat-GGUF": "deepseek-llm-7b-chat.Q5_K_M.gguf",
        "TheBloke/deepseek-coder-6.7B-instruct-GGUF": (
            "deepseek-coder-6.7b-instruct.Q5_K_M.gguf"
        ),
    }

    def __init__(self, **kwargs):
        kwargs = self.validate_and_transform(kwargs)
        self.max_tokens = kwargs.pop("max_tokens", 100)
        self.temperature = kwargs.pop("temperature", 0.7)
        self.frequency_penalty = kwargs.pop("frequency_penalty", 0.1)
        self.n_ctx = kwargs.pop("n_ctx", 512)

        self.model_name = kwargs.get("model_name", "TheBloke/deepseek-llm-7B-chat-GGUF")

        self.model_id = self.model_name
        self.filename = self.__FILENAMES_DICT.get(self.model_name)

        self.model = Llama.from_pretrained(
            repo_id=self.model_id,
            filename=self.filename,
            verbose=True,
            n_ctx=self.n_ctx,
            n_gpu_layers=-1 if kwargs.get("device", "gpu") == "gpu" else 0,
        )

    def generate(self, prompt: list[dict[str, str]]) -> List[str]:
        """Generate text based on prompts."""
        output = self.model.create_chat_completion(
            messages=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
        )

        generated_text = output["choices"][0]["message"]["content"]
        return [generated_text]
