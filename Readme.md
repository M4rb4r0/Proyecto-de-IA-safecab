# CC6409 - PROYECTO DE IA

## Fecha: 13 de octubre de 2025

## Profesor: Juan Manuel Barrios

## Descripción del Proyecto – SafeCab: No+Chat

Hoy en Chile, la distracción del conductor ya es la causa de cerca del 40% de los accidentes de tránsito. Para las empresas con flotas vehiculares, esto no solo significa un riesgo humano enorme, sino también multas de hasta 160 mil pesos por infracción, suspensión de licencias, vehículos detenidos más de 60 días y primas de seguro laboral que se disparan con cada siniestro.

Nuestra solución es un sistema de cámara inteligente que detecta en tiempo real cuando un chofer se distrae con el celular. El conductor recibe una alerta inmediata y la empresa accede a reportes preventivos.

Así, con No+Chat, reducimos los accidentes, evitamos pérdidas millonarias y protegemos lo más valioso: la vida de los trabajadores y la seguridad de los demás.

# Probar localmente aplicación 1 (detección de objetos con YOLO)

En un terminal abrir la aplicación para usuarios:

```
cd app1-front
python main.py
 * Running on http://127.0.0.1:7001
```

En otro terminal abrir la aplicación con el módulo de IA:

```
cd app1-ia
python main.py
 * Running on http://127.0.0.1:7002
```

En el navegador entrar a http://127.0.0.1:7001/safe-cab/app1-front/ y hacer upload de una imagen. El backend ejecuta YOLO y devuelve `clase_id` y `clase_nombre` de la mejor detección. Si no hay detecciones, devuelve `-1` y `no_detection`.

# Entrenar el modelo YOLO con tu dataset

El dataset ya está en formato Ultralytics en `Distracted Driver Detection.v3i.yolov8/data.yaml`.

Para entrenar (crea `runs/detect/train/weights/best.pt`):

```
yolo train model=yolo11n.pt data="Distracted Driver Detection.v3i.yolov8/data.yaml" epochs=50 imgsz=640 project=runs name=train
```

Al reiniciar `app1-ia`, el backend cargará automáticamente `runs/detect/train/weights/best.pt` si existe; de lo contrario usará `yolo11n.pt` preentrenado.

# Solución de problemas

- **Puerto en uso (7001/7002)**: si aparece "Port XXXX is in use", cierre el proceso que usa el puerto o cambie el puerto en `app1-front/main.py` o `app1-ia/main.py`.
  - macOS: `lsof -i :7001` y luego `kill -9 <PID>`.
- **Plantilla no encontrada o error al renderizar**: la UI está en `app1-front/templates/index.html`. Asegúrese de abrir la ruta exacta `http://127.0.0.1:7001/safe-cab/app1-front/`.
