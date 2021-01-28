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

import asyncio
from functools import wraps
from typing import Callable, Any

from virtex.core.timing import now, async_now


def profile(profile_fn,
            *fn_args,
            tstamp_fn: Callable[[float, float], Any],
            loop: asyncio.BaseEventLoop = None):

    """
    Parameters
    ----------
    profile_fn: ``Callable[Any, Any]``
        Wrapped function
    fn_args: ``Tuple[Any]``
        Wrapped function arguments
    tstamp_fn: ``Callable[[float, float], Any]``
        A function that accepts a start_time,end_time
        argument pair and returns the profile value
    loop: ``Optional[asyncio.BaseEventLoop]``
        Event loop to be used for async functions
    """

    def _execute(func):

        @wraps(func)
        async def timeit_async(*args, **kwargs):
            start_time = async_now(loop)
            result = await func(*args, **kwargs)
            end_time = async_now(loop)
            profile_fn(*fn_args, tstamp_fn(start_time, end_time))
            return result

        @wraps(func)
        def timeit(*args, **kwargs):
            start_time = now()
            result = func(*args, **kwargs)
            end_time = now()
            profile_fn(*fn_args, tstamp_fn(start_time, end_time))
            return result

        if asyncio.iscoroutinefunction(func):
            assert loop is not None
            return timeit_async

        return timeit

    return _execute
