#!/bin/bash
#$ -cwd
#$ -V
#$ -N NGramComparison
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free3G,ram_free=3G

python -u -m Quora.exp.ngram_comp -q /export/a04/wpovell/scrape_data_ordered -t /export/a04/fferraro/twitter/rand10/2013/02/2013_02_14_05_24_31.gz