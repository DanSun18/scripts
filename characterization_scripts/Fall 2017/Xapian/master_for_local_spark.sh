#!/bin/bash

#This script is used to characterize the performance of server
#run expSetup on server, client, and master machines before doing experiment

source  /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh

if (( $# < 2 ))
then
    echo "Usage:"
	echo "${BASH_SOURCE[0]} QPS FILE_NAME [SPARK_APP]"
 	exit 1
fi

if ! [ -d ${XAPIAN_HOME} ]
then
        echo "XAPIAN_HOME path ${XAPIAN_HOME} does not exist"
        exit 1
fi

if ! [ -d ${SCRIPT_HOME} ]
then
        echo "SCRIPT_HOME path ${SCRIPT_HOME} does not exist"
        exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

SERVER_THREADS=1
SERVER_CORES=0-7
SERVER_MACHINE=bcl15-cmp-00.egr.duke.edu
LAUNCH_SERVER_SCRIPT_CORE=0

CLIENT_MACHINE=bcl15-cmp-01.egr.duke.edu
LAUNCH_CLIENT_SCRIPT_CORE=4
CLIENT_CORES=5-7
CLIENT_THREADS=1


SPARK_CORES=3-7,11-15

QPS=$1
FILE_NAME=$2
SPARK_APP=$3

if [ -z ${SPARK_APP} ]
then
	echo "NO SPARK JOB IS GIVEN"
else
	if ! [ -d ${SPARK_SCRIPTS_HOME} ]
	then
        echo "SCRIPT_HOME path ${SPARK_SCRIPTS_HOME} does not exist"
        exit 1
	fi
fi

sleep 3s
	
#launch server
MAXREQS=$((400 * ${QPS}))
WARMUPREQS=$((50 * ${QPS}))
echo "--Starting server on ${SERVER_MACHINE}"
ssh ds318@${SERVER_MACHINE} \
	"taskset -c ${LAUNCH_SERVER_SCRIPT_CORE} ${SCRIPT_HOME}/characterization_scripts/server.sh ${SERVER_THREADS} ${MAXREQS} ${WARMUPREQS} " &
echo $! > server_connection.pid 
sleep 5s #wait for server to start up

#launch client
echo "--Starting client on ${CLIENT_MACHINE}" 
ssh ds318@${CLIENT_MACHINE} \
	"screen -d -m taskset -c ${LAUNCH_CLIENT_SCRIPT_CORE} ${SCRIPT_HOME}/characterization_scripts/client.sh ${QPS} ${CLIENT_THREADS} ${CLIENT_CORES} ${SERVER_MACHINE}" &

#start spark job on server machine
if ! [ -z ${SPARK_APP} ]
then
	sleep 3m
	echo "--submitting spark job ${SPARK_APP}"
	ssh ds318@${SERVER_MACHINE} \
	 " ${SPARK_SCRIPTS_HOME}/local_mode/run_${SPARK_APP}.sh ${SPARK_CORES}" &
fi

echo "--Waiting for server..."
wait $(cat server_connection.pid)
echo "--QPS = ${QPS} completed"

if ! [ -z ${SPARK_APP} ]
then
	#kill spark job
	echo "--killing spark job on ${SERVER_MACHINE}"
	ssh ds318@${SERVER_MACHINE} \
		"${SCRIPT_HOME}/kill_spark_job.sh"
	#kill spark worker on server
	sleep 5s
	echo "--stoping spark worker on ${SERVER_MACHINE}"
	ssh ds318@${SERVER_MACHINE} \
		"${SCRIPT_HOME}/kill_spark_worker.sh"
	sleep 5s
fi
	
#move data stored on client machine
sleep 5s #wait for client to dump stats
echo "moving data"
DATADIR=${SCRIPT_HOME}/server_characterization_data
ssh ds318@${CLIENT_MACHINE} \
	"cp lats.bin ${DATADIR}/${FILE_NAME}.bin"

