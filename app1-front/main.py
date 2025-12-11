# -*- coding: utf-8 -*-
import os
import json
from app import app, IA_SERVER, IA_VIDEO_URL
from flask import request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
from utils import allowed_video
from models import (
    init_db, crear_conductor, obtener_conductores, obtener_conductor,
    eliminar_conductor, crear_video, actualizar_video_analisis,
    obtener_videos_conductor, obtener_video, crear_incidente,
    obtener_incidentes_video, obtener_incidentes_conductor,
    obtener_incidentes_recientes, obtener_estadisticas_generales,
    marcar_incidente_revisado, eliminar_video, resetear_video
)
import secrets
import requests

# Inicializar base de datos
init_db()


# ============ DASHBOARD ============

@app.route('/safecab/app1-front/')
def dashboard():
    """Dashboard principal con resumen y alertas."""
    stats = obtener_estadisticas_generales()
    conductores = obtener_conductores()
    incidentes_recientes = obtener_incidentes_recientes(5)
    return render_template('dashboard.html',
                           stats=stats,
                           conductores=conductores,
                           incidentes_recientes=incidentes_recientes)


# ============ CONDUCTORES ============

@app.route('/safecab/app1-front/conductores')
def lista_conductores():
    """Lista de todos los conductores."""
    conductores = obtener_conductores()
    return render_template('conductores.html', conductores=conductores)


@app.route('/safecab/app1-front/conductor/<int:conductor_id>')
def detalle_conductor(conductor_id):
    """Detalle de un conductor con sus videos e incidentes."""
    conductor = obtener_conductor(conductor_id)
    if not conductor:
        return redirect(url_for('lista_conductores'))

    videos = obtener_videos_conductor(conductor_id)
    incidentes = obtener_incidentes_conductor(conductor_id)
    return render_template('conductor_detalle.html',
                           conductor=conductor,
                           videos=videos,
                           incidentes=incidentes)


@app.route('/safecab/app1-front/conductor/nuevo', methods=['GET', 'POST'])
def nuevo_conductor():
    """Crear nuevo conductor."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        rut = request.form.get('rut')
        turno = request.form.get('turno', 'dia')

        if nombre:
            conductor_id = crear_conductor(nombre, rut, turno)
            if conductor_id:
                return redirect(url_for('detalle_conductor', conductor_id=conductor_id))
            else:
                return render_template('conductor_form.html', error='El RUT ya existe')

    return render_template('conductor_form.html')


@app.route('/safecab/app1-front/conductor/<int:conductor_id>/eliminar', methods=['POST'])
def eliminar_conductor_route(conductor_id):
    """Eliminar (desactivar) un conductor."""
    eliminar_conductor(conductor_id)
    return redirect(url_for('lista_conductores'))


# ============ VIDEOS ============

@app.route('/safecab/app1-front/conductor/<int:conductor_id>/subir', methods=['GET', 'POST'])
def subir_video(conductor_id):
    """Subir y analizar video de un conductor."""
    conductor = obtener_conductor(conductor_id)
    if not conductor:
        return redirect(url_for('lista_conductores'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('subir_video.html', conductor=conductor,
                                   error='No se envió ningún archivo')

        file = request.files['file']
        if not file or file.filename == '':
            return render_template('subir_video.html', conductor=conductor,
                                   error='No se seleccionó ningún archivo')

        if not allowed_video(file.filename):
            return render_template('subir_video.html', conductor=conductor,
                                   error='Formato no permitido. Use MP4, AVI, MOV, MKV o WEBM.')

        # Guardar archivo
        filename = secrets.token_hex(nbytes=8) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)

        # Obtener datos adicionales
        fecha_grabacion = request.form.get('fecha_grabacion')
        turno = request.form.get('turno', 'dia')
        sample_rate = request.form.get('sample_rate', 5, type=int)

        # Crear registro de video
        video_id = crear_video(conductor_id, filename, fecha_grabacion, turno)

        # Enviar a análisis
        try:
            files = {'file': open(filepath, 'rb')}
            data = {'sample_rate': sample_rate}
            response = requests.post(IA_SERVER + IA_VIDEO_URL, files=files, data=data)

            if response.status_code == 200:
                resultado = response.json()

                # Actualizar video con resultados
                actualizar_video_analisis(video_id, resultado)

                # Crear incidentes
                for incident in resultado.get('texting_incidents', []):
                    crear_incidente(video_id, conductor_id, incident)

                return redirect(url_for('ver_video', video_id=video_id))
            else:
                return render_template('subir_video.html', conductor=conductor,
                                       error='Error al procesar el video')
        except Exception as e:
            return render_template('subir_video.html', conductor=conductor,
                                   error=f'Error: {str(e)}')

    return render_template('subir_video.html', conductor=conductor)


@app.route('/safecab/app1-front/video/<int:video_id>')
def ver_video(video_id):
    """Ver resultados de análisis de un video."""
    video = obtener_video(video_id)
    if not video:
        return redirect(url_for('dashboard'))

    conductor = obtener_conductor(video['conductor_id'])
    incidentes = obtener_incidentes_video(video_id)

    return render_template('video_detalle.html',
                           video=video,
                           conductor=conductor,
                           incidentes=incidentes)


@app.route('/safecab/app1-front/display/<filename>')
def display_file(filename):
    """Servir archivos subidos."""
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/safecab/app1-front/video/<int:video_id>/eliminar', methods=['POST'])
def eliminar_video_route(video_id):
    """Eliminar un video y sus registros."""
    video = obtener_video(video_id)
    if not video:
        return redirect(url_for('dashboard'))

    conductor_id = video['conductor_id']
    filename = video['filename']

    # Eliminar archivo físico
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    # Eliminar registros de la base de datos
    eliminar_video(video_id)

    return redirect(url_for('detalle_conductor', conductor_id=conductor_id))


@app.route('/safecab/app1-front/video/<int:video_id>/reanalizar', methods=['POST'])
def reanalizar_video(video_id):
    """Re-analizar un video existente."""
    video = obtener_video(video_id)
    if not video:
        return redirect(url_for('dashboard'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], video['filename'])
    if not os.path.exists(filepath):
        return redirect(url_for('ver_video', video_id=video_id))

    # Obtener sample_rate del form o usar default
    sample_rate = request.form.get('sample_rate', 5, type=int)

    # Resetear análisis anterior
    resetear_video(video_id)

    # Re-analizar
    try:
        files = {'file': open(filepath, 'rb')}
        data = {'sample_rate': sample_rate}
        response = requests.post(IA_SERVER + IA_VIDEO_URL, files=files, data=data)

        if response.status_code == 200:
            resultado = response.json()
            actualizar_video_analisis(video_id, resultado)

            for incident in resultado.get('texting_incidents', []):
                crear_incidente(video_id, video['conductor_id'], incident)

    except Exception as e:
        print(f"Error re-analizando video: {e}")

    return redirect(url_for('ver_video', video_id=video_id))


# ============ INCIDENTES ============

@app.route('/safecab/app1-front/incidente/<int:incidente_id>/revisar', methods=['POST'])
def revisar_incidente(incidente_id):
    """Marcar incidente como revisado."""
    marcar_incidente_revisado(incidente_id)
    return jsonify({'success': True})


# ============ API ============

@app.route('/safecab/app1-front/api/stats')
def api_stats():
    """API para obtener estadísticas."""
    stats = obtener_estadisticas_generales()
    return jsonify(dict(stats))


if __name__ == "__main__":
    app.run(port=7001)
