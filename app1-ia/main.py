# -*- coding: utf-8 -*- 
from app import app
from utils import get_prediction
from flask import Flask, jsonify, request


@app.route('/safecab/app1-ia/predict', methods=['POST'])
def predict():
    file = request.files['file']
    img_bytes = file.read()
    clase_id, clase_nombre = get_prediction(image_bytes=img_bytes)
    json_respuesta = {'clase_id': clase_id, 'clase_nombre': clase_nombre}
    print("responder: {}".format(json_respuesta))
    return jsonify(json_respuesta)


if __name__ == "__main__":
    app.run(port=7002)
