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


class ColumnEditor:
    """Use to handle column editing within a text widget."""

    INSERTION_MARK_PREFIX = 'markinsert'

    def __init__(self, text: tk.Text):
        self.text = text

        # Whether column editing is active
        self.active = False

        # The starting line and column when column editing begins
        self.start_line = None
        # self.start_col = None

        # Whether select mode is active
        # self.select = False

        # Configure key bindings for column editing
        # Hold down Alt-Shift-Arrow to activate
        self.text.bind('<Alt-Shift-Up>', lambda e: self.key_motion(offset='-1l'))
        self.text.bind('<Alt-Shift-Down>', lambda e: self.key_motion(offset='+1l'))
        self.text.bind('<Alt-Shift-Left>', lambda e: self.key_motion(offset='-1c'))
        self.text.bind('<Alt-Shift-Right>', lambda e: self.key_motion(offset='+1c'))
        self.text.bind('<Alt-Shift-Home>', lambda e: self.key_motion(offset='linestart'))
        self.text.bind('<Alt-Shift-End>', lambda e: self.key_motion(offset='lineend'))
        # Disable the class level key bindings which will interfere with our own
        self.text.bind_class('Text', '<Alt-Shift-Up>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Down>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Left>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Right>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Home>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-End>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Next>', lambda e: None)
        self.text.bind_class('Text', '<Alt-Shift-Prior>', lambda e: None)
        # self.text.bind_class('Text', '<Alt-Shift-Up>', lambda e: self.key_motion(offset='-1l'))
        # self.text.bind_class('Text', '<Alt-Shift-Down>', lambda e: self.key_motion(offset='+1l'))
        # self.text.bind_class('Text', '<Alt-Shift-Left>', lambda e: self.key_motion(offset='-1c'))
        # self.text.bind_class('Text', '<Alt-Shift-Right>', lambda e: self.key_motion(offset='+1c'))
        # self.text.bind_class('Text', '<Alt-Shift-Home>', self.key_motion)
        # self.text.bind_class('Text', '<Alt-Shift-End>', self.key_motion)
        # self.text.bind_class('Text', '<Next>', self.key_motion)
        # self.text.bind_class('Text', '<Prior>', self.key_motion)

        # Key bindings for block selection
        # self.text.bind('<Shift-Up>', self.select_on)
        # self.text.bind('<Shift-Down>', self.select_on)
        # self.text.bind('<Shift-Left>', self.select_on)
        # self.text.bind('<Shift-Right>', self.select_on)
        # self.text.bind('<Shift-Home>', self.select_on)
        # self.text.bind('<Shift-End>', self.select_on)
        # self.text.bind('<Shift-Next>', self.select_on)
        # self.text.bind('<Shift-Prior>', self.select_on)
        # self.text.bind('<KeyRelease-Shift_L>', self.select_off)
        # self.text.bind('<KeyRelease-Shift_R>', self.select_off)

        # Key bindings for text modification
        self.text.bind('<Key>', self.insert)
        self.text.bind_class('Text', '<BackSpace>', self.backspace)
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
        self.text.bind('<ButtonRelease-2>', self.deactivate)
        self.text.bind('<ButtonRelease-3>', self.deactivate)
        self.text.bind('<Escape>', self.deactivate)

    def key_motion(self, offset):
        """Respond to a key press that moves the cursor applying the specified offset."""
        if not self.start_line:
            self.start_line = self.index_as_tuple(tk.INSERT)[0]
        self.update(f'{self.text.index(tk.INSERT)} {offset}')

    def update(self, index: str):
        """Update the text widget to display the column highlight.

        Args:
            index: An index in the format 'line.col'
        """
        if not self.active:
            self.active = True
            self.text.config(blockcursor=True)

        # Ensure the cursor is moved to the current index
        self.text.mark_set(tk.INSERT, index)

        # Clear any existing highlight
        self.remove_highlight()

        current_index = self.index_as_tuple(index)
        lines_moved = current_index[0] - self.start_line
        # cols_moved = current_index[1] - self.start_col

        # Block selection is calculated from the top left corner
        # top_left = f'{min(self.start_line, current_index[0])}.{min(self.start_col, current_index[1])}'

        # Highlight the start position if more than one line moved
        if lines_moved:
            self.highlight_index('{}.{}'.format(self.start_line, current_index[1]))

        # Start the column highlight from the lowest line number and work down the page
        highlight_from = min(self.start_line, current_index[0])

        for i in range(abs(lines_moved)):
            index = f'{highlight_from + i}.{current_index[1]}'

            if index != self.text.index(tk.INSERT):
                self.highlight_index(index)

            # if self.select:
            #     # Block selection is implemented by layering multiple single line selections
            #     sel_start = '{}.{}'.format(*self.index_as_tuple(f'{top_left}+{i}l'))
            #     sel_end = '{}.{}'.format(*min(
            #         self.index_as_tuple(f'{top_left}+{i}l lineend'),
            #         self.index_as_tuple(f'{top_left}+{i}l+{abs(cols_moved)}c')
            #     ))
            #
            #     self.text.tag_add(tk.SEL, f'{sel_start}', f'{sel_end}')
            #     self.text.mark_set(tk.INSERT, index)

    # def highlight_column(self, event):
    #     if not self.active:
    #         self.active = True
    #         self.text.config(blockcursor=True)
    #         self.start_line = self.index_as_tuple(tk.INSERT)[0]
    #     self.update(tk.INSERT)

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

    def mouse_motion(self, event):
        # TODO: do we need mouse control for column edit?
        if self.alt or self.active:
            mouse_index = f'@{event.x},{event.y}'
            self.update(mouse_index)

            return 'break'

    # def select_on(self, event):
    #     """Handle text selection."""
    #     if self.alt or self.active:
    #         if not self.select:
    #             self.start_col = self.index_as_tuple(tk.INSERT)[1]
    #             self.select = True
    #
    # def select_off(self, event):
    #     """Handle text deselection."""
    #     self.select = False

    def insert(self, event):
        """Insert the character represented by the event into a highlighted column."""
        if self.active and event.char.isprintable():
            for name in self.highlight_names():
                self.text.insert(name, event.char)

    def backspace(self, event):
        """Delete characters before the cursor's current position."""
        if self.active:
            for name in self.highlight_names():
                index = self.text.index(name)
                self.text.delete(f'{index}-1c', index)
            self.update(self.text.index(tk.INSERT))

    def delete(self, event):
        """Delete characters after the cursor's current position."""
        if self.active:
            for name in self.highlight_names():
                index = self.text.index(name)
                self.text.delete(index, f'{index}+1c')
            self.update(self.text.index(tk.INSERT))

    def deactivate(self, event):
        """Deactivate column editing."""
        if self.active:
            self.active = False
            self.start_line = None
            # self.select = False
            self.remove_highlight()
            self.text.config(blockcursor=False)
            self.text.tag_remove(tk.SEL, '0.0', tk.END)

    def index_as_tuple(self, index: str) -> Tuple[int, ...]:
        """Take an index in the form '12.23' and convert to a tuple of two integers."""
        return tuple(map(int, self.text.index(index).split('.')))


