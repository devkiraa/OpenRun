from openrun.adapters.base import BaseAdapter
import sys
import subprocess

class VLLMAdapter(BaseAdapter):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.llm = None
        self.tokenizer = None

    def load(self):
        try:
            from vllm import LLM
        except ImportError:
            print("\033[93m[WARNING] Missing vLLM dependencies. Auto-installing now...\033[0m")
            subprocess.run([sys.executable, "-m", "pip", "install", "vllm"], check=True)
            from vllm import LLM

        print(f"\033[96m[INFO] Loading model via vLLM: '{self.model_name}'...\033[0m")
        
        # enable_prefix_caching=True provides a massive speedup for multi-turn conversations
        self.llm = LLM(
            model=self.model_name,
            enable_prefix_caching=True,
            trust_remote_code=True
        )
        print("\033[92m⚡ vLLM Engine active (Continuous Batching & Prefix Caching enabled)\033[0m")

    def _convert_to_prompt(self, messages: list) -> str:
        # vLLM's LLM class uses offline inference by default. 
        # For a truly OpenAI-compatible vLLM experience, one usually uses AsyncLLMEngine,
        # but for this adapter we'll wrap the basic LLM.
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"<|{role}|>\n{content}\n"
        prompt += "<|assistant|>\n"
        return prompt

    def generate(self, input_data: list, stop=None) -> str:
        from vllm import SamplingParams
        
        stop_seqs = None
        if stop:
            stop_seqs = [stop] if isinstance(stop, str) else list(stop)
            
        sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=200, stop=stop_seqs)
        prompt = self._convert_to_prompt(input_data)
        
        outputs = self.llm.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text

    def stream(self, input_data: list, stop=None):
        # The standard LLM.generate in vLLM is not streaming-friendly for simple scripts.
        # However, we can simulate it or encourage the use of vLLM's OpenAI server.
        # For the sake of this adapter, we will return the full response in chunks
        # since offline LLM.generate doesn't yield tokens one by one.
        response = self.generate(input_data, stop=stop)
        # To make it 'feel' like streaming even if the backend is offline:
        for word in response.split():
            yield word + " "

    def unload(self):
        if self.llm:
            # vLLM is notoriously hard to unload fully without killing the process
            # but we'll try our best.
            import gc
            import torch
            del self.llm
            self.llm = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
