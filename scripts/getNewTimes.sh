#!/bin/bash
#$ -cwd
#$ -V
#$ -N GetNewTimes
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l arch="*86"

python -u getNewTimes.py -i /export/a04/wpovell/missingTimes.txt