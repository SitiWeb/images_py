"""
Main module for the Image Processor application.
"""
from PIL import Image, ImageTk
import customtkinter as ctk
import os
import sys
from ui.menu import MenuBar  # Import the new MenuBar class
from ui.log_frame import LogWindow
from ui.button_frame import ButtonFrame
from ui.frame_info import InfoFrame
from ui.settings_tab import SettingsTab
from config.decrypt_config import ConfigDecryptor, DECRYPTION_KEY
from config.encrypt_config import ConfigEncryptor
from controller import AppController

from ui.preview_frame import PreviewFrame  # Import the new PreviewFrame class


def resource_path(relative_path: str) -> str:
    """Get absolute path to a resource (dev or PyInstaller)."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



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
        self.root.geometry("553x800")

        # Window/taskbar icon (Windows prefers .ico)
        try:
            ico_path = resource_path("ui/images/image_processor.ico")
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
        except Exception:
            pass

        # Cross-platform icon (uses PNG)
        try:
            png_path = resource_path("ui/images/image_processor.png")
            if os.path.exists(png_path):
                self._icon_photo = ImageTk.PhotoImage(Image.open(png_path))
                self.root.iconphoto(True, self._icon_photo)
        except Exception:
            pass

        # Initialize the controller
        self.controller = AppController(self.root)

        # Create the menu bar
        self.menu_bar = MenuBar(self.root, self.controller)

        # Create the main frame to hold tabs, log window, and other sections
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="both")  # Ensure the main frame expands both vertically and horizontally

        # Configure row and column to expand and fill available space
        self.root.grid_rowconfigure(0, weight=1)  # Ensures the frames expand vertically
        self.root.grid_columnconfigure(0, weight=1)  # Ensures the frames expand horizontally

        # Create a master frame to hold all the other frames
        self.master_main_frame = ctk.CTkFrame(main_frame)
        self.master_main_frame.grid(row=0, column=0, sticky="nsew")
        self.master_main_frame.grid_rowconfigure(0, weight=1)
        self.master_main_frame.grid_columnconfigure(0, weight=1)  # Ensure full-width spanning

        # Log Frame (appears at the bottom)
        self.log_frame = ctk.CTkFrame(self.master_main_frame)
        self.log_frame.grid(row=3, column=0, sticky="ew")  # Set sticky to "ew" to expand horizontally
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_window = LogWindow(self.log_frame)
        self.controller.set_log(self.log_window)
        # Button Frame
        self.button_frame = ctk.CTkFrame(self.master_main_frame, height=250)
        self.button_frame.grid(row=0, column=0, sticky="nsew")  # Set sticky to "ew" to expand horizontally
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame = ButtonFrame(self.button_frame, self.controller, None)

        # Info Frame
        self.info_frame = ctk.CTkFrame(self.master_main_frame)
        self.info_frame.grid(row=1, column=0, sticky="ew")  # Set sticky to "ew" to expand horizontally
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame = InfoFrame(self.info_frame)

        # Preview Frame
        self.preview_frame = ctk.CTkFrame(self.master_main_frame)
        self.preview_frame.grid(row=2, column=0, sticky="nsew")  # Expand both horizontally and vertically
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame = PreviewFrame(self.preview_frame)  # Initialize the PreviewFrame

        

        # Settings Tab
        self.settings_tab = SettingsTab(main_frame, self.controller)

        # Register the tabs and preview frame with the controller
        self.controller.set_local_processing_tab(self.master_main_frame)
        self.controller.set_settings_tab(self.settings_tab)
        self.controller.set_preview_bar(self.preview_frame)
        self.controller.set_info_bar(self.info_frame)
        self.controller.set_menu_bar( self.menu_bar)
        # Position the tabs
        self.master_main_frame.grid(row=0, column=0, sticky="nsew")  # Make sure master_main_frame expands
        self.settings_tab.tab.grid(row=0, column=0, sticky="nsew")

        # Show the default tab (Local Processing Tab)
        self.controller.update_options()
        self.open_local_processing_tab()

    def open_local_processing_tab(self):
        """
        Show the Local Processing tab.
        """
        self.master_main_frame.tkraise()

    def show_local_processing_options(self):
        """
        Show the Local Processing tab.
        """
        self.master_main_frame.open_options_window()

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
        # Load the active credentials
        config = decryptor.load_credentials()
        print(config)
        if config:
            wc_url = config.get("url", "")
            wc_consumer_key = config.get("consumer_key", "")
            wc_consumer_secret = config.get("consumer_secret", "")
            wp_username = config.get("username", "")
            wp_password = config.get("password", "")
        else:
            print("No active credentials found.")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    root = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ImageProcessorApp(root)
    app.run()
