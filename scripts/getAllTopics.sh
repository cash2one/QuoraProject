#!/bin/bash
#$ -cwd
#$ -V
#$ -N GetTopics
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u getAllTopics.py /export/a04/wpovell/compressed_data /export/a04/wpovell/topics.txt
