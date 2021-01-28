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
from typing_extensions import Literal

from virtex.core.logging import LOGGER
from virtex.core.task import Task
from virtex.core.state_machine import VirtexStateMachine
from virtex.core.profile import profile
from virtex.http.message import HttpMessage
from virtex.inference import RequestHandler


__all__ = ['HttpServer']


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
            'headers': [[b'content-type',
                         b'application/json']]}


def make_body(response):
    return {'type': 'http.response.body',
            'body': response.json}


class HttpServer(VirtexStateMachine):

    """
    Virtex HTTP Server
    """

    def __init__(self,
                 name : str,
                 handler : RequestHandler,
                 max_batch_size : int = 512,
                 max_time_on_queue : float = 0.005,
                 metrics_host : str = '127.0.0.1',
                 metrics_port : int = 9090,
                 metrics_mode : Literal['push', 'scrape'] = 'scrape',
                 metrics_interval : float = 0.01,
                 max_conn : int = 10000):
        """
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
        metrics_host: ``str``
        metrics_port: ``int``
        metrics_mode: ``str``
        metrics_interval: ``float``
        max_conn: ``int``
            Max number of concurrent server connections
        """
        super().__init__(
            name=name,
            handler=handler,
            max_batch_size=max_batch_size,
            max_time_on_queue=max_time_on_queue,
            metrics_host=metrics_host,
            metrics_port=metrics_port,
            metrics_mode=metrics_mode,
            metrics_interval=metrics_interval
        )
        self.__name = name
        self.__max_conn = max_conn

    @property
    def app(self):

        async def _send(send, status, response):
            await send(make_header(status))
            await send(make_body(response))

        @profile(self._metrics_client.observe,
                 'server_latency',
                 tstamp_fn=lambda t0, t1: t1 - t0,
                 loop=self.loop)
        async def handler(scope, receive, send):
            self._check_running()
            if scope['type'] != 'http':
                await _send(send, 403, HttpMessage(
                    error="This endpoint accepts http requests."))
                return
            try:
                body = await read_body(receive)
                request = HttpMessage(**body)
            except Exception as e:
                msg = f"HttpServer caught exception: {str(e)}"
                LOGGER.exception(msg=msg)
                await _send(send, 400, HttpMessage(error=msg))
                return
            try:
                tasks = []
                for item in request.data:
                    task = Task(item=item)
                    self._input_queue.put(task)
                    tasks.append(self._poll_output_queue(task.key))
                await _send(send, 200, HttpMessage(
                    data=await asyncio.gather(*tasks)))
                return
            except Exception as e:
                msg = f"HttpServer caught exception: {str(e)}"
                LOGGER.exception(msg=msg)
                await _send(send, 500, HttpMessage(error=msg))

        return handler
