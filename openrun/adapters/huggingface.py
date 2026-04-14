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
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        import warnings
        
        # Suppress verbose warnings related to torch_dtype payload
        warnings.filterWarning(action='ignore', category=UserWarning)

        # print(f"Loading HuggingFace model '{self.model_name}'...")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
        except RuntimeError as e:
            if "TORCH_LIBRARY" in str(e) or "triton" in str(e).lower():
                print("\n⚠️ PyTorch runtime conflict detected.")
                print("This happens in Jupyter/Colab when re-running cells.\n")
                print("👉 Fix: Restart your runtime and run again.")
                print("(Runtime → Restart session)\n")
            else:
                raise

    def generate(self, input_data: list) -> str:
        if not hasattr(self, "model") or not hasattr(self, "tokenizer"):
            raise RuntimeError("Model not loaded. Call load() first.")
        
        prompt = ""
        if input_data:
            for msg in input_data:
                prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
        prompt += "<|assistant|>\n"
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        generation_kwargs = {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }

        try:
            outputs = self.model.generate(
                **inputs,
                **generation_kwargs
            )

            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            if prompt in generated:
                generated = generated.split(prompt, 1)[-1]
            
            return generated.strip()
        except RuntimeError as e:
            if "TORCH_LIBRARY" in str(e) or "triton" in str(e).lower():
                print("\n⚠️ PyTorch runtime conflict detected.")
                print("This happens in Jupyter/Colab when re-running cells.\n")
                print("👉 Fix: Restart your runtime and run again.")
                print("(Runtime → Restart session)\n")
                return "Error: PyTorch runtime conflict. Restart session."
            else:
                raise

    def stream(self, input_data: list):
        try:
            from transformers import TextIteratorStreamer
            import threading

            prompt = ""
            for msg in input_data:
                prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
            prompt += "<|assistant|>\n"

            streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=True)

            inputs = self.tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            generation_kwargs = {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "streamer": streamer
            }

            thread = threading.Thread(
                target=self.model.generate,
                kwargs={
                    **inputs,
                    **generation_kwargs
                }
            )
            thread.daemon = True
            thread.start()

            for token in streamer:
                yield token

        except RuntimeError as e:
            if "TORCH_LIBRARY" in str(e) or "triton" in str(e).lower():
                print("\n⚠️ PyTorch runtime conflict detected.")
                print("This happens in Jupyter/Colab when re-running cells.\n")
                print("👉 Fix: Restart your runtime and run again.")
                print("(Runtime → Restart session)\n")
                yield "Error: PyTorch runtime conflict. Restart session."
            else:
                raise
        except Exception as e:
            print(f"⚠️ Streaming failed, falling back: {e}")

            # fallback to safe generation
            response = self.generate(input_data)
            for word in response.split():
                yield word + " "
