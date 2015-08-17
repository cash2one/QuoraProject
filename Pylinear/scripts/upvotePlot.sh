#!/bin/bash
#$ -cwd
#$ -V
#$ -N upvotePlot
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u upvotePlot.py