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

import socket
import requests
import asyncio
from asyncio import BaseEventLoop
from uuid import uuid4

from aiohttp.client_exceptions import ClientOSError
from aioprometheus import CollectorRegistry, Service, pusher

from virtex.core.logging import LOGGER
from virtex.core.prom_registry import PROM_METRICS

__all__ = ['PrometheusBase', 'PrometheusClient', 'PrometheusGatewayClient',
           'PROM_CLIENT']


def check_port(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        in_use = sock.connect_ex(("127.0.0.1", port)) != 0
    return in_use


SERVER_ID = uuid4().hex[:8]


PROM_LABELS = {'server_instance': SERVER_ID}


class PrometheusBase:

    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 loop: BaseEventLoop):
        self._name = f'{name}-{SERVER_ID}'
        self._host = host
        self._port = port
        self.loop = loop
        self._registry = CollectorRegistry()
        for _, metric in PROM_METRICS.items():
            self._registry.register(metric)
        LOGGER.info('%s prometheus client registered successfully.',
                    self._name)

    @staticmethod
    def add(key, value):
        PROM_METRICS[key].add(labels=PROM_LABELS, value=value)

    @staticmethod
    def observe(key, value):
        PROM_METRICS[key].observe(labels=PROM_LABELS, value=value)


class PrometheusClient(PrometheusBase):

    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 loop: BaseEventLoop,
                 *args):
        super().__init__(name, host, port, loop)
        asyncio.ensure_future(self.start())

    async def start(self):
        """
        Runs a prometheus metrics server on ``port``. If ``port`` is already
        in use, we send a request to validate that its running a prometheus
        server and raise an error if not.
        """
        if check_port(self._port):
            try:
                service = Service(self._registry, loop=self.loop)
                await service.start(addr=self._host.lstrip('http://'), port=self._port)
                self._service = service
                LOGGER.info("Prometheus service launched on %s:%d",
                            self._host, self._port)
            except Exception as exc:
                LOGGER.error('Could not start server on %s:%d: %s',
                             self._host, self._port, exc)
        else:
            check = requests.get(f"{self._host}:{self._port}/metrics")
            if check.status_code != 200:
                LOGGER.error('Could not find prometheus service on %s:%d: %s',
                             self._host, self._port)
            else:
                LOGGER.info("Prometheus service found on %s:%d",
                            self._host, self._port)

    def __del__(self):
        if getattr(self, '_service', None):
            asyncio.ensure_future(self._service.stop())


class PrometheusGatewayClient(PrometheusBase):

    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 loop: BaseEventLoop,
                 interval: float):
        super().__init__(name, host, port, loop)
        self._interval = interval
        self._client = pusher.Pusher(
            job_name=self._name,
            addr=f'{self._host}:{self._port}')
        self._push_future = asyncio.ensure_future(
            self._client.add(self._registry))
        self.push_coro = asyncio.ensure_future(
            self._push_gateway_cronjob())

    def __del__(self):
        self._push_future.cancel()

    async def _push_gateway_cronjob(self):
        while True:
            try:
                await self._push_future
                self._push_future = asyncio.ensure_future(
                    self._client.add(self._registry))
            except ClientOSError as exc:
                LOGGER.warning('Exception caught in client %s: %s',
                               self._name, exc)
            await asyncio.sleep(self._interval)


class NullMetricsClient:
    def __init__(self, *args, **kwargs):
        pass
    def add(self, *args, **kwargs):
        pass
    def observe(self, *args, **kwargs):
        pass


PROM_CLIENT = dict(scrape=PrometheusClient,
                   push=PrometheusGatewayClient,
                   off=NullMetricsClient)
