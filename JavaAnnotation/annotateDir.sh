DIR=`head -n $SGE_TASK_ID /export/a04/wpovell/fileList.txt | tail -n 1`
java -cp .:concrete-stanford-4.2.1-jar-with-dependencies.jar AnnotationTool -i "/export/a04/wpovell/hashed_data" -o "/export/a04/wpovell/annotated_data" -f $DIR
echo "DONE"
