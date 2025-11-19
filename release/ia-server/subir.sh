#!/bin/bash

AMBIENTE="safecab-ia"
APP="app1-ia"
PORT=7060

RUTA_APP="$HOME/safecab-ia-server/$APP"
RUTA_LOGS="$HOME/safecab-ia-server/logs"

source "$HOME/miniforge3/bin/activate" "$AMBIENTE"

cd "$RUTA_APP" && \
mkdir -p "$RUTA_LOGS"

nohup gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile "$RUTA_LOGS/access.log" \
    --error-logfile "$RUTA_LOGS/error.log" \
    --daemon \
    --pid "$RUTA_APP/server.pid" \
    main:app

echo "Servidor IA iniciado en puerto $PORT (PID: $(cat $RUTA_APP/server.pid))"
echo "Accesible desde: http://10.0.218.101:$PORT/safecab/app1-ia/predict"
echo "Ver logs: tail -f $RUTA_LOGS/error.log"
