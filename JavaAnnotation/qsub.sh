#!/bin/bash
mkdir /export/a04/wpovell/annotated_data
N=`cat /export/a04/wpovell/fileList.txt | wc -l`
qsub -N AnnotateData -cwd -l mem_free=50G,ram_free=50G,h_vmem=50G,arch=*64 -t 1-$N \
-tc 10 -v PATH -j y -o /export/a04/wpovell/logs -S /bin/bash annotateDir.sh

