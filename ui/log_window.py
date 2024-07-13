import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class LogWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Processing Log")
        self.geometry("600x400")
        self.log_text = ScrolledText(self, state='disabled', wrap='word')
        self.log_text.pack(expand=True, fill='both')

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
