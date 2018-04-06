#!/bin/bash
for THREADS in {1..2..1}
do
	for QPS in {100..1000..100}
	do
		source ./master.sh $THREADS $QPS
	done
done
