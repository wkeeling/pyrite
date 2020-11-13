import tkinter as tk

from pyrite import settings

dark = {
    'ttktheme': 'equilux',
    'menuconfig': {
        'relief': tk.FLAT,
        'activeborderwidth': 0,
        'fg': '#a6a6a6',
        'bg': '#464646',
        'activeforeground': '#a6a6a6',
        'activebackground': '#2367ce',
    },
    'documentconfig': {
        'relief': tk.FLAT,
        'borderwidth': 2,
        'fg': '#a6a6a6',
        'bg': '#2b2b2b',
        'selectforeground': '#a6a6a6',
        'selectbackground': '#1a4991',
    }
}

light = {
    'ttktheme': 'arc',
    'menuconfig': {
        'relief': tk.FLAT,
        'activeborderwidth': 0,
    }
}


def current() -> dict:
    """Get the current theme based on the user's settings."""
    return globals().get(settings['theme'], dark)
