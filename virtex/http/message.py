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

from typing import Any, List, Callable

import orjson as json

from virtex.core.logging import LOGGER

__all__ = ['HttpMessage']


class HttpMessage(dict):

    """JSON object wrapper for virtex messaging"""

    def __init__(self, data=None, error=None, **kwargs):
        """
        Parameters
        ----------
        data : ``list``
            Python ``list`` of data objects to be transported
        error : ``str``
            Error message
        **kwargs : ``kwargs``
            Unpacked dictionary with json-serializable values
        """
        super().__init__(**kwargs)
        self.data = data or []
        self.error = error

    def __call__(self):
        return self

    def encode(self, encode_fn: Callable, **kwargs):
        """
        Encodes each member of ``HttpMessage``.data`` emplace according to a
        user specified callback function.

        Parameters
        ----------
        encode_fn : ``Callable``
            Callback with signature ``encode_fn(item)`` where ``item`` is of
            the same type as the native ``HttpMessage.data`` elements.
        kwargs : key-word arguments for encode_fn function

        Returns
        -------
        None
        """
        self['data'] = [encode_fn(item, **kwargs) for item in self['data']]

    def decode(self, decode_fn: Callable, **kwargs):
        """
        Decodes each member of ``HttpMessage.data`` emplace according to a
        user specified callback function.

        Parameters
        ----------
        decode_fn : ``Callable``
            Callback with signature ``decode_fn(item)`` where ``item`` is a
            bytestring representation of the native data type of the elements
            in ``HttpMessage.data``.
        kwargs : key-word arguments for encode_fn

        Returns
        -------
        None
        """
        self['data'] = [decode_fn(item, **kwargs) for item in self['data']]

    def validate(self):
        """
        Validates that the message can be converted to a json string.

        Returns
        -------
        status : ``bool``
        """
        try:
            self.json
            return True
        except Exception as e:
            LOGGER.info(
                "Message validation failed with following exception: %s", e)
            return False

    @property
    def json(self):
        """
        Returns
        -------
        json_string : ``str``
            Jsonified ``HttpMessage``

        Notes
        -----
        1. This method uses ``orjson.dumps()`` with its default json
            encoder. Make sure to run ``HttpMessage.encode()`` passing
            in an appropriate callback to ensure that all data
            members are json serializable (as necessary) prior
            to calling this method.
        """
        return json.dumps(self)

    @property
    def data(self) -> List[Any]:
        """
        Returns
        -------
        data : ``list``
            Array data elements. Each element in ``data`` represents an
            individual request to be processed in the server callbacks.
        """
        return self['data']

    @property
    def error(self):
        """
        Returns
        -------
        error : ``str``
            Error message. Primarily used in server response messages.
        """
        return self['error']

    @data.setter
    def data(self, data: List[Any]):
        self['data'] = data

    @error.setter
    def error(self, error: str):
        self['error'] = error
