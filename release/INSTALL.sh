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
        runTest "$CONDA_PATH/bin/conda" create -n "$AMBIENTE" python=3.10 -y
    fi
    
    # Instalar dependencias
    echo "Instalando dependencias en ambiente '$AMBIENTE'..."
    source "$CONDA_PATH/bin/activate" "$AMBIENTE"
    runTest conda install -n "$AMBIENTE" -c conda-forge mod_wsgi -y
    runTest pip install flask requests torch torchvision pillow
    
    runTest mkdir -p "$APPS_DESTINATION"
    for app in app1-front app1-ia
    do
        echo "instalando $app en $APPS_DESTINATION ..."
        if [[ -f "$APPS_DESTINATION/bajar_$app.sh" ]]; then
            echo "[`date "+%F %T"`]\$ bash $APPS_DESTINATION/bajar_$app.sh"
            bash "$APPS_DESTINATION/bajar_$app.sh" || true
        fi
        runTest cp -r "../$app/" "$APPS_DESTINATION/"
        runTest cp "subir_$app.sh" "bajar_$app.sh" "$APPS_DESTINATION"
        runTest chmod +x "$APPS_DESTINATION/subir_$app.sh" "$APPS_DESTINATION/bajar_$app.sh"
        runTest bash "$APPS_DESTINATION/subir_$app.sh"
    done
    echo "ok $ACCION"
elif [[ "$ACCION" == "servicios" ]]; then
    SERVICES_DIR="$HOME/.config/systemd/user/"
    runTest mkdir -p "$SERVICES_DIR"
    runTest cp server_app1-front.service server_app1-ia.service "$SERVICES_DIR"
	# configurar servicios para que suban en bootear
    runTest loginctl enable-linger
    runTest systemctl --user daemon-reload
    runTest systemctl --user enable server_app1-front
    runTest systemctl --user enable server_app1-ia

	# subir servicios
    runTest systemctl --user start server_app1-front
    runTest systemctl --user start server_app1-ia

    echo "ok $ACCION"
fi
