import tkinter as tk

from pyrite import settings


dark = {
    'ttktheme': 'equilux',
    'menuconfig': {
        'relief': tk.FLAT,
        'activeborderwidth': 0,
        'fg': '#a6a6a6',
        'bg': '#464646',
        'activebackground': '#2367ce',
        'activeforeground': '#a6a6a6',
    },
    'documentconfig': {
        'relief': tk.FLAT,
        'borderwidth': 2,
        'bg': '#2b2b2b',
        'fg': '#a6a6a6',
    }
}

light = {
    'ttktheme': 'arc',
    'menuconfig': {
        'relief': tk.FLAT,
        'activeborderwidth': 0,
        'fg': '#a6a6a6',
        'bg': '#464646',
        'activebackground': '#2367ce',
        'activeforeground': '#a6a6a6',
    }
}


def current() -> dict:
    """Get the current theme based on the user's settings."""
    return globals().get(settings['theme'], dark)
