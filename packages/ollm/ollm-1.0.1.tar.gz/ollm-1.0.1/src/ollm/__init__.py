# src/ollm/__init__.py
from .inference import Inference, AutoInference
from .utils import file_get_contents
from transformers import TextStreamer