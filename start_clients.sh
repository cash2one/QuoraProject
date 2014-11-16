#!/bin/bash
set -o nounset
HOST=$1
PORT=$2
NUM_TO_START=$3

echo "Starting $NUM_TO_START clients sending requests to $HOST:$PORT"

qsub -N ScrapeClient -l mem_free=1G,ram_free=1G -t 1-$NUM_TO_START \
-M willipovell@gmail.com -m eas \
-j y -v HOST="$HOST",PORT="$PORT" -o /export/a04/wpovell/logs -cwd -S /bin/bash start.sh
