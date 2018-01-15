#!/bin/bash

for i in "$@";
do
sudo cpufreq-set -c $i -g userspace
sudo cpufreq-set -c $i -f 2.7GHz
done

