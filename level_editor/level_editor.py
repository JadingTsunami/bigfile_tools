# SoR4 Bigfile Level Editor
# Copyright (C) 2023 JadingTsunami
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; If not, see <http://www.gnu.org/licenses/>.

import zlib
import sys
import struct
import os

import uuid
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from enum import IntEnum

class WireType(IntEnum):
    VARINT = 0
    I64 = 1
    LEN = 2
    SGROUP = 3
    EGROUP = 4
    I32 = 5

# FIXME
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
+ '/bigfile_editor/')

from bigfile_editor import BigFileEditor

class DataSpooler:
    def __init__(self, data):
        self.load(data)

    def load(self, data):
        self.data = data
        self.ptr = 0
        self.len = len(data)

    def read(self, howmany):
        if howmany <= 0:
            return None
        self.ptr += howmany
        return self.data[self.ptr-howmany:self.ptr]

    def tell(self):
        return self.ptr

    def has_more(self):
        return self.ptr < self.len

    def _clip_bounds(self):
        self.ptr = max(0, min(self.ptr, self.len))

    def seek(self, where, whence):
        if whence == 0:
            self.ptr = where
        elif whence == 1:
            self.ptr = self.ptr + where
        elif whence == 2:
            self.ptr = self.len + where
        self._clip_bounds()

def read_varint(data, dataspool):
    return read_varint_raw(data, dataspool.tell(), dataspool)

def read_varint_raw(data, index, dataspool=None):
    assert index < len(data) and index >= 0
    varint = data[index] & 0x7F
    more = data[index] & 0x80
    index += 1
    while more:
        assert index < len(data)
        varint = ((data[index] & 0x7F) << 7) | (varint)
        more = data[index] & 0x80
        index += 1
    if dataspool:
        dataspool.seek(index,0)
    return varint

def read_tag(data, index, dataspool=None):
    assert index < len(data) and index >= 0
    v = read_varint(data, dataspool)
    field = v >> 3
    msgtype = v & 0x7
    return (field, msgtype)

def read_field(data, dataspool):
    (field, msgtype) = read_tag(data, dataspool.tell(), dataspool)
    if msgtype == WireType.VARINT:
        return field, msgtype, read_varint(data, dataspool)
    elif msgtype == WireType.I64:
        df = dataspool.read(8)
        df = struct.unpack('<d', df)[0]
        return field, msgtype, df
    elif msgtype == WireType.I32:
        df = dataspool.read(4)
        df = struct.unpack('<f', df)[0]
        return field, msgtype, df
    elif msgtype == WireType.SGROUP or msgtype == WireType.EGROUP:
        # fail on this for now
        raise ValueError("Did not expect SGROUP/EGROUP encoding but found at " + str(dataspool.tell()))
    elif msgtype == WireType.LEN:
        length = read_varint(data, dataspool)
        content = dataspool.read(length)
        if content.isascii():
            content = content.decode('utf-8')
        return field, msgtype, content
    else:
        raise ValueError("Unknown message type encoding " + str(msgtype) + " found at " + str(dataspool.tell()))

if __name__ == "__main__":
    bfe = BigFileEditor()
    bfe.read_uncompressed_bigfile('bigdata/bigfile.decomp')

    level_data = [l for l in bfe.tables if l['s1'].decode('utf-16') == 'LevelData']

    for level in level_data:
        l = level['data']
        spool = DataSpooler(l)
        while spool.has_more():
            print(read_field(l, spool))
        break
