#!/bin/sh

location="%location%"
dep_unit="%du%"
publish_ports="%publish_ports%"

trial_count=3

# Try wget and docker_load
stage1_success=false
RETRIES=0
until [ $RETRIES -ge $trial_count ]; do
  wget "$location" --output-document="$dep_unit"
  docker load < $dep_unit
  if [[ $? == 0 ]]; then
     stage1_success=true
     break
  fi
  RETRIES=$[$RETRIES+1]
  sleep 2
done

if [ "$stage1_success" = false ]; then
  wc_notify --data-binary '{"status": "FAILURE", "reason": "wget and docker load failed."}'
fi


# Try docker run
docker_run_success=false
RETRIES=0
until [ $RETRIES -ge $trial_count ]; do
  docker run $publish_ports -d $dep_unit
  docker ps |grep $dep_unit
  if [[ $? == 0 ]]; then
     docker_run_success=true
     break
  fi
  RETRIES=$[$RETRIES+1]
  sleep 2
done

if [ "$docker_run_success" = false ]; then
  wc_notify --data-binary '{"status": "FAILURE", "reason": "docker run failed."}'
else
  wc_notify --data-binary '{"status": "SUCCESS"}'
fi
