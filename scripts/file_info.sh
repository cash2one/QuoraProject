#!/bin/bash
#$ -cwd
#$ -V
#$ -N QuoraDataFileInfo
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.util.fileInfo
