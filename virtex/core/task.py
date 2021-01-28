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

from uuid import uuid4
from typing import Any


__all__ = ['Task']


class Task(dict):

    """Internal class for storing queued objects"""

    def __init__(self, item: Any):
        """
        Parameters
        ----------
        item : ``Any``
            Item to be placed on the queue. Theoretically
            can be any type, in the virtex context `items`
            correspond to the elements contained in
            `Message.data`, and consist of decoded json
            objects.
        """
        super().__init__()
        self.key = uuid4()
        self.item = item

    @property
    def key(self):
        """
        Returns
        -------
        key : ``str``
        """
        return self['key']

    @property
    def item(self):
        """
        Returns
        -------
        item : ``Any``
        """
        return self['item']

    @key.setter
    def key(self, key):
        self['key'] = key

    @item.setter
    def item(self, item):
        self['item'] = item
