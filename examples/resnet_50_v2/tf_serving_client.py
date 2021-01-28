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

import sys
import time
import json
import base64
import asyncio
import requests

from aiohttp import ClientSession

"""
This code is based on this:
    https://raw.githubusercontent.com/tensorflow/serving/master/tensorflow_serving/example/resnet_client.py
"""

SERVER_URL = 'http://localhost:8501/v1/models/resnet:predict'
IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'


async def post(url, session, message):
    async with session.post(url, data=message) as resp:
        return await resp.text()


async def post_bundle(url, messages):
    tasks = []
    async with ClientSession() as session:
        for msg in messages:
            tasks.append(asyncio.ensure_future(post(url, session, msg)))
        return await asyncio.gather(*tasks)


if __name__ == '__main__':
    N = 10000
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    # path = os.path.dirname(os.path.abspath(__file__))
    # images = []
    # for fn in glob.glob(os.path.join(path, '../../data/tiny-imagenet-200/test/images/*.JPEG'))[:N]:
    #   images.append(encode_bytes(open(fn, 'rb').read()))

    img = requests.get(IMAGE_URL, stream=True)
    img.raise_for_status()
    jpeg_bytes = base64.b64encode(img.content).decode('utf-8')
    images = [json.dumps({"instances": [
        {"b64": jpeg_bytes} for _ in range(M)]}) for _ in range(N // M)]

    # Run examples
    loop = asyncio.get_event_loop()
    t = time.time()
    loop.run_until_complete(asyncio.ensure_future(post_bundle(SERVER_URL, images)))
    t = time.time() - t
    loop.close()
    print("AVG LATENCY: %d ms" % int(1000 * t / (N // M)))
    print(" THROUGHPUT: %d TPS" % int(N / t))
