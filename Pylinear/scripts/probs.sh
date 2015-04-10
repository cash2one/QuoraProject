#!/bin/bash
#$ -cwd
#$ -V
#$ -N PyLinearProbs
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -m Pylinear.scripts.probs /export/a04/wpovell/splits/train
