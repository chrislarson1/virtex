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

import mxnet as mx

from virtex.serial.numpy import encode_numpy, decode_numpy

__all__ = ['encode_mx', 'decode_mx']


def encode_mx(obj : mx.nd.array) -> str:
    """
    Encode a mxnet nd-array as a bytestring.

    Parameters
    ----------
    obj : ``mx.nd.array``
        Object to be encoded

    Returns
    -------
    bytestr : ``str``
        bytestring representation of the passed object
    """
    return encode_numpy(obj.asnumpy())


def decode_mx(bytestr : str) -> mx.nd.array:
    """
    Decode a bytestring into a mxnet nd-array.

    Parameters
    ----------
    bytestr : ``str``
        bytestring to be decoded

    Returns
    -------
    object : ``mx.nd.array``
        Original python object
    """
    return mx.nd.array(decode_numpy(bytestr))
