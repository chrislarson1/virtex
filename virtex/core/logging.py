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


LOG_LEVEL = os.getenv("LOG_LEVEL", "CRITICAL")


# Force tensorflow to respect loglevel
if LOG_LEVEL.lower() == 'critical':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
elif LOG_LEVEL.lower() == 'error':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
elif LOG_LEVEL.lower() == 'warning':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
else:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'


FORMAT = {
    "time": "%(asctime)s",
    "log_level": LOG_LEVEL,
    "log": "[%(name)s] %(message)s",
    "stream": "stderr"
}


def get_formatter():
    return logging.Formatter(json.dumps(FORMAT),
                             datefmt='%Y-%m-%d %H:%M:%S %z')


def get_logger(logger_name: str):
    handler = logging.StreamHandler()
    handler.setFormatter(get_formatter())
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False
    return logger


LOGGER = get_logger(logger_name='virtex')
