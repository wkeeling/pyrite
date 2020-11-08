import tkinter as tk
from tkinter import filedialog

from pyrite.ui import theme


def create(master: tk.Widget, editor):
    menubar = tk.Menu(master=master, tearoff=False)
    master.config(menu=menubar)
    menubar.config(**theme.current()['menuconfig'])

    filemenu = FileMenu(master=menubar, editor=editor)
    menubar.add_cascade(label='File', underline=0, menu=filemenu)


class FileMenu(tk.Menu):

    def __init__(self, master: tk.Menu, editor):
        super().__init__(master=master, tearoff=False)
        self.editor = editor

        self.config(**theme.current()['menuconfig'])
        self.add_command(label='New...', underline=0, command=self.destroy)
        self.add_command(label='Open...', underline=0, command=self.open)
        self.add_separator()
        self.add_command(label='Exit', underline=1, command=self.destroy)

    def open(self):
        filename = tk.filedialog.askopenfilename(
            initialdir='/',
            title='Open',
            filetypes=(('all files', '*.*'),)
        )

        self.editor.open(filename, 'utf-8')
