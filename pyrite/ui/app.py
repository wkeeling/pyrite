import logging
import platform

from ttkthemes import ThemedTk

from pyrite import settings
from pyrite.ui import editor, menu, theme


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

        ed = editor.create(master=self)
        menu.create(master=self, editor=ed)

    def show(self):
        self.mainloop()


def run():
    main_window = MainWindow()
    main_window.show()
