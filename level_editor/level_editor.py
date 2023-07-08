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
import string

import uuid
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from enum import IntEnum

class WireType(IntEnum):
    STRING = -2
    MESSAGE = -1
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
from object_types import *

class DataSpooler:
    def __init__(self, data, end=None):
        self.load(data, end)

    def load(self, data, end):
        self.data = data
        self.ptr = 0
        if end:
            self.len = end
        else:
            self.len = len(data)

    def read(self, howmany, advance=True):
        if howmany <= 0:
            raise ValueError("Read less than or equal to 0")
        if self.ptr + howmany > self.len:
            raise EOFError("Tried to read past end of file")
        if advance:
            self.ptr += howmany
        return self.data[self.ptr-howmany:self.ptr]

    def splice(self, where, howmany, what):
        if where < 0:
            raise ValueError("Splice location less than 0")
        elif howmany <= 0:
            raise ValueError("Splice width less than or equal to 0")

        self.data = self.data[:where] + what + self.data[where+howmany:]

    def peek(self, howmany):
        return self.read(howmany, advance=False)

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
    v = read_varint_raw(data, index, dataspool)
    field = v >> 3
    msgtype = v & 0x7
    return (field, msgtype)

def encode_varint(v):
    if not v:
        return bytearray([0])

    b = bytearray()
    while v:
        cur_byte = (v & 0x7F)
        v >>= 7
        if v:
            cur_byte |= 0x80
        b.append(cur_byte)
    return b

def encode_tag(field_num, wire_type):
    assert wire_type >= WireType.VARINT and wire_type <= WireType.I32
    assert field_num > 0
    tag = (wire_type & 0x7) | (field_num << 3)
    return encode_varint(tag)

def likely_string(value, threshold=0.6):
    if not value:
        return False
    if not value.isascii():
        return False

    value = str(value, 'utf-8')
    length = len(value)
    alpha = 0
    num = 0
    for c in value:
        if c.isalpha():
            alpha += 1
        elif c.isnumeric():
            num += 1
        elif c not in string.punctuation:
            return False

    if float(alpha + num)/float(length) >= threshold and alpha > 0:
        return True

    return False

def guess_if_message(data, dataspool, length):
    rewind = dataspool.tell()
    try:
        (f, m) = read_tag(data, dataspool.tell(), dataspool)
    except:
        return False
    # arbitrary limit on field numbers based on experience, but should revise this
    # based on what's actually present in the decoded file (todo)
    if f > 1024:
        return False

    if m == WireType.LEN:
        size = read_varint(data, dataspool)
        bytes_read = dataspool.tell() - rewind
        if size <= length - bytes_read:
            # will guess this is a message
            dataspool.seek(rewind, 0)
            return True
    dataspool.seek(rewind, 0)
    if m >= WireType.VARINT and m <= WireType.I32 and m != WireType.LEN:
        return True
    return False

def read_field(data, dataspool):
    (field, msgtype) = read_tag(data, dataspool.tell(), dataspool)
    if msgtype == WireType.VARINT:
        return field, msgtype, read_varint(data, dataspool)
    elif msgtype == WireType.I64:
        df = dataspool.read(8)
        if df:
            df = struct.unpack('<d', df)[0]
        return field, msgtype, df
    elif msgtype == WireType.I32:
        df = dataspool.read(4)
        if df:
            df = struct.unpack('<f', df)[0]
        return field, msgtype, df
    elif msgtype == WireType.SGROUP or msgtype == WireType.EGROUP:
        # fail on this for now
        raise ValueError("Did not expect SGROUP/EGROUP encoding but found at " + str(dataspool.tell()))
    elif msgtype == WireType.LEN:
        length = read_varint(data, dataspool)
        guess_message = guess_if_message(data, dataspool, length)
        content = dataspool.read(length)
        if likely_string(content):
            content = content.decode('utf-8')
            msgtype = WireType.STRING
        elif guess_message:
            msgtype = WireType.MESSAGE
        return field, msgtype, content
    else:
        raise ValueError("Unknown message type encoding " + str(msgtype) + " found at " + str(dataspool.tell()))

