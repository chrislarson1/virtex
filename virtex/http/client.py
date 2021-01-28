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
from typing import List

import orjson as json

from virtex.http.message import HttpMessage
from virtex.core.event_loop import ClientEventLoopContext

__all__ = ['HttpClient']


class HttpClient(ClientEventLoopContext):

    """
    Virtex HTTP client
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def __validate_message(message: HttpMessage):
        if not isinstance(message, HttpMessage):
            raise RuntimeError("message must be of type HttpMessage!")
        if not isinstance(message.data, list):
            raise RuntimeError(
                "message.data must be of form [ item1 ... itemN ].")

    async def post_async(self, url, message):
        """ POST message to url (async)

        Parameters
        ----------
        url: ``str``
            Full url to which POST is sent
        message: ``HttpMessage``
            Virtex message to be sent. The ``data`` member contains
            an array of requests of form ``{ "data": [ req1 ... reqN ] }``.

        Returns
        -------
        response: ``HttpMessage``
            Virtex message with member ``data`` containing responses.
            The ``data`` member contains an array of responses of form
            ``{ "data": [ resp1 ... respN ] }``.
        """
        self.__validate_message(message)
        async with self.session.post(url, data=message.json) as resp:
            return HttpMessage(**json.loads(await resp.text()))

    async def post_bundle_async(self, url, messages) -> List[HttpMessage]:
        """ POST message bundle to url (async)

        Parameters
        ----------
        url: ``str``
            Full url to which POST is sent
        messages: ``List[HttpMessage]``
            List of valid Virtex messages to be sent. The ``data``
            member of each message contains an array of requests
            of form ``{ "data": [ req1 ... reqN ] }``.

        Returns
        -------
        responses: ``List[HttpMessage]``
            Virtex message with member ``data`` containing responses.
            The ``data`` member contains an array of responses of form
            ``{ "data": [ resp1 ... respN ] }``.
        """
        tasks = []
        for msg in messages:
            tasks.append(asyncio.ensure_future(self.post_async(url, msg)))
        return await asyncio.gather(*tasks)

    def post_bundle(self, url, messages) -> List[HttpMessage]:
        """ POST message bundle to url

        Parameters
        ----------
        url: ``str``
            Full url to which POST is sent
        messages: ``List[HttpMessage]``
            List of valid Virtex messages to be sent. The ``data``
            member of each message contains an array of requests
            of form ``{ "data": [ req1 ... reqN ] }``.

        Returns
        -------
        responses: ``List[HttpMessage]``
            Virtex message with member ``data`` containing responses.
            The ``data`` member contains an array of responses of form
            ``{ "data": [ resp1 ... respN ] }``.
        """
        return self.loop.run_until_complete(asyncio.ensure_future(
            coro_or_future=self.post_bundle_async(url, messages),
            loop=self.loop))

    def post(self, url:str, message:HttpMessage) -> HttpMessage:
        """
        POST message to url

        Parameters
        ----------
        url: ``str``
            Full url to which POST is sent
        message: ``HttpMessage``
            Virtex message to be sent. The ``data`` member contains
            an array of requests of form ``{ "data": [ req1 ... reqN ] }``.

        Returns
        -------
        response: ``HttpMessage``
            Virtex message with member ``data`` containing responses. The
            ``data`` member contains an array of responses of form
            ``{ "data": [ resp1 ... respN ] }``.

        Notes
        -----
        1. To speed up the debugging process, use the ``HttpMessage.validate()``
            and ``HttpServer.validate()`` methods to ensure that your data
            serialization and callback functions work properly.
        """
        return self.loop.run_until_complete(asyncio.ensure_future(
            coro_or_future=self.post_async(url, message),
            loop=self.loop))
