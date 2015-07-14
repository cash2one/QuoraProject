#!/bin/bash

threads="709f97e52894d9843f5b6523b8bc481f
9aaa149fbfbd1aae1e0c2d0352c54316
93b6185d1bae094601a92484882ee227
3e3d7bb31dfe3348fc4586adbd1594bd
4c5787ad7d686f2fc7e3dfa6ec33cdcb
40a7243d8750a68441f791a62182f24f
4e78b5b4e25d9b578500f7b004cdbaab"

rmFromArchive() {
	gunzip $1
	tar --delete --file=${1:0:-3} ${2:2:1}/$2
	gzip ${1:0:-3}
}

for i in $threads; do
	file=${i:0:1}/${i:1:1}/${i:2:1}.tar.gz
	thread=${i:2:1}/$i
	rmFromArchive /export/a04/wpovell/compressed_data/$file $thread
	rmFromArchive /export/a04/wpovell/annotated_data/$file $thread
	if [ -z $(tar -tzf /export/a04/wpovell/compressed_data/$file | grep $i) ]
	then
	  echo "SUCCESS: $i"
	else
	  echo "FAILURE: $i"
	fi
	if [ -z $(tar -tzf /export/a04/wpovell/annotated_data/$file | grep $i) ]
	then
	  echo "SUCCESS: $i"
	else
	  echo "FAILURE: $i"
	fi
done;