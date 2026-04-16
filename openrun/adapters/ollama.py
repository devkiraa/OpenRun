from openrun.adapters.base import BaseAdapter
import subprocess
import sys
import json
import time
import requests

class OllamaAdapter(BaseAdapter):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def load(self):
        try:
            # Check if Ollama is running
            response = requests.get("http://127.0.0.1:11434/")
            if response.status_code != 200:
                print("\033[93m[WARNING] Ollama server returned an unusual status. It might not be ready yet.\033[0m")
        except requests.exceptions.ConnectionError:
            print("\033[91m[ERROR] Ollama is not running on http://127.0.0.1:11434.\033[0m")
            print("Please install Ollama from https://ollama.com and start the service.")
            print("You can run `ollama serve` in another terminal.")
            sys.exit(1)

        print(f"\033[96m[INFO] Loading Ollama model '{self.model_name}'...\033[0m")
        
        # Check if model exists, if not, pull it automatically
        models_resp = requests.get("http://127.0.0.1:11434/api/tags")
        models = [m["name"] for m in models_resp.json().get("models", [])]
        
        if self.model_name not in models and f"{self.model_name}:latest" not in models:
            print(f"\033[93m[INFO] Model '{self.model_name}' not found locally. Auto-pulling from Ollama registry. This might take a while...\033[0m")
            try:
                subprocess.run(["ollama", "pull", self.model_name], check=True)
            except FileNotFoundError:
                print("\033[91m[ERROR] The `ollama` CLI tool is not installed or not in your PATH.\033[0m")
                sys.exit(1)
            except subprocess.CalledProcessError:
                print("\033[91m[ERROR] Failed to pull the model using Ollama.\033[0m")
                sys.exit(1)

    def _convert_messages(self, input_data: list):
        # OpenRun standard array of {"role": x, "content": y} translates perfectly to Ollama Chat
        return input_data

    def generate(self, input_data: list) -> str:
        messages = self._convert_messages(input_data)
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        
        res = requests.post("http://127.0.0.1:11434/api/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        return data.get("message", {}).get("content", "")

    def stream(self, input_data: list):
        messages = self._convert_messages(input_data)
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True
        }
        
        with requests.post("http://127.0.0.1:11434/api/chat", json=payload, stream=True) as res:
            res.raise_for_status()
            for line in res.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk