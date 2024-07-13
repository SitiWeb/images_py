import os
import shutil
from tkinter import filedialog, messagebox
from utils.image_processing import ImageProcessor


class FileProcessor:
    """
    Class to handle file processing operations.
    """

    def __init__(self):
        self.selected_directory = ""

    def browse_directory(self):
        """
        Open a dialog to select a directory.

        Returns:
            str: The selected directory path.
        """
        self.selected_directory = filedialog.askdirectory()
        return self.selected_directory

    def get_first_image_path(self):
        """
        Get the path of the first image in the selected directory.

        Returns:
            str: The path to the first image, or None if no images found.
        """
        if not self.selected_directory:
            return None

        for root, dirs, files in os.walk(self.selected_directory):
            if "ProcessedImages" in dirs:
                dirs.remove("ProcessedImages")
            for file in files:
                if file.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")
                ):
                    return os.path.join(root, file)
        return None

    def log_message(self, message, log=None):
        """
        Log a message or print it if no log function is provided.

        Args:
            message (str): The message to log or print.
            log (function, optional): The log function to use. Defaults to None.
        """
        if log:
            log(message)
        else:
            print(message)

    def process_directory_with_logging(self, options):
        """
        Process images in the selected directory with logging.

        Args:
            options (dict): Processing options.
        """
        if not self.selected_directory:
            messagebox.showwarning(
                "No Directory", "Please select a directory.")
            return
        log = options.get("log_message", None)
        self.log_message(
            f"Processing started for directory: {self.selected_directory}", log
        )

        output_directory = self.create_output_directory(log)
        image_paths = self.collect_image_paths(log)

        self.process_images(image_paths, output_directory, options, log)

        messagebox.showinfo("Process Complete",
                            "Image processing is complete.")
        self.log_message("Processing complete.", log)

    def create_output_directory(self, log):
        """
        Create the output directory for processed images.

        Args:
            log (function): The log function to use.

        Returns:
            str: The path to the output directory.
        """
        output_directory = os.path.join(
            self.selected_directory, "ProcessedImages")
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
            self.log_message("Existing directory removed.", log)
        os.makedirs(output_directory, exist_ok=True)
        self.log_message(f"Output directory created: {output_directory}", log)
        return output_directory

    def collect_image_paths(self, log):
        """
        Collect all image paths in the selected directory.

        Args:
            log (function): The log function to use.

        Returns:
            list: A list of image paths.
        """
        image_paths = []
        for root, dirs, files in os.walk(self.selected_directory):
            if "ProcessedImages" in dirs:
                dirs.remove("ProcessedImages")
            for file in files:
                if file.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")
                ):
                    file_path = os.path.join(root, file)
                    image_paths.append(file_path)
                    self.log_message(f"Found: {file_path}", log)
        self.log_message(f"Total images found: {len(image_paths)}", log)
        return image_paths

    def process_images(self, image_paths, output_directory, options, log):
        """
        Process each image by resizing and saving it to the output directory.

        Args:
            image_paths (list): A list of image paths.
            output_directory (str): The path to the output directory.
            options (dict): Processing options.
            log (function): The log function to use.
        """
        image = ImageProcessor()
        for file_path in image_paths:
            output_path = os.path.join(
                output_directory, os.path.relpath(
                    file_path, self.selected_directory)
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.resize_image(
                file_path, output_path, options.get("additional_name", "")
            )

            if os.path.exists(file_path) and options.get("is_checked", False):
                self.log_message(f"Removing: {file_path}", log)
                os.remove(file_path)
            self.log_message(f"Processed: {file_path}", log)
