#!/bin/bash

APP="app1-ia"
RUTA_APP="$HOME/safecab-ia-server/$APP"

if [[ -f "$RUTA_APP/server.pid" ]]; then
    PID=$(cat "$RUTA_APP/server.pid")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Deteniendo servidor IA (PID: $PID)"
        kill $PID
        sleep 2
        # Si aún está corriendo, forzar
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID
        fi
        echo "Servidor detenido"
    else
        echo "Proceso $PID no está corriendo"
    fi
    rm "$RUTA_APP/server.pid"
else
    echo "No se encontró archivo PID, buscando procesos manualmente"
    pkill -f "gunicorn.*7060"
    echo "Procesos gunicorn detenidos"
fi
