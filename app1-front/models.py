# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime

DATABASE = 'safecab.db'


def get_db():
    """Obtiene conexión a la base de datos."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Inicializa la base de datos con las tablas necesarias."""
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS conductores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rut TEXT UNIQUE,
            turno TEXT DEFAULT 'dia',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conductor_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_grabacion DATE,
            turno TEXT,
            duracion_segundos REAL,
            total_frames INTEGER,
            frames_analizados INTEGER,
            fps REAL,
            porcentaje_texting REAL DEFAULT 0,
            porcentaje_safe REAL DEFAULT 0,
            porcentaje_undefined REAL DEFAULT 0,
            cantidad_incidentes INTEGER DEFAULT 0,
            procesado INTEGER DEFAULT 0,
            FOREIGN KEY (conductor_id) REFERENCES conductores(id)
        );

        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            conductor_id INTEGER NOT NULL,
            start_frame INTEGER,
            end_frame INTEGER,
            start_time REAL,
            end_time REAL,
            duracion REAL,
            fecha_incidente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            revisado INTEGER DEFAULT 0,
            FOREIGN KEY (video_id) REFERENCES videos(id),
            FOREIGN KEY (conductor_id) REFERENCES conductores(id)
        );
    ''')
    db.commit()
    db.close()


# ============ CONDUCTORES ============

def crear_conductor(nombre, rut=None, turno='dia'):
    """Crea un nuevo conductor."""
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO conductores (nombre, rut, turno) VALUES (?, ?, ?)',
            (nombre, rut, turno)
        )
        db.commit()
        conductor_id = cursor.lastrowid
        db.close()
        return conductor_id
    except sqlite3.IntegrityError:
        db.close()
        return None


def obtener_conductores():
    """Obtiene todos los conductores activos."""
    db = get_db()
    conductores = db.execute('''
        SELECT c.*,
               COUNT(DISTINCT v.id) as total_videos,
               COUNT(DISTINCT i.id) as total_incidentes,
               COALESCE(AVG(v.porcentaje_texting), 0) as promedio_texting
        FROM conductores c
        LEFT JOIN videos v ON c.id = v.conductor_id
        LEFT JOIN incidentes i ON c.id = i.conductor_id
        WHERE c.activo = 1
        GROUP BY c.id
        ORDER BY c.nombre
    ''').fetchall()
    db.close()
    return conductores


def obtener_conductor(conductor_id):
    """Obtiene un conductor por ID."""
    db = get_db()
    conductor = db.execute(
        'SELECT * FROM conductores WHERE id = ?', (conductor_id,)
    ).fetchone()
    db.close()
    return conductor


def eliminar_conductor(conductor_id):
    """Desactiva un conductor (soft delete)."""
    db = get_db()
    db.execute('UPDATE conductores SET activo = 0 WHERE id = ?', (conductor_id,))
    db.commit()
    db.close()


# ============ VIDEOS ============

def crear_video(conductor_id, filename, fecha_grabacion=None, turno=None):
    """Crea un registro de video."""
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO videos (conductor_id, filename, fecha_grabacion, turno)
           VALUES (?, ?, ?, ?)''',
        (conductor_id, filename, fecha_grabacion, turno)
    )
    db.commit()
    video_id = cursor.lastrowid
    db.close()
    return video_id


def actualizar_video_analisis(video_id, resultado):
    """Actualiza un video con los resultados del análisis."""
    db = get_db()
    db.execute('''
        UPDATE videos SET
            duracion_segundos = ?,
            total_frames = ?,
            frames_analizados = ?,
            fps = ?,
            porcentaje_texting = ?,
            porcentaje_safe = ?,
            porcentaje_undefined = ?,
            cantidad_incidentes = ?,
            procesado = 1
        WHERE id = ?
    ''', (
        resultado.get('video_duration', 0),
        resultado.get('total_frames', 0),
        resultado.get('frames_analizados', 0),
        resultado.get('fps', 0),
        resultado.get('porcentaje_texting', 0),
        resultado.get('porcentaje_safe_driving', 0),
        resultado.get('porcentaje_no_detection', 0),
        len(resultado.get('texting_incidents', [])),
        video_id
    ))
    db.commit()
    db.close()


