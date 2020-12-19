import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from pyrite import state, theme
from pyrite.editor import Editor


def create(master: tk.Tk, editor: Editor):
    menubar = tk.Menu(master=master, tearoff=False)
    master.config(menu=menubar)
    menubar.config(**theme.menuconfig)

    filemenu = FileMenu(master=menubar, editor=editor)
    menubar.add_cascade(label='File', underline=0, menu=filemenu)


class FileMenu(tk.Menu):

    def __init__(self, master: tk.Menu, editor: Editor):
        super().__init__(master=master, tearoff=False)
        self.editor = editor

        self.config(**theme.menuconfig)
        self.add_command(label='New...', underline=0, command=self.new)
        self.add_command(label='Open...', underline=0, command=self.open)
        self.add_command(label='Save', underline=0, command=self.save)
        self.add_command(label='Save As...', command=self.save_as)
        self.add_separator()
        self.add_command(label='Exit', underline=1, command=self.destroy)

    def new(self):
        pass

    def save(self):
        pass

    def save_as(self):
        filename = filedialog.asksaveasfilename(
            initialdir=state.get('last_open_loc', '/'),
            initialfile=self.editor.current_document.name or '',
            title='Save As',
            filetypes=(('all files', '*.*'),)
        )

        if filename:
            self.editor.save(filename)

            state['last_open_loc'] = Path(filename).parent
            state.save()

    def open(self):
        filename = filedialog.askopenfilename(
            initialdir=state.get('last_open_loc', '/'),
            title='Open',
            filetypes=(('all files', '*.*'),)
        )

        if filename:
            self.editor.open(filename)

            state['last_open_loc'] = Path(filename).parent
            state.save()
