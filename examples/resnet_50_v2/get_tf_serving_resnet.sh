#!/bin/bash
sudo mkdir -p /tmp/resnet
sudo curl -s https://storage.googleapis.com/download.tensorflow.org/models/official/20181001_resnet/savedmodels/resnet_v2_fp32_savedmodel_NHWC_jpg.tar.gz \
  | tar --strip-components=2 -C /tmp/resnet -xvz
docker pull tensorflow/serving:latest-gpu
