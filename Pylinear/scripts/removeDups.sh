#!/bin/bash
#$ -cwd
#$ -V
#$ -N removeDups
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u -m Pylinear.scripts.removeDups
