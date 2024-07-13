import tkinter as tk
from tkinter import ttk
from ui.log_window import LogWindow
from ui.local_processing_tab import LocalProcessingTab
from ui.settings_tab import SettingsTab
from config.decrypt_config import ConfigDecryptor, key

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("700x400")
        
        self.tab_parent = ttk.Notebook(self.root)
        self.log_window = None

        self.local_processing_tab = LocalProcessingTab(self.tab_parent, "Local Processing", self.open_log_window)
        self.settings_tab = SettingsTab(self.tab_parent, "Settings")

        self.tab_parent.pack(expand=True, fill='both')

    def open_log_window(self):
        if self.log_window is None or not self.log_window.winfo_exists():
            self.log_window = LogWindow(self.root)
        else:
            self.log_window.lift()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        decryptor = ConfigDecryptor(key)
        config = decryptor.decrypt()
        wc_url = config['url']
        wc_consumer_key = config['consumer_key']
        wc_consumer_secret = config['consumer_secret']
        wp_username = config['username']
        wp_password = config['password']
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    root = tk.Tk()
    app = ImageProcessorApp(root)
    app.run()
