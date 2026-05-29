"""OpenRun core package."""

import importlib.metadata
import os
import re

# Automatically resolve HF_TOKEN in settings or Google Colab secrets and inject it into os.environ
if "HF_TOKEN" not in os.environ:
    try:
        settings_file = os.path.expanduser("~/.openrun/settings.json")
        if os.path.exists(settings_file):
            import json
            with open(settings_file, "r") as f:
                settings = json.load(f)
                token = settings.get("hf_token")
                if token:
                    os.environ["HF_TOKEN"] = token
    except Exception:
        pass

if "HF_TOKEN" not in os.environ:
    try:
        from google.colab import userdata  # type: ignore
        token = userdata.get("HF_TOKEN")
        if token:
            os.environ["HF_TOKEN"] = token
            try:
                from huggingface_hub import login
                login(token)
            except Exception:
                pass
    except Exception:
        pass

__version__ = None

# 1. Try to read from pyproject.toml in development workspace
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pyproject_path = os.path.join(os.path.dirname(current_dir), "pyproject.toml")
    if os.path.exists(pyproject_path):
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'^\s*version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                __version__ = match.group(1)
except Exception:
    pass

# 2. Fall back to installed package metadata
if not __version__:
    try:
        __version__ = importlib.metadata.version("openrun-llm")
    except importlib.metadata.PackageNotFoundError:
        __version__ = "dev"

from .server import serve

__all__ = ["serve"]
