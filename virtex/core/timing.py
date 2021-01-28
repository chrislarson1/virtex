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

from time import time
from typing import Callable
from asyncio import BaseEventLoop

__all__ = ['now', 'async_now']


#: Get time (unit: seconds)
now: Callable[[], float] = lambda: float(time())


#: Get time from event loop (unit: fractional seconds)
async_now: Callable[[BaseEventLoop], float] = lambda loop: float(loop.time())
