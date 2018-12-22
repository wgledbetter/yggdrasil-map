#!/usr/bin/env sh

set -e

cron
python /src/yggdrasil-map/web/web.py
exit $?
