import logging
import platform
import tkinter as tk

from ttkthemes import ThemedTk

from pyrite import settings
from pyrite.ui import theme
from pyrite.ui.editor import Editor


log = logging.getLogger(__name__)


class MainWindow(ThemedTk):
    """The outer window of the application that contains everything else."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if platform == 'Windows':
            self.attributes('-fullscreen', True)
        else:
            self.attributes('-zoomed', True)

        self.set_theme(theme.current()['ttktheme'])

        settings.on_save(lambda: self.set_theme(theme.current()['ttktheme']))

        self._createmenus()

        self.editor = Editor(master=self, on_tab_change=lambda x: print(x))

    def show(self):
        self.mainloop()

    def _createmenus(self):
        menubar = tk.Menu(master=self)
        menubar.config(**theme.current()['menuconfig'])

        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.config(**theme.current()['menuconfig'])
        filemenu.add_command(label='New...', underline=0, command=self.destroy)
        filemenu.add_command(label='Open...', underline=0, command=self.destroy)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', underline=1, command=self.destroy)

        menubar.add_cascade(label='File', menu=filemenu)

        self.config(menu=menubar)


class FileMenu(tk.Menu):

    def __init__(self, menubar: tk.Menu):
        super().__init__(master=menubar, tearoff=False)


def run():
    main_window = MainWindow()
    main_window.show()
