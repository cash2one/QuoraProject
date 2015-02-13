#!/bin/bash

I=0
arr=()

for i in $1/*; do
	if [ -d $1/$i ]
	then
	    for j in $i/*; do
	    	if [ -d $j ]
	    	then
	    		for k in $j/*; do
	    			if [ -d $k ]
	    			then
	    				arr[$I]="$k"
	    				I=`expr $I + 1`
			    	fi
		    	done
	    	fi
	    done
	fi
done

qsub -N AnnotateData -l mem_free=3G,ram_free=3G -t 1-${#arr[*]} \
-M willipovell@gmail.com -m eas \
-j y -v DIRS=arr -o /export/a04/wpovell/logs -cwd -S /bin/bash annotateDir.sh
