"""This module acts as the entry point for running the application."""

from tkinter import ttk
from ttkthemes import ThemedTk


def main():
    root = ThemedTk(theme='equilux')
    label = ttk.Label(master=root, text='Hello')
    label.pack()
    ttk.Button(root, text="Quit", command=root.destroy).pack()

    root.mainloop()


if __name__ == '__main__':
    main()
