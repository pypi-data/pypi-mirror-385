"""
test-monitoring-gpt2 LLM Service for Modal

Auto-generated service for model: gpt2
Architecture: gpt
"""

import modal
from typing import Dict, Any, List

app = modal.App("test-monitoring-gpt2")

image = modal.Image.debian_slim().pip_install(
    "transformers>=4.35.0", "torch>=2.0.0", "accelerate>=0.24.0", "httpx>=0.26.0", "numpy>=1.24.0", "requests>=2.31.0", "pydantic>=2.0.0"
)

@app.cls(
    image=image,
    gpu=modal.gpu.A10G(count=1),
    container_idle_timeout=300,
    memory=32768
)
class Test_Monitoring_Gpt2Service:
    
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.model = AutoModelForCausalLM.from_pretrained(
            "gpt2",
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
    
    @modal.method()
    def generate(self, messages: List[Dict[str, str]], **kwargs):
        # Generate response (simplified)
        prompt = messages[-1]["content"] if messages else ""
        return {"response": f"Generated response for: {prompt}", "model": "gpt2"}

@app.function(image=image)
@modal.web_endpoint(method="POST")
def inference_endpoint(item: Dict[str, Any]):
    service = Test_Monitoring_Gpt2Service()
    return service.generate(**item)
