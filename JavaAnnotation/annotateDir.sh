echo $SGE_TASK_ID
I=`expr $SGE_TASK_ID - 1`

java -cp .:/home/ferraro/code/concrete-stanford/target/concrete-stanford-3.10.3-jar-with-dependencies.jar StanfordAnnotationTool "/export/a04/wpovell/hashed_data" "/export/a04/wpovell/annotated_data" ${DIRS[$I]}