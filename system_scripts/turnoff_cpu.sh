#!/bin/bash
	for i in "$@";do
		sudo echo 0 > /sys/devices/system/cpu/cpu$i/online
	done
