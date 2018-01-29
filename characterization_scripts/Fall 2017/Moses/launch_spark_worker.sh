#!/bin/bash

source /home/ds318/scripts/bash_helpers/readPathsConfiguration.sh

if ! [ -d ${SPARK_HOME} ]
then
        echo "SPARK_HOME path ${SPARK_HOME} does not exist"
        exit 1
fi

if [ "$#" -ne 3 ]
then 
	echo "Usage:"
	echo "${BASH_SOURCE[0]} SPARK_CORES CORE_FREQUENCY MASTER_IP"
	exit 1
fi

SPARK_CORES=$1
CORE_FREQUENCY=$2
MASTER_IP=$3

sudo cpupower -c ${SPARK_CORES} frequency-set -f ${CORE_FREQUENCY}

taskset -c ${SPARK_CORES} ${SPARK_HOME}/sbin/start-slave.sh ${MASTER_IP}:7077
