#!/bin/bash
#$ -cwd
#$ -V
#$ -N AnswerHist
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=60G,ram_free=60G
python -u -m Pylinear.scripts.answerHist /export/a04/wpovell/compressed_data