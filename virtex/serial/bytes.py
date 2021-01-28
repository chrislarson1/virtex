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

import base64

__all__ = ['encode_bytes', 'decode_bytes']


def encode_bytes(_bytes : bytes) -> str:
    """
    Encode a bytes to a bytestring

    Parameters
    ----------
    _bytes : ``bytes``

    Returns
    -------
    bytestr : ``str``
        bytestring representation of ``array``
    """
    return base64.encodebytes(_bytes).decode("utf-8")


def decode_bytes(bytestr : str) -> bytes:
    """
    Decode a bytestring to bytes.

    Parameters
    ----------
    bytestr : ``str``
        bytestring to be decoded

    Returns
    -------
    bytestr : ``str``
    """
    return base64.b64decode(bytestr.encode())
