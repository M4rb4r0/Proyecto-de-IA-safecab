# -*- coding: utf-8 -*- 
import os
import torch
from ultralytics import YOLO
from flask import Flask

app = Flask(__name__)

_candidates = [
    'yolo8medium.pt',
    'yolo8nano.pt',
    os.path.join('runs', 'detect', 'train', 'weights', 'roboflow_dataset.pt'),
    os.path.join('runs', 'detect', 'train2', 'weights', 'roboflow_dataset.pt'),
    os.path.join('runs', 'detect', 'train3', 'weights', 'roboflow_dataset.pt'),
    os.path.join('runs', 'detect', 'train', 'roboflow_dataset.pt'),
    'roboflow_dataset.pt',
    'yolo11n.pt'
]
_weights = next((p for p in _candidates if os.path.exists(p)), 'yolo11n.pt')
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
