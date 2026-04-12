class BaseAdapter:
    def load(self):
        pass

    def generate(self, input_data: list) -> str:
        pass

    def stream(self, input_data: list):
        raise NotImplementedError
