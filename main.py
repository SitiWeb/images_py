"""
Main module for the Image Processor application.
"""

import customtkinter as ctk
from ui.log_window import LogWindow
from ui.local_processing_tab import LocalProcessingTab
from ui.settings_tab import SettingsTab
from config.decrypt_config import ConfigDecryptor, DECRYPTION_KEY
from config.encrypt_config import ConfigEncryptor

class ImageProcessorApp:
    """
    Main application class for the Image Processor.
    """

    def __init__(self, root):
        """
        Initialize the ImageProcessorApp.

        Args:
            root (ctk.CTk): The root CustomTkinter window.
        """
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("480x800")
        # Create menu frame at the top
        menu_frame = ctk.CTkFrame(self.root)
        menu_frame.pack(side="top", fill="x")

        local_processing_button = ctk.CTkButton(menu_frame, text="Local Processing", command=self.show_local_processing_tab)
        local_processing_button.pack(side="left", padx=5, pady=5)

        settings_button = ctk.CTkButton(menu_frame, text="Settings", command=self.show_settings_tab)
        settings_button.pack(side="left", padx=5, pady=5)

        # Create main frame to hold tabs and log window
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="x")

        self.tab_parent = ctk.CTkFrame(main_frame)
        self.tab_parent.grid(row=0, column=0, sticky="nsew")

        self.log_frame = ctk.CTkFrame(main_frame)
        self.log_frame.grid(row=1, column=0, sticky="nsew")

        main_frame.grid_rowconfigure(0, weight=1)

        main_frame.grid_columnconfigure(0, weight=1)

        self.log_window = LogWindow(self.log_frame)

        self.local_processing_tab = LocalProcessingTab(self.tab_parent, self.log_window)
        self.settings_tab = SettingsTab(self.tab_parent)

        self.local_processing_tab.tab.grid(row=0, column=0, sticky="nsew")
        self.settings_tab.tab.grid(row=0, column=0, sticky="nsew")

        self.show_local_processing_tab()

    def show_local_processing_tab(self):
        """
        Show the Local Processing tab.
        """
        self.local_processing_tab.tab.tkraise() 

    def show_settings_tab(self):
        """
        Show the Settings tab.
        """
        self.settings_tab.tab.tkraise()

    def run(self):
        """
        Run the CustomTkinter main loop.
        """
        self.root.mainloop()


if __name__ == "__main__":
    try:
        decryptor = ConfigEncryptor(DECRYPTION_KEY)
        config = decryptor.load_credentials()
        if config:
            wc_url = config["url"]
            wc_consumer_key = config["consumer_key"]
            wc_consumer_secret = config["consumer_secret"]
            wp_username = config["username"]
            wp_password = config["password"]
    except FileNotFoundError as e:
        print(f"File not found: {e}")

    root = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ImageProcessorApp(root)
    app.run()
