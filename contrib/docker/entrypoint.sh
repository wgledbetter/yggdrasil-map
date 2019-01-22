#!/usr/bin/env sh

set -e

cron
cd /src/yggdrasil-map/web/ && python updateGraph.py
python /src/yggdrasil-map/web/web.py --host $HOST --port $PORT
exit $?
