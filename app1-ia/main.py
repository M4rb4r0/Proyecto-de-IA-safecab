# -*- coding: utf-8 -*- 
from app import app
from utils import get_prediction, get_video_prediction
from flask import Flask, jsonify, request
import logging


@app.route('/safecab/app1-ia/predict', methods=['POST'])
def predict():
    try:
        logging.basicConfig(level=logging.INFO)
        file = request.files.get('file')
        if file is None:
            logging.error("request sin archivo 'file'")
            return jsonify({'error': "campo 'file' ausente"}), 400
        filename = getattr(file, 'filename', None)
        mimetype = getattr(file, 'mimetype', None)
        clen = request.content_length
        logging.info(f"recibido archivo: name={filename} mimetype={mimetype} content_length={clen}")
        img_bytes = file.read()
        logging.info(f"tamaño bytes leídos: {len(img_bytes) if img_bytes else 0}")
        clase_id, clase_nombre = get_prediction(image_bytes=img_bytes)
        json_respuesta = {'clase_id': clase_id, 'clase_nombre': clase_nombre}
        logging.info(f"respuesta: {json_respuesta}")
        return jsonify(json_respuesta)
    except Exception as e:
        logging.exception("error procesando /safe-cab/app1-ia/predict")
        return jsonify({'error': str(e)}), 500


@app.route('/safecab/app1-ia/classes', methods=['GET'])
def get_classes():
    """Endpoint para ver las clases del modelo"""
    from app import model_names
    return jsonify({'classes': model_names})


@app.route('/safecab/app1-ia/predict-video', methods=['POST'])
def predict_video():
    try:
        logging.basicConfig(level=logging.INFO)
        file = request.files.get('file')
        if file is None:
            logging.error("request sin archivo 'file'")
            return jsonify({'error': "campo 'file' ausente"}), 400
        
        filename = getattr(file, 'filename', None)
        mimetype = getattr(file, 'mimetype', None)
        clen = request.content_length
        logging.info(f"recibido video: name={filename} mimetype={mimetype} content_length={clen}")
        
        video_bytes = file.read()
        logging.info(f"tamaño bytes leídos: {len(video_bytes) if video_bytes else 0}")
        
        # Obtener sample_rate del request (opcional)
        sample_rate = request.form.get('sample_rate', 5, type=int)
        
        resultado = get_video_prediction(video_bytes=video_bytes, sample_rate=sample_rate)
        logging.info(f"respuesta: {resultado}")
        
        return jsonify(resultado)
    except Exception as e:
        logging.exception("error procesando /safecab/app1-ia/predict-video")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(port=7002)
