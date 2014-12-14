#!/bin/bash
#$ -cwd
#$ -V
#$ -N AnswerHistogram
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.exp.ans_hist /export/a04/wpovell/scrape_data/directory.json
