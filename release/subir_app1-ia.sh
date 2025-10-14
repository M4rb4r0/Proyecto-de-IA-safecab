#!/bin/bash

AMBIENTE="safecab"
APP="app1-ia"
PORT=7002

RUTA_APP="$HOME/safecab/$APP"
RUTA_SERVER="$HOME/safecab/apache-$APP"
RUTA_LOGS="$HOME/safecab/logs"

source "$HOME/miniforge3/bin/activate" "$AMBIENTE" && \
cd "$RUTA_APP" && \
mkdir -p "$RUTA_LOGS" && \
mod_wsgi-express start-server application.wsgi --port $PORT \
      --server-root "$RUTA_SERVER" \
      --access-log --log-to-terminal \
       2>&1 | /usr/bin/cronolog "$RUTA_LOGS/$APP.%Y-%m-%d.log"
