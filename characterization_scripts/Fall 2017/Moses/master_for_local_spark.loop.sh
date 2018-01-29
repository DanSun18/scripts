#!/bin/bash

for index in {1..6..1}
do
	./master_for_local_spark.sh 500 q500${index} | tee q500_${index}.rmsg
done
