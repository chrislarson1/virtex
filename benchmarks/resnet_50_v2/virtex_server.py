# -------------------------------------------------------------------
# Copyright 2021 Virtex authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# -------------------------------------------------------------------

import os

import numpy as np
from PIL import Image
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from keras.applications import resnet_v2
from keras.applications import resnet50
from keras_preprocessing import image

from virtex import RequestHandler, \
    HttpServer, HttpMessage
from virtex.serial import encode_bytes, \
    decode_pil_from_bytes, encode_pickle


# Build ResNet50 request handler
class ResnetComputation(RequestHandler):

    def __init__(self):
        self.model = resnet_v2.ResNet50V2(weights='imagenet')

    def process_request(self, data):
        for i, item in enumerate(data):
            img = decode_pil_from_bytes(item)
            img = img.convert('RGB')
            img = img.resize((224, 224), Image.NEAREST)
            data[i] = resnet50.preprocess_input(image.img_to_array(img))
        data = np.stack(data, axis=0)
        return data

    def run_inference(self, model_input):
        return self.model.predict(model_input)

    def process_response(self, model_output_item):
        return encode_pickle(model_output_item)

resnet_request_handler = ResnetComputation()


# Create http test messages
path = os.path.dirname(os.path.abspath(__file__))
img = open(os.path.join(
    path, "../../data/tiny-imagenet-200/test/images/test_0.JPEG"
), 'rb').read()

max_batch_size = 128

message1 = HttpMessage(data=[img])
message1.encode(encode_bytes)

message2 = HttpMessage(data=[img for _ in range(max_batch_size)])
message2.encode(encode_bytes)


# Validate the handler can process the message
response1 = resnet_request_handler.validate(message1)
response2 = resnet_request_handler.validate(message2)


# Create an http server
server = HttpServer(
    name='resnet_50_v2_image_classification_service',
    handler=ResnetComputation(),
    max_batch_size=128,
    max_time_on_queue=0.01,
    metrics_host='http://0.0.0.0',
    metrics_port=9090,
    metrics_mode='push',
    metrics_interval=0.005
)

app = server.app
