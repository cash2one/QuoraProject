# Continously reports memory usage of currently running job

JOB_ID=$1
echo $JOB_ID
qstat -j $JOB_ID > /dev/null
while [ $? -ne 1 ]
do
sleep 5
qstat -j $JOB_ID | grep -Po '(?<=mem=)[0-9\.]* [A-Z]*'
done
