# -*- coding: utf-8 -*- 
import io
from app import model, model_names
from PIL import Image


def get_prediction(image_bytes):
    print("evaluando imagen en la red...")
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    results = model.predict(image, imgsz=640, conf=0.25, verbose=False)
    r = results[0]
    if r.boxes is None or len(r.boxes) == 0:
        print("sin detecciones")
        return "-1", "no_detection"
    best = None
    best_conf = -1.0
    for b in r.boxes:
        conf = float(b.conf[0].item())
        cls_id_iter = int(b.cls[0].item())
        cls_name_iter = model_names.get(cls_id_iter, str(cls_id_iter)) if isinstance(model_names, dict) else str(cls_id_iter)
        if cls_name_iter != 'texting':
            continue
        if conf > best_conf:
            best = b
            best_conf = conf
    if best is None:
        print("sin detecciones de texting")
        return "-1", "no_detection"
    cls_id = int(best.cls[0].item())
    cls_name = model_names.get(cls_id, str(cls_id)) if isinstance(model_names, dict) else str(cls_id)
    print("clase: {} {} conf: {:.3f}".format(cls_id, cls_name, best_conf))
    return str(cls_id), cls_name
