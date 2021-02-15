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

import time

import pytest
import orjson
import torch
import numpy as np
import pandas as pd
import tensorflow as tf

from virtex.serial import *
from virtex.serial.pandas import encode_pandas, decode_pandas
from virtex.serial.pillow import encode_pil, decode_pil, decode_pil_from_bytes
from virtex.serial.tf import encode_tf, decode_tf
from virtex.serial.torch import encode_torch, decode_torch


def test_numpy():
    x = np.random.random((1000, 1000))
    xb = encode_numpy(x)
    xd = decode_numpy(xb)
    assert isinstance(xb, str)
    assert np.all(x == xd)


def test_pandas():
    x = pd.DataFrame(data=[[0.1, 3, 'a'],
                           [7.2, 10, 'b']],
                     columns=['x1', 'x2', 'y'])
    xb = encode_pandas(x)
    xd = decode_pandas(xb)
    assert xd.equals(x)


def test_pil(test_image_pil):
    img_enc = encode_pil(test_image_pil)
    img_dec = decode_pil(img_enc)
    im1 = np.asarray(test_image_pil)
    im2 = np.asarray(img_dec)
    assert np.array_equal(im1, im2), \
        print(np.sum(im1 - im2, keepdims=False))


def test_pil_from_bytes(test_image_bytes, test_image_pil):
    img_enc = encode_bytes(test_image_bytes)
    img_dec = decode_pil_from_bytes(img_enc)
    im1 = np.asarray(test_image_pil)
    im2 = np.asarray(img_dec)
    assert np.array_equal(im1, im2), \
        print(np.sum(im1 - im2, keepdims=False))


@pytest.mark.serialization_speed
def test_check_numpy_serialization_speed():

    """
    orjson has built-in numpy serialization. It is faster than
    the base64<-pickle<-python-object scheme for encoding, but
    slower for decoding of larger numerical arrays; since we
    are primarily interested in decoding speed in Virtex, with
    the assumption being that heavy lifting for most virtex
    use cases will be decoding numerical input data on the
    server, virtex opts to use the base64 encoding of the
    pickled object. This test is a check to ensure that we
    become aware of any future changes made to these libraries
    that impact performance.
    """

    data = [np.random.random((1, 3, 32, 32)) for _ in range(25)]

    t0 = time.time()
    enc_orjson = orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY)
    t1 = time.time()
    t_orjson = t1 - t0

    t0 = time.time()
    enc_pickle = encode_numpy(data)
    t1 = time.time()
    t_pickle = t1 - t0

    ratio = t_pickle / t_orjson
    assert ratio < 2.25

    t0 = time.time()
    orjson.loads(enc_orjson)
    t1 = time.time()
    t_orjson = t1 - t0

    t0 = time.time()
    decode_numpy(enc_pickle)
    t1 = time.time()
    t_pickle = t1 - t0

    ratio = t_pickle / t_orjson
    assert ratio < 0.55


def test_torch():
    x_orig = torch.randn((1000, 10), dtype=torch.double)
    x_enc = encode_torch(x_orig)
    x_dec = decode_torch(x_enc)
    assert torch.eq(x_dec, x_orig).all()


def test_tensorflow():
    x_orig = tf.random.normal((1, 10), dtype=tf.double)
    x_enc = encode_tf(x_orig)
    x_dec = decode_tf(x_enc)
    assert tf.reduce_all(tf.math.equal(x_dec, x_orig))
