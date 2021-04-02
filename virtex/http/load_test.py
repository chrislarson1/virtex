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
from dataclasses import dataclass, asdict
from typing import List, Tuple, Union

import numpy as np

from virtex.http.client import HttpClient
from virtex.core.logging import LOGGER
from virtex.http.message import HttpMessage
from virtex.core.timing import async_now

__all__ = ['HttpLoadTest', 'LoadTestMetrics']


@dataclass()
class _LoadTestMetrics:

    test_duration: float
    num_requests: int
    num_queries: int
    client_requests_per_second: float
    server_requests_per_second: float
    server_queries_per_second: float
    latency_mean: float
    latency_std: float
    latency_max: float
    latency_p50: float
    latency_p90: float
    latency_p95: float
    latency_p99: float

    def dict(self):
        return asdict(self)

    @classmethod
    def build_from_dict(cls, metrics_dict: dict):
        return cls(**metrics_dict)

    @classmethod
    def build(cls,
              timestamps: List[Tuple[float]],
              num_queries: int,
              client_load: float):
        """
        Parameters
        ----------
        timestamps: ``List[Tuple[float]]``
            List of start-time,end-time pairs
        num_queries: ``int``
            Total number of data items
        client_load: ``float``
            client load to apply in requests per second
        """
        latencies = [tstamp[1] - tstamp[0] for tstamp in timestamps]
        num_requests = len(timestamps)
        test_duration = round(float(timestamps[-1][1] - timestamps[0][0]), 5)
        return cls(
            test_duration=test_duration,
            num_requests=num_requests,
            num_queries=num_queries,
            client_requests_per_second=client_load,
            server_requests_per_second=int(num_requests / test_duration),
            server_queries_per_second=int(num_queries / test_duration),
            latency_mean=round(np.mean(latencies), 7),
            latency_std=round(np.std(latencies), 7),
            latency_max=round(max(latencies), 7),
            latency_p50=round(np.percentile(latencies, 50), 7),
            latency_p90=round(np.percentile(latencies, 90), 7),
            latency_p95=round(np.percentile(latencies, 95), 7),
            latency_p99=round(np.percentile(latencies, 99), 7)
        )


@dataclass()
class LoadTestMetrics:

    num_requests: int
    num_queries: int
    test_duration_seconds: float
    client_requests_per_second: float
    server_requests_per_second: float
    server_queries_per_second: float
    server_mean_latency_seconds: float

    def dict(self):
        return asdict(self)

    @classmethod
    def build_from_dict(cls, metrics_dict: dict):
        return cls(**metrics_dict)

    @classmethod
    def build(cls,
              timestamps: List[Tuple[float]],
              num_queries: int,
              client_load: float):
        """
        Parameters
        ----------
        timestamps: ``List[Tuple[float]]``
            List of start-time,end-time pairs
        num_queries: ``int``
            Total number of data items
        client_load: ``float``
            client load to apply in requests per second
        """
        num_requests = len(timestamps)
        test_duration = round(float(timestamps[-1][1] - timestamps[0][0]), 5)
        return cls(
            test_duration_seconds=test_duration,
            num_requests=num_requests,
            num_queries=num_queries,
            client_requests_per_second=client_load,
            server_requests_per_second=int(num_requests / test_duration),
            server_queries_per_second=int(num_queries / test_duration),
            server_mean_latency_seconds=round(test_duration / num_requests, 5),
        )


class LoadTestTask:
    start_time: float
    end_time: float
    resp: Union[asyncio.Future, HttpMessage]


class HttpLoadTest():

    """
    Virtex HTTP load test client

    Notes
    -----
    * aiohttp does not give fine grained control over the timing of
      sending requests, at least using the patterns provided in the
      documentation. These patterns result in all of the request
      futures being dumped onto the event loop prior to execution,
      making it non trivial to measure end-to-end server latency as
      there is no easy way to record the timestamp when the POSTs are
      executed. Using the ``on_request_start`` and ``on_request_end``
      callback approach does not seem to fix this problem. As such,
      latency measurements are inaccurate. The throughput is accurate,
      though, and for a reasonable proxy for the average latency, here
      we divide the number of requests sent by the total test_duration.
      This issue is being addressed and will be fixed in a later release.
    """

    def __init__(self):
        super().__init__()
        self.client = HttpClient()
        self.loop = self.client.loop
        self.sleep = self.client.sleep

    async def __send(self, url, message):
        task = LoadTestTask()
        task.start_time = async_now(self.loop)
        task.resp = await self.client.post_async(url, message)
        task.end_time = async_now(self.loop)
        self._tasks.append(task)

    def __flush(self, n_messages: int):
        self._n_messages = n_messages
        self._n_recv = 0
        self._tasks = []

    def __wait(self, start_t, index, num_messages, duration):
        messages_fraction = index / num_messages
        time_fraction = (async_now(self.loop) - start_t) / duration
        return messages_fraction > time_fraction

    async def __collect(self):
        while len(self._tasks) < self._n_messages:
            await self.sleep()

    async def __run_async(self, url, messages, load_duration):
        start_t = async_now(self.loop)
        for idx, message in enumerate(messages):
            while self.__wait(
                    start_t, idx, self._n_messages, load_duration):
                await self.sleep()
            asyncio.ensure_future(
                self.__send(url, message))
        await self.__collect()

    def run(self,
            url: str,
            messages: List[HttpMessage],
            requests_per_second: int = 3500):
        """
        Run http load test on a virtex endpoint

        Parameters
        ----------
        url: ``str``
        requests_per_second: ``int``
            Load to apply to the server (max = 3500)
        messages: ``List[HttpMessage]``
            List of virtex messages to post

        Notes
        -----
        * The maximum request generation rate is ~3500 on a single
          thread in Python. For larger loads, run in distributed mode.

        Returns
        -------
        responses, metrics : ``Tuple[HttpMessage, LoadTestMetrics]``
        """
        if requests_per_second > 3500:
            LOGGER.warning("Virtex http client can apply a maximum of "
                           "~3500 requests per second per thread.")
        self.__flush(len(messages))
        load_duration = len(messages) / requests_per_second
        num_data = sum([len(message.data) for message in messages])
        self.loop.run_until_complete(
            asyncio.ensure_future(
                self.__run_async(url, messages, load_duration)))
        response, timestamps = zip(*sorted(
            [(task.resp, (task.start_time, task.end_time))
             for task in self._tasks],
            key=lambda tup: tup[1][0]))
        metrics = LoadTestMetrics.build(timestamps, num_data, requests_per_second)
        return response, metrics
