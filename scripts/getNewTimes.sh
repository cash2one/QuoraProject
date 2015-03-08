#!/bin/bash
#$ -cwd
#$ -V
#$ -N GetNewTimes
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

mkdir /tmp/lwork
python -u getNewTimes.py -i /export/a04/wpovell/missingTimes.txt -o /tmp/lwork/newMissingTimes.txt
mv /tmp/lwork/newMissingTimes.txt /export/a04/wpovell/newMissingTimes.txt