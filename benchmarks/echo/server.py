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

from virtex import HttpServer, RequestHandler


class EchoServer(RequestHandler):

    def process_request(self, data):
        return data

    def run_inference(self, model_input):
        return model_input

    def process_response(self, model_output_item):
        return model_output_item


server = HttpServer(
    name='bert_embedding_service',
    handler=EchoServer(),
    max_batch_size=512,
    max_time_on_queue=0.01,
    metrics_host='http://0.0.0.0',
    metrics_port=9091,
    metrics_mode='scrape',
    metrics_interval=0.1
)

app = server.app
