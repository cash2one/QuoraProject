#!/bin/bash
#$ -cwd
#$ -V
#$ -N GetUserFollowers
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u -m Pylinear.scripts.users /export/a04/wpovell/splits/train
