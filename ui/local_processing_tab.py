import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import tempfile
import os
from utils.file_operations import browse_directory, process_directory_with_logging, get_first_image_path
from utils.image_processing import set_canvas_size, resize_image
from api.woocommerce import process_product_images, process_all_products

class LocalProcessingTab:
    def __init__(self, tab_parent, text, log):
        self.log = log
        self.tab = ttk.Frame(tab_parent)
        tab_parent.add(self.tab, text=text)
        
        self.log_window = None
        self.create_log_window()

        self.canvas_width = 900
        self.canvas_height = 900

        self.source_type = tk.StringVar(value="local")
        self.checkbox_var = tk.BooleanVar(value=False)

        self.setup_ui()
        self.update_source_fields()

    def create_log_window(self):
        if self.log_window and tk.Toplevel.winfo_exists(self.log_window):
            return
        self.log_window = tk.Toplevel()
        self.log_window.title("Processing Log")
        self.log_text = ScrolledText(self.log_window, state='disabled', wrap='word', height=20, width=80)
        self.log_text.pack(expand=True, fill='both')

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.log_text.update_idletasks()

    def setup_ui(self):

        # Source selection section
        self.source_label = tk.Label(self.tab, text="Source Type:")
        self.source_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.source_type = tk.StringVar(value="local")
        self.source_dropdown = ttk.Combobox(self.tab, textvariable=self.source_type, values=["local", "product", "all_products"], state="readonly")
        self.source_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.source_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_source_fields())

        self.browse_button = ttk.Button(self.tab, text="Browse", command=self.browse_directory_command)
        self.browse_button.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        # WooCommerce Product ID section
        self.product_id_label = tk.Label(self.tab, text="Product ID:")
        self.product_id_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.product_id_entry = tk.Entry(self.tab)
        self.product_id_entry.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        # SKU section
        self.additional_name_label = tk.Label(self.tab, text="Add suffix:")
        self.additional_name_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        self.additional_name_entry = tk.Entry(self.tab)
        self.additional_name_entry.grid(row=3, column=2, padx=5, pady=5, sticky='w')

        # Template section
        self.template_label = tk.Label(self.tab, text="Filename Template:")
        self.template_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        self.template_entry = tk.Entry(self.tab)
        self.template_entry.insert(0, "{slug}_{sku}_{width}x{height}")
        self.template_entry.grid(row=3, column=2, padx=5, columnspan=2, pady=5, sticky='w')

        # Canvas size section
        width_label = tk.Label(self.tab, text="Canvas Width:")
        width_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        self.width_entry = tk.Entry(self.tab)
        self.width_entry.insert(0, "900")
        self.width_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        self.height_label = tk.Label(self.tab, text="Canvas Height:")
        self.height_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        self.height_entry = tk.Entry(self.tab)
        self.height_entry.insert(0, "900")
        self.height_entry.grid(row=1, column=2, padx=5, pady=5, sticky='w')  
        self.button_set_size = tk.Button(self.tab, text="Save Size", command=self.apply_canvas_size)
        self.button_set_size.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='w')

        # Checkbox for deleting images
        self.checkbox_var = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(self.tab, text="Delete image when done", variable=self.checkbox_var)
        self.checkbox.grid(row=0, column=3, columnspan=2, padx=5, pady=5, sticky='w')

        self.button_start = tk.Button(self.tab, text="Start Processing", command=self.start_processing)
        self.button_start.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky='w')
        
        # Image previews
        self.before_label = tk.Label(self.tab, text="Before:")
        self.before_label.grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.before_image_label = tk.Label(self.tab)
        self.before_image_label.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        
        self.after_label = tk.Label(self.tab, text="After:")
        self.after_label.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        self.after_image_label = tk.Label(self.tab)
        self.after_image_label.grid(row=6, column=1, padx=5, pady=5, sticky='w')


    def update_source_fields(self):
        source = self.source_type.get()
        if source == "local":
            self.browse_button.grid()
            self.product_id_label.grid_remove()
            self.product_id_entry.grid_remove()
            self.update_previews()
        else:
            self.browse_button.grid_remove()
            self.product_id_label.grid()
            self.product_id_entry.grid()

    def update_previews(self, before_path=None, after_path=None):
        if before_path and after_path:
            self.set_image_preview(before_path, self.before_image_label)
            self.set_image_preview(after_path, self.after_image_label)
        else:
            first_image_path = get_first_image_path()
            if first_image_path:
                self.set_image_preview(first_image_path, self.before_image_label)
                self.after_image_label.config(image='')

    def set_image_preview(self, image_path, label):
        img = Image.open(image_path)
        img.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo

    def browse_directory_command(self):
        directory = browse_directory()
        if directory:
            self.browse_button.config(text=directory)
            self.update_previews()

       
    def apply_canvas_size(self):
        self.canvas_width = int(self.width_entry.get())
        self.canvas_height = int(self.height_entry.get())
        set_canvas_size(self.canvas_width, self.canvas_height)
        self.update_previews()

    def start_processing(self):
        source = self.source_type.get()
        print(self.checkbox_var.get())
        if source == "local":
            process_directory_with_logging(self.browse_button.cget("text"), self.additional_name_entry.get(), self.checkbox_var.get(), self.log_message, self.update_previews)
        elif source == "product":
            process_product_images(self.product_id_entry.get(), self.canvas_width, self.canvas_height, self.log_message)
        elif source == "all_products":
            process_all_products(self.canvas_width, self.canvas_height, self.log_message)
        self.update_previews()
