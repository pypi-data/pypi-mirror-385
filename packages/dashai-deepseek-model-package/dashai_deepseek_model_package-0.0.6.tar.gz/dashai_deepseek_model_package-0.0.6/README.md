# DeepSeek LLM Plugin for DashAI

This plugin integrates two DeepSeek models into the DashAI framework using the `llama.cpp` backend. It enables text generation tasks through a lightweight and efficient inference engine with support for quantized GGUF models.

## Included Models

### 1. DeepSeek LLM 7B Chat

- Pretrained chat-oriented model for general text generation
- Based on [`TheBloke/deepseek-llm-7B-chat-GGUF`](https://huggingface.co/TheBloke/deepseek-llm-7B-chat-GGUF)
- Uses quantized file: `deepseek-llm-7b-chat.Q5_K_M.gguf`

### 2. DeepSeek Coder 6.7B Instruct

- Instruction-tuned model for code-related and general instruction tasks
- Initialized from `deepseek-coder-6.7b-base`, fine-tuned on 2B instruction tokens
- Based on [`TheBloke/deepseek-coder-6.7B-instruct-GGUF`](https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF)
- Uses quantized file: `deepseek-coder-6.7b-instruct.Q5_K_M.gguf`

Both models use the **Q5_K_M** quantization method for a balance of quality and efficiency, and are compatible with both CPU and GPU inference.

## Components

### DeepSeekModel

- Implements the `TextToTextGenerationTaskModel` interface from DashAI
- Uses the `llama.cpp` backend with GGUF support
- Loads the model from Hugging Face at runtime
- Supports configurable generation parameters
- Automatically truncates long prompts and uses custom stop sequences for cleaner output

## Features

- Configurable text generation with:
  - `max_tokens`: Number of tokens to generate
  - `temperature`: Controls output randomness
  - `frequency_penalty`: Reduces repetition
  - `n_ctx`: Context window size
  - `device`: `"cpu"` or `"gpu"`
- Efficient memory usage with GGUF quantization
- Custom stop sequence: `["Q:"]`

## Model Parameters

| Parameter           | Description                                      | Default              |
| ------------------- | ------------------------------------------------ | -------------------- |
| `max_tokens`        | Maximum number of tokens to generate             | 100                  |
| `temperature`       | Sampling temperature (higher = more random)      | 0.7                  |
| `frequency_penalty` | Penalizes repeated tokens to encourage diversity | 0.1                  |
| `n_ctx`             | Maximum context window (tokens in prompt)        | 4096                 |
| `device`            | Inference device                                 | `"gpu"` if available |

## Requirements

- `DashAI`
- `llama-cpp-python`
- Model files from Hugging Face:
  - [`TheBloke/deepseek-llm-7B-chat-GGUF`](https://huggingface.co/TheBloke/deepseek-llm-7B-chat-GGUF)
  - [`TheBloke/deepseek-coder-6.7B-instruct-GGUF`](https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF)

## Notes

This plugin uses the **GGUF** format, introduced by the `llama.cpp` team in August 2023.  
GGUF replaces the older **GGML** format, which is no longer supported.

GGUF models are optimized for fast inference and lower memory consumption, especially on CPU- or GPU-constrained devices.

Both models (`deepseek-llm-7b-chat` and `deepseek-coder-6.7b-instruct`) are distributed in the **Q5_K_M** quantized format.  
This quantization method offers a solid trade-off between model size and quality, making them suitable for real-time or resource-limited environments.

> ⚠️ These models are **pretrained and instruction-tuned** for inference only. They are **not intended for fine-tuning**.
