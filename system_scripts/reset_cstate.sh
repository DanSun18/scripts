#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
kill $(cat ${DIR}/setcstate_$( hostname ).pid)
rm ${DIR}/setcstate_$( hostname ).pid
