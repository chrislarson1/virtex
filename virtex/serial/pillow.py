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
import io
import pickle

import numpy as np
from PIL import Image

__all__ = ['encode_pil', 'decode_pil', 'decode_pil_from_bytes']


def encode_pil(image):
    """
    Encodes a Pillow image to a bytestring.

    Parameters
    ----------
    image : ``PIL.Image.image``
        Image to be encoded

    Returns
    -------
    bytestr : ``str``
        Bytestring representation of the image
    """
    return base64.encodebytes(pickle.dumps(np.asarray(image))).decode("utf-8")


def decode_pil(bytestr):
    """
    Decodes a bytestring representation of an image back to an image.

    Parameters
    ----------
    bytestr : ``str``
        Bytestring to be decoded

    Returns
    -------
    image : ``PIL.Image``
        Original image
    """
    return Image.fromarray(pickle.loads(base64.b64decode(bytestr.encode())))


def decode_pil_from_bytes(bytestr):
    """
    Decodes a bytestring representation of an image that was loaded from disk
    directly into a bytearray to a PIL image.

    Parameters
    ----------
    bytestr : ``str``
        Bytestring to be decoded

    Returns
    -------
    image : ``PIL.Image``
        Original image
    """
    return Image.open(io.BytesIO(base64.b64decode(bytestr.encode())))
