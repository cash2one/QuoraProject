#!/bin/bash
#$ -cwd
#$ -V
#$ -N scrapeLogs
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l num_proc=2
python -u -m Quora.util.scrapeLogs