#!/bin/bash

set -e

TASK=$1

case "$TASK" in
   "bert-server")
      WORKERS=$2
      cd "$HOME"/virtex/examples/bert_base_cased_embedding
      ./virtex_server.sh "$WORKERS"
      ;;
   "bert-client")
      NUM_DATA=$2
      BATCHSIZE=$3
      RPS=$4
      cd "$HOME"/virtex/examples/bert_base_cased_embedding
      python virtex_client.py "$NUM_DATA" "$BATCHSIZE" "$RPS"
      ;;
   "resnet-server")
      WORKERS=$2
      cd "$HOME"/virtex/examples/resnet50_v2
      ./virtex_server.sh "$WORKERS"
      ;;
   "resent-client")
      NUM_DATA=$2
      BATCHSIZE=$3
      RPS=$4
      cd "$HOME"/virtex/examples/resnet50_v2
      python virtex_client.py "$NUM_DATA" "$BATCHSIZE" "$RPS"
      ;;
   "echo-server")
      WORKERS=$2
      cd "$HOME"/virtex/examples/echo
      ./virtex_server.sh "$WORKERS"
      ;;
   "echo-client")
      NUM_DATA=$2
      BATCHSIZE=$3
      RPS=$4
      cd "$HOME"/virtex/examples/echo
      python virtex_client.py "$NUM_DATA" "$BATCHSIZE" "$RPS"
      ;;
   *)
     echo "$TASK is not a valid argument."
     exit 1
     ;;
esac
