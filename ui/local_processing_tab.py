import tempfile
import threading
import customtkinter as ctk
from tkinter.scrolledtext import ScrolledText
from tkinter import StringVar, BooleanVar
from PIL import Image, ImageTk
from utils.file_operations import FileProcessor
from utils.image_processing import ImageProcessor
from api.woocommerce_api import process_product_images, process_all_products
from ui.options_window import OptionsWindow
from pprint import pformat
from config.encrypt_config import ConfigEncryptor
import os


class LocalProcessingTab:
    """
    Class for the Local Processing Tab in the Image Processor application.
    """

    def __init__(self, tab_parent, log_window):
        """
        Initialize the LocalProcessingTab.

        Args:
            tab_parent (ctk.CTkFrame): The parent frame widget.
            log_window (LogWindow): The log window frame.
        """
        key = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="

        self.log_window = log_window
        self.log = self.log_window.log_message
        self.tab = ctk.CTkFrame(tab_parent)
        self.root = self.tab.winfo_toplevel()  # Store the root window reference
        self.config = ConfigEncryptor(key)

        self.canvas_width = 900
        self.canvas_height = 900
        self.template = "{slug}_{sku}_{width}x{height}"
        self.delete_images = False
        self.transparent = True
        self.background_color = "#000000"
        self.image_format = "AUTO"
        self.image_size = "contain"
        self.load_config()
        self.source_type = StringVar(value="directory")
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

    def setup_ui(self):
        """
        Set up the user interface for the tab.
        """
        current_row = 0
        start_options_frame = ctk.CTkFrame(self.tab, bg_color="gray30")
        start_options_frame.grid(row=current_row, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        self.options_button = ctk.CTkButton(
            start_options_frame, text="Options", command=self.open_options_window
        )
        self.options_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.button_start = ctk.CTkButton(
            start_options_frame, text="Start Processing", command=self.start_processing
        )
        self.button_start.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky="w")

        # Image previews section
        current_row += 1

        # Source selection section
        source_frame = ctk.CTkFrame(self.tab, bg_color="gray20")
        source_frame.grid(row=current_row, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        source_label = ctk.CTkLabel(source_frame, anchor="w", text="Source Type:")
        source_label.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="w")

        self.source_dropdown = ctk.CTkComboBox(
            source_frame,
            variable=self.source_type,
            values=["directory", "file", "wp_image", "product", "all_products"],
            state="readonly",
            command=self.update_options
        )
        self.source_dropdown.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.source_dropdown.bind(
            "<<ComboboxSelected>>", lambda e: self.update_options()
        )

        self.browse_button = ctk.CTkButton(
            source_frame, text="Browse directory", command=self.browse_directory_command
        )
        self.browse_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.browse_file_button = ctk.CTkButton(
            source_frame, text="Browse file", command=self.browse_file_command
        )
        self.browse_file_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="w")

        self.product_id_button = ctk.CTkButton(source_frame, text="Get", width=25)
        self.product_id_button.grid(row=2, column=4, columnspan=1, padx=5, pady=5, sticky="w")

        self.product_id_entry = ctk.CTkEntry(source_frame)
        self.product_id_entry.grid(row=2, column=5, columnspan=2, padx=5, pady=5, sticky="w")

        self.additional_name_label = ctk.CTkLabel(source_frame, text="Add suffix:")
        self.additional_name_label.grid(row=2, column=7, padx=5, pady=5, sticky="w")

        self.additional_name_entry = ctk.CTkEntry(source_frame)
        self.additional_name_entry.grid(row=2, column=8, padx=5, pady=5, sticky="w")

        # Destination selection section
        current_row += 1
        # destination_frame = ctk.CTkFrame(self.tab, bg_color="gray25")
        # destination_frame.grid(row=current_row, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        # destination_label = ctk.CTkLabel(destination_frame, anchor="w", text="Destination Type:")
        # destination_label.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="w")

        # self.destination_dropdown = ctk.CTkComboBox(
        #     destination_frame,
        #     variable=self.source_type,
        #     values=["auto", "directory", "file", "wp_image", "product"],
        #     state="readonly",
        #     command=self.update_options
        # )
        # self.destination_dropdown.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # # Start and Options section
        # current_row += 1
       
        preview_frame = ctk.CTkFrame(self.tab, bg_color="gray35")
        preview_frame.grid(row=current_row, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        self.before_label = ctk.CTkLabel(preview_frame, text="Before:")
        self.before_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.after_label = ctk.CTkLabel(preview_frame, text="After:")
        self.after_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.before_image_label = ctk.CTkLabel(preview_frame, text="")
        self.before_image_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        self.after_image_label = ctk.CTkLabel(preview_frame, text="")
        self.after_image_label.grid(row=1, column=3, columnspan=3, padx=5, pady=5, sticky="w")

        # Configure grid weights to make frames span the full width
        self.tab.grid_columnconfigure(0, weight=1)
        source_frame.grid_columnconfigure(0, weight=1)
  
        start_options_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

    def update_options(self, text=None):
        """
        Update the UI elements based on the selected source type.
        """
        self.product_id_button.grid_remove()
        self.product_id_entry.grid_remove()
        self.additional_name_label.grid_remove()
        self.additional_name_entry.grid_remove()
        self.browse_button.grid_remove()
        self.browse_file_button.grid_remove()
        if self.source_type.get() == "directory":
            self.browse_button.grid()
        elif self.source_type.get() == "product":
            self.product_id_button.grid()
            self.product_id_entry.grid()
        elif self.source_type.get() == "file":
            self.browse_file_button.grid()
        self.update_previews()

    def update_previews(self, before_path=None, after_path=None):
        """
        Update the image previews.

        Args:
            before_path (str, optional): The path to the 'before' image.
            after_path (str, optional): The path to the 'after' image.
        """
        first_image_path = self.file.get_first_image_path()
        if before_path and after_path:
            before_img = Image.open(before_path)
            before_img.thumbnail((200, 200))
            before_photo = ImageTk.PhotoImage(before_img)
            self.before_image_label.configure(image=before_photo)
            self.before_image_label.image = before_photo

            after_img = Image.open(after_path)
            after_img.thumbnail((200, 200))
            after_photo = ImageTk.PhotoImage(after_img)
            self.after_image_label.configure(image=after_photo)
            self.after_image_label.image = after_photo
        elif first_image_path:
            with tempfile.NamedTemporaryFile(
                suffix=".jpg", delete=False
            ) as temp_file:
                output_path = temp_file.name
                self.image.resize_image(
                    first_image_path, output_path, self.get_options()
                )
                before_img = Image.open(first_image_path)
                before_img.thumbnail((200, 200))
                before_photo = ImageTk.PhotoImage(before_img)
                self.before_image_label.configure(image=before_photo)
                self.before_image_label.image = before_photo

                after_img = Image.open(output_path)
                after_img.thumbnail((200, 200))
                after_photo = ImageTk.PhotoImage(after_img)
                self.after_image_label.configure(image=after_photo)
                self.after_image_label.image = after_photo

    def set_image_preview(self, image_path, label):
        """
        Set the image preview for a given label.

        Args:
            image_path (str): The path to the image file.
            label (ctk.CTkLabel): The label to set the image on.
        """
        img = Image.open(image_path)
        img.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo

    def browse_file_command(self):
        """
        Command to browse for a file.
        """
        file = self.file.browse_files()
        if file:
            file_name = os.path.basename(file)
            if len(file_name) > 20:
                file_name = f"...{file_name[-20:]}"
            self.browse_file_button.configure(text=file_name)
            self.apply_options(self.get_options())
            self.update_previews()

    def browse_directory_command(self):
        """
        Command to browse for a directory.
        """
        directory = self.file.browse_directory()
        if directory:
            dir_name = os.path.basename(directory)
            if len(dir_name) > 20:
                dir_name = f"...{dir_name[-20:]}"
            self.browse_button.configure(text=dir_name)
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
            "log_message": self.log,  # Use the log method from the log_window
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
            self.log_window.clear()  # Clear the log window if it exists
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
        self.log(formatted_message)

    def start_processing(self):
        """
        Start the image processing based on the selected options.
        """
        source = self.source_type.get()
        options = self.get_options()

        if source == "directory":
            threading.Thread(
                target=self.file.process_directory_with_logging, args=(options,)
            ).start()
        elif source == "product":
            threading.Thread(
                target=process_product_images,
                args=(options,)
            ).start()
        elif source == "file":
            threading.Thread(
                target=self.file.proces_single_image,
                args=(options,)
            ).start()
        elif source == "all_products":
            threading.Thread(
                target=process_all_products,
                args=(options,)
            ).start()
        self.update_previews()
