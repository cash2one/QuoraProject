#!/bin/bash
#$ -cwd
#$ -V
#$ -N QuoraDataStats
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.util.stats /export/a04/wpovell/scrape_data_ordered
