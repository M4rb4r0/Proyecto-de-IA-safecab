# -*- coding: utf-8 -*- 
import os
import torch
from ultralytics import YOLO
from flask import Flask

app = Flask(__name__)

_env_model = os.environ.get('MODEL_FILE') or os.environ.get('MODEL_WEIGHTS')

_candidates = [
    _env_model,
    os.path.join('runs', 'detect', 'train', 'weights', 'best.pt'),
    'best.pt',
]

_weights = next((p for p in _candidates if p and os.path.exists(p)), None)

if _weights is None:
    raise FileNotFoundError(
        "No se encontró el modelo best.pt. Por favor:\n"
        "1. Copia best.pt al directorio de la app, o\n"
        "2. Colócalo en runs/detect/train/weights/best.pt, o\n"
        "3. Define MODEL_FILE=/ruta/completa/a/best.pt"
    )

print(f"Cargando pesos YOLO desde: {_weights}")
model = YOLO(_weights)
if torch.cuda.is_available():
    model.to('cuda')
try:
    model.model.eval()
except Exception:
    pass

# expose class names for utils
model_names = model.names if hasattr(model, 'names') else {}
print(f"Clases del modelo YOLO: {model_names}")
