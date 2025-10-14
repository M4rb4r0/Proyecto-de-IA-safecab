#!/bin/bash

AMBIENTE="ejercicio3"
APP="app1-front"
PORT=7001

RUTA_APP="$HOME/safecab/$APP"
RUTA_SERVER="$HOME/safecab/apache-$APP"
RUTA_LOGS="$HOME/safecab/logs"

source "$HOME/miniforge3/bin/activate" "$AMBIENTE" && \
cd "$RUTA_APP" && \
mkdir -p "$RUTA_LOGS" && \
mod_wsgi-express setup-server application.wsgi --port $PORT \
      --server-root "$RUTA_SERVER" \
      --access-log --log-to-terminal && \
"$RUTA_SERVER/apachectl" start
