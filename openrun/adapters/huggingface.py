from openrun.adapters.base import BaseAdapter
try:
    from transformers import pipeline
except ImportError:
    raise ImportError("Please install transformers: pip install transformers torch")

class HuggingFaceAdapter(BaseAdapter):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.generator = None

    def load(self):
        print(f"Loading HuggingFace model '{self.model_name}'...")
        self.generator = pipeline('text-generation', model=self.model_name, device_map="auto")

    def generate(self, input_data: list) -> str:
        if not self.generator:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        prompt = ""
        if input_data:
            for msg in input_data:
                prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
        prompt += "<|assistant|>\n"
        
        # Basic generation. Adjust max_new_tokens as needed.
        result = self.generator(prompt, max_new_tokens=200, num_return_sequences=1)
        generated_text = result[0]['generated_text']
        
        # Safely remove prompt if present
        if prompt in generated_text:
            generated_text = generated_text.split(prompt, 1)[-1].strip()
        
        return generated_text

    def stream(self, input_data: list):
        response = self.generate(input_data)
        for word in response.split():
            yield word + " "
