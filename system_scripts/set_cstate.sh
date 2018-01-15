#!/bin/bash

if [ $# -ne 2 ]
then
	echo "Usage: ${BASH_SOURCE[0]} [core latency]"
	exit 1
fi
CORE=$1
LATENCY=$2
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
taskset -c ${CORE} ${DIR}/set_cstate ${LATENCY} &
echo $! > ${DIR}/setcstate_$( hostname ).pid
