import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import NamedTuple

from pyrite import keybindings, settings, theme


class Editor(ttk.Notebook):
    """Responsible for managing a collection of Documents in a tabbed view."""

    def __init__(self, master: tk.Tk, on_tab_change: callable):
        """Create a new Editor instance.

        Args:
            master: The parent widget.
            on_tab_change: Callable that gets invoked when the current tab is changed.
                The callable will be passed the Document instance associated with the
                tab.
        """
        super().__init__(master=master)

        self.documents = []

        self.new()

        self.bind('<<NotebookTabChanged>>', lambda e: on_tab_change(self.current_document))
        self.bind(keybindings.CLOSE_TAB_MOUSE, lambda e: self.close_tab(f'@{e.x},{e.y}'))

    def new(self):
        """Create a new document in the editor."""
        doc = Document(master=self, on_cursor=lambda: None, on_change=lambda: None)
        doc.pack(expand=True, fill=tk.BOTH)
        self.add(doc, text=doc.name)
        self.documents.append(doc)
        # Display the new document (make the tab active by selecting it)
        self.select(self.tabs()[-1])

    def open(self, filename: str, encoding: str = 'utf-8'):
        """Open a document into the editor from a file.

        Args:
            filename: The filename of the document to open.
            encoding: The character encoding of the document.
        """
        self.new()
        self.current_document.load(filename, encoding)
        self.tab('current', text=self.current_document.name)

    def save(self, filename: str = None, encoding: str = 'utf-8'):
        """Save the current document."""
        self.current_document.save(filename, encoding)
        self.tab('current', text=self.current_document.name)

    @property
    def current_document(self):
        current = self.documents[self.index('current')]
        return current

    def close_tab(self, tab_id):
        if tab_id:
            self.documents.pop(self.index(tab_id))
            self.forget(tab_id)


class Document(tk.Frame):

    defaultname = 'Untitled'

    filename: str = None

    encoding: str = 'UTF-8'

    def __init__(self, master: tk.Widget, on_cursor: callable, on_change: callable):
        super().__init__(master=master)

        self.text = tk.Text(
            master=self,
            wrap=tk.WORD if settings.getboolean('word_wrap') else tk.NONE,
            undo=True,
        )
        self.text.config(**theme.textconfig)
        self.text.pack(expand=True, fill=tk.BOTH)

        self.text.focus()

        # Enable column editing
        ColumnEditor(self.text)

    @property
    def name(self) -> str:
        if self.filename:
            return Path(self.filename).name

        return self.defaultname

    def load(self, filename: str = None, encoding: str = 'UTF-8'):
        """Load this document's content disk.

        Args:
            filename: The name of the file.
            encoding: The file encoding.
        """
        with open(filename, 'rt', encoding=encoding) as f:
            content = f.read()

            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, content)

            self.filename = filename

    def save(self, filename: str = None, encoding: str = 'UTF-8'):
        """Save this document to a file.

        Args:
            filename: The filename to save the document to. This can be omitted
                if the document already has a filename associated with it.
            encoding: The file encoding to use.
        """
        if filename is None and self.filename is None:
            raise RuntimeError('No filename set')

        if filename is not None:
            self.filename = filename

        with open(self.filename, 'wt', encoding=encoding) as f:
            f.write(self.text.get('1.0', tk.END + '-1c'))


class Index(NamedTuple):
    line: int
    char: int


