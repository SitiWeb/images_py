import tkinter as tk
from tkinter import ttk
from ui.local_processing_tab import create_tab_local
from ui.settings_tab import create_tab_settings
from ui.log_window import LogWindow


from decrypt_config import decrypt_config, key

try:
    config = decrypt_config(key)
    wc_url = config['url']
    wc_consumer_key = config['consumer_key']
    wc_consumer_secret = config['consumer_secret']
    wp_username = config['username']
    wp_password = config['password']

    # Now use these variables to create your WooCommerce API instance

except FileNotFoundError as e:
    print(e)
    # Handle the missing file case, e.g., by prompting the user to create it
except Exception as e:
    print(f"An error occurred: {e}")
    # Handle other potential errors
log_window = None

def open_log_window():
    global log_window
    if log_window is None or not log_window.winfo_exists():
        log_window = LogWindow(window)
    else:
        log_window.lift()

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Image Processor")
    window.geometry("700x400")

    tab_parent = ttk.Notebook(window)

    create_tab_local(tab_parent, "Local Processing", open_log_window)
    create_tab_settings(tab_parent, "Settings")

    tab_parent.pack(expand=True, fill='both')

    window.mainloop()
