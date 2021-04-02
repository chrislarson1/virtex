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

from io import open
from setuptools import setup, find_packages


setup(
    name="virtex",
    version="0.1.5-rc.1",
    author="Chris Larson",
    author_email="chris7larson@gmail.com",
    description="Serving for computational workloads",
    long_description=open("README.md", "r", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    keywords='machine deep learning ai serving asyncronous microservice',
    license='Apache Version 2.0',
    python_requires='>=3.6.6',
    url="https://github.com/virtexlabs/virtex.git",
    packages=find_packages(exclude=[
        "*.data",
        "*.data.*",
        "data.*",
        "data",
        ".local/",
        "tests/"
    ]),
    install_requires=[
        'aioprometheus[aiohttp]==20.0.1',
        'aiosonic==0.9.7',
        'gunicorn==20.0.4',
        'httptools==0.1.1',
        'numpy>=1.18.1',
        'orjson>=3.0.2',
        'uvloop==0.14.0',
        'uvicorn==0.13.3'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)
