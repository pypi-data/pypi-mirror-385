# isa_model_sdk - Unified AI Model Serving Framework

A comprehensive Python framework for working with multiple AI providers and models through a unified interface. Support for OpenAI, Replicate, Ollama, and more, with advanced training and evaluation capabilities.

## Installation

```bash
pip install isa_model_sdk
```

## Quick Start

The isa_model_sdk package supports three main usage patterns:

### 1. Pass API Keys Directly (Recommended)

This is the most flexible approach - no environment variables needed:

```python
from isa_model.inference.ai_factory import AIFactory

# Create factory instance
factory = AIFactory.get_instance()

# Use OpenAI with API key
llm = factory.get_llm(
    model_name="gpt-4o-mini", 
    provider="openai", 
    api_key="your-openai-api-key-here"
)

# Use Replicate for image generation
image_gen = factory.get_vision_model(
    model_name="stability-ai/sdxl", 
    provider="replicate", 
    api_key="your-replicate-token-here"
)
```

### 2. Use Environment Variables

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export REPLICATE_API_TOKEN="your-replicate-token"
```

Then use without passing keys:

```python
from isa_model.inference.ai_factory import AIFactory

factory = AIFactory.get_instance()

# Will automatically use OPENAI_API_KEY from environment
llm = factory.get_llm(model_name="gpt-4o-mini", provider="openai")

# Will automatically use REPLICATE_API_TOKEN from environment  
image_gen = factory.get_vision_model(model_name="stability-ai/sdxl", provider="replicate")
```

### 3. Use Local Models (No API Key Needed)

For local models like Ollama, no API keys are required:

```python
from isa_model.inference.ai_factory import AIFactory

factory = AIFactory.get_instance()

# Use local Ollama model (no API key needed)
llm = factory.get_llm(model_name="llama3.1", provider="ollama")
```

## 🎯 Training & Evaluation Framework

**NEW in v0.0.1**: Comprehensive training and evaluation capabilities for LLMs, Stable Diffusion, and ML models.

### Quick Training Example

```python
from isa_model.training import TrainingFactory, train_gemma
from isa_model.eval import EvaluationFactory

# Quick Gemma training
model_path = train_gemma(
    dataset_path="tatsu-lab/alpaca",
    model_size="4b",
    num_epochs=3,
    use_lora=True
)

# Comprehensive evaluation
evaluator = EvaluationFactory(use_wandb=True)
results = evaluator.evaluate_llm(
    model_path=model_path,
    dataset_path="test_data.json",
    metrics=["perplexity", "bleu", "rouge"]
)

# Run benchmarks
mmlu_results = evaluator.run_benchmark(
    model_path=model_path,
    benchmark="mmlu"
)
```

### Advanced Training Configuration

```python
from isa_model.training import TrainingFactory

factory = TrainingFactory()

# Advanced LLM training
model_path = factory.train_model(
    model_name="google/gemma-2-4b-it",
    dataset_path="custom_dataset.json",
    use_lora=True,
    batch_size=4,
    num_epochs=3,
    learning_rate=2e-5,
    lora_rank=8,
    lora_alpha=16
)

# Upload to HuggingFace
hf_url = factory.upload_to_huggingface(
    model_path=model_path,
    hf_model_name="your-username/gemma-4b-custom",
    hf_token="your-hf-token"
)
```

### Cloud Training on RunPod

```python
# Train on RunPod cloud infrastructure
result = factory.train_on_runpod(
    model_name="google/gemma-2-4b-it",
    dataset_path="tatsu-lab/alpaca",
    runpod_api_key="your-runpod-key",
    template_id="your-template-id",
    gpu_type="NVIDIA RTX A6000"
)
```

## Function Calling with bind_tools

**Enhanced in v0.0.1**: LangChain-compatible function calling interface for all LLM services.

### Basic Function Calling

```python
import asyncio
from isa_model.inference.ai_factory import AIFactory

# Define your tool functions
def get_weather(location: str) -> str:
    """Get weather information for a location"""
    weather_data = {
        "paris": "Sunny, 22°C",
        "london": "Cloudy, 18°C",
        "tokyo": "Clear, 25°C"
    }
    return weather_data.get(location.lower(), f"Weather data not available for {location}")

