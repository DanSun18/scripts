#!/bin/bash

#This script launches moses client and writes its pid to client.pid

source /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh

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

if [ "$#" -ne 4 ]
then 
	echo "Usage:"
	echo "${BASH_SOURCE[0]} QPS CLIENT_THREADS CLIENT_CORES SERVER_MACHINE"
	exit 1
fi


QPS=$1
CLIENT_THREADS=$2
CLIENT_CORES=$3
SERVER_MACHINE=$4

PID_FILE="client.pid"

if [ $# -ne 4 ]; then
        echo -e "Usage:"
        echo -e "${BASH_SOURCE[0]} [QPS CLIENT_THREADS CLIENT_CORES SERVER_MACHINE]"
        exit 1
fi

BINDIR=${ONLINE_HOME}/bin

# Launch Client
TBENCH_QPS=${QPS} TBENCH_MINSLEEPNS=10000 \
TBENCH_CLIENT_THREADS=${CLIENT_THREADS} TBENCH_SERVER=${SERVER_MACHINE} \
taskset -c ${CLIENT_CORES}  ${BINDIR}/moses_client_networked &
#write client pid to a file
echo $! > ${PID_FILE}
#give set process priority for client process
sudo chrt -f -p 99 $(cat ${PID_FILE})