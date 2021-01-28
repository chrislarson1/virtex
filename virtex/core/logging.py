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
import json
import logging

__all__ = ['LOGGER']


LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")


LOG_FORMAT = {"time": "%(asctime)s",
              "log_level": LOG_LEVEL,
              "log": "[%(name)s] %(message)s",
              "stream": "stderr"}


def logger(name=__name__):
    formatter = logging.Formatter(json.dumps(LOG_FORMAT),
                                  datefmt='%Y-%m-%d %H:%M:%S %z')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = 0
    return logger


LOGGER = logger('VIRTEX')
