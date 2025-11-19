#!/bin/bash
ACCION="$1"

if [[ "$ACCION" != "web" && "$ACCION" != "servicios" ]]; then
        echo "Error: Accion desconocida $ACCION"
        echo "Acciones validas: web servicios"
        exit 1
fi

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

if [[ "$ACCION" == "web" ]]; then
    AMBIENTE="ejercicio3"
    APPS_DESTINATION="$HOME/safecab"
    
    if ! command -v httpd &> /dev/null && ! command -v apache2 &> /dev/null; then
        echo "Error: Apache (httpd) no está instalado en el sistema"
        echo "Por favor instale Apache con uno de estos comandos:"
        echo "  Ubuntu/Debian: sudo apt-get install apache2 apache2-dev"
        echo "  RedHat/CentOS: sudo yum install httpd httpd-devel"
        echo "  Fedora: sudo dnf install httpd httpd-devel"
        exit 1
    fi
    
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

    if ! "$CONDA_PATH/bin/conda" env list | grep -q "^$AMBIENTE "; then
        echo "Creando ambiente conda '$AMBIENTE'..."
        runTest "$CONDA_PATH/bin/conda" create -n "$AMBIENTE" python=3.10 -y
    fi

    echo "Instalando dependencias en ambiente '$AMBIENTE'..."
    source "$CONDA_PATH/bin/activate" "$AMBIENTE"
    runTest conda install -n "$AMBIENTE" -c conda-forge mod_wsgi -y
    runTest pip install flask requests
    
    runTest mkdir -p "$APPS_DESTINATION"
    

    echo "instalando app1-front en $APPS_DESTINATION ..."
    echo "Nota: El backend IA está en http://10.0.218.101:7060"
    
    if [[ -f "$APPS_DESTINATION/bajar_app1-front.sh" ]]; then
        echo "[`date "+%F %T"`]\$ bash $APPS_DESTINATION/bajar_app1-front.sh"
        bash "$APPS_DESTINATION/bajar_app1-front.sh" || true
    fi
    
    runTest cp -r "../app1-front/" "$APPS_DESTINATION/"
    runTest cp "subir_app1-front.sh" "bajar_app1-front.sh" "$APPS_DESTINATION"
    runTest chmod +x "$APPS_DESTINATION/subir_app1-front.sh" "$APPS_DESTINATION/bajar_app1-front.sh"
    runTest bash "$APPS_DESTINATION/subir_app1-front.sh"
    
    echo "ok $ACCION"
elif [[ "$ACCION" == "servicios" ]]; then
    SERVICES_DIR="$HOME/.config/systemd/user/"
    runTest mkdir -p "$SERVICES_DIR"

    runTest cp server_app1-front.service "$SERVICES_DIR"

    runTest loginctl enable-linger
    runTest systemctl --user daemon-reload
    runTest systemctl --user enable server_app1-front

    runTest systemctl --user start server_app1-front

    echo "ok $ACCION"
    echo "Nota: El backend IA está en servidor dedicado (10.0.218.101:7060)"
fi
