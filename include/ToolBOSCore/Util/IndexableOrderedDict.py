#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright (c) Honda Research Institute Europe GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#


from collections import OrderedDict

from ToolBOSCore.Util import Any


class IndexableOrderedDict(OrderedDict):
    """
    Custom dictionary that maintains order of insertion and allows for querying
    items both by their key and by their position index.
    """

    def __getitem__(self, key, **args):
        if key in self:
            return super(IndexableOrderedDict, self).__getitem__( key )
        else:
            try:
                return self.values()[key]
            except (TypeError, IndexError):
                # To fully emulate dictionary behaviour in case of missing
                # element, we raise a KeyError if the list access raises
                # a TypeError or IndexError.
                raise KeyError(key)


    def index(self, key):
        return list(self.keys()).index(key)


def merge(orig, toMerge, position):
    """
    Commodity function that merges two IndexableOrderedDicts at `position`.

    `position` is the position where toMerge will be inserted in orig. Original
    ordering for both dicts is preserved.

    :param orig: Original dict
    :param toMerge: Dict whose contents are to be merged in 'orig'
    :param position: Position where the merge should be performed
    """

    Any.requireIsDict( orig )
    Any.requireIsDict( toMerge )

    keys   = list(orig.keys())[:position] + list(toMerge.keys()) + list(orig.keys())[position:]
    values = list(orig.values())[:position] + list(toMerge.values()) + list(orig.values())[position:]

    retVal = IndexableOrderedDict()

    for i, key in enumerate(keys):
        retVal[key] = values[i]

    return retVal


# EOF
