import os
import shutil
import tempfile
from tkinter import filedialog, messagebox
from utils.image_processing import resize_image

selected_directory = ""

def browse_directory():
    global selected_directory
    selected_directory = filedialog.askdirectory()
    return selected_directory

def get_first_image_path():
    if not selected_directory:
        return None

    for root, dirs, files in os.walk(selected_directory):
        if 'ProcessedImages' in dirs:
            dirs.remove('ProcessedImages')
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
                return os.path.join(root, file)
    return None

def process_directory_with_logging(additional_name, is_checked, log, update_previews):
    if not selected_directory:
        messagebox.showwarning("No Directory", "Please select a directory.")
        return
    if log:
        log(f"Processing started for directory: {selected_directory}")
    output_directory = os.path.join(selected_directory, 'ProcessedImages')
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
        if log:
            log("Existing directory removed.")
    os.makedirs(output_directory, exist_ok=True)
    if log:
        log(f"Output directory created: {output_directory}")

    image_paths = []
    for root, dirs, files in os.walk(selected_directory):
        if 'ProcessedImages' in dirs:
            dirs.remove('ProcessedImages')
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
                file_path = os.path.join(root, file)
                image_paths.append(file_path)
                if log:
                    log(f"Found: {file_path}")
    if log:
        log(f"Total images found: {len(image_paths)}")

    for file_path in image_paths:
        output_path = os.path.join(output_directory, os.path.relpath(file_path, selected_directory))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        resize_image(file_path, output_path, additional_name)
        
        # with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        #     temp_output_path = temp_file.name
        #     resize_image(file_path, temp_output_path, additional_name)
        #     update_previews(file_path, temp_output_path)
        
        if os.path.exists(file_path) and is_checked:
            os.remove(file_path)
        if log:
            log(f"Processed: {file_path}")

    messagebox.showinfo("Process Complete", "Image processing is complete.")
    if log:
        log("Processing complete.")
