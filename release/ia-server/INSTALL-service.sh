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
runTest cp safecab-ia-server.service "$SERVICES_DIR"

runTest loginctl enable-linger
runTest systemctl --user daemon-reload
runTest systemctl --user enable safecab-ia-server

runTest systemctl --user start safecab-ia-server

echo ""
echo "=== Servicio systemd configurado ==="
echo "El servidor se iniciará automáticamente al arrancar el sistema"
echo ""
echo "Comandos útiles:"
echo "  Ver estado:  systemctl --user status safecab-ia-server"
echo "  Iniciar:     systemctl --user start safecab-ia-server"
echo "  Detener:     systemctl --user stop safecab-ia-server"
echo "  Reiniciar:   systemctl --user restart safecab-ia-server"
echo "  Ver logs:    journalctl --user -u safecab-ia-server -f"
