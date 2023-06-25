import blackboxprotobuf
import sys
import struct
import os

# https://gist.github.com/wware/a1d90a3ca3cbef31ed3fbb7002fd1318
import uuid
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

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


# adapted from:
# https://stackoverflow.com/questions/8574070/python-display-a-dict-of-dicts-using-a-ui-tree-for-the-keys-and-any-other-widg
class BigFileGui:
    def __init__(self, bfe):
        self.root = tk.Tk()
        self.bfe = bfe
        self.root.title("bigfile table editor")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.TableFrame = ttk.Frame(self.root)
        self.listbox = tk.Listbox(self.TableFrame)
        self.scrollbar = ttk.Scrollbar(self.TableFrame)
        self.listbox.config(yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.listbox.bind('<<ListboxSelect>>', self.table_select)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.TableFrame.grid(row=0, column=0, rowspan=2, sticky=tk.NS)

        self.LabelFrame = ttk.Frame(self.root)
        self.QuitButton = ttk.Button(self.root, text="Quit", command=self.root.destroy)
        self.s1 = tk.StringVar()
        self.s2 = tk.StringVar()
        self.s1label = ttk.Label(self.LabelFrame, textvariable=self.s1)
        self.s2label = ttk.Label(self.LabelFrame, textvariable=self.s2)
        self.s1label.pack()
        self.s2label.pack()
        self.QuitButton.grid(row=2, column=1)
        self.LabelFrame.grid(row=0, column=1)

        self.TreeFrame = ttk.Frame(self.root, padding="3")
        self.TreeFrame.grid(row=1, column=1, sticky=tk.NSEW)

        self.tree = ttk.Treeview(self.TreeFrame, columns=('Values'))
        self.tree.column('Values', width=100, anchor='center')
        self.tree.heading('Values', text='Values')
        self.tree.bind('<Double-1>', self.edit_cell)
        self.tree.bind('<Return>', self.edit_cell)
        self.tree.pack(fill=tk.BOTH, expand=1)

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())

        self.bfe.import_all_tables()
        self.list_tables(self.bfe.tables)
        self.root.mainloop()

    def table_select(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        tsel = w.get(index)

        selected_table = self.bfe.tables[index]

        if not selected_table:
            mb.showerror("No table found", "Internal error: Table loaded but not found!")
        else:
            message = self.bfe.read_table(selected_table)
            self.s1.set(selected_table['s1'])
            self.s2.set(selected_table['s2'])
            self.clear_tree()
            self.build_gui_tree(self.tree ,'', message)

    def clear_tree(self):
        for item in self.tree.get_children():
           self.tree.delete(item)

    def list_tables(self, tables):
        self.listbox.delete(0,tk.END)
        for t in tables:
            self.listbox.insert(tk.END, t['s1'])

    def close_ed(self, parent, edwin):
        parent.focus_set()
        edwin.destroy()

    def set_cell(self, edwin, w, tvar):
        value = tvar.get()
        w.item(w.focus(), values=(value,))
        self.close_ed(w, edwin)

    def edit_cell(self, e):
        w = e.widget
        if w and len(w.item(w.focus(), 'values')) > 0:
            edwin = tk.Toplevel(e.widget)
            edwin.protocol("WM_DELETE_WINDOW", lambda: self.close_ed(w, edwin))
            edwin.wait_visibility()
            edwin.grab_set()
            edwin.overrideredirect(1)
            opt_name = w.focus()
            (x, y, width, height) = w.bbox(opt_name, 'Values')
            edwin.geometry('%dx%d+%d+%d' % (width, height, x/4, y))
            value = w.item(opt_name, 'values')[0]
            tvar = tk.StringVar()
            tvar.set(str(value))
            ed = tk.Entry(edwin, textvariable=tvar)
            if ed:
                ed.pack()
                ed.focus_set()
            edwin.bind('<Return>', lambda e: self.set_cell(edwin, w, tvar))
            edwin.bind('<Escape>', lambda e: self.close_ed(w, edwin))

    def build_gui_tree(self, tree, parent, message):
        for key in message:
            uid = uuid.uuid4()
            if isinstance(message[key], dict):
                tree.insert(parent, 'end', uid, text=key)
                self.build_gui_tree(tree, uid, message[key])
            elif isinstance(message[key], list):
                tree.insert(parent, 'end', uid, text=key + '[]')
                self.build_gui_tree(tree,
                         uid,
                         dict([(i, x) for i, x in enumerate(message[key])]))
            else:
                value = message[key]
                if isinstance(value, str) or isinstance(value, str):
                    value = value.replace(' ', '_')
                tree.insert(parent, 'end', uid, text=key, value=value)

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

    def read_table(self, tr):
        if not tr['data']:
            self.fi.seek(tr['offset'], 0)
            tr['data'] = self.fi.read(tr['size'])
        
        message,typedef = blackboxprotobuf.decode_message(tr['data'])
        return message

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

            self.tables.append({"s1": s1, "s2": s2, "offset": offset, "size": protobuf_size, "data": protobuf, "edited": False})

        
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
    global edited
    global done_editing
    done_editing = False
    bigfile_in = "bigdata/bigfile.decomp"
    while not os.path.isfile(bigfile_in):
        bigfile_in = fd.askopenfile(title="Open bigfile.decomp", filetype=(("Decompressed bigfile", "*.decomp")))

    bigfile_out = "bigdata/bigfile.mod"
    while not os.path.isfile(bigfile_out):
        bigfile_out = fd.asksaveasfilename(title="Write bigfile.mod", filetype=(("Modified bigfile", "*.mod")))

    bfe = BigFileEditor(bigfile_in, bigfile_out)
    bfg = BigFileGui(bfe)

