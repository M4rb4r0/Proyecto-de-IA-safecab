# Ejercicio 3 - CC6409 - PROYECTO DE IA

## Fecha: 01 de octubre de 2025

## Profesor: Juan Manuel Barrios

# 1. Configurar ambiente Python con Miniforge

Existen varias formas de instalar Python. Se recomienda usar **MiniForge** https://conda-forge.org/ que es una distribución de python que ofrece un administrador de paquetes (`conda`) y que usa un repositorio de paquetes libre (llamado `conda-forge`).

Existen otras distribuciones de python basadas en `conda` (como _Anaconda_ y _MiniConda_) que son gratuitas pero utilizan repositorios de paquetes que no son de libre de uso. Más detalles en https://www.anaconda.com/blog/is-conda-free

Al crear un ambiente con `conda` se instala el intérprete de python y también se instala `pip` para descargar librerías. A veces se vuelve difícil lograr compatibilidad entre todas las librerías, por lo que hay que probar instalando con `pip` o con `conda` o cambiando python a una versión más antigua.

## (opcional) Instalar MiniForge en Windows

1. En el panel de configuración de Windows entrar a "Aplicaciones" y "Alias de ejecución de aplicaciones". Aparece un listado de programas, desactivar "python.exe" y "python3.exe" que está asociado a "Instalador de aplicación". Si no se hace esto, al escribir "python" Windows abrirá el Microsoft Store.

2. Entrar a https://conda-forge.org/download/ y descargar el instalador para Windows.

3. Doble click en el instalador `Miniforge3-Windows-x86_64.exe`

4. Seleccionar instalación recomendada (usar "Just me") y ruta de instalación por defecto (propone `%USERPROFILE%\miniconda3`)

5. Aceptar configuración propuesta (crear accesos directos, no agregar al PATH, no registrar como intérprete python por defecto)

6. Para abrir un terminal python, en el menú de inicio de Windows buscar "Miniforge Prompt"

## Instalar MiniForge en Linux o MacOS

1. Entrar a https://conda-forge.org/download/ y descargar el instalador: `wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh`

2. Abrir un terminal y ejecutar el script descargado: `bash Miniforge3-Linux-x86_64.sh`

Aparece este mensaje:

```
In order to continue the installation process, please review the license agreement.
Please, press ENTER to continue
```

Presionar la tecla ENTER.

Aparece la licencia (avanzar página o presionar 'q')

```
Do you accept the license terms? [yes|no]
```

Escribir "yes".

Pregunta la ruta de instalación:

```
Miniforge3 will now be installed into this location:
[$HOME/miniforge3] >>>
```

Presionar la tecla ENTER.

Al finalizar pregunta si modifica el script de inicio (`$HOME/.bashrc`):

```
Do you wish to update your shell profile to automatically initialize conda?
```

Escribir "yes".

3. Ejecutar `source $HOME/.bashrc` o abrir un nuevo terminal para usar la nueva configuración.

4. Si al hacer login el prompt del terminal dice `(base)` es porque conda está activado. Se recomienda activarlo manualmente y no dejarlo activo por defecto. Para eso ejecutar el comando: `conda config --set auto_activate_base false` y cerrar el terminal.

# 2. Crear ambiente conda para aplicaciones Flask

Las aplicaciónes web usan servicios REST segun el framework Flask.
Para hacer llamadas a servicios REST externos usan la librería `requests`.

Para este ejemplo basta crear un único ambiente para las dos aplicaciones.
Por compatibilidad entre librerías se recomienda usar python 3.11.

```
conda update --all
conda create -n ejercicio3 python=3.11
conda activate ejercicio3
conda install python=3.11 flask requests
conda install cudatoolkit
pip install torch torchvision torchaudio chardet
pip install ultralytics opencv-python pillow
```

# Probar localmente aplicación 1 (detección de objetos con YOLO)

En un terminal abrir la aplicación para usuarios:

```
conda activate ejercicio3
cd app1-front
python main.py
 * Running on http://127.0.0.1:7001
```

En otro terminal abrir la aplicación con el módulo de IA:

```
conda activate ejercicio3
cd app1-ia
python main.py
 * Running on http://127.0.0.1:7002
```

En el navegador entrar a http://127.0.0.1:7001/ejercicio3/app1-front/ y hacer upload de una imagen. El backend ejecuta YOLO y devuelve `clase_id` y `clase_nombre` de la mejor detección. Si no hay detecciones, devuelve `-1` y `no_detection`.

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
- **Plantilla no encontrada o error al renderizar**: la UI está en `app1-front/templates/index.html`. Asegúrese de abrir la ruta exacta `http://127.0.0.1:7001/ejercicio3/app1-front/`.
