#!/bin/bash
docker run \
  --rm \
  --runtime=nvidia \
  --name tfserving_resnet \
  --cpuset-cpus="5" \
  -p 8501:8501 \
  -v /tmp/resnet:/models/resnet \
  -e MODEL_NAME=resnet \
  -t tensorflow/serving:latest-gpu \
  &