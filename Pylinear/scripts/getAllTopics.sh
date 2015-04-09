#!/bin/bash
#$ -cwd
#$ -V
#$ -N GetTopics
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -m Pylinear.scripts.getAllTopics /export/a04/wpovell/compressed_data /export/a04/wpovell/topics.txt