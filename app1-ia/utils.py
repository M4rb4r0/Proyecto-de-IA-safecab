# -*- coding: utf-8 -*- 
import io
import cv2
import tempfile
import os
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
    
    # Buscar primero texting (prioridad alta)
    best_texting = None
    best_texting_conf = -1.0
    
    # Buscar safe-driving
    best_safe_driving = None
    best_safe_driving_conf = -1.0
    
    print(f"Total detecciones: {len(r.boxes)}")
    for b in r.boxes:
        conf = float(b.conf[0].item())
        cls_id_iter = int(b.cls[0].item())
        cls_name_iter = model_names.get(cls_id_iter, str(cls_id_iter)) if isinstance(model_names, dict) else str(cls_id_iter)
        print(f"  - Detección: clase_id={cls_id_iter}, clase_nombre='{cls_name_iter}', conf={conf:.3f}")
        
        # Detectar texting (día o noche)
        if 'texting' in cls_name_iter.lower():
            if conf > best_texting_conf:
                best_texting = b
                best_texting_conf = conf
        # Detectar safe driving (día o noche)
        elif 'safe' in cls_name_iter.lower():
            if conf > best_safe_driving_conf:
                best_safe_driving = b
                best_safe_driving_conf = conf
    
    # Prioridad: texting > safe-driving > no_detection
    if best_texting is not None:
        cls_id = int(best_texting.cls[0].item())
        cls_name = model_names.get(cls_id, str(cls_id)) if isinstance(model_names, dict) else str(cls_id)
        print("clase: {} {} conf: {:.3f}".format(cls_id, cls_name, best_texting_conf))
        return str(cls_id), cls_name
    elif best_safe_driving is not None:
        cls_id = int(best_safe_driving.cls[0].item())
        cls_name = model_names.get(cls_id, str(cls_id)) if isinstance(model_names, dict) else str(cls_id)
        print("clase: {} {} conf: {:.3f}".format(cls_id, cls_name, best_safe_driving_conf))
        return str(cls_id), cls_name
    else:
        print("sin detecciones de texting o safe-driving")
        return "-1", "no_detection"


