import tkinter as tk

from pyrite import settings


dark = {
    'ttktheme': 'equilux',
    'menuconfig': {
        'relief': tk.FLAT,
        'activeborderwidth': 0,
        'fg': '#a6a6a6',
        'bg': '#464646',
        'activebackground': '#1762d3',
        'activeforeground': '#a6a6a6',
    }
}

light = {
    'ttktheme': 'arc',
    'menuconfig': {
        'relief': tk.FLAT,
        'activeborderwidth': 0,
        'fg': '#a6a6a6',
        'bg': '#464646',
        'activebackground': '#1762d3',
        'activeforeground': '#a6a6a6',
    }
}


def current() -> dict:
    """Get the current theme based on the user's settings."""
    return globals().get(settings['theme'], dark)
