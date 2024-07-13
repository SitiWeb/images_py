import tkinter as tk
from tkinter import ttk


class OptionsWindow(tk.Toplevel):
    def __init__(self, parent, apply_callback, current_options):
        super().__init__(parent)
        self.title("Options")
        self.geometry("400x400")

        self.apply_callback = apply_callback
        self.options = current_options
        self.inputs = {}

        self.setup_ui()

    def setup_ui(self):
        """
        Set up the UI components.
        """
        self.row_index = 0
        for name, details in self.options.items():
            if details["type"] == "number":
                self.add_number_input(
                    name,
                    details["label"],
                    details["default"],
                    details["min"],
                    details["max"],
                )
            elif details["type"] == "text":
                self.add_text_input(name, details["label"], details["default"])
            elif details["type"] == "checkbox":
                self.add_checkbox(name, details["label"], details["default"])

        self.create_apply_button()

    def add_number_input(self, name, label, default, min_val, max_val):
        """
        Add a number input field.

        Args:
            name (str): The name of the input field.
            label (str): The label for the input field.
            default (int): The default value.
            min_val (int): The minimum value.
            max_val (int): The maximum value.
        """
        lbl = tk.Label(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        entry = tk.Entry(self)
        entry.insert(0, str(default))
        entry.grid(row=self.row_index, column=1, padx=5, pady=5, sticky="w")

        self.inputs[name] = {
            "type": "number",
            "widget": entry,
            "min": min_val,
            "max": max_val,
        }
        self.row_index += 1

    def add_text_input(self, name, label, default):
        """
        Add a text input field.

        Args:
            name (str): The name of the input field.
            label (str): The label for the input field.
            default (str): The default value.
        """
        lbl = tk.Label(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        entry = tk.Entry(self)
        entry.insert(0, default)
        entry.grid(row=self.row_index, column=1, padx=5, pady=5, sticky="w")

        self.inputs[name] = {"type": "text", "widget": entry}
        self.row_index += 1

    def add_checkbox(self, name, label, default):
        """
        Add a checkbox.

        Args:
            name (str): The name of the input field.
            label (str): The label for the input field.
            default (bool): The default value.
        """
        var = tk.BooleanVar(value=default)
        chk = tk.Checkbutton(self, text=label, variable=var)
        chk.grid(row=self.row_index, column=0,
                 columnspan=2, padx=5, pady=5, sticky="w")

        self.inputs[name] = {"type": "checkbox", "variable": var}
        self.row_index += 1

    def create_apply_button(self):
        """
        Create the apply button.
        """
        apply_button = tk.Button(
            self, text="Apply", command=self.apply_options)
        apply_button.grid(row=self.row_index, column=0, columnspan=2, pady=10)

    def apply_options(self):
        """
        Apply the options and call the callback function.
        """
        options = {}
        for name, details in self.inputs.items():
            if details["type"] == "number":
                value = int(details["widget"].get())
                min_val = details["min"]
                max_val = details["max"]
                if min_val <= value <= max_val:
                    options[name] = value
                else:
                    messagebox.showerror(
                        "Error", f"{name} must be between {min_val} and {max_val}"
                    )
                    return
            elif details["type"] == "text":
                options[name] = details["widget"].get()
            elif details["type"] == "checkbox":
                options[name] = details["variable"].get()

        self.apply_callback(options)
        self.destroy()
