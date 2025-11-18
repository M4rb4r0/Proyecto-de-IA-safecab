#!/bin/bash

AMBIENTE="safecab-ia"
APP="app1-ia"
PORT=7060

RUTA_APP="$HOME/safecab/$APP"
RUTA_SERVER="$HOME/safecab/apache-$APP"
RUTA_LOGS="$HOME/safecab/logs"

# Activar ambiente conda
source "$HOME/miniforge3/bin/activate" "$AMBIENTE"

# Usar mod_wsgi standalone (no requiere Apache del sistema)
# mod_wsgi-express incluye su propio httpd
cd "$RUTA_APP" && \
mkdir -p "$RUTA_LOGS" && \
nohup python -m mod_wsgi.express start-server application.wsgi \
    --port $PORT \
    --host 0.0.0.0 \
    --server-name 10.0.218.101 \
    --log-to-terminal \
    --access-log \
    > "$RUTA_LOGS/app1-ia.log" 2>&1 &

echo $! > "$RUTA_APP/server.pid"
echo "Servidor iniciado en puerto $PORT (PID: $(cat $RUTA_APP/server.pid))"
echo "Accesible desde: http://10.0.218.101:$PORT/safecab/app1-ia/predict"