class ColumnEditor:
    """Use to handle column editing within a text widget."""

    INSERTION_MARK_PREFIX = 'markinsert'

    def __init__(self, text: tk.Text):
        # The text widget we're acting on
        self.text = text

        # Whether column editing is active
        self.active = False

        # The starting line and column when column editing begins
        self.start_line = None
        self.start_char = None

        # Key bindings for activating column editing
        self.text.bind(keybindings.COLUMN_EDIT_UP, lambda e: self.key_motion(offset='-1l'))  # noqa
        self.text.bind(keybindings.COLUMN_EDIT_DOWN, lambda e: self.key_motion(offset='+1l'))
        self.text.bind(keybindings.COLUMN_EDIT_LEFT, lambda e: self.key_motion(offset='-1c'))
        self.text.bind(keybindings.COLUMN_EDIT_RIGHT, lambda e: self.key_motion(offset='+1c'))
        self.text.bind(keybindings.COLUMN_EDIT_HOME, lambda e: self.key_motion(offset='display linestart'))
        self.text.bind(keybindings.COLUMN_EDIT_END, lambda e: self.key_motion(offset='display lineend'))
        self.text.bind(keybindings.COLUMN_EDIT_DOC_HOME, lambda e: self.key_motion(
            offset=f'-{self.index_as_tuple(tk.INSERT)[0]}l'
        ))
        self.text.bind(keybindings.COLUMN_EDIT_DOC_END, lambda e: self.key_motion(
            offset=f'+{self.index_as_tuple(tk.END)[0] - self.index_as_tuple(tk.INSERT)[0] - 1}l'
        ))
        self.text.bind(keybindings.COLUMN_EDIT_DRAG, self.mouse_motion)

        # Disable the class level key bindings which will otherwise interfere
        # with our own.
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_UP, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_DOWN, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_LEFT, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_RIGHT, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_HOME, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_END, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_NEXT, lambda e: None)
        self.text.bind_class('Text', keybindings.COLUMN_EDIT_PRIOR, lambda e: None)

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
        """Move the cursor by the specified offset.

        The offset is in index form, e.g. +1c
        """
        if not self.start_line:
            self.start_line, self.start_char = self.index_as_tuple(tk.INSERT)
        self.update(f'{self.text.index(tk.INSERT)} {offset}')

    def mouse_motion(self, event):
        """Respond to a mouse drag event."""
        mouse_index = f'@{event.x},{event.y}'
        if not self.start_line:
            self.start_line, self.start_char = self.index_as_tuple(mouse_index)
        self.update(mouse_index)

        return 'break'

    def update(self, index: str):
        """Update the text widget to display the column highlight and
        block selection.

        Args:
            index: An index in the format 'line.char'
        """
        if not self.active:
            self.active = True

        # Clear any existing highlight and selection
        self.remove_highlight()
        self.text.tag_remove(tk.SEL, '0.0', tk.END)

        # Ensure the cursor is moved to the current index
        self.text.mark_set(tk.INSERT, index)

        current_index = self.index_as_tuple(index)
        lines_moved = current_index.line - self.start_line
        chars_moved = current_index.char - self.start_char

        # Add selection for the current row
        args = f'{current_index.line}.{self.start_char}', tk.INSERT
        if chars_moved < 0:
            args = reversed(args)

        self.text.tag_add(tk.SEL, *args)

        for i in range(abs(lines_moved)):
            if lines_moved < 0:
                i = i * -1  # Moving up the page

            index = f'{self.start_line + i}.{current_index.char}'

            # Add the column highlight
            self.highlight_index(index)

            # Block selection is implemented by layering multiple single line selections
            args = f'{self.start_line + i}.{self.start_char}', index
            if chars_moved < 0:
                args = reversed(args)

            self.text.tag_add(tk.SEL, *args)

    def highlight_index(self, index: str):
        """Highlight the specified index."""
        name = f'{self.INSERTION_MARK_PREFIX}_{index}'
        self.text.tag_add(name, index)
        self.text.mark_set(name, index)
        self.text.tag_config(
            name,
            background=theme.textconfig['insertbackground'],
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
        """Insert the character represented by the event into a
        highlighted column."""
        if self.active and event.char:
            self.delete_selected_chars()

            for name in self.highlight_names():
                self.text.insert(name, event.char)

            self.text.insert(tk.INSERT, event.char)
            # Reset the starting position
            self.start_char = self.index_as_tuple(tk.INSERT).char
            self.update(self.text.index(f'{tk.INSERT}'))

            return 'break'

    def backspace(self, event):
        """Delete characters before the cursor's current position
        from a highlighted column.
        """
        if self.active:
            if not self.delete_selected_chars():
                for name in self.highlight_names():
                    index = self.text.index(name)
                    self.text.delete(f'{index}-1c', index)

                self.text.delete(f'{tk.INSERT}-1c', tk.INSERT)

            # Reset the starting position
            self.start_char = self.index_as_tuple(tk.INSERT).char
            self.update(self.text.index(f'{tk.INSERT}'))

            return 'break'

    def delete(self, event):
        """Delete characters after the cursor's current position
        from a highlighted column.
        """
        if self.active:
            if not self.delete_selected_chars():
                for name in self.highlight_names():
                    index = self.text.index(name)
                    self.text.delete(index, f'{index}+1c')

                self.text.delete(tk.INSERT, f'{tk.INSERT}+1c')

            # Reset the starting position
            self.start_char = self.index_as_tuple(tk.INSERT).char
            self.update(self.text.index(f'{tk.INSERT}'))

            return 'break'

    def delete_selected_chars(self) -> bool:
        """Delete characters that are currently selected from a
        highighted column.

        Returns: True if selected characters were deleted, False otherwise.
        """
        if self.text.tag_ranges(tk.SEL):
            start_sel = self.index_as_tuple(tk.SEL_FIRST)
            end_sel = self.index_as_tuple(tk.SEL_LAST)

            for line in range(start_sel.line, end_sel.line + 1):
                self.text.delete(f'{line}.{start_sel.char}', f'{line}.{end_sel.char}')

            return True

        return False

    def deactivate(self, event):
        """Deactivate column editing."""
        if self.active:
            self.active = False
            self.start_line = None
            self.start_char = None
            self.remove_highlight()
            self.text.tag_remove(tk.SEL, '0.0', tk.END)
            return 'break'

    def index_as_tuple(self, index: str) -> Index:
        """Take an index in the form '12.23' and convert to a tuple of two integers."""
        return Index(*map(int, self.text.index(index).split('.')))


def create(master: tk.Tk) -> Editor:
    """Convenience function for creating an Editor instance.

    Args:
        master: The parent top level window.
    Returns: The Editor instance.
    """
    def build_title(document):
        parts = [
            document.name,
        ]

        if document.filename:
            parts.append('-')
            parts.append(f'{document.filename}')

        parts.append('-')
        parts.append('pyrite')

        master.title(' '.join(parts))

    editor = Editor(master=master, on_tab_change=build_title)
    editor.pack(expand=True, fill=tk.BOTH)
    return editor
