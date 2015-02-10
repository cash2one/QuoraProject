#!/bin/bash

for i in $( ls $1 ); do
	if [ -d $1/$i ]
	then
	    for j in $( ls $1/$i ); do
	    	if [ -d $1/$i/$j ]
	    	then
	    		for k in $( ls $1/$i/$j ); do
	    			if [ -d $1/$i/$j/$k ]
	    			then
	    				echo $i/$j/$k
			    		java -cp .:concrete-stanford-3.10.3-jar-with-dependencies.jar StanfordAnnotationTool "../data_new" "annotated_data" "$i/$j/$k"
			    	fi
		    	done
	    	fi
	    done
	fi
done