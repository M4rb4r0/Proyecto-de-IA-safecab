#!/bin/bash

APP="app1-front"

RUTA_SERVER="$HOME/safecab/apache-$APP"

if [[ -f "$RUTA_SERVER/apachectl" ]]; then
    "$RUTA_SERVER/apachectl" stop
fi
