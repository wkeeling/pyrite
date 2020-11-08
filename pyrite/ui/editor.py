import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Optional

from pyrite.ui import theme


class Editor(ttk.Notebook):
    """Responsible for managing a collection of Documents in a tabbed view."""

    new_document_name = 'Untitled'

    def __init__(self, master: tk.Tk, on_tab_change: callable):
        super().__init__(master=master)

        self.documents = []

        self.new()

        self.bind('<<NotebookTabChanged>>', lambda e: on_tab_change(self.identify(e.x, e.y)))

    def new(self):
        tab = ttk.Frame(self)
        doc = Document(master=tab, on_cursor=lambda: None, on_change=lambda: None)
        doc.pack(expand=True, fill='both')
        self.add(tab, text=doc.name or self.new_document_name)
        self.documents.append(doc)

    def open(self, filename: str, encoding: str = 'utf-8'):
        with open(filename, 'rt', encoding=encoding) as f:
            content = f.read()
            active_doc = self.documents[self.index('current')]
            active_doc.content = content

    def save(self):
        # Saves the currently active document
        pass


class Document(tk.Frame):

    def __init__(self, master: tk.Widget, on_cursor: callable, on_change: callable):
        super().__init__(master=master)

        self.filename: str = None

        self._content = tk.Text(master=self)
        self._content.config(**theme.current()['documentconfig'])
        self._content.pack(expand=True, fill='both')

    @property
    def name(self) -> Optional[str]:
        if self.filename:
            return Path(self.filename).name

        return None

    @property
    def content(self) -> str:
        return self._content.get(0, tk.END)

    @content.setter
    def content(self, content: str):
        self._content.insert(tk.END, content)

    @property
    def length(self) -> int:
        return len(self.content)


def create(master: tk.Widget) -> Editor:
    """Convenience function for creating an Editor instance.

    Args:
        master: The parent widget.
    Returns: The Editor instance.
    """
    editor = Editor(master=master, on_tab_change=lambda x: print(x))
    editor.pack(expand=True, fill='both')
    return editor
