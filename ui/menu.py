from PIL import Image
import customtkinter as ctk
import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to a resource, whether we're running in development or a PyInstaller package. """
    try:
        # PyInstaller stores files in _MEIPASS when built
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, 'ui/images/'+ relative_path +'.png')

class MenuBar:
    def __init__(self, parent, controller):
        """
        Initialize the MenuBar.

        Args:
            parent (ctk.CTkFrame): The parent frame for the menu.
            controller (AppController): The controller instance to manage the app.
        """
        self.parent = parent
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):

        button_width = 40
        icon_size = 24
        # Create menu frame
        self.menu_frame = ctk.CTkFrame(self.parent)
        self.menu_frame.pack(side="top", fill="x")

        # Create the buttons with icons
        self.create_menu_button(
            "house-user-solid",
            "#363636",
            "",
            self.controller.show_local_processing_tab,
            button_width,
            icon_size,
        )
        self.create_menu_button(
            "filters",
            "#363636",
            "",
            self.controller.show_local_processing_options,
            button_width,
            icon_size,
        )
        self.create_menu_button(
            "cogs",
            "#363636",
            "",
            self.controller.show_settings_tab,
            button_width,
            icon_size,
        )
       
        self.start_button = self.create_menu_button(
            "play",
            "#008000",
            "Start",
            self.controller.start_processing,
            button_width,
            icon_size,
            side="right",
        )
    

    def create_menu_button(
        self, icon_path, bg_color, text, command, button_width, icon_size, side="left"
    ):
        """
        Create a button with an icon for the menu.

        Args:
            icon_path (str): Path to the icon.
            command (callable): The function to call when the button is pressed.
            button_width (int): The width of the button.
            icon_size (int): The size of the icon.
            side (str): Where to place the button ('left' or 'right').
        """

        if icon_path:
            path = resource_path(icon_path)
            icon_image = ctk.CTkImage(
                light_image=Image.open(path), size=(icon_size, icon_size)
            )

            button = ctk.CTkButton(
                self.menu_frame,
                image=icon_image,
                text=text,
                fg_color=bg_color,
                command=command,
                width=button_width,
            )
            button.pack(side=side, padx=5, pady=5)
            return button  