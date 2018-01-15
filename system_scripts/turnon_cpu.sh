#!/bin/bash
        for i in "$@";do
		echo $i
                sudo echo 1 > /sys/devices/system/cpu/cpu$i/online
        done
           
