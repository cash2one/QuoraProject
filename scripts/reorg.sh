#!/bin/bash
#$ -cwd
#$ -V
#$ -N ReorgQuoraData
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.util.reorganizeData