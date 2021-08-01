#!/usr/bin/env bash

APP_HTTP_PORT=":${APP_HTTP_PORT:-6000}"
APP_WORKERS=${APP_WORKERS:-2}
APP_THREADS=${APP_THREADS:-4}
APP_CELERY_WORKERS=${APP_CELERY_WORKERS:-1}
APP_LOG_LEVEL=${APP_LOG_LEVEL:-WARNING}
APP_LOG_FILE=${APP_LOG_FILE:-"-"}
APP_TIMEOUT=${APP_TIMEOUT:-10}
APP_TYPE=${APP_TYPE:-'gunicorn'}
APP_AUTO_RELOAD=${APP_AUTO_RELOAD:-false}
CELERY_TYPE=${CELERY_TYPE:-"worker"}
CELERY_QUEUE=${CELERY_QUEUE:-""}
CELERY_NAME=${CELERY_NAME:-'worker-celery.%%h'}
CELERY_SCHEDULE_DB=${CELERY_SCHEDULE_DB:-'/app/run/celerybeat-schedule'}
CELERY_BEAT_PID_FILE=${CELERY_BEAT_PID_FILE:-'/app/run/celerybeat.pid'}
MAX_MEMORY_PER_CHILD=${MAX_MEMORY_PER_CHILD:-1000000}

echo PWD: `pwd`
echo ID: `id`
echo HOME: $HOME

if [[ "$APP_TYPE" == "celery" ]]; then
   if [[ "${CELERY_TYPE}" == 'worker' ]]; then
      celery -A warehouse_main ${CELERY_TYPE} -l ${APP_LOG_LEVEL} --pool prefork --concurrency ${APP_CELERY_WORKERS} -Q ${CELERY_QUEUE} -n ${CELERY_NAME} -Ofair --max-memory-per-child=${MAX_MEMORY_PER_CHILD}
   fi
   
   if [[ "${CELERY_TYPE}" == 'beat' ]]; then
      celery -A warehouse_main ${CELERY_TYPE} -l ${APP_LOG_LEVEL} -s ${CELERY_SCHEDULE_DB} --pidfile ${CELERY_BEAT_PID_FILE}
   fi
fi

if [[ "$APP_TYPE" == "gunicorn" ]]; then
  gunicorn "warehouse_main.wsgi:application" --bind ${APP_HTTP_PORT} --reuse-port \
    --preload --worker-class sync --worker-tmp-dir "/dev/shm" --workers ${APP_WORKERS} \
    --threads ${APP_THREADS} --log-file=${APP_LOG_FILE} --log-level ${APP_LOG_LEVEL} --access-logfile '-' \
    --timeout ${APP_TIMEOUT}
fi
