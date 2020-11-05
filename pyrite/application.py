import logging
from tkinter import ttk

from ttkthemes import ThemedTk

from pyrite import settings

log = logging.getLogger(__name__)

THEMES = dict(
    dark='equilux',
    light='arc',
)


def run():
    root = ThemedTk(theme=settings['theme'])
    settings.on_save(lambda v: root.set_theme(THEMES[v]))
    label = ttk.Label(master=root, text='Hello')
    label.pack()
    ttk.Button(root, text="Quit", command=root.destroy).pack()

    root.mainloop()
