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

import torch

from virtex.serial.numpy import encode_numpy, decode_numpy

__all__ = ['encode_torch', 'decode_torch']


def encode_torch(obj : torch.tensor) -> str:
    """
    Encode a torch tensor as a bytestring.

    Parameters
    ----------
    obj : ``torch.tensor``
        Object to be encoded

    Returns
    -------
    bytestr : ``str``
        bytestring representation of the passed object
    """
    return encode_numpy(obj.cpu().detach().numpy())


def decode_torch(bytestr:str) -> torch.tensor:
    """
    Decode a bytestring into a torch tensor.

    Parameters
    ----------
    bytestr : ``str``
        bytestring to be decoded

    Returns
    -------
    object : ``torch.tensor``
        Original python object
    """
    return torch.tensor(decode_numpy(bytestr))