def calculate_math(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        result = eval(expression)  # Use safely in production
        return f"The result of {expression} is {result}"
    except:
        return f"Error calculating {expression}"

async def main():
    factory = AIFactory.get_instance()
    
    # Create LLM with any provider
    llm = factory.get_llm("gpt-4o-mini", "openai", api_key="your-key")
    # or: llm = factory.get_llm("llama3.1", "ollama")  # Local model
    
    # Bind tools to the service (LangChain-style interface)
    llm_with_tools = llm.bind_tools([get_weather, calculate_math])
    
    # Use the service with tools
    response = await llm_with_tools.achat([
        {"role": "user", "content": "What's the weather in Paris? Also calculate 15 * 8"}
    ])
    
    print(response)  # Model will use tools automatically
    await llm.close()

asyncio.run(main())
```

## Supported Services

### Language Models (LLM)

```python
# OpenAI models
llm = factory.get_llm("gpt-4o-mini", "openai", api_key="your-key")
llm = factory.get_llm("gpt-4o", "openai", api_key="your-key") 

# Ollama models (local)
llm = factory.get_llm("llama3.1", "ollama")
llm = factory.get_llm("codellama", "ollama")

# Replicate models
llm = factory.get_llm("meta/llama-3-70b-instruct", "replicate", api_key="your-token")

# All LLM services support bind_tools() for function calling
llm_with_tools = llm.bind_tools([your_functions])
```

### Vision Models

```python
# OpenAI vision
vision = factory.get_vision_model("gpt-4o", "openai", api_key="your-key")

# Replicate image generation
image_gen = factory.get_vision_model("stability-ai/sdxl", "replicate", api_key="your-token")

# Ollama vision (local)
vision = factory.get_vision_model("llava", "ollama")
```

### Embedding Models

```python
# OpenAI embeddings
embedder = factory.get_embedding("text-embedding-3-small", "openai", {"api_key": "your-key"})

# Ollama embeddings (local)
embedder = factory.get_embedding("bge-m3", "ollama")
```

## Training Framework Features

### Multi-Modal Training Support
- **LLM Training**: Gemma, Llama, GPT-style models with LoRA/QLoRA
- **Stable Diffusion**: Image generation model training  
- **ML Models**: XGBoost, Random Forest, traditional ML
- **Computer Vision**: CNN, Vision Transformers

### Training Modes
- **Local Training**: On your machine with CPU/GPU
- **Cloud Training**: RunPod, AWS, GCP integration
- **Distributed Training**: Multi-GPU support

### Data Pipeline
- **Annotation Service**: Human-in-the-loop data annotation
- **Dataset Management**: HuggingFace, local, cloud storage
- **Quality Control**: Data validation and filtering

## Evaluation Framework Features

### Comprehensive Evaluation
- **LLM Metrics**: Perplexity, BLEU, ROUGE, BERTScore
- **Benchmark Tests**: MMLU, HellaSwag, ARC, GSM8K
- **Image Metrics**: FID, IS, LPIPS for generative models
- **Custom Metrics**: Domain-specific evaluations

### Experiment Tracking
- **Weights & Biases**: Experiment tracking and visualization
- **MLflow**: Model registry and experiment management
- **Model Comparison**: Side-by-side performance analysis

## Usage Examples

### Chat Completion

```python
import asyncio
from isa_model.inference.ai_factory import AIFactory

async def chat_example():
    factory = AIFactory.get_instance()
    llm = factory.get_llm("gpt-4o-mini", "openai", api_key="your-key")
    
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    response = await llm.achat(messages)
    print(response)

# Run the async function
asyncio.run(chat_example())
```

### Image Generation

```python
import asyncio
from isa_model.inference.ai_factory import AIFactory

async def image_gen_example():
    factory = AIFactory.get_instance()
    image_gen = factory.get_vision_model(
        "stability-ai/sdxl", 
        "replicate", 
        api_key="your-replicate-token"
    )
    
    result = await image_gen.generate_image(
        prompt="A beautiful sunset over mountains",
        width=1024,
        height=1024
    )
    
    # Save the generated image
    with open("generated_image.png", "wb") as f:
        f.write(result["image_data"])

asyncio.run(image_gen_example())
```

### Complete Training and Evaluation Workflow

```python
from isa_model.training import TrainingFactory
from isa_model.eval import EvaluationFactory

# Initialize factories
trainer = TrainingFactory()
evaluator = EvaluationFactory(use_wandb=True, wandb_project="my-project")

# Train model
model_path = trainer.train_model(
    model_name="google/gemma-2-4b-it",
    dataset_path="training_data.json",
    use_lora=True,
    num_epochs=3
)

# Evaluate model
results = evaluator.evaluate_llm(
    model_path=model_path,
    dataset_path="test_data.json",
    metrics=["bleu", "rouge", "accuracy"]
)

# Run benchmarks
benchmark_results = evaluator.run_benchmark(
    model_path=model_path,
    benchmark="mmlu"
)

# Compare with base model
comparison = evaluator.compare_models([
    "google/gemma-2-4b-it",  # Base model
    model_path  # Fine-tuned model
], benchmark="arc")

print(f"Training completed: {model_path}")
print(f"Evaluation results: {results}")
```

## What's New in v0.0.1

### 🎯 Training Framework
- **Multi-modal training**: LLM, Stable Diffusion, ML models
- **Cloud integration**: RunPod training support
- **LoRA/QLoRA**: Memory-efficient fine-tuning
- **HuggingFace integration**: Direct dataset loading and model uploading

### 📊 Evaluation Framework
- **Comprehensive metrics**: BLEU, ROUGE, perplexity, and more
- **Standard benchmarks**: MMLU, HellaSwag, ARC, GSM8K
- **Experiment tracking**: Weights & Biases and MLflow integration
- **Model comparison**: Side-by-side performance analysis

### 🔧 Enhanced Inference
- **Improved function calling**: Better tool binding and execution
- **Better error handling**: More informative error messages
- **Performance optimizations**: Faster model loading and inference

## Development

### Installing for Development

```bash
git clone <repository-url>
cd isA_Model
pip install -e .
```

### Running Tests

```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export REPLICATE_API_TOKEN="your-token"

# Run inference tests
python tests/units/inference/test_all_services.py

# Run training tests
python tests/test_training_setup.py
```

### Building and Publishing

```bash
# Build the package
python -m build

# Upload to PyPI (requires PYPI_API_TOKEN in .env.local)
source .venv/bin/activate
source .env.local
python -m twine upload dist/isa_model_sdk-0.0.1* --username __token__ --password "$PYPI_API_TOKEN"
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

## Support

For questions and support, please open an issue on our GitHub repository. 