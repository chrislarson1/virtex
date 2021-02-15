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
import asyncio
from asyncio import BaseEventLoop
from uuid import uuid4

from aiohttp.client_exceptions import ClientOSError
from aioprometheus import CollectorRegistry, Service, pusher

from virtex.core.logging import LOGGER
from virtex.core.prom_registry import PROM_METRICS

__all__ = ['PrometheusBase', 'PrometheusClient', 'PrometheusGatewayClient',
           'PROM_CLIENT']


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        addr = sock.getsockname()[0]
    except Exception as exc:
        LOGGER.warning('ip address not available: %s', exc)
        addr = 'null'
    finally:
        sock.close()
    return addr


SERVER_IP = get_ip()

SERVER_ID = uuid4().hex[:8]

PROM_LABELS = {'server_ip': SERVER_IP, 'instance': SERVER_ID}

MAX_PORT_INC = 10


class PrometheusBase:

    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 interval: float,
                 loop: BaseEventLoop):
        self._name = f'{name}-{SERVER_ID}'
        self._host = host
        self._port = port
        self._interval = interval
        self.loop = loop
        self._registry = CollectorRegistry()
        for _, metric in PROM_METRICS.items():
            self._registry.register(metric)
        LOGGER.info('%s prometheus client registered successfully.',
                    self._name)

    @staticmethod
    def observe(key, value):
        PROM_METRICS[key].observe(labels=PROM_LABELS, value=value)


class PrometheusClient(PrometheusBase):

    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 interval: float,
                 loop: BaseEventLoop):
        if host in ('http://127.0.0.1', 'http://0.0.0.0'):
            host = 'localhost'
        super().__init__(name, host, port, interval, loop)
        asyncio.ensure_future(self.start(port))

    async def start(self, port):
        """
        Runs a prometheus metrics server on ``port``. If ``port`` is already
        in use, this function will try to increment the port number until
        it finds an available one, up to ``MAX_PROC_WHEN_SCRAPE``.
        """
        for _ in range(MAX_PORT_INC):
            try:
                service = Service(self._registry, loop=self.loop)
                await service.start(addr=self._host, port=self._port)
                self._service = service
                break
            except OSError:
                LOGGER.warning(
                    'Failed to launch prometheus server on port %d.',
                    self._port
                )
                self._port += 1
        if not getattr(self, '_service', None):
            raise RuntimeError(
                "Failed to launch prometheus server on ports %d-%d, Exiting.",
                port, self._port
            )
        else:
            LOGGER.info("Prometheus service running on %s:%d",
                        self._host, self._port)

    def __del__(self):
        if getattr(self, '_service', None):
            asyncio.ensure_future(self._service.stop())


class PrometheusGatewayClient(PrometheusBase):

    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 interval: float,
                 loop: BaseEventLoop):
        super().__init__(name, host, port, interval, loop)
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


PROM_CLIENT = dict(scrape=PrometheusClient,
                   push=PrometheusGatewayClient)
