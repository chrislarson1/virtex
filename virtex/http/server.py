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

import asyncio

import orjson as json

from virtex.core.logging import LOGGER
from virtex.core.task import Task
from virtex.core.state_machine import VirtexStateMachine
from virtex.core.profile import profile
from virtex.http.message import HttpMessage
from virtex.inference import RequestHandler
from virtex.core.timing import async_now


__all__ = ['http_server']


async def read_body(receive):
    """
    Read http request body in chunks
    """
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return json.loads(body)


def make_header(status):
    return {'type': 'http.response.start',
            'status': status,
            'headers': [(b'content-type', b'application/json'),
                        (b'connection', b'keep-alive')]}


def make_body(response):
    return {'type': 'http.response.body',
            'body': response.json}


def app(state_machine: VirtexStateMachine):

    async def _send(send, status, response,
                    start_t=None, num_queries=None):
        await send(make_header(status))
        await send(make_body(response))
        if status == 200 and start_t and num_queries:
            end_t = async_now(state_machine.loop)
            latency = end_t - start_t
            if latency > 0:
                state_machine.prom_client.observe(
                    'server_rps', value=1000 * (1 / latency))
                state_machine.prom_client.observe(
                    'server_qps', value=1000 * (num_queries / latency))

    def _app():
        """ASGI3 wrapper"""
        @profile(state_machine.prom_client.observe,
                 'server_latency',
                 tstamp_fn=lambda t0, t1: t1 - t0,
                 loop=state_machine.loop)
        async def request_handler(scope, receive, send):
            start_t = async_now(state_machine.loop)
            state_machine.check_running()
            if scope['type'] != 'http':
                await _send(send, 403, HttpMessage(
                    error="This endpoint accepts http requests."))
                return
            try:
                body = await read_body(receive)
                request = HttpMessage(**body)
                state_machine.prom_client.add('requests_total', 1)
                state_machine.prom_client.add('queries_total', len(request.data))
                state_machine.prom_client.observe('queries_per_request', len(request.data))
            except Exception as e:
                msg = f"HttpServer caught exception: {str(e)}"
                LOGGER.exception(msg=msg)
                await _send(send, 400, HttpMessage(error=msg))
                return
            try:
                tasks = []
                for item in request.data:
                    task = Task(item=item)
                    state_machine.input_queue.put(task)
                    tasks.append(state_machine.poll_output_queue(task.key))
                await _send(send=send,
                            status=200,
                            response=HttpMessage(data=await asyncio.gather(*tasks)),
                            num_queries=len(tasks),
                            start_t=start_t)
                return
            except Exception as exc:
                msg = f"{state_machine.name} caught exception: {str(exc)}"
                LOGGER.exception(msg=msg)
                await _send(send, 500, HttpMessage(error=msg))

        return request_handler

    return _app


def http_server(name: str,
                handler: RequestHandler,
                max_batch_size: int = 512,
                max_time_on_queue: float = 0.005,
                prom_host: str = 'http://127.0.0.1',
                prom_port: int = 9090,
                prom_mode: str = 'off',
                prom_push_interval: float = 0.01):
    """
    Returns a web server that implements the computation handler

    Parameters
    ----------
    name : ``str``
        Service name
    handler: RequestHandler
        Wrapper for server-side computation
    max_batch_size : ``Optional[int]``
        Maximum batch size
    max_time_on_queue : ``Optional[float]``
        Maximum time that items spend on processing
        queue (seconds). Can be fractional.
    prom_host: ``str``
    prom_port: ``int``
    prom_mode: ``str``
        "off": no metrics collection
        "scrape": prometheus scrape
        "push": prometheus pushgateway
    prom_push_interval: ``float``
    """
    return app(VirtexStateMachine(name,
                                  handler,
                                  max_batch_size,
                                  max_time_on_queue,
                                  prom_host,
                                  prom_port,
                                  prom_mode,
                                  prom_push_interval))
