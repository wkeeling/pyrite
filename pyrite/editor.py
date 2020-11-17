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

        # EnableBlockSelection(self._content)
        ColumnEdit(self._content)

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


class ColumnEdit:
    """Use to handle column editing within a text widget."""

    def __init__(self, text: tk.Text):
        self.text = text
        self.enabled = False

        # The starting line of a column selection
        self.start_line = None

        # Whether the alt key is pressed
        self.alt = False

        # TODO: externalise these to configure_column_edit()
        self.text.bind('<Alt_L>', self.alt_on)
        self.text.bind('<KeyRelease-Alt_L>', self.alt_off)
        self.text.bind('<Up>', self.up)
        self.text.bind('<Down>', self.down)
        self.text.bind('<Left>', self.left)
        self.text.bind('<Right>', self.right)
        self.text.bind('<KeyRelease-Up>', self.up_)
        self.text.bind('<KeyRelease-Down>', self.down_)
        self.text.bind('<KeyRelease-Left>', self.left_)
        self.text.bind('<KeyRelease-Right>', self.right_)
        self.text.bind('<ButtonRelease>', self.disable)
        self.text.bind('<Escape>', self.disable)

    def mouse_motion(self, event):
        if self.alt or self.start_index:
            mouse_index = f'@{event.x},{event.y}'
            self.update(mouse_index)

            return 'break'

    def up(self, event):
        index = '{}-1l'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def down(self, event):
        index = '{}+1l'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def left(self, event):
        index = '{}-1c'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def right(self, event):
        index = '{}+1c'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def up_(self, event):
        index = '{}'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def down_(self, event):
        index = '{}'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def left_(self, event):
        index = '{}'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def right_(self, event):
        index = '{}'.format(tk.INSERT)
        return self.arrowkey_motion(index)

    def arrowkey_motion(self, index):
        if self.alt or self.enabled:
            self.enabled = True
            self.text.config(blockcursor=True)
            self.update(index)

    def update(self, index):
        # Configure the column highlight
        self.text.tag_remove('colhighlight', '0.0', tk.END)
        self.text.mark_unset('colhighlight')
        self.text.tag_config(
            'colhighlight',
            background=theme.current()['documentconfig']['insertbackground'],
            bgstipple='gray25'
        )

        current_index = self.index_as_tuple(index)
        lines_moved = current_index[0] - self.start_line

        # We start at the lowest line number and highlight down the page
        start_from = min(self.start_line, current_index[0])

        for i in range(abs(lines_moved)):
            # Don't try and highlight beyond the end of a line
            index = '{}.{}'.format(*min(
                self.index_as_tuple(f'{start_from + i}.{current_index[1]}'),
                self.index_as_tuple(f'{start_from + i}.{current_index[1]} lineend'),
            ))

            self.text.tag_add('colhighlight', index)
            self.text.mark_set('colhighlight', index)

    def alt_on(self, event):
        self.alt = True
        self.start_line = self.index_as_tuple(tk.INSERT)[0]

    def alt_off(self, event):
        self.alt = False

    def disable(self, event):
        self.enabled = False
        self.alt = False
        self.text.mark_unset('colhighlight')
        self.text.tag_delete('colhighlight')
        self.text.config(blockcursor=False)

    def index_as_tuple(self, index: str) -> Tuple[int, ...]:
        """Take an index in the form '12.23' and convert to a tuple of two integers."""
        return tuple(map(int, self.text.index(index).split('.')))


class ConfigureBlockSelection:
    """Used to handle block-select (column-select) within a text widget."""

    def __init__(self, text: tk.Text):
        self.text = text

        # These track the starting position of a block selection
        self.start_line = 0
        self.start_col = 0

        # Whether the control key is pressed
        self.ctrl = False

        # Whether the alt key is pressed
        self.alt = False

        # Configure how block select is activated/deactivated
        # Mouse control
        self.text.bind('<Control-1>', self.ctrl_on)
        self.text.bind('<B1-Motion>', self.mouse_b1_motion)
        self.text.bind('<ButtonRelease-1>', self.mouse_release)
        self.text.bind('<B2-Motion>', self.mouse_motion)
        self.text.bind('<ButtonRelease-2>', self.mouse_release)
        # Keyboard control
        self.text.bind('<Alt_L>', self.alt_on)
        self.text.bind('<KeyRelease-Alt_L>', self.alt_off)
        self.text.bind('<Left>', self.arrowkey_motion)
        self.text.bind('<KeyRelease-Left>', self.arrowkey_motion)
        self.text.bind('<KeyRelease-Right>', self.arrowkey_motion)
        self.text.bind('<KeyRelease-Up>', self.arrowkey_motion)
        self.text.bind('<KeyRelease-Down>', self.arrowkey_motion)

        self.text.bind('sel', )

    def mouse_b1_motion(self, event):
        if self.ctrl:
            return self.mouse_motion(event)

    def mouse_motion(self, event):
        mouse_index = f'@{event.x},{event.y}'

        if not self.start_line and not self.start_col:
            self.start_line, self.start_col = self.index_as_tuple(mouse_index)

        self.update_selection(mouse_index)

        return 'break'

    def arrowkey_motion(self, event):
        if self.alt:
            self.update_selection(tk.INSERT)

    def update_selection(self, index):
        # Clear any previous selection
        self.text.tag_remove(tk.SEL, '0.0', tk.END)

        # Get the current index of the mouse/insertion cursor
        cur_line, cur_col = self.index_as_tuple(index)

        # Find the distance between the mouse/insertion cursor and the start point
        lines_moved = abs(cur_line - self.start_line)
        cols_moved = abs(cur_col - self.start_col)

        # The block selection is calculated from the top left corner
        top_left = f'{min(self.start_line, cur_line)}.{min(self.start_col, cur_col)}'

        for line_offset in range(lines_moved + 1):  # +1 to allow the last line to be selected

            # The block selection is implemented by layering multiple single line selections
            sel_start = '{}.{}'.format(*self.index_as_tuple(f'{top_left}+{line_offset}l'))
            sel_end = '{}.{}'.format(*min(
                self.index_as_tuple(f'{top_left}+{line_offset}l lineend'),
                self.index_as_tuple(f'{top_left}+{line_offset}l+{cols_moved}c')
            ))

            print(tk.SEL, f'{sel_start}', f'{sel_end}')

            self.text.tag_add(tk.SEL, f'{sel_start}', f'{sel_end}')
            self.text.mark_set(tk.INSERT, index)

    def ctrl_on(self, event):
        self.ctrl = True

    def alt_on(self, event):
        self.alt = True
        self.start_line, self.start_col = self.index_as_tuple(tk.INSERT)

    def alt_off(self, event):
        self.alt = False
        self.start_line = None
        self.start_col = None

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
