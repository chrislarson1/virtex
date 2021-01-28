#!/bin/bash

gunicorn \
  virtex_server:app \
  -w $1 \
  -k virtex.VirtexWorker \
  --bind localhost:8081 \
  --max-requests 10000 \
  --worker-connections 10000 \
  --log-level critical
