#!/bin/bash
#$ -cwd
#$ -V
#$ -N AnswerHist
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
python -u -m Pylinear.scripts.answerHist /export/a04/wpovell/compressed_data