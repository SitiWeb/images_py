import customtkinter as ctk
from PIL import Image

class PreviewFrame:
    """
    Class to handle the preview frames (Before and After) for image processing.
    """

    def __init__(self, parent):
        """
        Initialize the PreviewFrame.

        Args:
            parent (ctk.CTkFrame): The parent frame where the preview frames will be placed.
        """
   
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface for the preview frames.
        """
        row = 0
        start_row = row
        # Creating the main preview frame
        preview_frame = ctk.CTkFrame(self.parent, bg_color="gray35")
        preview_frame.grid(row=row, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        # Ensure the preview_frame expands to the full width
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(1, weight=1)

        # Creating the "Before" frame
        before_frame = ctk.CTkFrame(preview_frame)
        before_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")

        # Adding "Before" label and image label to the before_frame
        self.before_label = ctk.CTkLabel(before_frame, text="Before:")
        self.before_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        row += 1
        self.before_image_label = ctk.CTkLabel(before_frame, text="", height=175)
        self.before_image_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        row += 1
        # Adding a filename label under the "Before" image label
        self.before_filename_label = ctk.CTkLabel(before_frame, text="Filename")
        self.before_filename_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        # Creating the "After" frame
        after_frame = ctk.CTkFrame(preview_frame)
        after_frame.grid(row=start_row, column=1, padx=5, pady=5, sticky="ew")

        # Adding "After" label and image label to the after_frame
        self.after_label = ctk.CTkLabel(after_frame, text="After:")
        self.after_label.grid(row=start_row, column=0, padx=5, pady=5, sticky="w")
        start_row += 1
        self.after_image_label = ctk.CTkLabel(after_frame, text="", height=175)
        self.after_image_label.grid(row=start_row, column=0, padx=5, pady=5, sticky="w")
        start_row += 1
        # Adding a filename label under the "After" image label
        self.after_filename_label = ctk.CTkLabel(after_frame, text="Filename")
        self.after_filename_label.grid(row=start_row, column=0, padx=5, pady=5, sticky="w")

    # def update_before_image(self, image, filename=""):
    #     """
    #     Update the before image and filename label.

    #     Args:
    #         image (PIL.Image): The image to display.
    #         filename (str): The filename to display.
    #     """
    #     self.before_image_label.config(image=image)
    #     self.before_filename_label.config(text=filename)

    # def update_after_image(self, image, filename=""):
    #     """
    #     Update the after image and filename label.

    #     Args:
    #         image (PIL.Image): The image to display.
    #         filename (str): The filename to display.
    #     """
    #     self.after_image_label.config(image=image)
    #     self.after_filename_label.config(text=filename)
