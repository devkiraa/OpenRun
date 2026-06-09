class BaseAdapter:
    def load(self):
        pass

    def generate(self, input_data: list, stop=None) -> str:
        pass

    def stream(self, input_data: list, stop=None):
        raise NotImplementedError

    def unload(self):
        """Releases the model and garbage-collects GPU VRAM cache cleanly."""
        pass
