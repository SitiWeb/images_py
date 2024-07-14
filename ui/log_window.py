import customtkinter as ctk

class LogWindow:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(expand=True, fill="both")

        self.log_text = ctk.CTkTextbox(self.frame, state="disabled", wrap="word", height=10)
        self.log_text.pack(side="left", expand=True, fill="both")

        self.scrollbar = ctk.CTkScrollbar(self.frame, command=self.log_text.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.log_text.configure(yscrollcommand=self.scrollbar.set)

    def log_message(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(ctk.END, message + "\n")
        self.log_text.see(ctk.END)
        self.log_text.configure(state="disabled")
        self.log_text.update_idletasks()

    def clear(self):
        self.log_text.configure(state="normal")
        self.log_text.delete('1.0', ctk.END)
        self.log_text.configure(state="disabled")

# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    log_window = LogWindow(root)

    # Example log messages
    log_window.log_message("This is a test message.")
    log_window.log_message("Another test message.")

    root.mainloop()
