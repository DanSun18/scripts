#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SYSTEM_SCRIPT_DIR=${DIR}/system_scripts

#turn on all cores
sudo ${SYSTEM_SCRIPT_DIR}/enable_cores.sh

#turn on turbo boost
sudo ${SYSTEM_SCRIPT_DIR}/turbo-boost.sh enable

#enable c-states
sudo ${SYSTEM_SCRIPT_DIR}/reset_cstate.sh 

#turn on puppet agent
#sudo puppet agent --enable

sudo cpupower frequency-set -g ondemand

echo "Experiment Finish Summary:"
echo -e "\tAll logcial cores turned on"
echo -e "\tTurboBoost enabled"
echo -e "\tC-states enabled"
echo -e "\tCPU governor set to on-demand"
