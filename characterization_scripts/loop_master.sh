#!/bin/bash
for THREADS in {2..2..1}
do
	for QPS in {100..1100..100}
	do
		source ./master.sh $THREADS $QPS
	done
done
