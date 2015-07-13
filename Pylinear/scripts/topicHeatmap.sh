#!/bin/bash
#$ -cwd
#$ -V
#$ -N topicHeatmap
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=10G,ram_free=10G,h_vmem=10G
python -u -m Pylinear.scripts.topicHeatmap