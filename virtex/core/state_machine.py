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
from typing import Any

from typing_extensions import Literal

from virtex.inference import RequestHandler
from virtex.core.timing import async_now
from virtex.core.profile import profile
from virtex.core.event_loop import EventLoopContext
from virtex.core.queue import RequestQueue, ResponseQueue, WAIT_KEY
from virtex.core.prom_client import PROM_CLIENT

__all__ = ['VirtexStateMachine']


class VirtexStateMachine(EventLoopContext):

    """
    Finite state machine for executing inference with
    dynamic batching on the virtex server.
    """

    def __init__(self,
                 name: str,
                 handler: RequestHandler,
                 max_batch_size: int,
                 max_time_on_queue: float,
                 metrics_host: str,
                 metrics_port: int,
                 metrics_mode: Literal['push', 'scrape'],
                 metrics_interval: float):
        """
        Parameters
        ----------
        name: ``str``
            Application name
        handler: ``virtex.RequestHandler``
            User compute wrapper
        max_batch_size : ``int``, optional
            Maximum batch size
        max_time_on_queue : ``float``, optional
            Maximum time that items spend on
            processing queue (seconds)
        metrics_host: str default = '127.0.0.1'
            Prometheus metrics URL or gateway host
        metrics_port: ``int``
        metrics_mode: ``str``
        metrics_interval: ``float``
            Metrics push interval (seconds)
        """
        if metrics_mode not in ('scrape', 'push'):
            raise ValueError(
                "metrics_mode must be set to 'scrape' or 'push'.")
        super().__init__()
        self._max_batch_size = max_batch_size
        self._max_time_on_queue = max_time_on_queue
        self.handler = handler
        self.input_queue = RequestQueue(max_batch_size)
        self.output_queue = ResponseQueue()
        self.metrics_client = PROM_CLIENT[metrics_mode](
            name,
            metrics_host,
            metrics_port,
            metrics_interval,
            loop=self.loop)
        self._running = False

    def check_running(self):
        if not self._running:
            asyncio.ensure_future(self.__poll_input_queue())
            self._running = True

    async def _process_request(self, items: list):
        @profile(self.metrics_client.observe,
                 'process_request_latency',
                 tstamp_fn=lambda t0, t1: t1 - t0)
        def execute():
            return self.handler.process_request(items)
        return execute()

    async def _run_inference(self, batch: Any):
        @profile(self.metrics_client.observe,
                 'run_inference_latency',
                 tstamp_fn=lambda t0, t1: t1 - t0)
        def execute():
            return self.handler.run_inference(batch)
        return execute()

    async def _process_response(self, result) -> Any:
        @profile(self.metrics_client.observe,
                 'process_response_latency',
                 tstamp_fn=lambda t0, t1: t1 - t0)
        def execute():
            return self.handler.process_response(result)
        return execute()

    async def __process(self):
        tasks = self.input_queue.pull()
        self.metrics_client.observe('batch_size', len(tasks))
        inputs = asyncio.ensure_future(
            self._process_request([task.item for task in tasks]))
        outputs = asyncio.ensure_future(
            self._run_inference(await inputs))
        resp_futures = []
        for key, result in zip([task.key for task in tasks],
                               await outputs):
            resp_futures.append((key, asyncio.ensure_future(
                self._process_response(result))))
        for key, future in resp_futures:
            self.output_queue.update({key: await future})
        self.metrics_client.observe('response_queue_size',
                                    self.output_queue.qsize())

    async def __poll_input_queue(self):
        size: int
        full: bool
        wait: bool
        time: float = async_now(self.loop)
        while True:
            size = self.input_queue.qsize()
            full = size >= self._max_batch_size
            wait = (async_now(self.loop) - time) \
                < self._max_time_on_queue
            if size and (full or not wait):
                time = async_now(self.loop)
                self.metrics_client.observe(
                    'task_queue_size', size)
                await self.__process()
            else:
                await self.sleep()

    async def poll_output_queue(self, key: str):
        while True:
            response = self.output_queue.poll(key)
            if response is not WAIT_KEY:
                return response
            else:
                await self.sleep()
