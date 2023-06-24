import blackboxprotobuf
import sys
import struct

# https://gist.github.com/wware/a1d90a3ca3cbef31ed3fbb7002fd1318
import uuid
import tkinter as tk
from tkinter import ttk


def close_ed(parent, edwin):
    parent.focus_set()
    edwin.destroy()

def set_cell(edwin, w, tvar):
    global edited
    edited = True
    value = tvar.get()
    w.item(w.focus(), values=(value,))
    close_ed(w, edwin)

def edit_cell(e):
    global edited
    w = e.widget
    if w and len(w.item(w.focus(), 'values')) > 0:
        edwin = tk.Toplevel(e.widget)
        edwin.protocol("WM_DELETE_WINDOW", lambda: close_ed(w, edwin))
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
        edwin.bind('<Return>', lambda e: set_cell(edwin, w, tvar))
        edwin.bind('<Escape>', lambda e: close_ed(w, edwin))


def build_gui_tree(tree, parent, message):
    for key in message:
        uid = uuid.uuid4()
        if isinstance(message[key], dict):
            tree.insert(parent, 'end', uid, text=key)
            build_gui_tree(tree, uid, message[key])
        elif isinstance(message[key], list):
            tree.insert(parent, 'end', uid, text=key + '[]')
            build_gui_tree(tree,
                     uid,
                     dict([(i, x) for i, x in enumerate(message[key])]))
        else:
            value = message[key]
            if isinstance(value, str) or isinstance(value, str):
                value = value.replace(' ', '_')
            tree.insert(parent, 'end', uid, text=key, value=value)

def gui_exit():
    global root
    global done_editing
    done_editing = True
    root.destroy()

# adapted from:
# https://stackoverflow.com/questions/8574070/python-display-a-dict-of-dicts-using-a-ui-tree-for-the-keys-and-any-other-widg
def gui_init(s1, s2, message):
    global edited
    global root
    root = tk.Tk()
    root.title("bigfile table editor")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(3, weight=1)
    LabelFrame = ttk.Frame(root)
    QuitButton = ttk.Button(root, text="Quit", command=gui_exit)
    NextButton = ttk.Button(root, text="Next Table", command=root.destroy)
    QuitButton.grid(row=0, column=0)
    NextButton.grid(row=1, column=0)
    LabelFrame.grid(row=2, column=0)
    s1label = ttk.Label(LabelFrame, text=s1)
    s2label = ttk.Label(LabelFrame, text=s2)
    s1label.pack()
    s2label.pack()
    TreeFrame = ttk.Frame(root, padding="3")
    TreeFrame.grid(row=3, column=0, sticky=tk.NSEW)

    tree = ttk.Treeview(TreeFrame, columns=('Values'))
    tree.column('Values', width=100, anchor='center')
    tree.heading('Values', text='Values')
    tree.bind('<Double-1>', edit_cell)
    tree.bind('<Return>', edit_cell)
    edited = False
    build_gui_tree(tree, '', message)
    tree.pack(fill=tk.BOTH, expand=1)

    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()


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

if __name__ == "__main__":
    global edited
    global done_editing
    done_editing = False
    with open("bigdata/bigfile.decomp", "rb") as f, open("bigdata/bigfile.mod", "wb") as of:
        total_chunks = struct.unpack('i', f.read(4))[0]
        of.write(total_chunks.to_bytes(4,"little"))
        for i in range(total_chunks):
            s1len = read7bit(f)
            s1 = f.read(s1len)
            write7bit(s1len, of)
            of.write(s1)

            s2len = read7bit(f)
            s2 = f.read(s2len)
            write7bit(s2len, of)
            of.write(s2)

            protobuf_size = struct.unpack('i', f.read(4))[0]
            protobuf = f.read(protobuf_size)

            if not done_editing:
                message,typedef = blackboxprotobuf.decode_message(protobuf)
                gui_init(s1, s2, message)
                if edited:
                    msg = blackboxprotobuf.encode_message(message,typedef)
                    of.write(len(msg).to_bytes(4,"little"))
                    of.write(msg)
            else:
                of.write(protobuf_size.to_bytes(4,"little"))
                of.write(protobuf)
