#!/bin/bash

function runTest() {
        echo "[`date "+%F %T"`]\$ $@"
        "$@"
        if [[ $? -ne 0 ]]; then
                echo "** ERROR IN $@"
                exit 1
        fi
}

cd `dirname "$0"`
BASE_DIR=`pwd`

AMBIENTE="safecab-ia"
APPS_DESTINATION="$HOME/safecab-ia-server"

echo "=== Instalación del Servidor IA (puerto 7060) ==="
echo "Este script configura el servidor de IA en un directorio separado"
echo ""


if [[ -d "$HOME/miniforge3" ]]; then
    CONDA_PATH="$HOME/miniforge3"
elif [[ -d "$HOME/miniconda3" ]]; then
    CONDA_PATH="$HOME/miniconda3"
elif [[ -d "$HOME/anaconda3" ]]; then
    CONDA_PATH="$HOME/anaconda3"
else
    echo "Error: No se encontró instalación de conda"
    echo "Instale miniforge3, miniconda o anaconda primero"
    echo ""
    echo "Para instalar miniforge:"
    echo "  cd ~"
    echo "  wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
    echo "  bash Miniforge3-Linux-x86_64.sh -b"
    echo "  ~/miniforge3/bin/conda init bash"
    echo "  source ~/.bashrc"
    exit 1
fi

if ! "$CONDA_PATH/bin/conda" env list | grep -q "^$AMBIENTE "; then
    echo "Creando ambiente conda '$AMBIENTE'..."
    runTest "$CONDA_PATH/bin/conda" create -n "$AMBIENTE" python=3.11 -y
fi

echo "Instalando dependencias en ambiente '$AMBIENTE'..."
source "$CONDA_PATH/bin/activate" "$AMBIENTE"
runTest pip install gunicorn flask torch torchvision pillow ultralytics opencv-python

runTest mkdir -p "$APPS_DESTINATION"

echo "Instalando app1-ia en $APPS_DESTINATION ..."

if [[ -f "$BASE_DIR/bajar.sh" ]]; then
    echo "[`date "+%F %T"`]\$ bash $BASE_DIR/bajar.sh"
    bash "$BASE_DIR/bajar.sh" 2>/dev/null || true
fi

runTest cp -r "../../app1-ia/" "$APPS_DESTINATION/"
runTest cp "subir.sh" "bajar.sh" "$APPS_DESTINATION"
runTest chmod +x "$APPS_DESTINATION/subir.sh" "$APPS_DESTINATION/bajar.sh"
runTest bash "$APPS_DESTINATION/subir.sh"

echo ""
echo "=== Instalación completada ==="
echo "Servidor IA instalado en: $APPS_DESTINATION"
echo "Puerto: 7060"
echo "Accesible desde: http://10.0.218.101:7060/safecab/app1-ia/predict"
echo ""
echo "Comandos útiles:"
echo "  Iniciar:  bash $APPS_DESTINATION/subir.sh"
echo "  Detener:  bash $APPS_DESTINATION/bajar.sh"
echo "  Ver logs: tail -f $APPS_DESTINATION/logs/error.log"
echo "  Ver procesos: ps aux | grep gunicorn"
