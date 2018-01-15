#!/bin/bash

for i in "$@";
do
echo $i
sudo cpufreq-set -c $i -g ondemand
done