class Node:
    def __init__(self, parent, tag_start, data_start, data_len, field_num, content=None):
        self.parent = parent
        self.tag_start = tag_start
        self.data_start = data_start
        self.data_len = data_len
        self.field_num = field_num
        self.content = content

def find_string_hierarchy(data, spool, parent=None, string_list=None, known_parents=None):
    # for each string, find:
    #  parent
    #  tag start
    #  string start
    #  string length (end)
    if string_list is None:
        string_list = []

    if known_parents is None:
        known_parents = {}

    while spool.has_more():
        # is the next field a string?
        try:
            tag_start = spool.tell()
            (field, msgtype) = read_tag(data, spool.tell(), spool)
            if msgtype == WireType.LEN:
                data_len = read_varint(data, spool)
            else:
                data_len = 0
            data_start = spool.tell()
            spool.seek(tag_start, 0)
            (f, m, c) = read_field(data, spool)
            data_end = spool.tell()
        except Exception as e:
            break
        if m == WireType.STRING:
            new_node = Node(parent, tag_start, data_start, data_len, f, c)
            string_list.append(new_node)
        elif m == WireType.MESSAGE and c:
            spool_new = DataSpooler(data, end=data_end)
            spool_new.seek(data_start, 0)
            if tag_start in known_parents:
                new_node = known_parents[tag_start]
            else:
                new_node = Node(parent, tag_start, data_start, data_len, f, None)
                known_parents[tag_start] = new_node
            find_string_hierarchy(data, spool_new, new_node, string_list, known_parents)

    return string_list

def replace_node(table, node, replacement_string):
    # node MUST be a leaf
    assert table
    assert node
    assert node.content

    spool = DataSpooler(table['data'])
    repl_bytes = bytearray(replacement_string,"utf-8")
    size_diff = len(repl_bytes) - len(node.content)
    new_tag = encode_tag(node.field_num, WireType.LEN)
    new_tag += encode_varint(len(repl_bytes))
    spool.splice(node.tag_start, (node.data_start-node.tag_start) + node.data_len, new_tag + repl_bytes)
    size_diff += len(new_tag) - (node.data_start-node.tag_start)
    # now write size delta all the way up
    p = node.parent
    while p:
        p_tag = encode_tag(p.field_num, WireType.LEN)
        p_tag += encode_varint(p.data_len + size_diff)
        spool.splice(p.tag_start, p.data_start-p.tag_start, p_tag)
        size_diff += len(p_tag) - (p.data_start-p.tag_start)
        p = p.parent

    table['data'] = spool.data
    table['size'] = len(spool.data)
    spool.seek(0,0)

    # certainly we could be more efficient than rebuilding
    # the entire node network. BUT, if a node has duplicates
    # in the tree, we really don't have a good way of finding
    # them unless we searched the structure for the same tag
    # start point and replaced on that basis.
    return find_string_hierarchy(table['data'], spool)


class SelectReplacementDialog:
    def __init__(self, root, prompt, choices):
        self.top = tk.Toplevel(root)
        self.label = tk.Label(self.top, text=prompt)
        self.ok_button = tk.Button(self.top, text="OK", command=self.on_ok)

        self.listframe = ttk.Frame(self.top)

        self.list = tk.Listbox(self.listframe)
        self.list.bind('<<ListboxSelect>>', self.select_replacement)

        self.bary = ttk.Scrollbar(self.listframe)
        self.barx = ttk.Scrollbar(self.listframe, orient=tk.HORIZONTAL)

        self.list.config(yscrollcommand = self.bary.set)
        self.list.config(xscrollcommand = self.barx.set)

        self.bary.config(command=self.list.yview)
        self.barx.config(command=self.list.xview)

        self.bary.pack(side=tk.RIGHT, fill=tk.Y)
        self.barx.pack(side=tk.BOTTOM, fill=tk.X)
        self.list.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(1, weight=1)
        
        self.label.grid(row=0, column=0, sticky=tk.N)
        self.listframe.grid(row=1, column=0, sticky=tk.NSEW)
        self.ok_button.grid(row=2, column=0, stick=tk.S)

        for choice in choices:
            self.list.insert(tk.END, choice)

        self.list.bind("<Return>", self.on_ok)
        self.list.bind('<Double-1>', self.on_ok)
        self.list.bind("<Escape>", self.abandon)

        self.top.geometry('700x350')
        self.replacement = None

    def abandon(self, event=None):
        self.replacement = None
        self.top.destroy()
        
    def on_ok(self, event=None):
        self.top.destroy()

    def select_replacement(self, e):
        sel = e.widget.curselection()
        if sel:
            self.replacement = self.list.get(sel[0])

    def show(self):
        self.top.wm_deiconify()
        self.list.focus_force()
        self.top.wait_window()
        return self.replacement

