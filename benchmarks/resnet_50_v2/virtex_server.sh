#!/bin/bash

gunicorn \
  virtex_server:app \
  -w "$1" \
  -k virtex.VirtexWorker \
  --bind localhost:8081 \
  --log-level "$2"