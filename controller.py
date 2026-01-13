import tempfile
import threading
from utils.file_operations import FileProcessor
from utils.image_processing import ImageProcessor
from ui.options_window import OptionsWindow
from config.encrypt_config import ConfigEncryptor
from api.woocommerce_api import get_first_image
from PIL import Image, ImageTk
from pprint import pformat
from api.woocommerce_api import process_product_images, process_all_products, search_product, get_first_image_path, get_product
import customtkinter as ctk
import os

class AppController:
    """
    The controller class for managing the overall state and interactions of the application.
    """

    def __init__(self, root):
        """
        Initialize the AppController.

        Args:
            root (ctk.CTk): The root CustomTkinter window.
        """
        key = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="
        self.root = root
        self.file = FileProcessor()
        self.image = ImageProcessor()
        self.menu_bar = None
        self.local_processing_tab = None
        self.settings_tab = None
        self.preview_bar = None
        self.log = None
        self.canvas_width = 900
        self.canvas_height = 900
        self.template = "{slug}_{sku}_{width}x{height}"
        self.delete_images = False
        self.transparent = True
        self.background_color = "#000000"
        self.image_format = "AUTO"
        self.image_size = "contain"
        self.config = ConfigEncryptor(key)
        self.type = None
        self.destination_path = None
        self.found_products = None
        self.selected_directory = None
        self.current_product = 0
        self.status = "stopped"
        self.load_config()

    def load_config(self):
        config = self.config.load_config()
        if config:
            if options := config.get("options"):
                self.canvas_width = options.get("canvas_width", 900)
                self.canvas_height = options.get("canvas_height", 900)
                self.template = options.get("template", "{slug}_{sku}_{width}x{height}")
                self.delete_images = options.get("delete_images", False)
                self.transparent = options.get("transparent", True)
                self.background_color = options.get("background_color", "#000000")
                self.image_format = options.get("image_format", "AUTO")
                self.image_size = options.get("image_size", "contain")

    def set_menu_bar(self, menu_bar):
        """
        Set the MenuBar for the application.

        Args:
            menu_bar (MenuBar): The MenuBar instance.
        """
        self.log_message("Init menu bar")
        self.menu_bar = menu_bar

    def set_log(self, log):
        """
        Set the MenuBar for the application.

        Args:
            menu_bar (MenuBar): The MenuBar instance.
        """
        self.log = log
        self.log_message("Init Logs")

    def set_local_processing_tab(self, local_processing_tab):
        """
        Set the LocalProcessingTab for the application.

        Args:
            local_processing_tab (LocalProcessingTab): The LocalProcessingTab instance.
        """
        self.local_processing_tab = local_processing_tab
        self.log_message("Init main")

    def set_preview_bar(self, preview):
        """
        Set the MenuBar for the application.

        Args:
            menu_bar (MenuBar): The MenuBar instance.
        """
        self.preview_bar = preview
        self.log_message("Init previews")

    def set_info_bar(self, info):
        """
        Set the MenuBar for the application.

        Args:
            menu_bar (MenuBar): The MenuBar instance.
        """
        self.info_bar = info
        self.log_message("Init info")

    def set_settings_tab(self, settings_tab):
        """
        Set the SettingsTab for the application.

        Args:
            settings_tab (SettingsTab): The SettingsTab instance.
        """
        self.settings_tab = settings_tab
        self.log_message("Init settings")

    def show_local_processing_tab(self):
        """
        Display the local processing tab.
        """
        if self.local_processing_tab:
            self.log_message("Show main tab")
            self.local_processing_tab.tkraise()  # Make sure to raise the correct tab frame

    def show_settings_tab(self):
        """
        Display the settings tab.
        """
        if self.settings_tab:
            self.log_message("Show settings tab")
            self.settings_tab.tab.tkraise()  # Make sure to raise the correct tab frame

    def show_local_processing_options(self):
        """
        Display the options window in the local processing tab.
        """
        if self.local_processing_tab:
            self.log_message("Open options")
            self.open_options_window()

    def log_message(self, obj):
        """
        Log a formatted message to the log window using pprint.

        Args:
            obj (object): The object to format and log.
        """
        if self.log:
            formatted_message = pformat(obj)
            self.log.log_message(formatted_message)

    import threading

    def start_processing(self):
        """
        Start the image processing based on the selected options.
        """
        source = self.type
        options = self.get_options()
        self.log_message(f"Start import source: {source}")
        self.status = "started"
        self.menu_bar.start_button.configure(fg_color="red", text="Running")

        # Wrapper to process and update status after completion
        def process_and_update_status(target_func, *args):
            try:
                # Execute the actual processing function
                target_func(*args)
            finally:
                # Update status to 'stopped' after processing is done
                self.status = "stopped"
                self.menu_bar.start_button.configure(fg_color="#008000", text="Start")
                self.log_message(f"Processing completed for source: {source}")

        if source == "directory":
            threading.Thread(
                target=process_and_update_status, args=(self.file.process_directory_with_logging, options)
            ).start()
        elif source == "product":
            threading.Thread(
                target=process_and_update_status, args=(process_product_images, options)
            ).start()
        elif source == "file":
            threading.Thread(
                target=process_and_update_status, args=(self.file.proces_single_image, options)
            ).start()
        elif source == "all_products":
            threading.Thread(
                target=process_and_update_status, args=(process_all_products, options)
        ).start()


    def update_options(self, text=None):
        """
        Update the UI elements based on the selected source type.
        """
        self.type = text
        self.log_message(f"Update options {text}")
        if text:
            self.update_info(text)
        # if self.local_processing_tab:
            # self.local_processing_tab.product_id_button.grid_remove()
            # self.local_processing_tab.product_id_entry.grid_remove()
            # self.local_processing_tab.additional_name_label.grid_remove()
            # self.local_processing_tab.additional_name_entry.grid_remove()
            # self.local_processing_tab.browse_button.grid_remove()
            # self.local_processing_tab.browse_file_button.grid_remove()
            # if self.type == "directory":
            #     self.local_processing_tab.browse_button.grid()
            # elif self.type == "file":
            #     self.local_processing_tab.browse_button.grid()
            # elif self.type == "all_products":
            #     pass
            # elif self.type == "wp_image":
            #     self.local_processing_tab.product_id_button.grid()
            #     self.local_processing_tab.product_id_entry.grid()
            # elif self.type == "product":
            #     self.local_processing_tab.product_id_button.grid()
            #     self.local_processing_tab.product_id_entry.grid()
             
        self.update_previews()

    def update_previews(self, before_path=None, after_path=None):
        """
        Update the image previews.

        Args:
            before_path (str, optional): The path to the 'before' image.
            after_path (str, optional): The path to the 'after' image.
        """
        first_image_path = False
        if self.status != "started":
            if self.type == "all_products":
                first_image_path = get_first_image()
                
            elif self.type == "product" and self.found_products:
                first_image_path = get_first_image_path(self.found_products[self.current_product])
            else:
            
                print("getting first path")
                first_image_path = self.file.get_first_image_path()

        if before_path :
            before_img = Image.open(before_path)
            before_img.thumbnail((200, 200))
            before_photo = ImageTk.PhotoImage(before_img)
            self.preview_bar.before_image_label.configure(image=before_photo)
            self.preview_bar.before_image_label.image = before_photo
            dir_name = os.path.basename(before_path)
            if len(dir_name) > 35:
                dir_name = f"...{dir_name[-35:]}"
            self.preview_bar.before_filename_label.configure(text=dir_name)

        if after_path:
            after_img = Image.open(after_path)
            after_img.thumbnail((200, 200))
            after_photo = ImageTk.PhotoImage(after_img)
            self.preview_bar.after_image_label.configure(image=after_photo)
            self.preview_bar.after_image_label.image = after_photo
            dir_name = os.path.basename(after_path)
            if len(dir_name) > 35:
                dir_name = f"...{dir_name[-35:]}"
            self.preview_bar.before_filename_label.configure(text=dir_name)

        if first_image_path:
            fd, output_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            self.image.resize_image(
                first_image_path, output_path, self.get_options()
            )
            before_img = Image.open(first_image_path)
            before_img.thumbnail((200, 200))
            before_photo = ImageTk.PhotoImage(before_img)
            self.preview_bar.before_image_label.configure(image=before_photo)
            self.preview_bar.before_image_label.image = before_photo

            after_img = Image.open(output_path)
            after_img.thumbnail((200, 200))
            after_photo = ImageTk.PhotoImage(after_img)
            self.preview_bar.after_image_label.configure(image=after_photo)
            self.preview_bar.after_image_label.image = after_photo
            name = self.file.generate_output_path("/",first_image_path,self.get_options())
            dir_name = os.path.basename(name)
            if len(dir_name) > 35:
                dir_name = f"...{dir_name[-35:]}"
            self.preview_bar.after_filename_label.configure(text=dir_name)
            dir_name = os.path.basename(first_image_path)
            if len(dir_name) > 35:
                dir_name = f"...{dir_name[-35:]}"
            self.preview_bar.before_filename_label.configure(text=dir_name)
     
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
            if len(file_name) > 35:
                file_name = f"...{file_name[-35:]}"
            self.info_bar.selected_button_label.configure(text=file_name)
            self.apply_options(self.get_options())
            self.update_previews()

    def browse_directory_command(self):
        """
        Command to browse for a directory.
        """
        directory = self.file.browse_directory()
        if directory:
            dir_name = os.path.basename(directory)
            if len(dir_name) > 35:
                dir_name = f"...{dir_name[-35:]}"
            # self.browse_button.configure(text=dir_name)
            self.selected_directory = directory
            self.apply_options(self.get_options())
            self.update_previews()
            
    def browse_destination_command(self):
        """
        Open directory dialog to select a destination directory.
        """
        destination_path = self.file.browse_directory()
        if destination_path:
            self.info_bar.destination_label.configure(text=f"Destination: {destination_path}")
            print(f"Selected destination: {destination_path}")
            self.destination_path = destination_path

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
        if not self.destination_path:
            self.destination_path = False
        product = None
        product_id = 0
        if self.found_products and len(self.found_products) >= self.current_product:
            product_id = self.found_products[self.current_product]['id']
            product = self.found_products[self.current_product]
        options = {
            # "selected_directory": self.local_processing_tab.browse_button.cget("text"),
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "log_message": self.log,  # Use the log method from the log_window
            "format_log_message": self.log_message,
            "update_previews": self.update_previews,
            "product_id": product_id,
            "product": product,
            "template": self.template,
            "delete_images": self.delete_images,
            "background_color": self.background_color,
            "image_format": self.image_format,
            "image_size": self.image_size,
            "selected_directory": self.selected_directory,
            "destination_path" : self.destination_path
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
                "default": self.background_color,
            },
            "image_format": {
                "type": "dropdown",
                "label": "Image Format:",
                "options": ["AUTO", "JPEG", "PNG", "GIF", "DZI", "AVIF", "WEBP"],
                "default": self.image_format,
            },
            "image_size": {
                "type": "dropdown",
                "label": "Image Size:",
                "options": ["contain", "cover"],
                "default": self.image_size,
            },
        }

        OptionsWindow(self.root, self.apply_options, current_options)

    def apply_options(self, options):
        """
        Apply the selected options from the options window.

        Args:
            options (dict): The options to apply.
        """
        # if self.log_window:
        #     self.log_window.clear()  # Clear the log window if it exists
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

    def process_product(self, input):
        cleaned_input = (input or "").strip()
        self.found_products = None
        self.current_product = 0

        if cleaned_input.isdigit():
            product = get_product(int(cleaned_input))
            if product:
                self.found_products = [product]
        else:
            self.found_products = search_product(cleaned_input)

        if self.found_products:
            count_products = len(self.found_products)
            print(f"Found {count_products} products")
            print(f"Current product {self.current_product}")
            print(self.found_products[self.current_product])
            self.info_bar.selected_button_label.configure(text=self.found_products[self.current_product]['name'] + " (id: "+ str(self.found_products[self.current_product]['id']) +")" )
            number = self.current_product
            number += 1
            text = f"Viewing product {number}/{count_products}"
            self.info_bar.destination_label.configure(text=text)
            self.update_previews()
            self.update_product_nav_buttons()
            return self.found_products[self.current_product]
        self.info_bar.destination_label.configure(text="No products found")
        self.update_product_nav_buttons()
        pass

    def change_product(self, data):
        if not self.found_products:
            self.update_product_nav_buttons()
            return
        count_products = len(self.found_products)
        self.current_product = max(0, min(self.current_product + data, count_products - 1))
        if count_products > 0:
            count_products = len(self.found_products)
            print(self.found_products[self.current_product])
            self.info_bar.selected_button_label.configure(text=self.found_products[self.current_product]['name'] + " (id: "+ str(self.found_products[self.current_product]['id'])+")" )
            number = self.current_product
            number += 1
            text = f"Viewing product {number}/{count_products}"
            self.info_bar.destination_label.configure(text=text)
            self.update_previews()
            self.update_product_nav_buttons()
        pass

    def update_product_nav_buttons(self):
        if not getattr(self.info_bar, "next_button", None) or not getattr(self.info_bar, "prev_button", None):
            return
        total = len(self.found_products) if self.found_products else 0
        can_prev = total > 0 and self.current_product > 0
        can_next = total > 0 and self.current_product < (total - 1)
        self.info_bar.prev_button.configure(state="normal" if can_prev else "disabled")
        self.info_bar.next_button.configure(state="normal" if can_next else "disabled")

    def update_info(self, selected_option):
        """
        Update the info frame based on the selected option.

        Args:
            selected_option (str): The currently selected option (e.g., "product", "file", etc.).
        """
        
        # Clear previous description and input fields
        if self.info_bar.input_field:
            self.info_bar.input_field.grid_forget()
        if self.info_bar.input_button:
            self.info_bar.input_button.grid_forget()
        if self.info_bar.next_button:
            self.info_bar.next_button.grid_forget()
        if self.info_bar.prev_button:
            self.info_bar.prev_button.grid_forget()
        if self.info_bar.destination_button:
            self.info_bar.destination_button.grid_forget()
        if self.info_bar.destination_label:
            self.info_bar.destination_label.grid_forget()
            
        display_label = selected_option.replace("_", " ").title()
        self.info_bar.selected_button_label.configure(text=display_label)

        # Update the description and input fields based on the selected option
        if selected_option == "product":
            self.info_bar.description_label.configure(text="Search")
            self.info_bar.input_field = ctk.CTkEntry(self.info_bar.parent_frame)
            self.info_bar.input_field.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

            self.info_bar.input_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Search product:",
                command=lambda: self.process_product(self.info_bar.input_field.get())
            )
            self.info_bar.input_button.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

            self.info_bar.next_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Next",
                command=lambda: self.change_product(1)
            )
            self.info_bar.next_button.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

            self.info_bar.prev_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Prev",
                command=lambda: self.change_product(-1)
            )
            self.info_bar.prev_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

            # Destination Directory Label (to show the selected destination)
            self.info_bar.destination_label = ctk.CTkLabel(
                self.info_bar.parent_frame, text="No products found"
            )
            self.info_bar.destination_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
            self.update_product_nav_buttons()

        elif selected_option == "file":
            self.info_bar.description_label.configure(text="Choose a file to process:")
            
            # Browse File Button
            self.info_bar.input_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Browse File",
                command=self.browse_file_command
            )
            self.info_bar.input_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

            # Destination Directory Button
            self.info_bar.destination_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Select Destination",
                command=self.browse_destination_command  # Command to browse destination directory
            )
            self.info_bar.destination_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

            # Destination Directory Label (to show the selected destination)
            self.info_bar.destination_label = ctk.CTkLabel(
                self.info_bar.parent_frame, text="No destination selected"
            )
            self.info_bar.destination_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        elif selected_option == "directory":
            self.info_bar.description_label.configure(text="Choose a directory to process:")
            
            # Browse Directory Button
            self.info_bar.input_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Browse Directory",
                command=self.browse_directory_command
            )
            self.info_bar.input_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

            # Destination Directory Button
            self.info_bar.destination_button = ctk.CTkButton(
                self.info_bar.parent_frame,
                text="Select Destination",
                command=self.browse_destination_command  # Command to browse destination directory
            )
            self.info_bar.destination_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

            # Destination Directory Label (to show the selected destination)
            self.info_bar.destination_label = ctk.CTkLabel(
                self.info_bar.parent_frame, text="No destination selected"
            )
            self.info_bar.destination_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")



    def run(self):
        """
        Run the main event loop.
        """
        self.root.mainloop()
