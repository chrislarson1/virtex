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

from aioprometheus import CollectorRegistry, Service, pusher

from virtex.core.logging import LOGGER
from virtex.core.prom_registry import PROM_METRICS

__all__ = ['PrometheusBase', 'PrometheusClient', 'PrometheusGatewayClient',
           'PROM_CLIENT_REGISTER']


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        IP = sock.getsockname()[0]
    except Exception:
        IP = 'null'
    finally:
        sock.close()
    return IP


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
        if host == 'localhost':
            host = 'http://0.0.0.0'
        super().__init__(name, host, port, interval, loop)
        self._client = pusher.Pusher(
            job_name=self._name,
            addr=f'{self._host}:{self._port}')
        self._push_future = asyncio.ensure_future(
            self._client.add(self._registry))
        asyncio.ensure_future(self._push_gateway_cronjob())

    async def _push_gateway_cronjob(self):
        while True:
            await self._push_future
            self._push_future = asyncio.ensure_future(
                self._client.add(self._registry))
            await asyncio.sleep(self._interval)


PROM_CLIENT_REGISTER = dict(scrape=PrometheusClient,
                            push=PrometheusGatewayClient)
