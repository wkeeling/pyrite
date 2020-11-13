import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Optional, Tuple

from pyrite import settings, theme


class Editor(ttk.Notebook):
    """Responsible for managing a collection of Documents in a tabbed view."""

    new_document_name = 'Untitled'

    def __init__(self, master: tk.Widget, on_tab_change: callable):
        super().__init__(master=master)

        self.documents = []

        self.new()

        self.bind('<<NotebookTabChanged>>', lambda e: on_tab_change(self.identify(e.x, e.y)))

    def new(self):
        doc = Document(master=self, on_cursor=lambda: None, on_change=lambda: None)
        doc.pack(expand=True, fill=tk.BOTH)
        self.add(doc, text=self.new_document_name)
        self.documents.append(doc)
        # Display the new document (make the tab active by selecting it)
        self.select(self.tabs()[-1])

    def open(self, filename: str, encoding: str = 'utf-8'):
        with open(filename, 'rt', encoding=encoding) as f:
            content = f.read()

            if self.current_document.length > 0:
                self.new()

            self.current_document.content = content

    def save(self):
        # Saves the currently active document
        pass

    @property
    def current_document(self):
        current = self.documents[self.index('current')]
        return current


class Document(tk.Frame):

    def __init__(self, master: tk.Widget, on_cursor: callable, on_change: callable):
        super().__init__(master=master)

        self.filename: str = None

        self._content = tk.Text(
            master=self,
            wrap=tk.WORD if settings.getboolean('word_wrap') else tk.NONE,
        )
        self._content.config(**theme.current()['documentconfig'])
        self._content.pack(expand=True, fill=tk.BOTH)

        with open('/home/will/Documents/cv_case_studies.txt', 'rt') as f:
            self._content.insert(tk.END, f.read())

        self._content.focus()

        BlockSelection(self._content)

    @property
    def name(self) -> Optional[str]:
        if self.filename:
            return Path(self.filename).name

        return None

    @property
    def content(self) -> str:
        return self._content.get(1.0, 'end-1c')

    @content.setter
    def content(self, content: str):
        self._content.insert(tk.END, content)
        self._content.tag_configure('start', background='black', foreground='white')

    @property
    def length(self) -> int:
        return len(self.content)


class BlockSelection:
    """Used to handle block-select (column-select) within a text widget."""

    def __init__(self, text: tk.Text):
        self.text = text
        # These track the starting position of a block selection
        self.start_line = None
        self.start_col = None
        # Whether the control key is pressed
        self.ctrl = False

        # Configure how block select is activated/deactivated
        self.text.bind('<Control-1>', self.ctrl_on)
        self.text.bind('<B1-Motion>', self.mouse_b1_motion)
        self.text.bind('<ButtonRelease-1>', self.mouse_release)
        self.text.bind('<B2-Motion>', self.mouse_motion)
        self.text.bind('<ButtonRelease-2>', self.mouse_release)

    def mouse_b1_motion(self, event):
        if self.ctrl:
            return self.mouse_motion(event)

    def mouse_motion(self, event):
        self.text.tag_remove('sel', '0.0', tk.END)
        cur_line, cur_col = self.index_as_tuple(f'@{event.x},{event.y}')

        if self.start_line is None:
            self.start_line, self.start_col = cur_line, cur_col
        else:
            lines_moved = abs(cur_line - self.start_line)
            cols_moved = abs(cur_col - self.start_col)

            for line_offset in range(lines_moved + 1):
                sel_start = f'{min(self.start_line, cur_line)}.{min(self.start_col, cur_col)}'
                line_start = self.index_as_tuple(f'{sel_start}+{line_offset}l')
                line_end = min(
                    self.index_as_tuple(f'{sel_start}+{line_offset}l lineend'),
                    self.index_as_tuple(f'{sel_start}+{line_offset}l+{cols_moved}c')
                )

                self.text.tag_add('sel', '{}.{}'.format(*line_start), '{}.{}'.format(*line_end))

        return 'break'

    def ctrl_on(self, event):
        self.ctrl = True

    def mouse_release(self, event):
        self.start_line = None
        self.start_col = None
        self.ctrl = False
        return 'break'

    def index_as_tuple(self, index: str) -> Tuple[int, ...]:
        """Take an index in the form '12.23' and convert to a tuple of two integers."""
        return tuple(map(int, self.text.index(index).split('.')))


def create(master: tk.Widget) -> Editor:
    """Convenience function for creating an Editor instance.

    Args:
        master: The parent widget.
    Returns: The Editor instance.
    """
    editor = Editor(master=master, on_tab_change=lambda x: print(x))
    editor.pack(expand=True, fill=tk.BOTH)
    return editor
