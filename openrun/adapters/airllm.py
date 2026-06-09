from openrun.adapters.base import BaseAdapter
import sys
import subprocess

class AirLLMAdapter(BaseAdapter):
    def __init__(self, model_name):
        self.model_name = model_name

    def load(self):
        import sys
        if 'optimum.bettertransformer' not in sys.modules:
            class DummyBetterTransformer:
                @staticmethod
                def transform(model):
                    # Return the model unmodified since BetterTransformer was deprecated
                    return model
            
            sys.modules['optimum.bettertransformer'] = type('dummy_optimum', (), {'BetterTransformer': DummyBetterTransformer})()

        try:
            from airllm import AutoModel
        except ModuleNotFoundError:
            print("\033[93m[WARNING] Missing AirLLM/Optimum dependencies. Auto-installing now...\033[0m")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "airllm", "optimum"], check=True)
            
            import importlib
            import site
            importlib.reload(site)
            # Clear partially loaded modules from cache
            for key in list(sys.modules.keys()):
                if key.startswith("airllm") or key.startswith("optimum"):
                    del sys.modules[key]
                    
            from airllm import AutoModel
            
        print(f"\033[96m[INFO] Loading AirLLM model '{self.model_name}'...\033[0m")
        try:
            self.model = AutoModel.from_pretrained(self.model_name)
        except Exception as e:
            err_str = str(e).lower()
            if "gated" in err_str or "restricted" in err_str or "403" in err_str:
                msg = (
                    f"\n\033[91m🛑 Gated Repository Access Restricted\033[0m\n"
                    f"You are trying to access a gated HuggingFace model: \033[93m{self.model_name}\033[0m\n"
                    f"Access to this model is restricted. You must be authorized to load it.\n\n"
                    f"👉 \033[96mHow to get access:\033[0m\n"
                    f"1. Visit the model page: https://huggingface.co/{self.model_name}\n"
                    f"2. Log in to Hugging Face, accept the terms, and click 'Request Access'.\n"
                )
                print(msg)
                raise RuntimeError(f"Gated Repository: Access to {self.model_name} is restricted. Visit https://huggingface.co/{self.model_name} to request access.")
            else:
                raise

    def generate(self, input_data, stop=None):
        prompt = input_data[-1]["content"]
        response = self.model.generate(prompt)
        if stop:
            stop_seqs = [stop] if isinstance(stop, str) else list(stop)
            for stop_seq in stop_seqs:
                if response.lower().endswith(stop_seq.lower()):
                    response = response[:-len(stop_seq)]
                    break
        return response

    def stream(self, input_data: list, stop=None):
        response = self.generate(input_data, stop=stop)
        for word in response.split():
            yield word + " "

    def unload(self):
        import gc
        import torch
        if hasattr(self, "model"):
            del self.model
        self.model = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()