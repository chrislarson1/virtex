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

from pandas.core.generic import NDFrame

from virtex.serial.pickle import encode_pickle, decode_pickle

__all__ = ['encode_pandas', 'decode_pandas']


def encode_pandas(obj : NDFrame) -> str:
    """
    Encode a pandas datastructure as a bytestring.

    Parameters
    ----------
    obj : ``pd.core.generic.NDFrame``
        Dataframe to be encoded

    Returns
    -------
    bytestr : ``str``
        bytestring representation of the passed object
    """
    return encode_pickle(obj)


def decode_pandas(bytestr:str) -> NDFrame:
    """
    Decode a bytestring into a pandas data object.

    Parameters
    ----------
    bytestr : ``str``
        bytestring to be decoded

    Returns
    -------
    object : ``pd.core.generic.NDFrame``
        Original pandas object
    """
    return decode_pickle(bytestr)
