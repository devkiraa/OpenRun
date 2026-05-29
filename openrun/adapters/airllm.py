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
                    f"3. Create an Access Token: https://huggingface.co/settings/tokens\n"
                    f"4. Provide the token using the settings in the Web Playground, or log in via CLI:\n"
                    f"   \033[90mhuggingface-cli login\033[0m or by setting the HF_TOKEN environment variable.\n"
                )
                print(msg)
                raise RuntimeError(f"Gated Repository: Access to {self.model_name} is restricted. Visit https://huggingface.co/{self.model_name} to request access.")
            else:
                raise

    def generate(self, input_data):
        prompt = input_data[-1]["content"]
        return self.model.generate(prompt)

    def stream(self, input_data: list):
        response = self.generate(input_data)
        for word in response.split():
            yield word + " "