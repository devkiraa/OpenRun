from openrun.adapters.base import BaseAdapter

class AirLLMAdapter(BaseAdapter):
    def __init__(self, model_name):
        self.model_name = model_name

    def load(self):
        from airllm import AutoModel
        self.model = AutoModel.from_pretrained(self.model_name)

    def generate(self, input_data):
        prompt = input_data[-1]["content"]
        return self.model.generate(prompt)

    def stream(self, input_data: list):
        response = self.generate(input_data)
        for word in response.split():
            yield word + " "