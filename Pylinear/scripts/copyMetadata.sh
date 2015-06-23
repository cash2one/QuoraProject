#!/bin/bash
#$ -cwd
#$ -V
#$ -N copyMetadata
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=10G,ram_free=10G,h_vmem=10G
python -m Pylinear.scripts.copyMetadata /export/a04/wpovell/compressed_data /export/a04/wpovell/annotated_data