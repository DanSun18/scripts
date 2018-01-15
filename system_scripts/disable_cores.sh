#!/bin/sh

for i in `seq 15 23`;
do
echo 0 > /sys/devices/system/cpu/cpu$i/online
done
for i in `seq 39 47`;
do
echo 0 > /sys/devices/system/cpu/cpu$i/online
done


