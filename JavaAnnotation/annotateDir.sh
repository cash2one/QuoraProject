DIR=`head -n $SGE_TASK_ID /export/a04/wpovell/fileList.txt | tail -n 1`
java -cp .:concrete-stanford-4.2.1-jar-with-dependencies.jar StanfordAnnotationTool "/export/a04/wpovell/hashed_data" "/export/a04/wpovell/annotated_data" $DIR
echo "DONE"
