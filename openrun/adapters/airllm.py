from openrun.adapters.base import BaseAdapter
import sys
import subprocess

class AirLLMAdapter(BaseAdapter):
    def __init__(self, model_name):
        self.model_name = model_name

    def load(self):
        try:
            from airllm import AutoModel
        except ModuleNotFoundError:
            print("\033[93m[WARNING] Missing AirLLM/Optimum dependencies. Auto-installing now...\033[0m")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "airllm", "optimum"], check=True)
            from airllm import AutoModel
            
        print(f"\033[96m[INFO] Loading AirLLM model '{self.model_name}'...\033[0m")
        self.model = AutoModel.from_pretrained(self.model_name)

    def generate(self, input_data):
        prompt = input_data[-1]["content"]
        return self.model.generate(prompt)

    def stream(self, input_data: list):
        response = self.generate(input_data)
        for word in response.split():
            yield word + " "