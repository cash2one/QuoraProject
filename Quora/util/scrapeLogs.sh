#!/bin/bash
#$ -cwd
#$ -V
#$ -N scrapeLogs
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u scrapeLogs.py