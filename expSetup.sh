#!/bin/bash

#First argument is cpu to turn off, e.g. "1 2 3"
#Second argument is cpu frequency, e.g. 2.10GHz
#if arguments are not provided, the default values below will be used
DEFAULT_CPU_TO_TURNOFF="12 13 14 15" 
DEFAULT_FREQUENCY=2.10GHz
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SYSTEM_SCRIPT_DIR=${DIR}/system_scripts
#turn off puppet agent
#sudo puppet agent --disable "running experiment"

#turn on all cores
sudo ${SYSTEM_SCRIPT_DIR}/enable_cores.sh

#turn off cores as indicated
CPU_TO_TURNOFF=""
if [ -z "$1" ]
  then
    CPU_TO_TURNOFF=${DEFAULT_CPU_TO_TURNOFF}
  else
    CPU_TO_TURNOFF="$1"
fi
sudo ${SYSTEM_SCRIPT_DIR}/turnoff_cpu.sh ${CPU_TO_TURNOFF}

#change sudo time windows
#sudo visudo

#disable c-states
sudo ${SYSTEM_SCRIPT_DIR}/set_cstate.sh 1 0 

#turn off turbo boost
sudo ${SYSTEM_SCRIPT_DIR}/turbo-boost.sh disable

#set core frequency
CPU_FREQUENCY=""
if [ -z "$2" ]
  then
    CPU_FREQUENCY=${DEFAULT_FREQUENCY}
  else
    CPU_FREQUENCY="$2"
fi
sudo cpupower frequency-set -f 2.10GHz
echo "Experiment Setup:"
echo -e  "\tAll logical cores are turned on"
echo -e "\tLogical cores ${CPU_TO_TURNOFF} are turned off"
echo -e "\tC states are disabled"
echo -e "\tTurboboost turned off"
echo -e "\tCore frequency set to ${CPU_FREQUENCY}"
echo "----------"
echo "Specify cores to turn off and core frequency using this format"
echo -e "\t${BASH_SOURCE[0]} [ CPU_TO_TURNOFF CORE_FREQUENCY ]"
