#!/bin/bash


function run () {

  server=$1  # server:app
  n_workers=$2  # Number of server instances
  port=$3  # Port number
  log_level=$4  # log level

  gunicorn \
  "$server" \
  -w "$n_workers" \
  -k virtex.VirtexWorker \
  --bind localhost:"$port" \
  --log-level "$log_level" \
  --logger-class virtex.VirtexLogger
}


function f () {
  TEMP=$(getopt --long -o "u:h:" "$@")
  eval set -- "$TEMP"
  while true ; do
      case "$1" in
          -s )
              server=$2
              shift 2
          ;;
          -n )
              n_workers=$2
              shift 2
          ;;
          -p )
              port=$2
              shift 2
          ;;
          -l )
              log_level=$2
              shift 2
          ;;
          *)
              break
          ;;
      esac
done;
}
