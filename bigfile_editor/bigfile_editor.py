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
import sys
import struct
import os
import copy

# https://gist.github.com/wware/a1d90a3ca3cbef31ed3fbb7002fd1318
import uuid
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import known_types 

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
        self.listbox = tk.Listbox(self.TableFrame, width=48, height=32)
        self.scrollbar = ttk.Scrollbar(self.TableFrame)
        self.scrollbarx = ttk.Scrollbar(self.TableFrame, orient=tk.HORIZONTAL)
        self.listbox.config(yscrollcommand = self.scrollbar.set)
        self.listbox.config(xscrollcommand = self.scrollbarx.set)
        self.scrollbar.config(command = self.listbox.yview)
        self.scrollbarx.config(command = self.listbox.xview)
        self.listbox.bind('<<ListboxSelect>>', self.table_select)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.scrollbarx.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.TableFrame.grid(row=0, column=0, rowspan=2, sticky=tk.NS)

        self.LabelFrame = ttk.Frame(self.root)
        self.AddButton = ttk.Button(self.root, text="Append New Node to Array", command=self.add_node)
        self.QuitButton = ttk.Button(self.root, text="Quit", command=self.root.destroy)
        self.SaveButton = ttk.Button(self.root, text="Save Changes", command=self.bfe.export_all_tables)
        self.s1 = tk.StringVar()
        self.s2 = tk.StringVar()
        self.s1label = ttk.Label(self.LabelFrame, textvariable=self.s1)
        self.s2label = ttk.Label(self.LabelFrame, textvariable=self.s2)
        self.s1label.pack()
        self.s2label.pack()
        self.AddButton.grid(row=2, column=1)
        self.SaveButton.grid(row=3, column=0)
        self.QuitButton.grid(row=3, column=1)
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

        self.bfe.import_all_tables()
        self.uuid_lookup = {}
        self.selected_table = None

        self.list_tables(self.bfe.tables)
        self.root.geometry('1200x600')
        self.user_is_expert = False
        self.root.mainloop()

    def add_node(self):
        if not self.selected_table or not self.tree or not self.tree.focus():
            return

        self.user_is_expert = mb.askyesno("Are you sure?", "Are you absolutely sure you know what this does?\nYou really shouldn't use this if you aren't sure!")

        if not self.user_is_expert:
            return

        uid = self.tree.focus()
        if uid not in self.uuid_lookup or not isinstance(self.uuid_lookup[uid], list):
            mb.showerror("Error", "Can't add nodes to an endpoint (select an array instead).")
            return
        else:
            self.uuid_lookup[uid].append(copy.deepcopy(self.uuid_lookup[uid][-1]))
            self.selected_table['edited'] = True
            self.clear_tree()
            self.build_gui_tree(self.tree ,'', self.selected_table['message'])

    def table_select(self, event):
        w = event.widget
        if not w or not w.curselection():
            return
        index = int(w.curselection()[0])
        tsel = w.get(index)

        self.selected_table = self.bfe.tables[index]

        if not self.selected_table:
            mb.showerror("No table found", "Internal error: Table loaded but not found!")
        else:
            message = self.bfe.read_table(self.selected_table)
            self.s1.set(self.selected_table['s1'])
            self.s2.set(self.selected_table['s2'])
            self.clear_tree()
            self.build_gui_tree(self.tree ,'', message)

    def clear_tree(self):
        self.uuid_lookup = {}
        for item in self.tree.get_children():
           self.tree.delete(item)

    def list_tables(self, tables):
        self.listbox.delete(0,tk.END)
        for t in tables:
            self.listbox.insert(tk.END, (t['s1']).decode() + " : " + (t['s2']).decode())

    def close_ed(self, parent, edwin):
        parent.focus_set()
        edwin.destroy()

    def set_cell(self, edwin, w, tvar):
        value = tvar.get()
        uid = self.tree.focus()
        if uid not in self.uuid_lookup:
            uid = self.tree.parent(uid)
        if uid not in self.uuid_lookup:
            mb.showerror("Internal Error", "Could not find uid: " + str(uid))
        if uid in self.uuid_lookup:
            if value.isnumeric():
                self.uuid_lookup[uid][w.item(w.focus())['text']] = int(value)
            else:
                self.uuid_lookup[uid][w.item(w.focus())['text']] = value
            self.selected_table['edited'] = True
        w.item(w.focus(), values=(value,))
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
                self.uuid_lookup[str(uid)] = message[key]
                self.build_gui_tree(tree,
                         uid,
                         dict([(i, x) for i, x in enumerate(message[key])]),
                         crumb)
            else:
                value = message[key]
                tree.insert(parent, 'end', uid, text=key, value=(value, meaning))

