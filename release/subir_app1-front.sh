#!/bin/bash

AMBIENTE="ejercicio3"
APP="app1-front"
PORT=7001

RUTA_APP="$HOME/safecab/$APP"
RUTA_SERVER="$HOME/safecab/apache-$APP"
RUTA_LOGS="$HOME/safecab/logs"

# Detectar la ubicación de httpd y sus módulos
if command -v httpd &> /dev/null; then
    HTTPD_BIN=$(which httpd)
    # Intentar detectar el directorio de módulos para httpd
    if [[ -d "/usr/lib64/httpd/modules" ]]; then
        MODULES_DIR="/usr/lib64/httpd/modules"
    elif [[ -d "/usr/lib/httpd/modules" ]]; then
        MODULES_DIR="/usr/lib/httpd/modules"
    fi
elif command -v apache2 &> /dev/null; then
    HTTPD_BIN=$(which apache2)
    # Intentar detectar el directorio de módulos para apache2
    if [[ -d "/usr/lib/apache2/modules" ]]; then
        MODULES_DIR="/usr/lib/apache2/modules"
    elif [[ -d "/usr/lib64/apache2/modules" ]]; then
        MODULES_DIR="/usr/lib64/apache2/modules"
    fi
else
    echo "Error: No se encontró httpd o apache2 en el sistema"
    exit 1
fi

# Construir comando con parámetros opcionales (usar el módulo de Python del entorno)
WSGI_CMD="python -m mod_wsgi setup-server application.wsgi --port $PORT --server-root $RUTA_SERVER --httpd-executable $HTTPD_BIN --access-log --log-to-terminal"

if [[ -n "$MODULES_DIR" ]]; then
    WSGI_CMD="$WSGI_CMD --modules-directory $MODULES_DIR"
fi

source "$HOME/miniforge3/bin/activate" "$AMBIENTE" && \
cd "$RUTA_APP" && \
mkdir -p "$RUTA_LOGS" && \
eval $WSGI_CMD && \
"$RUTA_SERVER/apachectl" start
