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
APPS_DESTINATION="$HOME/safecab"

# Verificar si httpd está instalado
if ! command -v httpd &> /dev/null && ! command -v apache2 &> /dev/null; then
    echo "Error: Apache (httpd) no está instalado en el sistema"
    echo "Por favor instale Apache con uno de estos comandos:"
    echo "  Ubuntu/Debian: sudo apt-get install apache2 apache2-dev"
    echo "  RedHat/CentOS: sudo yum install httpd httpd-devel"
    echo "  Fedora: sudo dnf install httpd httpd-devel"
    exit 1
fi

# Verificar si existe miniforge3/miniconda/anaconda
if [[ -d "$HOME/miniforge3" ]]; then
    CONDA_PATH="$HOME/miniforge3"
elif [[ -d "$HOME/miniconda3" ]]; then
    CONDA_PATH="$HOME/miniconda3"
elif [[ -d "$HOME/anaconda3" ]]; then
    CONDA_PATH="$HOME/anaconda3"
else
    echo "Error: No se encontró instalación de conda"
    echo "Instale miniforge3, miniconda o anaconda"
    exit 1
fi

# Verificar si existe el ambiente
if ! "$CONDA_PATH/bin/conda" env list | grep -q "^$AMBIENTE "; then
    echo "Creando ambiente conda '$AMBIENTE'..."
    runTest "$CONDA_PATH/bin/conda" create -n "$AMBIENTE" python=3.11 -y
fi

# Instalar dependencias
echo "Instalando dependencias en ambiente '$AMBIENTE'..."
source "$CONDA_PATH/bin/activate" "$AMBIENTE"
runTest conda install -n "$AMBIENTE" -c conda-forge mod_wsgi -y
runTest pip install flask torch torchvision pillow ultralytics opencv-python

runTest mkdir -p "$APPS_DESTINATION"

echo "instalando app1-ia en $APPS_DESTINATION ..."
if [[ -f "$APPS_DESTINATION/bajar_app1-ia-server.sh" ]]; then
    echo "[`date "+%F %T"`]\$ bash $APPS_DESTINATION/bajar_app1-ia-server.sh"
    bash "$APPS_DESTINATION/bajar_app1-ia-server.sh" || true
fi
runTest cp -r "../app1-ia/" "$APPS_DESTINATION/"
runTest cp "subir_app1-ia-server.sh" "bajar_app1-ia-server.sh" "$APPS_DESTINATION"
runTest chmod +x "$APPS_DESTINATION/subir_app1-ia-server.sh" "$APPS_DESTINATION/bajar_app1-ia-server.sh"
runTest bash "$APPS_DESTINATION/subir_app1-ia-server.sh"

echo "ok - Servidor IA instalado en puerto 7060"
echo "Accesible desde: http://10.0.218.101:7060/safecab/app1-ia/predict"
