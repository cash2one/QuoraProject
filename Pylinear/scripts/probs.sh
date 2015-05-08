#!/bin/bash
#$ -cwd
#$ -V
#$ -N PyLinearProbs
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=50G,ram_free=50G
python -u -m Pylinear.scripts.probs /export/a04/wpovell/compressed_data/
