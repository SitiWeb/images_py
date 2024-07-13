from tkinter import Toplevel, Text

class LogWindow(Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Log Window")
        self.geometry("500x300")
        self.text = Text(self)
        self.text.pack(expand=True, fill='both')
        self.protocol("WM_DELETE_WINDOW", self.hide)

    def log(self, message):
        self.text.insert('end', message + '\n')
        self.text.see('end')

    def hide(self):
        self.withdraw()
