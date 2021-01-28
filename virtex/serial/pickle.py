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
import pickle
from typing import Any

__all__ = ['encode_pickle', 'decode_pickle']


def encode_pickle(obj:Any) -> str:
    """
    Encode a python object as a bytestring.

    Parameters
    ----------
    obj : ``Any``
        Object to be encoded

    Returns
    -------
    bytestr : ``str``
        bytestring representation of the passed object
    """
    return base64.encodebytes(pickle.dumps(obj)).decode("utf-8")


def decode_pickle(bytestr:str) -> Any:
    """
    Decode a bytestring representation of a generic python object back
    to the original object.

    Parameters
    ----------
    bytestr : ``str``
        bytestring to be decoded

    Returns
    -------
    object : ``Any``
        Original python object
    """
    return pickle.loads(base64.b64decode(bytestr.encode()))
