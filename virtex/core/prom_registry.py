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

from aioprometheus import Summary, Counter

__all__ = ['PROM_METRICS']


PROM_METRICS = dict(
    requests_total = Counter('requests_total',
                             'requests total'),
    queries_total = Counter('queries_total',
                             'queries total'),
    queries_per_request = Summary('queries_per_request',
                                  'number of queries per request'),
    server_latency = Summary('server_latency_milliseconds',
                             'server request handler latency'),
    server_qps = Summary('server_throughput_qps',
                         'server queries per second'),
    server_rps = Summary('server_throughput_rps',
                         'server requests per second'),
    process_request_latency = Summary('process_request_latency_milliseconds',
                                      'process_request handler latency'),
    run_inference_latency = Summary('run_inference_latency_milliseconds',
                                    'run_inference handler latency'),
    process_response_latency = Summary('process_response_latency_milliseconds',
                                       'process_response handler latency (ms)'),
    inference_batch_size = Summary('inference_batch_size',
                                   'inference batch size'),
    request_queue_size = Summary('request_queue_size',
                                 'request queue size'),
    response_queue_size = Summary('response_queue_size',
                                  'response queue size')
)
