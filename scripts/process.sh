#!/bin/bash
#$ -cwd
#$ -V
#$ -N CreateQuoraComms
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

python -u -m Quora.process -i /export/a04/wpovell/scrape_data_ordered -o /tmp/lwork/compressed_data -m /tmp/lwork/missingTimes.txt
mv -Tf /tmp/lwork/compressed_data /export/a04/wpovell/compressed_data
mv -Tf /tmp/lwork/missingTimes.txt /export/a04/wpovell/missingTimes.txt