class ColumnEditor2:
    """Use to handle column editing within a text widget."""
    
    HIGHLIGHTPREFIX = 'colhighlight'
    BINDTAG_KEYMOTION = 'keymotion'

    def __init__(self, text: tk.Text):
        self.text = text

        # Whether column editing is active
        self.active = False

        # The starting line and column when column editing begins
        self.start_line = None
        # self.start_col = None

        # Whether the alt key is pressed
        self.alt = False

        # Whether select mode is active
        # self.select = False

        # Configure key bindings for column editing
        # Holding down the left Alt key and pressing an arrow key will activate
        self.text.bind('<Alt_L>', self.alt_on)
        self.text.bind('<KeyRelease-Alt_L>', self.alt_off)
        self.text.bind('<Key>', self.insert)

        # Configure a bindtag after the default class binding. This ensures that
        # the binding will receive the cursor position after the cursor has moved.
        bindtags = []
        for bindtag in self.text.bindtags():
            bindtags.append(bindtag)
            if bindtag == 'Text':
                bindtags.append(self.BINDTAG_KEYMOTION)
        self.text.bindtags(bindtags)

        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Up>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Down>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Left>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Right>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Home>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<End>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Next>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Prior>', self.key_motion)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<BackSpace>', self.backspace)
        self.text.bind_class(self.BINDTAG_KEYMOTION, '<Delete>', self.delete)


        # Key bindings for block selection
        # self.text.bind('<Shift-Up>', self.select_on)
        # self.text.bind('<Shift-Down>', self.select_on)
        # self.text.bind('<Shift-Left>', self.select_on)
        # self.text.bind('<Shift-Right>', self.select_on)
        # self.text.bind('<Shift-Home>', self.select_on)
        # self.text.bind('<Shift-End>', self.select_on)
        # self.text.bind('<Shift-Next>', self.select_on)
        # self.text.bind('<Shift-Prior>', self.select_on)
        # self.text.bind('<KeyRelease-Shift_L>', self.select_off)
        # self.text.bind('<KeyRelease-Shift_R>', self.select_off)

        # Key bindings for deactivating column editing
        self.text.bind('<ButtonRelease-1>', self.disable)
        self.text.bind('<ButtonRelease-2>', self.disable)
        self.text.bind('<ButtonRelease-3>', self.disable)
        self.text.bind('<Escape>', self.disable)
        self.text.bind('<Alt-Shift-Down>', lambda e: print('default alt-shift-down'))

    def update(self, index: str):
        """Update the text widget to display the column highlight.
        
        Args:
            index: An index in the format 'line.col'
        """
        # Clear any existing highlight
        self.remove_highlight()

        current_index = self.index_as_tuple(index)
        lines_moved = current_index[0] - self.start_line
        # cols_moved = current_index[1] - self.start_col

        # Block selection is calculated from the top left corner
        # top_left = f'{min(self.start_line, current_index[0])}.{min(self.start_col, current_index[1])}'

        # Highlight the start position if more than one line moved
        if lines_moved:
            self.highlight_index('{}.{}'.format(self.start_line, current_index[1]))

        # Start the column highlight from the lowest line number and work down the page
        highlight_from = min(self.start_line, current_index[0])

        for i in range(abs(lines_moved)):
            index = f'{highlight_from + i}.{current_index[1]}'

            if index != self.text.index(tk.INSERT):
                self.highlight_index(index)
                print(f'highlighting index {index}')

            # if self.select:
            #     # Block selection is implemented by layering multiple single line selections
            #     sel_start = '{}.{}'.format(*self.index_as_tuple(f'{top_left}+{i}l'))
            #     sel_end = '{}.{}'.format(*min(
            #         self.index_as_tuple(f'{top_left}+{i}l lineend'),
            #         self.index_as_tuple(f'{top_left}+{i}l+{abs(cols_moved)}c')
            #     ))
            #
            #     self.text.tag_add(tk.SEL, f'{sel_start}', f'{sel_end}')
            #     self.text.mark_set(tk.INSERT, index)

    # def highlight_column(self, event):
    #     if not self.active:
    #         self.active = True
    #         self.text.config(blockcursor=True)
    #         self.start_line = self.index_as_tuple(tk.INSERT)[0]
    #     self.update(tk.INSERT)

    def highlight_index(self, index: str):
        """Highlight the specified index."""
        name = f'{self.HIGHLIGHTPREFIX}_{index}'
        self.text.tag_add(name, index)
        self.text.mark_set(name, index)
        self.text.tag_config(
            name,
            background=theme.current()['documentconfig']['insertbackground'],
        )

    def remove_highlight(self):
        """Remove the column highlight."""
        for name in self.text.mark_names():
            if name.startswith(self.HIGHLIGHTPREFIX):
                self.text.tag_remove(name, '0.0', tk.END)
                self.text.mark_unset(name)

    def highlight_names(self):
        """Return an iterator of current highlight names."""
        for name in self.text.mark_names():
            if name.startswith(self.HIGHLIGHTPREFIX):
                yield name

    def mouse_motion(self, event):
        # TODO: do we need mouse control for column edit?
        if self.alt or self.active:
            mouse_index = f'@{event.x},{event.y}'
            self.update(mouse_index)

            return 'break'

    def key_motion(self, event):
        """Respond to a key press that moves the cursor."""
        if self.alt or self.active:
            self.active = True
            self.text.config(blockcursor=True)
            self.update(tk.INSERT)

    # def select_on(self, event):
    #     """Handle text selection."""
    #     if self.alt or self.active:
    #         if not self.select:
    #             self.start_col = self.index_as_tuple(tk.INSERT)[1]
    #             self.select = True
    #
    # def select_off(self, event):
    #     """Handle text deselection."""
    #     self.select = False

    def insert(self, event):
        """Insert the character represented by the event into a highlighted column."""
        if self.active and event.char.isprintable():
            for name in self.highlight_names():
                self.text.insert(name, event.char)

    def backspace(self, event):
        """Delete characters before the cursor's current position."""
        if self.active:
            for name in self.highlight_names():
                index = self.text.index(name)
                self.text.delete(f'{index}-1c', index)
            self.update(self.text.index(tk.INSERT))

    def delete(self, event):
        """Delete characters after the cursor's current position."""
        if self.active:
            for name in self.highlight_names():
                index = self.text.index(name)
                self.text.delete(index, f'{index}+1c')
            self.update(self.text.index(tk.INSERT))

    def alt_on(self, event):
        """Handle alt key press."""
        self.alt = True
        print('alt on')
        if not self.active:
            self.start_line = self.index_as_tuple(tk.INSERT)[0]

    def alt_off(self, event):
        """Handle alt key release."""
        print('alt off')
        self.alt = False

    def disable(self, event):
        """Disable the current column editing session."""
        self.active = False
        self.alt = False
        # self.select = False
        self.remove_highlight()
        self.text.config(blockcursor=False)
        self.text.tag_remove(tk.SEL, '0.0', tk.END)

    def index_as_tuple(self, index: str) -> Tuple[int, ...]:
        """Take an index in the form '12.23' and convert to a tuple of two integers."""
        return tuple(map(int, self.text.index(index).split('.')))


class BlockSelection:
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

        # Find the distance between the cursor and the start point
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
