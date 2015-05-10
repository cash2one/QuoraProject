#!/bin/bash
#$ -cwd
#$ -V
#$ -N NumAnswers
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -m Pylinear.scripts.numAnswers /export/a04/wpovell/compressed_data