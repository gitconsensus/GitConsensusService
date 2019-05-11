#!/usr/bin/env bash

if [[ ! -v 'MINIMUM_WORKERS' ]]; then
  MINIMUM_WORKERS=2
fi

if [[ ! -v 'MAXIMUM_WORKERS' ]]; then
  MAXIMUM_WORKERS=10
fi

if [ "$DISABLE_BEAT" = "true" ]
then
  echo 'Launching celery worker without beat'
  celery -A gitconsensusservice.worker.celery worker --loglevel=info --autoscale=$MAXIMUM_WORKERS,$MINIMUM_WORKERS
else
  echo 'Launching celery worker with beat enabled'
  rm -f ~/celerybeat-schedule
  celery -A gitconsensusservice.worker.celery worker --loglevel=info --autoscale=$MAXIMUM_WORKERS,$MINIMUM_WORKERS -B -s ~/celerybeat-schedule
fi