class LevelEditorGUI:
    def __init__(self, bfe):
        self.root = tk.Tk()
        self.bfe = bfe
        self.root.title("bigfile level editor")

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.levelframe = ttk.Frame(self.root)

        self.levellist = tk.Listbox(self.levelframe)
        self.levelbary = ttk.Scrollbar(self.levelframe)
        self.levelbarx = ttk.Scrollbar(self.levelframe, orient=tk.HORIZONTAL)

        self.levellist.config(yscrollcommand = self.levelbary.set)
        self.levellist.config(xscrollcommand = self.levelbarx.set)

        self.levelbary.config(command=self.levellist.yview)
        self.levelbarx.config(command=self.levellist.xview)

        self.levellist.bind('<<ListboxSelect>>', self.select_level)

        self.levelbary.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.levelbarx.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.levellist.pack(side=tk.LEFT, fill=tk.BOTH)
        self.levelframe.grid(row=0, column=0, sticky=tk.NS)

        self.QuitButton = ttk.Button(self.root, text="Quit", command=self.root.destroy)

        self.FileButtonFrame = ttk.Frame(self.root)
        self.ImportCompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Import COMPRESSED Bigfile", command=self.import_compressed_bigfile)
        self.ImportUncompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Import UNCOMPRESSED Bigfile", command=self.import_uncompressed_bigfile)
        self.ExportCompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Export COMPRESSED Bigfile", command=self.export_compressed_bigfile)
        self.ExportUncompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Export UNCOMPRESSED Bigfile", command=self.export_uncompressed_bigfile)

        self.ImportCompressedBigfileButton.grid(row=0, column=0)
        self.ImportUncompressedBigfileButton.grid(row=0, column=1) 
        self.ExportUncompressedBigfileButton.grid(row=0, column=2)
        self.ExportCompressedBigfileButton.grid(row=0, column=3) 
        
        self.FileButtonFrame.grid(row=1, column=0, columnspan=2)
        self.QuitButton.grid(row=2, column=1, sticky=tk.E)

        self.TreeFrame = ttk.Frame(self.root, padding="3")
        self.TreeFrame.grid(row=0, column=1, sticky=tk.NSEW)

        self.tree = ttk.Treeview(self.TreeFrame)
        self.tree.bind('<Double-1>', self.edit_item)
        self.tree.bind('<Return>', self.edit_item)

        self.tvsb = ttk.Scrollbar(self.TreeFrame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tvsb.set)
        self.thsb = ttk.Scrollbar(self.TreeFrame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.thsb.set)

        self.tvsb.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.thsb.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.tree.pack(fill=tk.BOTH, expand=1)

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())

        self.uuid_lookup = {}
        self.level_lookup = []
        self.selected_level = None
        self.replacements = {}
        self.children = {}

        self.root.geometry('1200x600')
        self.root.mainloop()

    def import_compressed_bigfile(self):
        self._import_bigfile(True)

    def import_uncompressed_bigfile(self):
        self._import_bigfile(False)

    def _import_bigfile(self, compressed):
        inf = fd.askopenfilename(parent=self.root, title="Import Compressed Bigfile")
        if inf:
            try:
                if compressed:
                    self.bfe.read_compressed_bigfile(inf)
                else:
                    self.bfe.read_uncompressed_bigfile(inf)
                self.build_gui(self.bfe.tables)
            except Exception as e:
                mb.showerror("Error importing file", "Error importing big file.\nDid you choose the right file?\nException details:\n" + str(e))
                self.clear_gui()

    def export_compressed_bigfile(self):
        self._export_bigfile(True)

    def export_uncompressed_bigfile(self):
        self._export_bigfile(False)

    def _export_bigfile(self, compressed):
        ouf = fd.asksaveasfilename(parent=self.root, title="Export Uncompressed Bigfile")
        if ouf:
            try:
                self.apply_replacements()
                if compressed:
                    self.bfe.write_compressed_bigfile(ouf)
                else:
                    self.bfe.write_uncompressed_bigfile(ouf)
            except Exception as e:
                mb.showerror("Error exporting file", "Error exporting bigfile.\nDo you have write permissions and enough drive space?\nException details:\n" + str(e))

    def apply_replacements(self):
        # 1. walk each replacement and apply it
        # WARNING: This relies on the fact that we never replace or
        # delete nodes, we only modify them.
        # Therefore they end up in the same relative location every
        # time we make changes, no matter what those changes are.
        # *IF* nodes can be added or removed, then a new method to link
        # old and new nodes would be required.
        new_children = {}
        for r in self.replacements:
            (t, n, r) = self.replacements[r]
            s2 = t['s2']
            index = self.children[s2].index(n)
            if not index:
                mb.showerror("Uh oh", "Internal error: Index of child node not found!")
            elif s2 in new_children:
                new_children[s2] = replace_node(t, new_children[s2][index], r)
            else:
                new_children[s2] = replace_node(t, n, r)

        # 2. clear replacements (they're applied)
        self.replacements = {}

        # 3. rebuild GUI
        self.build_gui(self.bfe.tables)

    def build_gui(self, tables):
        self.clear_gui()
        for table in tables:
            max_name = 0
            if table['s1'].decode('utf-16') == "LevelData":
                s2 = table['s2'].decode('utf-16')
                self.levellist.insert(tk.END, s2)
                self.level_lookup.append(table)
                max_name = max(max_name, len(s2))
        self.levellist.configure(width=max_name)

    def clear_gui(self):
        self.clear_tree()
        self.selected_level = None
        self.children = {}
        self.level_lookup = []
        self.levellist.delete(0, tk.END)

    def edit_item(self, e):
        uid = str(self.tree.focus())
        if uid not in self.uuid_lookup:
            mb.showwarning("Can't edit top-level", "Can't replace top-level items; choose an enemy, destroyable or pickup instead.")
        else:
            n = self.uuid_lookup[uid]
            choices = []
            if n.content in enemy_list:
                choices = enemy_list
            elif n.content in destroyable_list:
                choices = destroyable_list
            elif n.content in pickup_list:
                choices = pickup_list
            chosen = SelectReplacementDialog(self.root, "Replace " + str(n.content) + " with:", choices).show()
            if chosen:
                self.replacements[uid] = (self.selected_level, n, chosen)
                w = e.widget
                w.item(w.focus(), text=chosen)

    def clear_tree(self):
        self.uuid_lookup = {}
        for item in self.tree.get_children():
            self.tree.delete(item)

    def build_gui_tree(self, tree, parent, data):
        children = find_string_hierarchy(data, DataSpooler(data))
        self.children[self.selected_level['s2']] = children
        current_parent = ''
        for c in children:
            path = ""
            p = c.parent
            while p:
                path = str(p.field_num) + "." + path
                p = p.parent
            path += str(c.field_num)
            if path == "101.13.1":
                current_parent = self.tree.insert('', 'end', text=c.content)
            elif c.content in enemy_list or c.content in destroyable_list or c.content in pickup_list:
                uid = uuid.uuid4()
                self.tree.insert(current_parent, 'end', uid, text=c.content)
                self.uuid_lookup[str(uid)] = c

    def select_level(self, e):
        sel = e.widget.curselection()
        if sel:
            self.selected_level = self.level_lookup[sel[0]]
            self.clear_tree()
            self.build_gui_tree(self.tree, '', self.selected_level['data'])

if __name__ == "__main__":
    bfe = BigFileEditor()
    leg = LevelEditorGUI(bfe)
