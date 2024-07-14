from tkinter import Toplevel, Text
from pprint import pprint

class LogWindow(Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Log Window")
        self.geometry("500x300")
        self.text = Text(self)
        self.text.pack(expand=True, fill="both")
        self.protocol("WM_DELETE_WINDOW", self.hide)

    def log(self, message):
        self.text.insert("end", pprint(message) + "\n")
        self.text.see("end")

    def hide(self):
        self.withdraw()
