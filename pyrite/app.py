import logging

from ttkthemes import ThemedTk

from pyrite import editor, menu, settings, state, theme

log = logging.getLogger(__name__)

DEFAULT_GEOMETRY = '1024x768+500+100'


class MainWindow(ThemedTk):
    """The outer window of the application that contains everything else."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry(state.get('geometry', DEFAULT_GEOMETRY))
        self.set_theme(theme.ttktheme)

        settings.on_save(lambda: self.set_theme(theme.ttktheme))

        self.protocol('WM_DELETE_WINDOW', self.on_close)

        ed = editor.create(master=self)
        menu.create(master=self, editor=ed)

    def show(self):
        self.mainloop()

    def on_close(self):
        # Record the current dimensions
        state['geometry'] = self.geometry()
        state.save()

        self.destroy()


def run():
    main_window = MainWindow()
    main_window.show()
