#!/bin/bash
#$ -cwd
#$ -V
#$ -N statTests
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=60G,ram_free=60G

python -u -m Pylinear.scripts.statTests /export/a04/wpovell/splits/test/data