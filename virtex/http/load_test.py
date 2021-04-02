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
from virtex.http.message import HttpMessage
from virtex.core.timing import async_now

__all__ = ['HttpLoadTest', 'LoadTestMetrics']


MAX_RPS = 5000


@dataclass()
class LoadTestMetrics:
    """
    Attributes
    ----------
    num_requests: ``int``
    num_queries: ``int``
    test_duration_seconds: ``float``
    client_requests_per_second: ``float``
    server_requests_per_second: ``float``
    server_queries_per_second: ``float``
    server_latency_mean_seconds: ``float``
    server_latency_std_seconds: ``float``
    server_latency_max_seconds: ``float``
    server_latency_p50_seconds: ``float``
    server_latency_p90_seconds: ``float``
    server_latency_p95_seconds: ``float``
    server_latency_p99_seconds: ``float``
    """

    num_requests: int
    num_queries: int
    test_duration_seconds: float
    client_requests_per_second: float
    server_requests_per_second: float
    server_queries_per_second: float
    server_latency_mean_seconds: float
    server_latency_std_seconds: float
    server_latency_max_seconds: float
    server_latency_p50_seconds: float
    server_latency_p90_seconds: float
    server_latency_p95_seconds: float
    server_latency_p99_seconds: float

    def dict(self):
        return asdict(self)

    @classmethod
    def build_from_dict(cls, metrics_dict: dict):
        return cls(**metrics_dict)

    @classmethod
    def build(cls, timestamps: List[Tuple[float]], num_queries: int):
        """
        Parameters
        ----------
        timestamps: ``List[Tuple[float]]``
            List of start-time,end-time pairs
        num_queries: ``int``
            Total number of data items
        """
        num_requests = len(timestamps)
        send_duration = round(float(timestamps[-1][0] - timestamps[0][0]), 5)
        test_duration = round(float(timestamps[-1][1] - timestamps[0][0]), 5)
        client_load_measured = int(num_requests / send_duration)
        latencies = [tstamp[1] - tstamp[0] for tstamp in timestamps]
        return cls(
            test_duration_seconds=test_duration,
            num_requests=num_requests,
            num_queries=num_queries,
            client_requests_per_second=client_load_measured,
            server_requests_per_second=int(num_requests / test_duration),
            server_queries_per_second=int(num_queries / test_duration),
            server_latency_mean_seconds=round(np.mean(latencies), 9),
            server_latency_std_seconds=round(np.std(latencies), 9),
            server_latency_max_seconds=round(max(latencies), 9),
            server_latency_p50_seconds=round(np.percentile(latencies, 50), 9),
            server_latency_p90_seconds=round(np.percentile(latencies, 90), 9),
            server_latency_p95_seconds=round(np.percentile(latencies, 95), 9),
            server_latency_p99_seconds=round(np.percentile(latencies, 99), 9)
        )


@dataclass()
class LoadTestResult:

    """
    Attributes
    ----------
    metrics: LoadTestMetrics
    responses: List[HttpMessage]
    """

    metrics: LoadTestMetrics
    responses: List[HttpMessage]
    num_errors: int

    @classmethod
    def build(cls, metrics, responses):
        num_errors = len([resp.error for resp in responses if resp.error])
        return cls(metrics=metrics,
                   responses=responses,
                   num_errors=num_errors)

    def dict(self):
        _dict = {
            'metrics': asdict(self.metrics),
            'num_errors': self.num_errors,
            'responses': self.responses
        }
        return _dict

    @classmethod
    def build_from_dict(cls, result_dict: dict):
        metrics = LoadTestMetrics.build_from_dict(
            result_dict['metrics'])
        return cls(metrics=metrics,
                   responses=result_dict['responses'],
                   num_errors=result_dict['num_errors'])


class LoadTestTask:
    start_time: float
    end_time: float
    resp: Union[asyncio.Future, HttpMessage]


class HttpLoadTest():

    """
    Virtex HTTP load test client
    """

    def __init__(self):
        super().__init__()
        self.client = HttpClient()
        self.loop = self.client.loop

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
            await asyncio.sleep(self.client.CLOCK)

    async def __run_async(self, url, messages, load_duration):
        start_t = async_now(self.loop)
        for idx, message in enumerate(messages):
            while self.__wait(
                    start_t, idx, self._n_messages, load_duration):
                await asyncio.sleep(self.client.CLOCK)
            asyncio.ensure_future(
                self.__send(url, message))
        await self.__collect()

    def run(self,
            url: str,
            messages: List[HttpMessage],
            requests_per_second: int = MAX_RPS):
        """
        Parameters
        ----------
        url: ``str``
        messages: ``List[HttpMessage]``
            List of virtex messages to post
        requests_per_second: ``int``
            Load to apply to the server (max = 5000)

        Notes
        -----
        * The Virtex HttpClient can reliably apply
          up to ~5000 requests per second per thread
          for single query requests carrying a small
          payload.

        Returns
        -------
        result: ``LoadTestResult``
        """
        self.__flush(len(messages))
        load_duration = len(messages) / requests_per_second
        num_data = sum([len(message.data) for message in messages])
        self.loop.run_until_complete(
            asyncio.ensure_future(
                self.__run_async(url, messages, load_duration)))
        responses, timestamps = zip(*sorted(
            [(task.resp, (task.start_time, task.end_time))
             for task in self._tasks],
            key=lambda tup: tup[1][0]))
        metrics = LoadTestMetrics.build(timestamps, num_data)
        return LoadTestResult.build(metrics=metrics, responses=responses)
