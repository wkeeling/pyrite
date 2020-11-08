import tkinter as tk
from tkinter import ttk

from pyrite.ui import theme


class Editor(ttk.Notebook):

    default_name = 'Untitled {}'

    def __init__(self, master: tk.Tk, on_tab_change: callable):
        super().__init__(master=master)
        self.pack(expand=True, fill='both')

        self.documents = []

        self.new()

        self.bind('<<NotebookTabChanged>>', lambda e: on_tab_change(self.identify(e.x, e.y)))

    def new(self):
        tab = ttk.Frame(self)
        doc = Document(master=tab, on_cursor=lambda: None, on_change=lambda: None)
        self.add(tab, text=doc.filename or self.default_name.format(doc.count))
        self.documents.append(doc)

    def open(self, filename: str, encoding: str = 'utf-8'):
        with open(filename, 'rt', encoding=encoding) as f:
            active_doc = self.documents[self.index('current')]
            active_doc.content = f.read()

    def save(self):
        # Saves the currently active document
        pass


class Document(tk.Frame):

    count = 0

    def __init__(self, master: tk.Widget, on_cursor: callable, on_change: callable):
        super().__init__(master=master)
        self.pack(expand=True, fill='both')

        self.filename: str = None

        Document.count += 1

        self._content = tk.Text(master=self)
        self._content.config(**theme.current()['documentconfig'])
        self._content.pack(expand=True, fill='both')

    @property
    def content(self) -> str:
        return self._content.get(0, tk.END)

    @content.setter
    def content(self, content: str):
        self._content = content

    @property
    def length(self) -> int:
        return len(self.content)
