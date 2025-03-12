#!/bin/bash

if [ -f kafka/kafka-logs-*/meta.properties]; then
    echo "Deleting meta.properties"
    rm -f kafka/kafka-logs-*/meta.properties
fi 

echo "Kafka Starting"

exec start-kafka.sh