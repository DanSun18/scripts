#!/bin/bash

#warmup reqs is normally set to 1000

source /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh

# Check if folder xapian exists at the indicated location
if ! [ -d ${XAPIAN_HOME} ]
then
        echo "XAPIAN_HOME path ${XAPIAN_HOME} does not exist"
        exit 1
fi
echo "CONFIREMD: XAPIAN_HOME exists at path ${XAPIAN_HOME}"

#check for command line arguments
if [ "$#" -ne 3 ]
then 
	echo "Usage:"
	echo "${BASH_SOURCE[0]} SERVER_THREADS MAXREQS WARMUPREQS"
	exit 1
fi

#variables
SERVER_THREADS=$1
MAXREQS=$2
WARMUPREQS=$3
echo "Summary of arguments:"
echo -e "\t SERVER_THREADS = ${SERVER_THREADS}" 
echo -e "\t MAXREQS = ${MAXREQS}" 
echo -e "\t WARMUPREQS = ${WARMUPREQS}"

PID_FILE="xapian_server.pid" #used for store pid of server

# $1 is the core number
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# read tailbench configuration
CONFIG_FILE_PATH=${XAPIAN_HOME}/../configs.sh
source ${CONFIG_FILE_PATH}
echo "SUCCESS: configuration read from ${CONFIG_FILE_PATH}"

LD_LIBRARY_PATH=LD_LIBRARY_PATH:${XAPIAN_HOME}/xapian-core-1.2.13/install/lib
export LD_LIBRARY_PATH
echo "SUCCESS: LD_LIBRARY_PATH updated"

NSERVERS=1

# CORES=$1
# QPS=$2
# WARMUPREQS=500
# REQUESTS=$3

# echo "NSERVERS = ${NSERVERS}" 

#/home/yl408/scripts/bash_scripts/turnoff_HT.sh
echo "Executing command"
echo "TBENCH_MAXREQS=${MAXREQS} TBENCH_WARMUPREQS=${WARMUPREQS} \
  ${XAPIAN_HOME}/xapian_networked_server -n ${NSERVERS} -d ${DATA_ROOT}/xapian/wiki \
    -r 1000000000 &"

TBENCH_MAXREQS=${MAXREQS} TBENCH_WARMUPREQS=${WARMUPREQS} \
  ${XAPIAN_HOME}/xapian_networked_server -n ${NSERVERS} -d ${DATA_ROOT}/xapian/wiki \
    -r 1000000000 &

#store pid to a file
echo $! > ${PID_FILE}
echo "SUCCESS: server pid written to ${PID_FILE}"

#give set process priority for client process
PID=$(cat ${PID_FILE})
echo "CONFIRMATION: pid of server is ${PID}"
sudo chrt -f -p 99 ${PID}
echo "SUCCESS: priority of server has been set"

#wait to finish, then delete pid file
echo "Waiting on process ${PID}"
wait ${PID}
#clean up
rm ${PID_FILE}
echo "SUCCESS: pid file ${PID_FILE} has been removed, exiting"

