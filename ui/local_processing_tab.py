"""
Module for the Local Processing Tab in the Image Processor application.
"""

import tempfile
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, Label, Button, Entry, Toplevel, StringVar, BooleanVar
from PIL import Image, ImageTk
from utils.file_operations import FileProcessor
from utils.image_processing import ImageProcessor
from api.woocommerce_api import process_product_images, process_all_products
from ui.options_window import OptionsWindow
from pprint import pformat, pprint
from config.encrypt_config import ConfigEncryptor

class LocalProcessingTab:
    """
    Class for the Local Processing Tab in the Image Processor application.
    """

    def __init__(self, tab_parent, text, log):
        """
        Initialize the LocalProcessingTab.

        Args:
            tab_parent (ttk.Notebook): The parent notebook widget.
            text (str): The text to display on the tab.
            log (function): The function to log messages.
        """
        key = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="
       
        self.log = log
        self.tab = ttk.Frame(tab_parent)
        self.root = self.tab.winfo_toplevel()  # Store the root window reference
        tab_parent.add(self.tab, text=text)
        self.config = ConfigEncryptor(key)
        self.log_window = None

        self.canvas_width = 900
        self.canvas_height = 900
        self.template = "{slug}_{sku}_{width}x{height}"
        self.delete_images = False
        self.transparent = True
        self.background_color = "#000000"
        self.image_format = "AUTO"
        self.image_size = "contain"
        self.load_config()
        self.source_type = StringVar(value="local")
        self.checkbox_var = BooleanVar(value=False)
        self.file = FileProcessor()
        self.image = ImageProcessor()
        # Automatically open the options window with default options

        self.setup_ui()
        self.update_options()

    def load_config(self):
 
        config = self.config.load_config()
        if config:
            if options := config.get("options"):
                self.canvas_width = options.get("canvas_width", 900)
                self.canvas_height = options.get("canvas_height", 900)
                self.template = options.get("template",  "{slug}_{sku}_{width}x{height}")
                self.delete_images = options.get("delete_images", False)
                self.transparent = options.get("transparent", True)
                self.background_color = options.get("background_color", "#000000")
                self.image_format = options.get("image_format", "AUTO")
                self.image_size = options.get("image_size", "contain")


    def create_log_window(self):
        """
        Create and display the log window.
        """
        if self.log_window and Toplevel.winfo_exists(self.log_window):
            return
        self.log_window = Toplevel()
        self.log_window.title("Processing Log")
        self.log_text = ScrolledText(
            self.log_window, state="disabled", wrap="word", height=20, width=80
        )

        self.log_text.pack(expand=True, fill="both")

    def log_message(self, message):
        """
        Log a message to the log window.

        Args:
            message (str): The message to log.
        """
        if self.log_window:
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
            self.log_text.update_idletasks()

    def setup_ui(self):
        """
        Set up the user interface for the tab.
        """
        # Source selection section
        self.source_label = Label(self.tab, text="Source Type:")
        self.source_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.source_dropdown = ttk.Combobox(
            self.tab,
            textvariable=self.source_type,
            values=["local", "product", "all_products"],
            state="readonly",
        )
        self.source_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.source_dropdown.bind(
            "<<ComboboxSelected>>", lambda e: self.update_options()
        )

        self.browse_button = ttk.Button(
            self.tab, text="Browse", command=self.browse_directory_command
        )
        self.browse_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # WooCommerce Product ID section
        self.product_id_label = Label(self.tab, text="Product ID:")
        self.product_id_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.product_id_entry = Entry(self.tab)
        self.product_id_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # SKU section
        self.additional_name_label = Label(self.tab, text="Add suffix:")
        self.additional_name_label.grid(
            row=2, column=1, padx=5, pady=5, sticky="w")

        self.additional_name_entry = Entry(self.tab)
        self.additional_name_entry.grid(
            row=2, column=2, padx=5, pady=5, sticky="w")

        # Options button
        self.options_button = ttk.Button(
            self.tab, text="Options", command=self.open_options_window
        )
        self.options_button.grid(row=2, column=3, columnspan=2,  padx=5, pady=5, sticky="w")

        self.button_start = Button(
            self.tab, text="Start Processing", command=self.start_processing
        )
        self.button_start.grid(
            row=1, column=3, columnspan=2, padx=5, pady=5, sticky="w"
        )

        # Image previews
        self.before_label = Label(self.tab, text="Before:")
        self.before_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.before_image_label = Label(self.tab)
        self.before_image_label.grid(
            row=6, column=0, padx=5, pady=5, sticky="w")

        self.after_label = Label(self.tab, text="After:")
        self.after_label.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.after_image_label = Label(self.tab)
        self.after_image_label.grid(
            row=6, column=1, padx=5, pady=5, sticky="w")

    def update_options(self):
        """
        Update the UI elements based on the selected source type.
        """
        if self.source_type.get() == "local":
            self.browse_button.grid()
            self.product_id_label.grid_remove()
            self.product_id_entry.grid_remove()
            self.additional_name_label.grid_remove()
            self.additional_name_entry.grid_remove()
        elif self.source_type.get() == "product":
            self.browse_button.grid_remove()
            self.product_id_label.grid()
            self.product_id_entry.grid()
            self.additional_name_label.grid_remove()
            self.additional_name_entry.grid_remove()
        else:
            self.browse_button.grid_remove()
            self.product_id_label.grid_remove()
            self.product_id_entry.grid_remove()
            self.product_id_label.grid()
            self.product_id_entry.grid()
            self.additional_name_label.grid_remove()
            self.additional_name_entry.grid_remove()
        self.update_previews()

    def update_previews(self, before_path=None, after_path=None):
        """
        Update the image previews.

        Args:
            before_path (str, optional): The path to the 'before' image.
            after_path (str, optional): The path to the 'after' image.
        """
        if before_path and after_path:
            before_img = Image.open(before_path)
            before_img.thumbnail((150, 150))
            before_photo = ImageTk.PhotoImage(before_img)
            self.before_image_label.config(image=before_photo)
            self.before_image_label.image = before_photo

            after_img = Image.open(after_path)
            after_img.thumbnail((150, 150))
            after_photo = ImageTk.PhotoImage(after_img)
            self.after_image_label.config(image=after_photo)
            self.after_image_label.image = after_photo
        else:
            first_image_path = self.file.get_first_image_path()
            if first_image_path:
                with tempfile.NamedTemporaryFile(
                    suffix=".jpg", delete=False
                ) as temp_file:
                    output_path = temp_file.name
                    self.image.resize_image(
                        first_image_path, output_path, self.get_options()
                    )
                    before_img = Image.open(first_image_path)
                    before_img.thumbnail((150, 150))
                    before_photo = ImageTk.PhotoImage(before_img)
                    self.before_image_label.config(image=before_photo)
                    self.before_image_label.image = before_photo

                    after_img = Image.open(output_path)
                    after_img.thumbnail((150, 150))
                    after_photo = ImageTk.PhotoImage(after_img)
                    self.after_image_label.config(image=after_photo)
                    self.after_image_label.image = after_photo

    def set_image_preview(self, image_path, label):
        """
        Set the image preview for a given label.

        Args:
            image_path (str): The path to the image file.
            label (Label): The label to set the image on.
        """
        img = Image.open(image_path)
        img.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo

    def browse_directory_command(self):
        """
        Command to browse for a directory.
        """
        directory = self.file.browse_directory()
        if directory:
            self.browse_button.config(text=directory)
            self.apply_options(self.get_options())
            self.update_previews()

    def apply_canvas_size(self):
        """
        Apply the canvas size settings and update previews.
        """
        self.image.set_canvas_size(self.canvas_width, self.canvas_height)

    def apply_image_size(self):
        """
        Apply the canvas size settings and update previews.
        """
        self.image.set_image_size(self.image_size)

    def apply_background_color(self):
        """
        Apply the canvas size settings and update previews.
        """
        self.image.set_background_color(self.background_color)
  

    def get_options(self) -> dict:
        """
        Get the current processing options.

        Returns:
            dict: The current processing options.
        """
        options = {
            "selected_directory": self.browse_button.cget("text"),
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "log_message": self.log_message,
            "format_log_message": self.pprint_log_message,
            "update_previews": self.update_previews,
            "product_id": self.product_id_entry.get(),
            "template": self.template,
            "delete_images": self.delete_images,
            "background_color": self.background_color,
            "image_format": self.image_format,
            "image_size": self.image_size,
        }
        return options

    def open_options_window(self):
        """
        Open the options window.
        """
        current_options = {
            "canvas_width": {
                "type": "number",
                "label": "Width:",
                "default": self.canvas_width,
                "min": 1,
                "max": 2540,
            },
            "canvas_height": {
                "type": "number",
                "label": "Height:",
                "default": self.canvas_height,
                "min": 1,
                "max": 2540,
            },
            "template": {
                "type": "text",
                "label": "Filename Template:",
                "default": self.template,
            },
            "delete_images": {
                "type": "checkbox",
                "label": "Delete image when done",
                "default": self.delete_images,
            },
            "background_color": {
                "type": "color", 
                "label": "Background Color:", 
                "default": self.background_color
                },
            "image_format": {
                "type": "dropdown", 
                "label": "Image Format:", 
                "options": ["AUTO", "JPEG", "PNG", "GIF", "DZI"],
                "default": self.image_format
            },
            "image_size": {
                "type": "dropdown", 
                "label": "Image Size:", 
                "options": ["contain", "cover"],
                "default": self.image_size
            }

        }
  
        OptionsWindow(self.root, self.apply_options, current_options)

    def apply_options(self, options):
        """
        Apply the selected options from the options window.

        Args:
            options (dict): The options to apply.
        """
        if self.log_window:
            self.log_window.destroy()
            self.log_window = None
        self.canvas_width = options["canvas_width"]
        self.canvas_height = options["canvas_height"]
        self.template = options["template"]
        self.delete_images = options["delete_images"]
        self.background_color = options["background_color"]
        self.image_size = options["image_size"]
        self.image_format = options["image_format"]
        self.apply_canvas_size()
        self.apply_background_color()
        self.apply_image_size()
        key = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="
        self.config.save_options(self.get_options())
        self.update_previews()

    def pprint_log_message(self, obj):
        """
        Log a formatted message to the log window using pprint.

        Args:
            obj (object): The object to format and log.
        """
        formatted_message = pformat(obj)
        self.log_message(formatted_message)

    def start_processing(self):
        """
        Start the image processing based on the selected options.
        """
        self.create_log_window()
        source = self.source_type.get()
        options = self.get_options()

        if source == "local":
            threading.Thread(
                target=self.file.process_directory_with_logging, args=(options,)
            ).start()
        elif source == "product":
            threading.Thread(
                target=process_product_images,
                args=(options,)
            ).start()
        elif source == "all_products":
            threading.Thread(
                target=process_all_products,
                args=(options,)
            ).start()
        self.update_previews()
