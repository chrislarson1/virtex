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

import tensorflow as tf

from virtex.serial.numpy import encode_numpy, decode_numpy

__all__ = ['encode_tf', 'decode_tf']


def encode_tf(obj : tf.Tensor) -> str:
    """
    Encode a tf.Tensor as a bytestring.

    Parameters
    ----------
    obj : ``tf.Tensor``
        Object to be encoded

    Returns
    -------
    bytestr : ``str``
        bytestring representation of the passed object
    """
    return encode_numpy(obj.numpy())


def decode_tf(bytestr : str) -> tf.Tensor:
    """
    Decode a bytestring into a tf.Tensor.

    Parameters
    ----------
    bytestr : ``str``
        bytestring to be decoded

    Returns
    -------
    object : ``tf.Tensor``
        Original python object
    """
    return tf.convert_to_tensor(decode_numpy(bytestr))
