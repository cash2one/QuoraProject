#!/bin/bash
#$ -cwd
#$ -V
#$ -N TopicHistogram
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.exp.topic_hist /export/a04/wpovell/scrape_data_ordered
