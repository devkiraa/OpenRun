from openrun.adapters.base import BaseAdapter
try:
    from transformers import pipeline
except ImportError:
    raise ImportError("Please install transformers: pip install transformers torch")

class HuggingFaceAdapter(BaseAdapter):
    def __init__(self, model_name: str, quantize: str = None, low_cpu_mem: bool = False, draft_model_name: str = None):
        self.model_name = model_name
        self.quantize = quantize  # "4bit", "8bit", or None
        self.low_cpu_mem = low_cpu_mem
        self.draft_model_name = draft_model_name
        self.generator = None
        self.draft_model = None


    def load(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        import warnings
        
        # Suppress verbose warnings related to torch_dtype payload
        warnings.filterwarnings(action='ignore', category=UserWarning)

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Auto-detect best attention implementation for this GPU
            attn_impl = "eager"  # safe default
            if torch.cuda.is_available():
                try:
                    cap = torch.cuda.get_device_capability()
                    if cap[0] >= 8:  # Ampere+ (A100, A10G, RTX 30xx/40xx)
                        try:
                            import flash_attn  # noqa: F401
                            attn_impl = "flash_attention_2"
                            print("\033[92m⚡ Flash Attention 2 enabled (Ampere+ GPU detected)\033[0m")
                        except ImportError:
                            attn_impl = "sdpa"
                            print("\033[90m⚡ Using SDPA attention (install flash-attn for even faster inference)\033[0m")
                    else:
                        attn_impl = "sdpa"
                except Exception:
                    attn_impl = "sdpa"

            model_kwargs = {
                "device_map": "auto",
                "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            }
            if self.low_cpu_mem:
                model_kwargs["low_cpu_mem_usage"] = True
                print("\033[92m💾 Lazy model offloading & memory mapping enabled (low host RAM mode)\033[0m")
            if attn_impl != "eager":
                model_kwargs["attn_implementation"] = attn_impl

            # Apply bitsandbytes quantization if requested
            if self.quantize and torch.cuda.is_available():
                try:
                    from transformers import BitsAndBytesConfig
                    if self.quantize == "4bit":
                        model_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_quant_type="nf4",
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_use_double_quant=True,
                        )
                        # Remove torch_dtype when using quantization config
                        model_kwargs.pop("torch_dtype", None)
                        print("\033[92m🗜️  4-bit quantization enabled (50-75% VRAM reduction)\033[0m")
                    elif self.quantize == "8bit":
                        model_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_8bit=True,
                        )
                        model_kwargs.pop("torch_dtype", None)
                        print("\033[92m🗜️  8-bit quantization enabled (40-50% VRAM reduction)\033[0m")
                except ImportError:
                    print("\033[93m⚠️  bitsandbytes not installed. Run: pip install bitsandbytes\033[0m")
                    print("\033[93m   Falling back to full precision.\033[0m")

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs,
            )

            # Load draft model for Speculative Decoding if requested
            if self.draft_model_name:
                print(f"\033[96m🚀 Loading draft model for Speculative Decoding: {self.draft_model_name}\033[0m")
                try:
                    self.draft_model = AutoModelForCausalLM.from_pretrained(
                        self.draft_model_name,
                        torch_dtype=model_kwargs.get("torch_dtype", torch.float16),
                        device_map="auto"
                    )
                    print("\033[92m⚡ Speculative Decoding active (Draft model loaded)\033[0m")
                except Exception as e:
                    print(f"\033[93m⚠️ Failed to load draft model: {e}. Falling back to standard inference.\033[0m")

            # PyTorch 2.0+ JIT compilation for 15-30% sustained speedup
            if hasattr(torch, "compile") and torch.cuda.is_available():
                try:
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                    print("\033[92m⚡ torch.compile() enabled (PyTorch 2.0+ JIT)\033[0m")
                except Exception:
                    pass  # Gracefully skip if compilation fails

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
            elif isinstance(e, RuntimeError) and ("TORCH_LIBRARY" in str(e) or "triton" in str(e).lower()):
                print("\n⚠️ PyTorch runtime conflict detected.")
                print("This happens in Jupyter/Colab when re-running cells.\n")
                print("👉 Fix: Restart your runtime and run again.")
                print("(Runtime → Restart session)\n")
                raise
            else:
                raise

    def _prune_history(self, messages: list, max_tokens: int = 4096) -> list:
        if not messages:
            return messages
            
        def estimate_tokens(msgs):
            total = 0
            for m in msgs:
                total += len(m.get("content", "").split()) * 1.3 + 10
            return total

        # If the whole history fits inside the token budget, return it unmodified
        if estimate_tokens(messages) <= max_tokens:
            return messages

        # Otherwise, prune the oldest non-system turns while keeping the system prompt intact
        system_msg = None
        other_msgs = list(messages)
        if other_msgs and other_msgs[0].get("role") == "system":
            system_msg = other_msgs.pop(0)

        while other_msgs and estimate_tokens([system_msg] + other_msgs if system_msg else other_msgs) > max_tokens:
            if len(other_msgs) <= 1:
                # Keep at least the latest user query
                break
            other_msgs.pop(0)

        print(f"\033[93m✂️ Context budget exceeded! Pruned oldest message(s) to fit {max_tokens} token window.\033[0m")
        return [system_msg] + other_msgs if system_msg else other_msgs

    def generate(self, input_data: list) -> str:
        if not hasattr(self, "model") or not hasattr(self, "tokenizer"):
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Prune conversation history dynamically to fit token budget and protect memory
        input_data = self._prune_history(input_data)

        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(input_data, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer(prompt, return_tensors="pt")
            prompt_length = inputs["input_ids"].shape[1]
        else:
            prompt = ""
            if input_data:
                for msg in input_data:
                    prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
            prompt += "<|assistant|>\n"
            inputs = self.tokenizer(prompt, return_tensors="pt")
            prompt_length = inputs["input_ids"].shape[1]
        
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        generation_kwargs = {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }

        if self.draft_model:
            generation_kwargs["assistant_model"] = self.draft_model

        try:
            outputs = self.model.generate(
                **inputs,
                **generation_kwargs
            )

            # slice the output to skip the prompt
            outputs = outputs[0][prompt_length:]
            generated = self.tokenizer.decode(outputs, skip_special_tokens=True)
            
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

            # Prune conversation history dynamically to fit token budget and protect memory
            input_data = self._prune_history(input_data)

            if hasattr(self.tokenizer, "apply_chat_template"):
                prompt = self.tokenizer.apply_chat_template(input_data, tokenize=False, add_generation_prompt=True)
            else:
                prompt = ""
                for msg in input_data:
                    prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
                prompt += "<|assistant|>\n"

            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)

            inputs = self.tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            generation_kwargs = {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "streamer": streamer
            }

            if self.draft_model:
                generation_kwargs["assistant_model"] = self.draft_model

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

    def unload(self):
        import gc
        import torch

        # Remove model, generator, and tokenizer attributes
        if hasattr(self, "model"):
            del self.model
        if hasattr(self, "tokenizer"):
            del self.tokenizer
        if hasattr(self, "generator"):
            del self.generator

        self.model = None
        self.tokenizer = None
        self.generator = None

        # Clean garbage and free PyTorch cache
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
