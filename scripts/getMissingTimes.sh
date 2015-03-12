#!/bin/bash
#$ -cwd
#$ -V
#$ -N GetMissingTimes
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u getMissingTimes.py