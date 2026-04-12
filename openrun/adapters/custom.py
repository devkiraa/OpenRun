import importlib.util
import sys
import os
import inspect
from openrun.adapters.base import BaseAdapter

class CustomAdapter(BaseAdapter):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.custom_module = None
        self.target_func = None
        self.func_type = "prompt"

    def load(self):
        print(f"Loading custom model from '{self.file_path}'...")
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Custom model file not found: {self.file_path}")
        
        print("⚠️ Running custom code. Ensure it is trusted.")
        spec = importlib.util.spec_from_file_location("custom_model", self.file_path)
        self.custom_module = importlib.util.module_from_spec(spec)
        sys.modules["custom_model"] = self.custom_module
        spec.loader.exec_module(self.custom_module)
        
        if hasattr(self.custom_module, "generate"):
            self.target_func = self.custom_module.generate
        elif hasattr(self.custom_module, "chat"):
            self.target_func = self.custom_module.chat
            self.func_type = "messages"
        elif hasattr(self.custom_module, "predict"):
            self.target_func = self.custom_module.predict
        else:
            for name, obj in inspect.getmembers(self.custom_module, inspect.isfunction):
                try:
                    sig = inspect.signature(obj)
                    if len(sig.parameters) == 1:
                        self.target_func = obj
                        break
                except ValueError:
                    pass

        if not self.target_func:
            print("❌ No valid function found.")
            print("Define one of:")
            print("- generate(prompt)")
            print("- chat(messages)")
            print("- predict(prompt)")
            raise AttributeError("No valid function found in custom model.")

        print(f"🧠 Using function: {self.target_func.__name__}()")

    def generate(self, input_data: list) -> str:
        if not self.target_func:
            raise RuntimeError("Custom model not loaded. Call load() first.")
        
        if self.func_type == "messages":
            return self.target_func(input_data)
        else:
            prompt = input_data[-1]["content"] if input_data else ""
            return self.target_func(prompt)

    def stream(self, input_data: list):
        response = self.generate(input_data)
        for word in response.split():
            yield word + " "
