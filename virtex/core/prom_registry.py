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

from aioprometheus import Summary

__all__ = ['PROM_METRICS']


PROM_METRICS = dict(
    server_latency = Summary('server_latency',
                             'server request handler latency (ms)'),
    server_throughput = Summary('server_throughput',
                                'server transactions per second'),
    process_request_latency = Summary('process_request_latency',
                                      'process_request handler latency (ms)'),
    run_inference_latency = Summary('run_inference_latency',
                                    'run_inference handler latency (ms)'),
    process_response_latency = Summary('process_response_latency',
                                       'process_response handler latency (ms)'),
    batch_size = Summary('batch_size',
                         'batch size of tasks processed from queue'),
    task_queue_size = Summary('task_queue_size',
                              'task queue size'),
    response_queue_size = Summary('response_queue_size',
                                  'response queue size')
)
