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

import os

import pytest
from PIL import Image

from virtex import HttpClient


rootdir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(autouse=True)
def test_image_bytes():
    return open(os.path.join(rootdir, "data/test_image.JPEG"), "rb").read()


@pytest.fixture(autouse=True)
def test_image_PIL():
    return Image.open(os.path.join(rootdir, "data/test_image.JPEG"))


@pytest.fixture(autouse=True)
def tweets():
    return [tweet.strip() for tweet in open(
        os.path.join(rootdir, "data/tweets.txt"), "r").readlines()]


@pytest.fixture(autouse=True)
def client():
    HttpClient()
