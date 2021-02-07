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
import sys
import time
import asyncio
from aiohttp import ClientSession


async def post(url, session, message):
    async with session.post(url, json=message) as resp:
        return await resp.text()


async def post_bundle(url, messages):
    tasks = []
    async with ClientSession() as session:
        for msg in messages:
            tasks.append(asyncio.ensure_future(post(url, session, msg)))
        return await asyncio.gather(*tasks)


def run_benchmark():

    # Get text data
    path = os.path.dirname(os.path.abspath(__file__))
    data = [line.strip().lower() for line in open(
        os.path.join(path, "../../tests/data/tweets.txt"), "r")]
    assert N == len(data)
    seqlen_mu = sum([len(x.split(" ")) for x in data]) / N
    messages = []
    for c, i in enumerate(range(0, N - 1, M)):
        messages.append({
            "id": c,
            "texts": data[i:i + M],
            "is_tokenized": False
        })

    # Instantiate client
    url = 'http://127.0.0.1:8081/encode'

    # Timeit
    loop = asyncio.get_event_loop()
    t = time.time()
    responses = loop.run_until_complete(asyncio.ensure_future(post_bundle(url, messages)))
    t = time.time() - t

    # Results
    print("RECEIVED DTYPE: %s" % type(responses[0]))
    print("AVG SEQ LENGTH: %d" % seqlen_mu)
    print("   AVG LATENCY: %d ms" % int(1000 * t / n))
    print("    THROUGHPUT: %d TPS" % int(N / t))


if __name__ == '__main__':
    N = 9000                # number of data elements
    M = int(sys.argv[1])    # request batch size
    n = N // M              # number of requests
    run_benchmark()
