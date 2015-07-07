#!/bin/bash
#$ -cwd
#$ -V
#$ -N gen
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=30G,ram_free=30G,h_vmem=30G
./pylin gen -f followers topics question_length has_N_answers -d /export/a04/wpovell/splits/train -N 1
./pylin gen -f has_N_answers -d /export/a04/wpovell/splits/train -N 2
./pylin gen -f has_N_answers -d /export/a04/wpovell/splits/train -N 3
echo "Done"