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

SERVICES_DIR="$HOME/.config/systemd/user/"
runTest mkdir -p "$SERVICES_DIR"
runTest cp server_app1-ia-server.service "$SERVICES_DIR"

# configurar servicio para que suba en bootear
runTest loginctl enable-linger
runTest systemctl --user daemon-reload
runTest systemctl --user enable server_app1-ia-server

# subir servicio
runTest systemctl --user start server_app1-ia-server

echo "ok - Servicio systemd configurado"
echo "Para ver el estado: systemctl --user status server_app1-ia-server"
echo "Para ver logs: journalctl --user -u server_app1-ia-server -f"
