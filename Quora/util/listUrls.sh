#!/bin/bash
#$ -cwd
#$ -V
#$ -N listUrls
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u listUrls.py