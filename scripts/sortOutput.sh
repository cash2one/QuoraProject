#!/bin/bash
#$ -cwd
#$ -V
#$ -N SortOutput
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.util.sortOutput /export/a04/wpovell/scrape_data /export/a04/wpovell/scrape_data_ordered
