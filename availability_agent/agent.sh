#!/bin/bash

TEST_PERIODICITY=5

if [ -z "$DB_USERNAME" ]; then
    echo "Error: Environment variable $DB_USERNAME is not set."
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "Error: Environment variable $DB_PASSWORD is not set."
    exit 1
fi

if [ -z "$INFLUXDB_URL" ]; then
    echo "Error: Environment variable $INFLUXDB_URL is not set."
    exit 1
fi

while true
do
  while read -r TESTED_HOST
  do
      RESULT=$(ping  -c 1 -W 2 "$TESTED_HOST"  | grep -oP '(?<=time=)\d+(\.\d+)?')
      TEST_TIMESTAMP=$(date +%s%N)

      if [[ ! -n "$RESULT" ]]
      then
        RESULT=0
      fi

      echo "Test Result for $TESTED_HOST is $RESULT at $TEST_TIMESTAMP"
      curl -X POST "$INFLUXDB_URL/write?db=hosts_metrics" -u $DB_USERNAME:$DB_PASSWORD  --data-binary "availability_test,host=$TESTED_HOST value=$RESULT $TEST_TIMESTAMP"

  done < hosts

  echo ""
  sleep $TEST_PERIODICITY
done