from tkinter import ttk


class Document(ttk.Frame):

    filename = 'Untitled_{}'
    index = 1

    def __init__(self, master):
        super().__init__(master=master)

        self.filename = self.filename.format(self.index)
        Document.index += 1

    def read(self, filename: str):
        pass

    def write(self):
        pass


class Editor(ttk.Notebook):

    def __init__(self, master):
        super().__init__(master=master)

    def new_document(self):
        pass

    def open_document(self, filename: str):
        pass
