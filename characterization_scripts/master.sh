#!/bin/bash

#This script is used to characterize the performance of server
#pin this to a core that is different from client and server
#sudo another command before executing to allow smooth operation

# First argument is the number of threads for server
# Second argument is QPS

source  /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh
source /home/ds318/scripts/bash_helpers/checkInputs.sh 2 "$#" "SERVER_THREADS, QPS" 

if ! [ -d ${ONLINE_HOME} ]
	then
	echo "ONLINE_HOME path ${ONLINE_HOME} does not exist"
	exit 1
fi

if ! [ -d ${SCRIPT_HOME} ]
	then
	echo "SCRIPT_HOME path ${SCRIPT_HOME} does not exist"
	exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# constants
# SERVER_CORES=0-7
SERVER_MACHINE=bcl15-cmp-00.egr.duke.edu
LAUNCH_SERVER_SCRIPT_CORE=0

CLIENT_MACHINE=bcl15-cmp-01.egr.duke.edu
LAUNCH_CLIENT_SCRIPT_CORE=4
CLIENT_CORES=5-7
CLIENT_THREADS=1

#inputs 

SERVER_THREADS=$1
QPS=$2

#launch server
MAXREQS=$((400 * ${QPS}))
WARMUPREQS=$((50 * ${QPS}))
echo "--Starting server on ${SERVER_MACHINE}"
ssh ds318@${SERVER_MACHINE} \
"taskset -c ${LAUNCH_SERVER_SCRIPT_CORE} ${SCRIPT_HOME}/characterization_scripts/server.sh ${SERVER_THREADS} ${MAXREQS} ${WARMUPREQS}" &	
	#"sudo taskset -c ${LAUNCH_SERVER_SCRIPT_CORE} ${SCRIPT_HOME}/characterization_scripts/server.sh ${SERVER_THREADS} ${MAXREQS} ${WARMUPREQS} ${SERVER_CORES}" &
echo $! > server_connection.pid 
sleep 5s #wait for server to start up

#launch client
echo "--Starting client on ${CLIENT_MACHINE}" 
ssh ds318@${CLIENT_MACHINE} \
"screen -d -m taskset -c ${LAUNCH_CLIENT_SCRIPT_CORE} ${SCRIPT_HOME}/characterization_scripts/client.sh ${QPS} ${CLIENT_THREADS} ${CLIENT_CORES} ${SERVER_MACHINE}" &

echo "--Waiting for server..."
wait $(cat server_connection.pid)
echo "--QPS = ${QPS} completed"

#move data stored on client machine
sleep 5s #wait for client to dump stats
echo "moving data"
DATADIR=/home/ds318/data
ssh ds318@${CLIENT_MACHINE} \
"cp lats.bin ${DATADIR}/t${SERVER_THREADS}q${QPS}.bin"