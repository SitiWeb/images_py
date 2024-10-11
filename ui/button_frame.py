import customtkinter as ctk
from PIL import Image
from tkinter import StringVar
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
class ButtonFrame:
    """
    Class for creating and managing the button frame.
    """

    def __init__(self, parent_frame, controller, log_window):
        """
        Initialize the ButtonFrame.

        Args:
            parent_frame (ctk.CTkFrame): The parent frame where the buttons will be placed.
            controller (AppController): The controller to handle logic and updates.
            log_window (LogWindow): The log window to display log messages.
        """
        self.parent_frame = parent_frame
        self.controller = controller
        self.log_window = log_window
        # self.log = self.log_window.log_message

        self.buttons = {"directory", "file", "wp_image", "product", "all_products"}
        self.source_buttons = {}
        self.selected_button = StringVar(value="")  # To store the selected button

        self.setup_ui()

    def setup_ui(self):
        """
        Set up the UI for the button frame.
        """
        row = 0
        self.create_buttons(self.parent_frame, self.buttons, self.source_buttons, row)

    def create_buttons(self, frame, button_data, button_store, row):
        """
        Create buttons from the button_data list and store them in button_store.
        """
        
        col_index = 0
        for label in button_data:
            path = resource_path(label)
            display_label = label.replace("_", " ").title()
            icon_path = path
            if icon_path:
                icon_image = ctk.CTkImage(
                    light_image=Image.open(icon_path), size=(24, 24)
                )
            else:
                icon_image = None

            button = ctk.CTkButton(
                frame,
                image=icon_image,
                text=display_label,
                font=("Helvetica", 12, "bold"),
                command=lambda l=label, s=button_store: self.set_active_button(l, s),
                fg_color="#666666",
                hover_color="#0f4d0f",
                compound="top",
                width=100,
                
            )
            button.grid(row=row, column=col_index,columnspan=1, padx=5, pady=5, sticky="ew")
            button_store[label] = button
            col_index += 1

    def set_active_button(self, active_label, button_store):
        """
        Set the clicked button to green and the rest to gray for a specific button store.
        Also update the description and input fields based on the active button.
        """
        if self.controller.status != "started":
            for label, button in button_store.items():
                if label == active_label:
                    self.controller.update_options(active_label)
                    button.configure(fg_color="#008000")
                else:
                    button.configure(fg_color="#666666")

