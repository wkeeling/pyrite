import logging

from ttkthemes import ThemedTk

from pyrite import settings
from pyrite.ui import editor, menu, theme

log = logging.getLogger(__name__)


class MainWindow(ThemedTk):
    """The outer window of the application that contains everything else."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('1024x768+100+100')

        self.set_theme(theme.current()['ttktheme'])

        settings.on_save(lambda: self.set_theme(theme.current()['ttktheme']))

        ed = editor.create(master=self)
        menu.create(master=self, editor=ed)

    def show(self):
        self.mainloop()


def run():
    main_window = MainWindow()
    main_window.show()
