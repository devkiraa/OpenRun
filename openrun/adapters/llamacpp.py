from openrun.adapters.base import BaseAdapter
import sys
import subprocess
import os

class LlamaCppAdapter(BaseAdapter):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None

    def load(self):
        try:
            from llama_cpp import Llama
        except ImportError:
            print("\033[93m[WARNING] Missing llama-cpp-python dependencies. Auto-installing now...\033[0m")
            # Default to basic installation; users on specific hardware (CUDA/Metal) 
            # should follow llama-cpp-python's specific install guides for max speed.
            subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python"], check=True)
            from llama_cpp import Llama

        print(f"\033[96m[INFO] Loading GGUF model via llama.cpp: '{self.model_path}'...\033[0m")
        
        # Initialize Llama model
        # n_gpu_layers=-1 attempts to offload all layers to GPU if available
        self.model = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_gpu_layers=-1, 
            verbose=False
        )
        print("\033[92m✔ GGUF Model loaded successfully.\033[0m")

    def generate(self, input_data: list) -> str:
        if not self.model:
            raise RuntimeError("Model not loaded.")
            
        response = self.model.create_chat_completion(
            messages=input_data,
            stream=False
        )
        return response["choices"][0]["message"]["content"]

    def stream(self, input_data: list):
        if not self.model:
            raise RuntimeError("Model not loaded.")
            
        stream = self.model.create_chat_completion(
            messages=input_data,
            stream=True
        )
        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                yield delta["content"]

    def unload(self):
        if self.model:
            del self.model
            self.model = None
        import gc
        gc.collect()
