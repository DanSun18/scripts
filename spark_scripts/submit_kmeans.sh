#!/bin/bash

/home/ds318/spark/bin/spark-submit --num-executors 20 --jars /home/ds318/spark/examples/target/scala-2.11/jars/scopt_2.11-3.3.0.jar \
--class org.apache.spark.examples.mllib.DenseKMeans --master spark://$(hostname):7077 \
--deploy-mode client \
/home/ds318/spark/examples/target/scala-2.11/jars/spark-examples_2.11-2.1.0.jar \
-k 1000 /home/ds318/yuhao_datasets/USCensus1990.data.txt &
