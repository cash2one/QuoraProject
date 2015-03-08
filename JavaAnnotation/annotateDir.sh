DIR=`head -n $SGE_TASK_ID /export/a04/wpovell/fileList.txt | tail -n 1`
java -cp .:commons-cli-1.2.jar:concrete-stanford-4.2.1-jar-with-dependencies.jar AnnotationTool -i "/export/a04/wpovell/hashed_data" -o "/tmp/lwork/annotated_data" -f $DIR
cp -r /tmp/lwork/annotated_data/* /export/a04/wpovell/annotated_data
rm -r /tmp/lwork/annotated_data
echo "DONE"
