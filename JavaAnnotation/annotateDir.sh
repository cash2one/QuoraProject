DIR=`head -n $SGE_TASK_ID /export/a04/wpovell/fileList.txt | tail -n 1`
echo $DIR
OUT_DIR="/tmp/lwork/annotated_data_$SGE_TASK_ID"
mkdir -p $OUT_DIR
java -cp .:commons-cli-1.2.jar:concrete-stanford-4.2.1-jar-with-dependencies.jar AnnotationTool -i "/export/a04/wpovell/compressed_data" -o "$OUT_DIR" -f $DIR
cp -r $OUT_DIR/* /export/a04/wpovell/annotated_data
rm -r $OUT_DIR
echo "DONE"
