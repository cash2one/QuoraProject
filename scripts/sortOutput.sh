#!/bin/bash
#$ -cwd
#$ -V
#$ -N SortOutput
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.util.sort_output /export/a04/wpovell/scrape_data /export/a04/wpovell/scrape_data_ordered
