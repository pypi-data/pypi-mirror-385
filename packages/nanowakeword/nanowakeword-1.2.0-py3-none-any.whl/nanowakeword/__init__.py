import os
from nanowakeword.model import Model
from nanowakeword.vad import VAD

__all__ = ['Model', 'VAD']


MODELS = {
    "nanowakeword-lstm-base": {
        "model_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/models/nanowakeword-lstm-base.onnx"),
        "download_url": "https://huggingface.co/arcosoph/nanowakeword-lstm-base/resolve/main/nanowakeword-lstm-base.onnx"
    }

}

model_class_mappings = {
    "timer": {
        "1": "1_minute_timer"
    }
}


def get_pretrained_model_paths(inference_framework="tflite"):
    if inference_framework == "tflite":
        return [MODELS[i]["model_path"] for i in MODELS.keys()]
    elif inference_framework == "onnx":
        return [MODELS[i]["model_path"].replace(".tflite", ".onnx") for i in MODELS.keys()]



from pathlib import Path

_INIT_PY_PATH = Path(__file__).resolve()

PROJECT_ROOT = _INIT_PY_PATH.parent
