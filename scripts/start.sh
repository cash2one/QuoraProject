#!/bin/bash
# Used by qsub command in start_clients.sh
python -u -m Quora.ScrapeClient $HOST $PORT -o /export/a04/wpovell/scrape_data
