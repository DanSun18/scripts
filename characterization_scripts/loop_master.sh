
for THREADS in {1..3..2}
do
	for QPS in {100..1100..100}
	do
		source ./master.sh $THREADS $QPS
	done
done