def obtener_videos_conductor(conductor_id):
    """Obtiene todos los videos de un conductor."""
    db = get_db()
    videos = db.execute('''
        SELECT * FROM videos
        WHERE conductor_id = ?
        ORDER BY fecha_subida DESC
    ''', (conductor_id,)).fetchall()
    db.close()
    return videos


def obtener_video(video_id):
    """Obtiene un video por ID."""
    db = get_db()
    video = db.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
    db.close()
    return video


def eliminar_video(video_id):
    """Elimina un video y sus incidentes asociados."""
    db = get_db()
    # Primero eliminar incidentes
    db.execute('DELETE FROM incidentes WHERE video_id = ?', (video_id,))
    # Luego eliminar video
    db.execute('DELETE FROM videos WHERE id = ?', (video_id,))
    db.commit()
    db.close()


def resetear_video(video_id):
    """Resetea el análisis de un video (elimina incidentes y marca como no procesado)."""
    db = get_db()
    db.execute('DELETE FROM incidentes WHERE video_id = ?', (video_id,))
    db.execute('''
        UPDATE videos SET
            procesado = 0,
            porcentaje_texting = 0,
            porcentaje_safe = 0,
            porcentaje_undefined = 0,
            cantidad_incidentes = 0,
            duracion_segundos = NULL,
            total_frames = NULL,
            frames_analizados = NULL,
            fps = NULL
        WHERE id = ?
    ''', (video_id,))
    db.commit()
    db.close()


# ============ INCIDENTES ============

def crear_incidente(video_id, conductor_id, incident_data):
    """Crea un registro de incidente."""
    db = get_db()
    cursor = db.execute('''
        INSERT INTO incidentes
        (video_id, conductor_id, start_frame, end_frame, start_time, end_time, duracion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        video_id,
        conductor_id,
        incident_data.get('start_frame'),
        incident_data.get('end_frame'),
        incident_data.get('start_time'),
        incident_data.get('end_time'),
        incident_data.get('duration')
    ))
    db.commit()
    incidente_id = cursor.lastrowid
    db.close()
    return incidente_id


def obtener_incidentes_video(video_id):
    """Obtiene todos los incidentes de un video."""
    db = get_db()
    incidentes = db.execute('''
        SELECT * FROM incidentes
        WHERE video_id = ?
        ORDER BY start_time
    ''', (video_id,)).fetchall()
    db.close()
    return incidentes


def obtener_incidentes_conductor(conductor_id):
    """Obtiene todos los incidentes de un conductor."""
    db = get_db()
    incidentes = db.execute('''
        SELECT i.*, v.filename, v.fecha_grabacion
        FROM incidentes i
        JOIN videos v ON i.video_id = v.id
        WHERE i.conductor_id = ?
        ORDER BY i.fecha_incidente DESC
    ''', (conductor_id,)).fetchall()
    db.close()
    return incidentes


def obtener_incidentes_recientes(limite=10):
    """Obtiene los incidentes más recientes."""
    db = get_db()
    incidentes = db.execute('''
        SELECT i.*, v.filename, c.nombre as conductor_nombre
        FROM incidentes i
        JOIN videos v ON i.video_id = v.id
        JOIN conductores c ON i.conductor_id = c.id
        ORDER BY i.fecha_incidente DESC
        LIMIT ?
    ''', (limite,)).fetchall()
    db.close()
    return incidentes


def marcar_incidente_revisado(incidente_id):
    """Marca un incidente como revisado."""
    db = get_db()
    db.execute('UPDATE incidentes SET revisado = 1 WHERE id = ?', (incidente_id,))
    db.commit()
    db.close()


# ============ ESTADÍSTICAS ============

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del sistema."""
    db = get_db()
    stats = db.execute('''
        SELECT
            (SELECT COUNT(*) FROM conductores WHERE activo = 1) as total_conductores,
            (SELECT COUNT(*) FROM videos WHERE procesado = 1) as total_videos,
            (SELECT COUNT(*) FROM incidentes) as total_incidentes,
            (SELECT COUNT(*) FROM incidentes WHERE revisado = 0) as incidentes_pendientes,
            (SELECT COALESCE(AVG(porcentaje_texting), 0) FROM videos WHERE procesado = 1) as promedio_texting
    ''').fetchone()
    db.close()
    return stats


# Inicializar DB al importar
if not os.path.exists(DATABASE):
    init_db()
