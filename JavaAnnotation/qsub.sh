#!/bin/bash
mkdir /export/a04/wpovell/annotated_data
N=`cat /export/a04/wpovell/fileList.txt | wc -l`
qsub -N AnnotateData -cwd -l mem_free=5G,ram_free=5G -t 1-$N \
-l 'arch=*64'  -v PATH -j y -o /export/a04/wpovell/logs -cwd -S /bin/bash annotateDir.sh