def get_video_prediction(video_bytes, sample_rate=5):
    """
    Analiza un video frame por frame y devuelve estadísticas de detección.
    
    Args:
        video_bytes: bytes del archivo de video
        sample_rate: analizar 1 de cada N frames (default: 5 para optimizar)
    
    Returns:
        dict con total_frames, frames_analizados, texting_count, safe_driving_count, no_detection_count y porcentajes
    """
    print("procesando video...")
    
    # Guardar video temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(video_bytes)
        tmp_path = tmp_file.name
    
    try:
        cap = cv2.VideoCapture(tmp_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        texting_count = 0
        safe_driving_count = 0
        no_detection_count = 0
        frame_idx = 0
        frames_analizados = 0

        # Lista de frames donde se detectó texting (para agrupar en incidentes)
        texting_frames = []

        print(f"video: {total_frames} frames totales, {fps:.2f} fps")
        print(f"analizando 1 de cada {sample_rate} frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Analizar solo cada N frames
            if frame_idx % sample_rate == 0:
                # Convertir BGR (OpenCV) a RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Predecir
                results = model.predict(pil_image, imgsz=640, conf=0.25, verbose=False)
                r = results[0]
                
                # Clasificar frame en 3 categorías
                # Primero revisar TODAS las detecciones, texting tiene prioridad absoluta
                found_texting = False
                found_safe_driving = False

                if r.boxes is not None and len(r.boxes) > 0:
                    print(f"  Frame {frame_idx}: {len(r.boxes)} detecciones")

                    # Primero: buscar si hay algún texting en todas las detecciones
                    for b in r.boxes:
                        cls_id = int(b.cls[0].item())
                        cls_name = model_names.get(cls_id, str(cls_id)) if isinstance(model_names, dict) else str(cls_id)
                        conf = float(b.conf[0].item())
                        print(f"    - Clase: {cls_name} (id={cls_id}), conf={conf:.3f}")

                        if 'texting' in cls_name.lower():
                            found_texting = True

                    # Solo si no hay texting, buscar safe driving
                    if not found_texting:
                        for b in r.boxes:
                            cls_id = int(b.cls[0].item())
                            cls_name = model_names.get(cls_id, str(cls_id)) if isinstance(model_names, dict) else str(cls_id)
                            if 'safe' in cls_name.lower():
                                found_safe_driving = True
                                break
                else:
                    print(f"  Frame {frame_idx}: sin detecciones")
                
                # Prioridad: texting > safe driving > no_detection
                if found_texting:
                    texting_count += 1
                    texting_frames.append(frame_idx)
                    print(f"  -> Clasificado como: TEXTING")
                elif found_safe_driving:
                    safe_driving_count += 1
                    print(f"  -> Clasificado como: SAFE-DRIVING")
                else:
                    no_detection_count += 1
                    print(f"  -> Clasificado como: NO_DETECTION")
                
                frames_analizados += 1
                
                if frames_analizados % 10 == 0:
                    print(f"  procesados {frames_analizados} frames...")
            
            frame_idx += 1
        
        cap.release()

        # Calcular porcentajes
        porcentaje_texting = (texting_count / frames_analizados * 100) if frames_analizados > 0 else 0
        porcentaje_safe_driving = (safe_driving_count / frames_analizados * 100) if frames_analizados > 0 else 0
        porcentaje_no_detection = (no_detection_count / frames_analizados * 100) if frames_analizados > 0 else 0

        # Agrupar frames de texting en incidentes continuos
        # Frames con menos de 10 frames de diferencia se consideran parte del mismo incidente
        texting_incidents = []
        if texting_frames:
            # Umbral: frames separados por menos de 10*sample_rate frames originales
            gap_threshold = 10 * sample_rate

            incident_start = texting_frames[0]
            incident_end = texting_frames[0]

            for i in range(1, len(texting_frames)):
                current_frame = texting_frames[i]
                prev_frame = texting_frames[i - 1]

                if current_frame - prev_frame <= gap_threshold:
                    # Continúa el mismo incidente
                    incident_end = current_frame
                else:
                    # Nuevo incidente, guardar el anterior
                    texting_incidents.append({
                        'start_frame': incident_start,
                        'end_frame': incident_end,
                        'start_time': round(incident_start / fps, 2) if fps > 0 else 0,
                        'end_time': round(incident_end / fps, 2) if fps > 0 else 0,
                        'duration': round((incident_end - incident_start) / fps, 2) if fps > 0 else 0
                    })
                    incident_start = current_frame
                    incident_end = current_frame

            # Guardar el último incidente
            texting_incidents.append({
                'start_frame': incident_start,
                'end_frame': incident_end,
                'start_time': round(incident_start / fps, 2) if fps > 0 else 0,
                'end_time': round(incident_end / fps, 2) if fps > 0 else 0,
                'duration': round((incident_end - incident_start) / fps, 2) if fps > 0 else 0
            })

        print(f"Incidentes de texting detectados: {len(texting_incidents)}")
        for idx, inc in enumerate(texting_incidents):
            print(f"  Incidente {idx+1}: {inc['start_time']}s - {inc['end_time']}s (duración: {inc['duration']}s)")

        video_duration = round(total_frames / fps, 2) if fps > 0 else 0

        resultado = {
            'total_frames': total_frames,
            'frames_analizados': frames_analizados,
            'texting_count': texting_count,
            'safe_driving_count': safe_driving_count,
            'no_detection_count': no_detection_count,
            'porcentaje_texting': round(porcentaje_texting, 2),
            'porcentaje_safe_driving': round(porcentaje_safe_driving, 2),
            'porcentaje_no_detection': round(porcentaje_no_detection, 2),
            'fps': round(fps, 2),
            'sample_rate': sample_rate,
            'video_duration': video_duration,
            'texting_incidents': texting_incidents
        }
        
        print(f"resultado: {frames_analizados} frames analizados")
        print(f"  texting: {texting_count} ({porcentaje_texting:.2f}%)")
        print(f"  safe-driving: {safe_driving_count} ({porcentaje_safe_driving:.2f}%)")
        print(f"  no detection: {no_detection_count} ({porcentaje_no_detection:.2f}%)")
        
        return resultado
        
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
