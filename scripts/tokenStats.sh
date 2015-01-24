#!/bin/bash
#$ -cwd
#$ -V
#$ -N QuoraTokenStats
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=3G,ram_free=3G

python -u -m Quora.util.tokenStats
