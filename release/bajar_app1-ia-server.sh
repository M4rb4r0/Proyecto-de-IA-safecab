#!/bin/bash

APP="app1-ia"
RUTA_APP="$HOME/safecab/$APP"

if [[ -f "$RUTA_APP/server.pid" ]]; then
    PID=$(cat "$RUTA_APP/server.pid")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Deteniendo servidor (PID: $PID)"
        kill $PID
        sleep 2
        # Si aún está corriendo, forzar
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID
        fi
    fi
    rm "$RUTA_APP/server.pid"
else
    echo "No se encontró archivo PID, buscando procesos manualmente"
    pkill -f "mod_wsgi.express.*7060"
fi
