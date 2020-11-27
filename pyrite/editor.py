import tkinter as tk
from collections import namedtuple
from pathlib import Path
from tkinter import ttk
from typing import NamedTuple, Optional, Tuple

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

        self.text = tk.Text(
            master=self,
            wrap=tk.WORD if settings.getboolean('word_wrap') else tk.NONE,
        )
        self.text.config(**theme.current()['documentconfig'])
        self.text.pack(expand=True, fill=tk.BOTH)

        with open('/home/will/Documents/cv_case_studies.txt', 'rt') as f:
            self.text.insert(tk.END, f.read())

        self.text.focus()

        # Enable column editing
        ColumnEditor(self.text)

    @property
    def name(self) -> Optional[str]:
        if self.filename:
            return Path(self.filename).name

        return None

    @property
    def content(self) -> str:
        return self.text.get(1.0, 'end-1c')

    @content.setter
    def content(self, content: str):
        self.text.insert(tk.END, content)
        self.text.tag_configure('start', background='black', foreground='white')

    @property
    def length(self) -> int:
        return len(self.content)


class Index(NamedTuple):
    line: int
    col: int


class ColumnEditor:
    """Use to handle column editing within a text widget."""

    INSERTION_MARK_PREFIX = 'markinsert'

    def __init__(self, text: tk.Text):
        self.text = text

        # Whether column editing is active
        self.active = False

        # The starting line and column when column editing begins
        self.start_line = None
        self.start_col = None

        # Key bindings for activating column editing
        # Hold down Alt-Shift-Arrow to activate, or Alt-Button-3 with the mouse
        self.text.bind('<Alt-Shift-Up>', lambda e: self.key_motion(offset='-1l'))
        self.text.bind('<Alt-Shift-Down>', lambda e: self.key_motion(offset='+1l'))
        self.text.bind('<Alt-Shift-Left>', lambda e: self.key_motion(offset='-1c'))
        self.text.bind('<Alt-Shift-Right>', lambda e: self.key_motion(offset='+1c'))
        self.text.bind('<Alt-Shift-Home>', lambda e: self.key_motion(offset='linestart'))
        self.text.bind('<Alt-Shift-End>', lambda e: self.key_motion(offset='lineend'))
        self.text.bind('<Alt-Shift-B3-Motion>', self.mouse_motion)

        # Disable the class level key bindings which will interfere with our own
        self.text.bind_class('Text', '<Alt-Shift-Up>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Down>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Left>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Right>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Home>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-End>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Next>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Prior>', lambda e: None)

        # Key bindings for text modification
        self.text.bind('<Key>', self.insert)
        self.text.bind('<BackSpace>', self.backspace)
        self.text.bind('<Delete>', self.delete)

        # Key bindings for deactivating column editing
        self.text.bind('<Up>', self.deactivate)
        self.text.bind('<Down>', self.deactivate)
        self.text.bind('<Left>', self.deactivate)
        self.text.bind('<Right>', self.deactivate)
        self.text.bind('<Home>', self.deactivate)
        self.text.bind('<End>', self.deactivate)
        self.text.bind('<Next>', self.deactivate)
        self.text.bind('<Prior>', self.deactivate)
        self.text.bind('<ButtonRelease-1>', self.deactivate)
        self.text.bind('<Escape>', self.deactivate)

    def key_motion(self, offset):
        """Respond to a key press that moves the cursor with the requested offset."""
        if not self.start_line:
            self.start_line, self.start_col = self.index_as_tuple(tk.INSERT)
        self.update(f'{self.text.index(tk.INSERT)} {offset}')

    def mouse_motion(self, event):
        """Respond to a mouse drag event."""
        mouse_index = f'@{event.x},{event.y}'
        if not self.start_line:
            self.start_line, self.start_col = self.index_as_tuple(mouse_index)
        self.update(mouse_index)

        return 'break'

    def update(self, index: str):
        """Update the text widget to display the column highlight.

        Args:
            index: An index in the format 'line.col'
        """
        if not self.active:
            self.active = True

        # Ensure the cursor is moved to the current index
        self.text.mark_set(tk.INSERT, index)

        # Clear any existing highlight and selection
        self.remove_highlight()
        self.text.tag_remove(tk.SEL, '0.0', tk.END)

        current_index = self.index_as_tuple(index)
        lines_moved = current_index.line - self.start_line
        cols_moved = current_index.col - self.start_col

        # Add selection for the current row
        args = f'{current_index.line}.{self.start_col}', tk.INSERT
        if cols_moved < 0:
            args = reversed(args)

        self.text.tag_add(tk.SEL, *args)

        for i in range(abs(lines_moved)):
            if lines_moved < 0:
                i = i * -1  # Moving up the page

            index = f'{self.start_line + i}.{current_index.col}'

            # Add the column highlight
            self.highlight_index(index)

            # Block selection is implemented by layering multiple single line selections
            args = f'{self.start_line + i}.{self.start_col}', index
            if cols_moved < 0:
                args = reversed(args)

            self.text.tag_add(tk.SEL, *args)

    def highlight_index(self, index: str):
        """Highlight the specified index."""
        name = f'{self.INSERTION_MARK_PREFIX}_{index}'
        self.text.tag_add(name, index)
        self.text.mark_set(name, index)
        self.text.tag_config(
            name,
            background=theme.current()['documentconfig']['insertbackground'],
        )

    def remove_highlight(self):
        """Remove the column highlight."""
        for name in self.text.mark_names():
            if name.startswith(self.INSERTION_MARK_PREFIX):
                self.text.tag_remove(name, '0.0', tk.END)
                self.text.mark_unset(name)

    def highlight_names(self):
        """Return an iterator of current highlight names."""
        for name in self.text.mark_names():
            if name.startswith(self.INSERTION_MARK_PREFIX):
                yield name

    def insert(self, event):
        """Insert the character represented by the event into a highlighted column."""
        if self.active and event.char:
            self.delete_selected_chars()
            for name in self.highlight_names():
                self.text.insert(name, event.char)
            self.start_col = self.index_as_tuple(tk.INSERT).col

    def backspace(self, event):
        """Delete characters before the cursor's current position."""
        if self.active:
            self.delete_selected_chars()
            for name in self.highlight_names():
                index = self.text.index(name)
                self.text.delete(f'{index}-1c', index)

            self.text.delete(f'{tk.INSERT}-1c', tk.INSERT)
            self.start_col = self.index_as_tuple(tk.INSERT).col
            self.update(self.text.index(f'{tk.INSERT}'))

            return 'break'

    def delete(self, event):
        """Delete characters after the cursor's current position."""
        if self.active:
            if self.delete_selected_chars():
                return 'break'

            for name in self.highlight_names():
                index = self.text.index(name)
                self.text.delete(index, f'{index}+1c')
            self.update(self.text.index(tk.INSERT))

    def delete_selected_chars(self) -> bool:
        """Delete characters that are currently selected.

        Returns: True if selected characters were deleted, False otherwise.
        """
        if self.text.tag_ranges(tk.SEL):
            start_sel = self.index_as_tuple(tk.SEL_FIRST)
            end_sel = self.index_as_tuple(tk.SEL_LAST)

            for line in range(start_sel.line, end_sel.line + 1):
                self.text.delete(f'{line}.{start_sel.col}', f'{line}.{end_sel.col}')

            return True

        return False

    def deactivate(self, event):
        """Deactivate column editing."""
        if self.active:
            self.active = False
            self.start_line = None
            self.remove_highlight()
            self.text.tag_remove(tk.SEL, '0.0', tk.END)
            return 'break'

    def index_as_tuple(self, index: str) -> Index:
        """Take an index in the form '12.23' and convert to a tuple of two integers."""
        return Index(*map(int, self.text.index(index).split('.')))


def create(master: tk.Widget) -> Editor:
    """Convenience function for creating an Editor instance.

    Args:
        master: The parent widget.
    Returns: The Editor instance.
    """
    editor = Editor(master=master, on_tab_change=lambda x: print(x))
    editor.pack(expand=True, fill=tk.BOTH)
    return editor
