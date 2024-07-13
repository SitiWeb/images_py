import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from PIL import Image, ImageTk
import tempfile
import os
from utils.file_operations import browse_directory, process_directory_with_logging, get_first_image_path
from utils.image_processing import set_canvas_size, resize_image
from api.woocommerce import process_product_images, process_all_products


canvas_width = 900
canvas_height = 900


def create_tab_local(tab_parent, text, log):
    tab = ttk.Frame(tab_parent)
    tab_parent.add(tab, text=text)

    log_window = None

    def create_log_window():
        nonlocal log_window
        if log_window and tk.Toplevel.winfo_exists(log_window):
            return
        log_window = tk.Toplevel()
        log_window.title("Processing Log")
        log_text = ScrolledText(log_window, state='disabled', wrap='word', height=20, width=80)
        log_text.pack(expand=True, fill='both')

        def log_message(message):
            log_text.config(state='normal')
            log_text.insert(tk.END, message + "\n")
            log_text.see(tk.END)
            log_text.config(state='disabled')
            log_text.update_idletasks()  # Ensure the GUI updates
        return log_message

    # Source selection section
    source_label = tk.Label(tab, text="Source Type:")
    source_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    source_type = tk.StringVar(value="local")
    source_dropdown = ttk.Combobox(tab, textvariable=source_type, values=["local", "product", "all_products"], state="readonly")
    source_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky='w')
    source_dropdown.bind("<<ComboboxSelected>>", lambda e: update_source_fields())

    # Local Directory selection section
    def update_directory():
        directory = browse_directory()
        if directory:
            # Show only the last directory name with ../
            truncated_directory = f"../{os.path.basename(directory)}"
            button_browse.config(text=truncated_directory)
        update_previews()

    button_browse = tk.Button(tab, text="Browse", command=update_directory)
    button_browse.grid(row=2, column=0, padx=5, pady=5, sticky='nw')
    
    # WooCommerce Product ID section
    product_id_label = tk.Label(tab, text="Product ID:")
    product_id_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
    
    product_id_entry = tk.Entry(tab)
    product_id_entry.grid(row=3, column=0, padx=5, pady=5, sticky='w')
      # SKU section
    additional_name_label = tk.Label(tab, text="Add suffix:")
    additional_name_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
    
    additional_name_entry = tk.Entry(tab)
    additional_name_entry.grid(row=3, column=2, padx=5, pady=5, sticky='w')

    # Template section
    template_label = tk.Label(tab, text="Filename Template:")
    template_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
    
    template_entry = tk.Entry(tab)
    template_entry.insert(0, "{slug}_{sku}_{width}x{height}")
    template_entry.grid(row=3, column=2, padx=5, columnspan=2, pady=5, sticky='w')

    
    def update_source_fields():
        print(source_type.get())
        if source_type.get() == "local":
            button_browse.grid()
            product_id_label.grid_remove()
            product_id_entry.grid_remove()
            additional_name_label.grid()
            additional_name_entry.grid()
            template_entry.grid_remove()
            template_label.grid_remove()
        elif source_type.get() == "product":
            button_browse.grid_remove()
            product_id_label.grid()
            product_id_entry.grid()
            additional_name_label.grid_remove()
            additional_name_entry.grid_remove()
        else:
            button_browse.grid_remove()
            product_id_label.grid_remove()
            product_id_entry.grid_remove()
            product_id_label.grid()
            product_id_entry.grid()
            additional_name_label.grid_remove()
            additional_name_entry.grid_remove()

    update_source_fields()  # Initial call to set correct fields

    # Canvas size section
    width_label = tk.Label(tab, text="Canvas Width:")
    width_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    
    width_entry = tk.Entry(tab)
    width_entry.insert(0, "900")
    width_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')
    
    height_label = tk.Label(tab, text="Canvas Height:")
    height_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
    
    height_entry = tk.Entry(tab)
    height_entry.insert(0, "900")
    height_entry.grid(row=1, column=2, padx=5, pady=5, sticky='w')
    
    def apply_canvas_size():
        global canvas_width, canvas_height
        canvas_width = int(width_entry.get())
        canvas_height = int(height_entry.get())
        set_canvas_size(canvas_width, canvas_height)
        update_previews()

    button_set_size = tk.Button(tab, text="Save Size", command=apply_canvas_size)
    button_set_size.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='w')

  


    # Checkbox for deleting images
    checkbox_var = tk.BooleanVar()
    checkbox = tk.Checkbutton(tab, text="Delete image when done", variable=checkbox_var)
    checkbox.grid(row=0, column=3, columnspan=2, padx=5, pady=5, sticky='w')

    # Start Processing button
    def start_processing():
        log_message = None # create_log_window()
        if source_type.get() == "local":
            process_directory_with_logging(additional_name_entry.get(), checkbox_var.get(), log_message, update_previews)
        elif source_type.get() == "product":
            product_id = product_id_entry.get()
            process_product_images(product_id, template_entry.get(), canvas_width, canvas_height)
        else:
            process_all_products(template_entry.get(), canvas_width, canvas_height)

    button_start = tk.Button(tab, text="Start Processing", command=start_processing)
    button_start.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky='w')
    
    # Image previews
    before_label = tk.Label(tab, text="Before:")
    before_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='w')
    before_image_label = tk.Label(tab)
    before_image_label.grid(row=6, columnspan=2, column=0, padx=5, pady=5, sticky='w')

    after_label = tk.Label(tab, text="After:")
    after_label.grid(row=5, columnspan=2, column=2, padx=5, pady=5, sticky='w')
    after_image_label = tk.Label(tab)
    after_image_label.grid(row=6, columnspan=2, column=2, padx=5, pady=5, sticky='w')

    def update_previews(before_path=None, after_path=None):
        if before_path and after_path:
            before_img = Image.open(before_path)
            before_img.thumbnail((150, 150))
            before_photo = ImageTk.PhotoImage(before_img)
            before_image_label.config(image=before_photo)
            before_image_label.image = before_photo

            after_img = Image.open(after_path)
            after_img.thumbnail((150, 150))
            after_photo = ImageTk.PhotoImage(after_img)
            after_image_label.config(image=after_photo)
            after_image_label.image = after_photo
        else:
            first_image_path = get_first_image_path()
            if first_image_path:
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    output_path = temp_file.name
                    resize_image(first_image_path, output_path, additional_name_entry.get())
                    before_img = Image.open(first_image_path)
                    before_img.thumbnail((150, 150))
                    before_photo = ImageTk.PhotoImage(before_img)
                    before_image_label.config(image=before_photo)
                    before_image_label.image = before_photo

                    after_img = Image.open(output_path)
                    after_img.thumbnail((150, 150))
                    after_photo = ImageTk.PhotoImage(after_img)
                    after_image_label.config(image=after_photo)
                    after_image_label.image = after_photo

    # Configure column weights to allow the log_text to expand
    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)
    tab.columnconfigure(2, weight=1)
    tab.columnconfigure(3, weight=1)
    tab.rowconfigure(6, weight=1)