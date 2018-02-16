# !/bin/bash
# sparkCoreFreqChangeEffect.sh

# This script runs the experiment to observe how promptly does service
# or latency time change with a change in batch core frequency running spark 
# applcations

# This script runs on core 4
# Plan to start spark locally on core 0-3,8-11 with high frequency
# wait for 30 s
# start moses server while manually starting client on the other machine
# wait for 6 minutes
# change batch core frequency to a lower value
# after tailbench finishes, kill spark job

#get necessary paths
source  /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh
if ! [ -d ${ONLINE_HOME} ]
	then
	echo "ONLINE_HOME path ${ONLINE_HOME} does not exist"
	exit 1
fi

if ! [ -d ${SCRIPT_HOME} ]
	then
	echo "SCRIPT_HOME path ${wait $(cat server_connection.pid)SCRIPT_HOME} does not exist"
	exit 1
fi

if ! [ -d ${SPARK_LOCAL_MODE_HOME} ]
	then 
	echo "SPARK_LOCAL_MODE_HOME path ${SPARK_LOCAL_MODE_HOME} does not exist"
	exit 1
fi

echo "ONLINE_HOME is ${ONLINE_HOME}"
echo "SCRIPT_HOME is ${SCRIPT_HOME}"
echo "SPARK_LOCAL_MODE_HOME is ${SPARK_LOCAL_MODE_HOME}"
# start spark application
SPARK_APPLICATION="kmeans"
SPARK_CORES="0-3,8-11"
echo "SPARK_APPLICATION is ${SPARK_APPLICATION}"
echo "SPARK_CORES is ${SPARK_CORES}"
${SPARK_LOCAL_MODE_HOME}/run_${SPARK_APPLICATION}.sh ${SPARK_CORES}
#wait for 30s
echo "Waiting for 30 seconds..."
sleep 30s
#start moses
echo "Starting moses"
#parameters
SERVER_THREADS=2
QPS=500
MAXREQS=$((400 * ${QPS}))
WARMUPREQS=$((50 * ${QPS}))
LAUNCH_SERVER_SCRIPT_CORE=4
#call other script
taskset -c ${LAUNCH_SERVER_SCRIPT_CORE} ${SCRIPT_HOME}/characterization_scripts/server.sh ${SERVER_THREADS} ${MAXREQS} ${WARMUPREQS} &	
echo $! > server.pid
#wait for 6 minutes
echo "Waiting for 6 minutes..."
sleep 6m
#change core frequency of batch cores
SECOND_FREQUENCY=1.20GHz
echo "Changing SPARK_CORES ${SPARK_CORES} to frequency ${SECOND_FREQUENCY}"
sudo cpupower -c ${SPARK_CORES} frequency-set -f ${SECOND_FREQUENCY}
#wait for server
echo "Waiting for server on process $(cat server.pid) to finish..."
wait $(cat server.pid)
#kill spark job
echo "Killing spark jobs"
${SCRIPT_HOME}/kill_spark_job.sh
