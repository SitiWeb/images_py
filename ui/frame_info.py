# info_frame.py

import customtkinter as ctk
from tkinter import filedialog


class InfoFrame:
    """
    Class for managing the info frame where descriptions and input fields are shown.
    """

    def __init__(self, parent_frame):
        """
        Initialize the InfoFrame.

        Args:
            parent_frame (ctk.CTkFrame): The parent frame for the info section.
            log_window (LogWindow): The log window to display log messages.
        """
        self.parent_frame = parent_frame
    
        self.selected_button_label = None
        self.description_label = None
        self.input_field = None
        self.input_button = None
        self.prev_button = None
        self.next_button = None
        self.destination_button = None
        self.destination_label = None
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the UI for the info frame.
        """
        # Label to display the selected button name
        self.selected_button_label = ctk.CTkLabel(
            self.parent_frame, text="", font=("Helvetica", 12, "bold")
        )
        self.selected_button_label.grid(row=0, column=0,  columnspan=12, padx=5, pady=5, sticky="w")

        # Description label to provide info about the selected button
        self.description_label = ctk.CTkLabel(
            self.parent_frame, text="", font=("Helvetica", 10)
        )
        self.description_label.grid(row=1, column=0,  columnspan=3, padx=5, pady=5, sticky="w")

    def process_product(self, product_id):
        # Handle product processing logic here
        self.log(f"Processing product with ID: {product_id}")

    def browse_file(self):
        # Open file dialog to select a file
        file_path = filedialog.askopenfilename()
     

    def browse_directory(self):
        # Open directory dialog to select a directory
        directory_path = filedialog.askdirectory()
    
