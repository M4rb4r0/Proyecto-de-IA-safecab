#!/bin/bash

AMBIENTE="ejercicio3"
APP="app1-front"
PORT=7001

RUTA_APP="$HOME/safecab/$APP"
RUTA_SERVER="$HOME/safecab/apache-$APP"
RUTA_LOGS="$HOME/safecab/logs"

# Detectar la ubicación de httpd (apache2 en Ubuntu/Debian, httpd en RedHat/Fedora)
if command -v httpd &> /dev/null; then
    HTTPD_BIN=$(which httpd)
elif command -v apache2 &> /dev/null; then
    HTTPD_BIN=$(which apache2)
else
    echo "Error: No se encontró httpd o apache2 en el sistema"
    exit 1
fi

export PATH=$(dirname "$HTTPD_BIN"):$PATH

source "$HOME/miniforge3/bin/activate" "$AMBIENTE" && \
cd "$RUTA_APP" && \
mkdir -p "$RUTA_LOGS" && \
mod_wsgi-express setup-server application.wsgi --port $PORT \
      --server-root "$RUTA_SERVER" \
      --access-log --log-to-terminal && \
"$RUTA_SERVER/apachectl" start
