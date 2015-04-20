DIR=`head -n $SGE_TASK_ID /export/a04/wpovell/fileList.txt | tail -n 1`
HOST=$(hostname)
echo "DIR=$DIR"
echo "HOST=$HOST"
OUT_DIR="/tmp/lwork/annotated_data_$SGE_TASK_ID"
mkdir -p $OUT_DIR
java -cp .:commons-cli-1.2.jar:concrete-stanford-4.2.1-jar-with-dependencies.jar AnnotationTool -i "/export/a04/wpovell/compressed_data" -o $OUT_DIR -f $DIR;
EXIT_CODE=$?
if [ $EXIT_CODE -eq 1 ]; then
    echo "Job $JOB_ID.$SGE_TASK_ID failed on machine $HOST processing dir $DIR"
    echo $_ | mail -s "JOB ERROR" willipovell@gmail.com
else
    cp -r $OUT_DIR/* /export/a04/wpovell/annotated_data
fi

rm -r $OUT_DIR
echo "DONE"
