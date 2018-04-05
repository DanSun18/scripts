#!/bin/bash
# $1 is the core number

# other than putting this file in the same folder with xapian 
# we have to tell it where the application is
# whether through command line or hard-coded
# for simplicity let us use hard-coded path here

source /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh

# Check if folder xapian exists at the indicated location
if ! [ -d ${XAPIAN_HOME} ]
then
        echo "XAPIAN_HOME path ${XAPIAN_HOME} does not exist"
        exit 1
fi
echo "CONFIREMD: XAPIAN_HOME exists at path ${XAPIAN_HOME}"

# Check if scirpt folder exists at the indicated location
# if ! [ -d ${SCRIPT_HOME} ]
# then
#         echo "SCRIPT_HOME path ${SCRIPT_HOME} does not exist"
#         exit 1
# fi
# echo "CONFIREMD: SCRIPT_HOME exists at path ${SCRIPT_HOME}"

#Check for command line arguments
if [ "$#" -ne 4 ]
then 
	echo "Usage:"
	echo "${BASH_SOURCE[0]} QPS CLIENT_THREADS CLIENT_CORES SERVER_MACHINE"
	exit 1
fi

#variables
QPS=$1
CLIENT_THREADS=$2
CLIENT_CORES=$3
SERVER_MACHINE=$4

echo "Summary of arguments:"
echo -e "\t QPS = ${QPS}" 
echo -e "\t CLIENT_THREADS = ${CLIENT_THREADS}" 
echo -e "\t CLIENT_CORES = ${CLIENT_CORES}" 
echo -e "\t SERVER_MACHINE = ${SERVER_MACHINE}"

PID_FILE="xapian_client.pid" #used for store pid of client

# from original script
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# read tailbench configuration
CONFIG_FILE_PATH=${XAPIAN_HOME}/../configs.sh
source ${CONFIG_FILE_PATH}
echo "SUCCESS: configuration read from ${CONFIG_FILE_PATH}"

LD_LIBRARY_PATH=LD_LIBRARY_PATH:${XAPIAN_HOME}/xapian-core-1.2.13/install/lib
export LD_LIBRARY_PATH
echo "SUCCESS: LD_LIBRARY_PATH updated"

NSERVERS=1 # number of servers

# WARMUPREQS=1000 # not used
echo "Executing command"
echo "TBENCH_QPS=${QPS} TBENCH_MINSLEEPNS=100000 TBENCH_SERVER=${SERVER_MACHINE} \
  TBENCH_TERMS_FILE=${DATA_ROOT}/xapian/terms.in TBENCH_CLIENT_THREADS={CLIENT_THREADS} \
  taskset -c ${CLIENT_CORES} ${XAPIAN_HOME}/xapian_networked_client &"
#start running xapian with the given parameters
TBENCH_QPS=${QPS} TBENCH_MINSLEEPNS=100000 TBENCH_SERVER=${SERVER_MACHINE} \
  TBENCH_TERMS_FILE=${DATA_ROOT}/xapian/terms.in TBENCH_CLIENT_THREADS={CLIENT_THREADS} \
  taskset -c ${CLIENT_CORES} ${XAPIAN_HOME}/xapian_networked_client &

#store pid to a file
echo $! > ${PID_FILE}
echo "SUCCESS: client pid written to ${PID_FILE}"

#give set process priority for client process
PID=$(cat ${PID_FILE})
echo "CONFIRMATION: pid of client is ${PID}"
sudo chrt -f -p 99 ${PID}
echo "SUCCESS: priority of client has been set"

#wait to finish, then delete pid file
echo "Waiting on process ${PID}"
wait ${PID}
#clean up
rm ${PID_FILE}
echo "SUCCESS: pid file ${PID_FILE} has been removed, exiting"


