# SoR4 Bigfile Editor
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

import blackboxprotobuf
from google.protobuf.internal import wire_format
import sys
import struct
import os
import copy
import zlib
import tempfile

# https://gist.github.com/wware/a1d90a3ca3cbef31ed3fbb7002fd1318
import uuid
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import known_types 

def deflate(data, compresslevel=9):
    compress = zlib.compressobj(compresslevel, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    deflated = compress.compress(data)
    deflated += compress.flush()
    return deflated

def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

def read7bit(f):
    more = True
    val = 0
    order = 0
    while more:
        num = int.from_bytes(f.read(1), 'little')
        more = ((num >> 7) & 0x01)
        val += ((num&0x7f) << (order*7))
        order += 1

    return val

def write7bit(val, of):
    while val:
        b = (val & 0x7F)
        val >>= 7
        if val:
            b |= 0x80
        of.write(b.to_bytes(1,"little"))


class BigFileGui:
    def __init__(self, bfe):
        self.root = tk.Tk()
        self.bfe = bfe
        self.root.title("bigfile table editor")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.TableFrame = ttk.Frame(self.root)
        self.tabletree = ttk.Treeview(self.TableFrame)
        self.scrollbar = ttk.Scrollbar(self.TableFrame)
        self.scrollbarx = ttk.Scrollbar(self.TableFrame, orient=tk.HORIZONTAL)
        self.tabletree.config(yscrollcommand = self.scrollbar.set)
        self.tabletree.config(xscrollcommand = self.scrollbarx.set)
        self.tabletree.column("#0", width=384, minwidth=512, stretch=True)
        self.scrollbar.config(command = self.tabletree.yview)
        self.scrollbarx.config(command = self.tabletree.xview)
        self.tabletree.bind('<<TreeviewSelect>>', self.select_table)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.scrollbarx.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.tabletree.pack(side=tk.LEFT, fill=tk.BOTH)
        self.TableFrame.grid(row=0, column=0, rowspan=2, sticky=tk.NS)

        self.TreeButtonFrame = ttk.Frame(self.root)
        self.AddButton = ttk.Button(self.TreeButtonFrame, text="Extend Array (+1 Node)", command=self.add_node)
        self.TreeExpandButton = ttk.Button(self.TreeButtonFrame, text="Expand Below", command=self.expand_subnodes)
        self.TreeCollapseButton = ttk.Button(self.TreeButtonFrame, text="Collapse Below", command=self.collapse_subnodes)
        self.QuitButton = ttk.Button(self.root, text="Quit", command=self.root.destroy)

        self.util_buttons = [self.AddButton, self.TreeExpandButton, self.TreeCollapseButton]
        self.set_util_buttons_enabled(False)

        self.FileButtonFrame = ttk.Frame(self.root)
        self.ImportCompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Import COMPRESSED Bigfile", command=self.import_compressed_bigfile)
        self.ImportUncompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Import UNCOMPRESSED Bigfile", command=self.import_uncompressed_bigfile)
        self.ExportCompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Export COMPRESSED Bigfile", command=self.export_compressed_bigfile)
        self.ExportUncompressedBigfileButton = ttk.Button(self.FileButtonFrame, text="Export UNCOMPRESSED Bigfile", command=self.export_uncompressed_bigfile)

        self.ImportCompressedBigfileButton.grid(row=0, column=0)
        self.ImportUncompressedBigfileButton.grid(row=0, column=1) 
        self.ExportUncompressedBigfileButton.grid(row=0, column=2)
        self.ExportCompressedBigfileButton.grid(row=0, column=3) 
        
        self.TreeExpandButton.grid(row=0, column=0)
        self.TreeCollapseButton.grid(row=0, column=1)
        self.AddButton.grid(row=0, column=2)
        self.TreeButtonFrame.grid(row=2, column=1)

        self.LabelFrame = ttk.Frame(self.root)
        self.s1 = tk.StringVar()
        self.s2 = tk.StringVar()
        self.s1label = ttk.Label(self.LabelFrame, textvariable=self.s1)
        self.s2label = ttk.Label(self.LabelFrame, textvariable=self.s2)
        self.s1label.pack()
        self.s2label.pack()
        self.FileButtonFrame.grid(row=3, column=0, columnspan=2)
        self.QuitButton.grid(row=4, column=1, sticky=tk.E)
        self.LabelFrame.grid(row=0, column=1)

        self.TreeFrame = ttk.Frame(self.root, padding="3")
        self.TreeFrame.grid(row=1, column=1, sticky=tk.NSEW)

        self.tree = ttk.Treeview(self.TreeFrame, columns=('Values', 'Meaning'))
        self.tree.column('Values', width=100, anchor='center')
        self.tree.column('Meaning', width=60, anchor='e')
        self.tree.heading('Values', text='Values')
        self.tree.heading('Meaning', text='Meaning')
        self.tree.bind('<Double-1>', self.edit_cell)
        self.tree.bind('<Return>', self.edit_cell)

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
        self.selected_table = None

        self.root.geometry('1200x600')
        self.user_is_expert = False
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
                self.set_util_buttons_enabled(True)
                self.build_table_tree(self.bfe.tables)
            except Exception as e:
                mb.showerror("Error importing file", "Error importing big file.\nDid you choose the right file?\nException details:\n" + str(e))
                self.clear_tables()
                self.set_util_buttons_enabled(False)

    def export_compressed_bigfile(self):
        self._export_bigfile(True)

    def export_uncompressed_bigfile(self):
        self._export_bigfile(False)
    
    def _export_bigfile(self, compressed):
        ouf = fd.asksaveasfilename(parent=self.root, title="Export Uncompressed Bigfile")
        if ouf:
            try:
                if compressed:
                    self.bfe.write_compressed_bigfile(ouf)
                else:
                    self.bfe.write_uncompressed_bigfile(ouf)
            except Exception as e:
                mb.showerror("Error exporting file", "Error exporting bigfile.\nDo you have write permissions and enough drive space?\nException details:\n" + str(e))

    def set_util_buttons_enabled(self, state):
        for button in self.util_buttons:
            if state:
                button.state(['!disabled'])
            else:
                button.state(['disabled'])

    def set_subnodes_state(self, subtree, parent, openstate=True):
        subtree.item(parent, open=openstate)
        for child in subtree.get_children(parent):
            self.set_subnodes_state(subtree, child, openstate)
        
    def expand_subnodes(self):
        self.set_subnodes_state(self.tree, self.tree.focus(), openstate=True)

    def collapse_subnodes(self):
        self.set_subnodes_state(self.tree, self.tree.focus(), openstate=False)

    def add_node(self):
        if not self.selected_table or not self.tree or not self.tree.focus():
            return

        self.user_is_expert = mb.askyesno("Are you sure?", "Are you absolutely sure you know what this does?\nYou really shouldn't use this if you aren't sure!")

        if not self.user_is_expert:
            return

        uid = self.tree.focus()
        node_text = self.tree.item(self.tree.focus())['text']
        node_is_array = isinstance(node_text, str) and node_text.endswith('[]')

        if uid not in self.uuid_lookup or not node_is_array:
            uid = self.tree.parent(uid)

        if uid not in self.uuid_lookup:
            mb.showerror("Error", "Could not find uuid for node (internal error)")
            return

        if not node_is_array and len(self.tree.item(self.tree.focus(), 'values')) > 0 and self.tree.item(self.tree.focus(), 'values')[1] is not None:
            model_node = self.uuid_lookup[uid][node_text]
        else:
            model_node = copy.deepcopy(self.uuid_lookup[uid][-1])
        
        if not isinstance(self.uuid_lookup[uid], list):
            mb.showerror("Error", "Can't add nodes to an endpoint (select an array instead).")
            return
        else:
            self.uuid_lookup[uid].append(model_node)
            self.selected_table['edited'] = True
            self.clear_tree()
            self.build_gui_tree(self.tree ,'', self.selected_table['message'])

    def select_table(self, event):
        uid = self.tabletree.focus()
        if uid not in self.table_uuids:
            return
        else:
            self.selected_table = self.table_uuids[uid]

        if not self.selected_table:
            mb.showerror("No table found", "Internal error: Table loaded but not found!")
        else:
            message = self.bfe.read_table(self.selected_table)
            self.s1.set(self.selected_table['s1'].decode('utf-16'))
            self.s2.set(self.selected_table['s2'].decode('utf-16'))
            self.clear_tree()
            self.build_gui_tree(self.tree ,'', message)

    def clear_tree(self):
        self.uuid_lookup = {}
        for item in self.tree.get_children():
           self.tree.delete(item)

    def clear_tables(self):
        self.clear_tree()
        self.table_uuids = {}
        self.table_tree_s1_to_uid = {}
        for item in self.tabletree.get_children():
            self.tabletree.delete(item)

    def build_table_tree(self, tables):
        self.clear_tables()
        for t in tables:
            s1 = t['s1'].decode('utf-16')
            s2 = t['s2'].decode('utf-16')
            if s1 not in self.table_tree_s1_to_uid:
                s1uid = uuid.uuid4()
                self.tabletree.insert('', 'end', s1uid, text=s1)
                self.table_tree_s1_to_uid[s1] = s1uid
            parent = self.table_tree_s1_to_uid[s1]
            s2uid = uuid.uuid4()
            self.table_uuids[str(s2uid)] = t
            self.tabletree.insert(parent, 'end', s2uid, text=s2)

    def close_ed(self, parent, edwin):
        parent.focus_set()
        edwin.destroy()

    def determine_value_type(self, uid, value):
        # uid can be used later to compare against
        # typedef, but for now, we have only
        # string, varint, float and double, and we
        # will infer types
        if not value:
            return None

        strip_value = str(value).strip()
        try:
            f = float(strip_value)
            if f.is_integer() and not '.' in strip_value:
                return int(f)
            else:
                return float(f)
        except ValueError:
            return value

    def set_cell(self, edwin, w, tvar):
        value = tvar.get()
        uid = self.tree.focus()
        if uid not in self.uuid_lookup:
            uid = self.tree.parent(uid)
        if uid in self.uuid_lookup:
            self.uuid_lookup[uid][w.item(w.focus())['text']] = self.determine_value_type(uid, value)
            self.selected_table['edited'] = True
        elif w.item(w.focus())['text'] not in self.selected_table['message']:
            mb.showerror("Internal Error", "Unknown node being edited; internal error.")
        else:
            # top-level (not in uid lookup)
            self.selected_table['message'][w.item(w.focus())['text']] = self.determine_value_type(uid, value)
            self.selected_table['edited'] = True

        meaning = w.item(w.focus())['values'][1]
        w.item(w.focus(), values=(value,meaning))
        self.close_ed(w, edwin)

    def check_edit(self, tvar, label):
        s = str(tvar.get())
        if s and s.isnumeric():
            label.set("As 16.16: " + str(float(int(s) / 65536.0)))

    def edit_cell(self, e):
        w = e.widget
        if w and len(w.item(w.focus(), 'values')) > 0:
            edwin = tk.Toplevel(e.widget)
            edwin.protocol("WM_DELETE_WINDOW", lambda: self.close_ed(w, edwin))
            edwin.wait_visibility()
            edwin.grab_set()
            edwin.overrideredirect(1)
            opt_name = w.focus()

            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (width/2)
            y = (height/2)
            edwin.geometry('+%d+%d' % (x, y))

            edframe = tk.Frame(edwin)
            value = w.item(opt_name, 'values')[0]
            tvar = tk.StringVar()
            tvar.set(str(value))
            lvar = tk.StringVar()
            if str(value).isnumeric():
                lvar.set("As 16.16: " + str(float(int(value) / 65536.0)))
            else:
                lvar.set("Original value: " + str(value))
            ed = tk.Entry(edframe, textvariable=tvar)
            label = tk.Label(edframe, textvariable=lvar)
            tvar.trace("w", lambda name, index, mode, sv=tvar: self.check_edit(tvar, lvar))
            if ed:
                edframe.pack()
                ed.pack()
                label.pack()
                ed.focus_set()
            edwin.bind('<Return>', lambda e: self.set_cell(edwin, w, tvar))
            edwin.bind('<Escape>', lambda e: self.close_ed(w, edwin))

    # adapted from:
    # https://stackoverflow.com/questions/8574070/python-display-a-dict-of-dicts-using-a-ui-tree-for-the-keys-and-any-other-widg
    def build_gui_tree(self, tree, parent, message, breadcrumb=None):
        if not breadcrumb:
            breadcrumb = [str(self.selected_table['s1'], 'utf-16')]
        for key in message:
            uid = uuid.uuid4()
            crumb = breadcrumb + [str(key)]
            meaning = known_types.lookup_type(crumb)
            if isinstance(message[key], dict):
                tree.insert(parent, 'end', uid, text=key, values=('', meaning))
                self.uuid_lookup[str(uid)] = message[key]
                self.build_gui_tree(tree, uid, message[key], crumb)
            elif isinstance(message[key], list):
                tree.insert(parent, 'end', uid, text=key + '[]', values=('', meaning))
                crumb[-1] = crumb[-1] + "[]"
                self.uuid_lookup[str(uid)] = message[key]
                self.build_gui_tree(tree,
                         uid,
                         dict([(i, x) for i, x in enumerate(message[key])]),
                         crumb)
            else:
                value = message[key]
                tree.insert(parent, 'end', uid, text=key, value=(value, meaning))

class BigFileEditor:
    def __init__(self):
        self.total_chunks = 0
        self.tables = []
        self.infile = None
        self.bb_config = blackboxprotobuf.lib.config.Config()
        self.bb_config.default_types[wire_format.WIRETYPE_FIXED32] = 'float'
        self.bb_config.default_types[wire_format.WIRETYPE_FIXED64] = 'double'

    def read_compressed_bigfile(self, filename):
        self._read_bigfile(filename, True)

    def read_uncompressed_bigfile(self, filename):
        self._read_bigfile(filename, False)

    def _read_bigfile(self, filename, compressed=True):
        with open(filename, "rb") as cb:
            if compressed:
                data = cb.read()
                data = inflate(data)
                cb = tempfile.TemporaryFile()
                cb.write(data)
            self.import_all_tables(cb)
            self.infile = filename

    def write_compressed_bigfile(self, filename):
        t = tempfile.TemporaryFile()
        self.export_all_tables(t)
        t.seek(0,0)
        data = t.read()
        with open(filename, "wb") as f:
            f.write(deflate(data))
        t.close()

    def write_uncompressed_bigfile(self, filename):
        with open(filename, "wb") as cb:
            self.export_all_tables(cb)
        
    def read_table(self, tr, decode=True):
        if not tr['data']:
            with open(self.infile, "rb") as f:
                f.seek(tr['offset'], 0)
                tr['data'] = f.read(tr['size'])
        
        if decode and (not tr['message'] or not tr['typedef']):
            tr['message'],tr['typedef'] = blackboxprotobuf.decode_message(tr['data'], config=self.bb_config)
        return tr['message']

    def export_all_tables(self, outfile):
        outfile.seek(0,0)
        # We never add tables to the list
        outfile.write(self.total_chunks.to_bytes(4,"little"))
        for t in self.tables:
            # We never change string headers, only data
            write7bit(t['s1len'], outfile)
            outfile.write(t['s1'])
            write7bit(t['s2len'], outfile)
            outfile.write(t['s2'])

            if t['edited']:
                data = blackboxprotobuf.encode_message(t['message'],t['typedef'], config=self.bb_config)
                outfile.write(len(data).to_bytes(4,"little"))
                outfile.write(data)
            else:
                if not t['data']:
                    self.read_table(t, decode=False)
                outfile.write(t['size'].to_bytes(4,"little"))
                outfile.write(t['data'])

    def import_all_tables(self, f, read_data=True):
        f.seek(0,0)
        self.total_chunks = struct.unpack('i', f.read(4))[0]
        self.tables = []
        for i in range(self.total_chunks):
            s1len = read7bit(f)
            s1 = f.read(s1len)

            s2len = read7bit(f)
            s2 = f.read(s2len)

            protobuf_size = struct.unpack('i', f.read(4))[0]
            offset = f.tell()
            if read_data:
                protobuf = f.read(protobuf_size)
            else:
                f.seek(protobuf_size, 1)
                protobuf = None

            self.tables.append({"s1": s1,
                                "s1len": s1len,
                                "s2": s2,
                                "s2len": s2len,
                                "offset": offset,
                                "size": protobuf_size,
                                "data": protobuf,
                                "message": None,
                                "typedef": None,
                                "edited": False})

if __name__ == "__main__":
    bfe = BigFileEditor()
    bfg = BigFileGui(bfe)

