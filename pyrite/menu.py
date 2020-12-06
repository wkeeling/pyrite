import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from pyrite import state, theme


def create(master: tk.Widget, editor):
    menubar = tk.Menu(master=master, tearoff=False)
    master.config(menu=menubar)
    menubar.config(**theme.menuconfig)

    filemenu = FileMenu(master=menubar, editor=editor)
    menubar.add_cascade(label='File', underline=0, menu=filemenu)


class FileMenu(tk.Menu):

    def __init__(self, master: tk.Menu, editor):
        super().__init__(master=master, tearoff=False)
        self.editor = editor

        self.config(**theme.menuconfig)
        self.add_command(label='New...', underline=0, command=self.destroy)
        self.add_command(label='Open...', underline=0, command=self._open)
        self.add_separator()
        self.add_command(label='Exit', underline=1, command=self.destroy)

    def _open(self):
        filename = tk.filedialog.askopenfilename(
            initialdir=state.get('last_open_loc', '/'),
            title='Open',
            filetypes=(('all files', '*.*'),)
        )

        self.editor.open(filename, 'utf-8')

        state['last_open_loc'] = Path(filename).parent
        state.save()
