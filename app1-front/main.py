# -*- coding: utf-8 -*- 
import os
import json
import csv
from io import StringIO
from app import app, IA_SERVER, IA_URL, IA_VIDEO_URL
from flask import request, redirect, url_for, render_template, session, make_response
from werkzeug.utils import secure_filename
from utils import allowed_file, allowed_video
import secrets
import requests

@app.route('/safecab/app1-front/')
def index_form():
    return render_template('index.html')


@app.route('/safecab/app1-front/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        error = 'No se envió ningún archivo'
        return render_template('index.html', error=error)
    file = request.files['file']
    if not file or file.filename == '':
        error = 'No se seleccionó ningún archivo'
        return render_template('index.html', error=error)
    if not allowed_file(file.filename):
        error = 'Archivo no permitido. Solo se permite JPG, JPEG o PNG.'
        return render_template('index.html', error=error)
    filename = secrets.token_hex(nbytes=8) + '_' + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print("guardando archivo " + filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    files = {'file': open(filepath, 'rb')}
    print("llamando a " + IA_SERVER + IA_URL)
    try:
        apicall = requests.post(IA_SERVER + IA_URL, files=files)
        if apicall.status_code != 200:
            error = 'Error contactando la aplicación IA'
            return render_template('index.html', error=error)
        api_json = json.loads(apicall.content.decode('utf-8'))
        return render_template('index.html', filename=filename, result=api_json)
    except Exception as e:
        error = 'Error: {}'.format(e)
        print (error)
        return render_template('index.html', error=error)


@app.route('/safecab/app1-front/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/safecab/app1-front/upload-video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        error = 'No se envió ningún archivo'
        return render_template('index.html', error=error)
    file = request.files['file']
    if not file or file.filename == '':
        error = 'No se seleccionó ningún archivo'
        return render_template('index.html', error=error)
    if not allowed_video(file.filename):
        error = 'Archivo no permitido. Solo se permite MP4, AVI, MOV, MKV o WEBM.'
        return render_template('index.html', error=error)
    
    filename = secrets.token_hex(nbytes=8) + '_' + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print("guardando video " + filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    
    # Obtener sample_rate del formulario (opcional)
    sample_rate = request.form.get('sample_rate', 5, type=int)
    
    files = {'file': open(filepath, 'rb')}
    data = {'sample_rate': sample_rate}
    print("llamando a " + IA_SERVER + IA_VIDEO_URL)
    try:
        apicall = requests.post(IA_SERVER + IA_VIDEO_URL, files=files, data=data)
        if apicall.status_code != 200:
            error = 'Error contactando la aplicación IA'
            return render_template('index.html', error=error)
        api_json = json.loads(apicall.content.decode('utf-8'))
        
        # Guardar los resultados en la sesión para exportación posterior
        session['last_video_result'] = api_json
        session['last_video_filename'] = filename
        
        return render_template('index.html', filename=filename, video_result=api_json, is_video=True)
    except Exception as e:
        error = 'Error: {}'.format(e)
        print(error)
        return render_template('index.html', error=error)


@app.route('/safecab/app1-front/export-csv')
def export_csv():
    """Exportar resultados del último video analizado como CSV"""
    video_result = session.get('last_video_result')
    video_filename = session.get('last_video_filename', 'video')
    
    if not video_result or 'frame_details' not in video_result:
        return "No hay resultados de video disponibles para exportar", 404
    
    # Crear CSV en memoria
    si = StringIO()
    csv_writer = csv.writer(si)
    
    # Escribir encabezados
    csv_writer.writerow(['Frame', 'Timestamp (s)', 'Clasificación', 'Confianza'])
    
    # Escribir datos de cada frame
    for frame_data in video_result['frame_details']:
        csv_writer.writerow([
            frame_data['frame_number'],
            frame_data['timestamp'],
            frame_data['clasificacion'],
            frame_data['confianza']
        ])
    
    # Agregar resumen al final
    csv_writer.writerow([])
    csv_writer.writerow(['=== RESUMEN ==='])
    csv_writer.writerow(['Total frames', video_result['total_frames']])
    csv_writer.writerow(['Frames analizados', video_result['frames_analizados']])
    csv_writer.writerow(['Sample rate', f"1 de cada {video_result['sample_rate']}"])
    csv_writer.writerow(['FPS', video_result['fps']])
    csv_writer.writerow([])
    csv_writer.writerow(['Texting (frames)', video_result['texting_count']])
    csv_writer.writerow(['Texting (%)', video_result['porcentaje_texting']])
    csv_writer.writerow(['Safe driving (frames)', video_result['safe_driving_count']])
    csv_writer.writerow(['Safe driving (%)', video_result['porcentaje_safe_driving']])
    csv_writer.writerow(['No detection (frames)', video_result['no_detection_count']])
    csv_writer.writerow(['No detection (%)', video_result['porcentaje_no_detection']])
    
    # Crear respuesta con CSV
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=safecab_resultados_{video_filename}.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    
    return output


if __name__ == "__main__":
    app.run(port=7003)

