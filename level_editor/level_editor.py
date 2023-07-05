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

from enum import Enum

class WireType(Enum):
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

    def seek(self, where, whence):
        if whence == 0:
            self.ptr = where
        elif whence == 1:
            self.ptr = self.ptr + where
        elif whence == 2:
            self.ptr = self.len + where

def read_varint(data, index):
    assert index < len(data) and index >= 0
    varint = data[index] & 0x7F
    more = data[index] & 0x80
    while more:
        index += 1
        assert index < len(data)
        varint = ((data[index] & 0x7F) << 7) | (varint)
        more = data[index] & 0x80
    return varint

def read_tag(data, index):
    assert index < len(data) and index >= 0
    v = read_varint(data, index)
    field = v >> 3
    msgtype = v & 0x7
    return (field, msgtype)

def read_field(data, index, parent=None):
    (field, msgtype) = read_tag(data, index)
    if msgtype == WireType.VARINT:
        pass

def find_strings(table):
    return None

if __name__ == "__main__":
    bfe = BigFileEditor()
    bfe.read_uncompressed_bigfile('bigdata/bigfile.decomp')

    level_data = [l for l in bfe.tables if l['s1'].decode('utf-16') == 'LevelData']

    print("-> " + str(read_tag(level_data[0]['data'], 0)))