class BigFileEditor:
    def __init__(self, bigfile_in, bigfile_out):
        self.fi = open(bigfile_in, "rb")
        self.fo = open(bigfile_out, "wb")
        self.total_chunks = 0
        self.tables = []

    def __del__(self):
        if not self.fi.closed:
            self.fi.close()
        if not self.fo.closed:
            self.fo.close()

    def read_table(self, tr, decode=True):
        if not tr['data']:
            self.fi.seek(tr['offset'], 0)
            tr['data'] = self.fi.read(tr['size'])
        
        if decode and (not tr['message'] or not tr['typedef']):
            tr['message'],tr['typedef'] = blackboxprotobuf.decode_message(tr['data'])
        return tr['message']

    def export_all_tables(self):
        self.fo.seek(0,0)
        # We never add tables to the list
        self.fo.write(self.total_chunks.to_bytes(4,"little"))
        for t in self.tables:
            # We never change string headers, only data
            write7bit(t['s1len'], self.fo)
            self.fo.write(t['s1'])
            write7bit(t['s2len'], self.fo)
            self.fo.write(t['s2'])

            if t['edited']:
                data = blackboxprotobuf.encode_message(t['message'],t['typedef'])
                self.fo.write(len(data).to_bytes(4,"little"))
                self.fo.write(data)
            else:
                if not t['data']:
                    self.read_table(t, decode=False)
                self.fo.write(t['size'].to_bytes(4,"little"))
                self.fo.write(t['data'])

    def import_all_tables(self, read_data=False):
        self.fi.seek(0,0)
        self.total_chunks = struct.unpack('i', self.fi.read(4))[0]
        self.tables = []
        for i in range(self.total_chunks):
            s1len = read7bit(self.fi)
            s1 = self.fi.read(s1len)

            s2len = read7bit(self.fi)
            s2 = self.fi.read(s2len)

            protobuf_size = struct.unpack('i', self.fi.read(4))[0]
            offset = self.fi.tell()
            if read_data:
                protobuf = self.fi.read(protobuf_size)
            else:
                self.fi.seek(protobuf_size, 1)
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

    def bigfile_readwrite(self):
        self.fo.seek(0,0)
        self.fi.seek(0,0)
        done_editing = True
        edited = False
        total_chunks = struct.unpack('i', self.fi.read(4))[0]
        self.fo.write(total_chunks.to_bytes(4,"little"))
        for i in range(total_chunks):
            s1len = read7bit(self.fi)
            s1 = self.fi.read(s1len)
            write7bit(s1len, self.fo)
            self.fo.write(s1)

            s2len = read7bit(self.fi)
            s2 = self.fi.read(s2len)
            write7bit(s2len, self.fo)
            self.fo.write(s2)

            protobuf_size = struct.unpack('i', self.fi.read(4))[0]
            protobuf = self.fi.read(protobuf_size)

            if not done_editing:
                message,typedef = blackboxprotobuf.decode_message(protobuf)
                #gui_init(s1, s2, message)
                if edited:
                    msg = blackboxprotobuf.encode_message(message,typedef)
                    self.fo.write(len(msg).to_bytes(4,"little"))
                    self.fo.write(msg)
            else:
                self.fo.write(protobuf_size.to_bytes(4,"little"))
                self.fo.write(protobuf)

if __name__ == "__main__":
    bigfile_in = "bigdata/bigfile.decomp"
    while not os.path.isfile(bigfile_in):
        bigfile_in = fd.askopenfile(title="Open bigfile.decomp", filetype=(("Decompressed bigfile", "*.decomp")))

    bigfile_out = "bigdata/bigfile.mod"
    while not os.path.isfile(bigfile_out):
        bigfile_out = fd.asksaveasfilename(title="Write bigfile.mod", filetype=(("Modified bigfile", "*.mod")))

    bfe = BigFileEditor(bigfile_in, bigfile_out)
    bfg = BigFileGui(bfe)

