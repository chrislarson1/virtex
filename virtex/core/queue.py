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

from queue import Queue
from uuid import uuid4
from typing import Any, List

from virtex.core.task import Task


__all__ = ['WAIT_KEY', 'RequestQueue', 'ResponseQueue']


WAIT_KEY = uuid4()
"""
Unique message to tell response poller to wait
"""


class RequestQueue(Queue):

    """
    Task queue for processing request data on the Virtex server.
    """

    def __init__(self, max_pop: int):
        """
        Parameters
        ----------
        max_pop: ``int``
            Maximum number of items to remove from the task queue
            when processing batches.
        """
        super().__init__()
        self.max_pop = max_pop

    def pull(self) -> List[Task]:
        """
        Pull a `batch` of tasks off of the queue

        Returns
        -------
        ``List[Task]``
        """
        return [self.get() for _ in
                range(min(self.qsize(), self.max_pop))]


class ResponseQueue(dict):

    """
    Response queue for processed tasks to be collected by the
    servers response poller.
    """


    def __init__(self):
        super().__init__()

    def put(self, key: uuid4, response: Any):
        """
        Place a processed task onto the queue using it's unique key.

        Parameters
        ----------
        key: ``uuid4``
        response: ``Any``
        """
        self[key] = response

    def poll(self, key: uuid4) -> Any:
        """
        Poll the response queue by key.

        Parameters
        ----------
        key : ``uuid4``

        Returns
        -------
        ``Union[Any, NoneType]``
        """
        return self.pop(key, WAIT_KEY)

    def qsize(self):
        """
        Get the current size of the queue
        """
        return len(self)
