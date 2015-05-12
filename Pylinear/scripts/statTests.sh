#!/bin/bash
#$ -cwd
#$ -V
#$ -N statTests
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=30G,ram_free=30G,h_vmem=30G
python -u -m Pylinear.scripts.statTests /export/a04/wpovell/splits/train/data
