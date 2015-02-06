#!/bin/bash
#$ -cwd
#$ -V
#$ -N getDates
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u getDates.py
