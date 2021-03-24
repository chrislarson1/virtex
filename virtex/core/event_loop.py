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

import uvloop

__all__ = ['EventLoopContext']


CLOCK_INTERVAL = 1e-6


class EventLoopContext:

    """
    Context manager for virtex event-loops
    """

    def __init__(self):
        uvloop.install()
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self._loop = uvloop.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def __del__(self):
        self._loop.close()

    @staticmethod
    async def sleep():
        await asyncio.sleep(CLOCK_INTERVAL)

    @property
    def loop(self):
        """
        Returns
        -------
        loop : ``asyncio.BaseEventLoop``
            Event loop
        """
        return self._loop
