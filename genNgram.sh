#!/bin/bash
#$ -cwd
#$ -V
#$ -N genNgram
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=30G,ram_free=30G,h_vmem=30G

python -u -m gen -f ngram tfidf