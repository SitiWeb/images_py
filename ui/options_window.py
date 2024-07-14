import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from pprint import pprint
class OptionsWindow(tk.Toplevel):
    def __init__(self, parent, apply_callback, current_options):
        super().__init__(parent)
        self.title("Options")
        self.geometry("400x500")

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
            elif details["type"] == "dropdown":
                self.add_dropdown(
                    name, details["label"], details["options"], details["default"]
                )
            elif details["type"] == "color":
                self.add_color_picker(name, details["label"], details["default"])

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
        lbl.grid(row=self.row_index, columnspan=1,column=0, padx=5, pady=5, sticky="w")

        entry = tk.Entry(self)
        entry.insert(0, str(default))
        entry.grid(row=self.row_index, columnspan=2, column=1, padx=5, pady=5, sticky="w")

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
        entry.grid(row=self.row_index, columnspan=2, column=1, padx=5, pady=5, sticky="w")

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

        self.inputs[name] = {"type": "checkbox", "variable": var, 'label': label, 'default': default}
        self.row_index += 1

    def add_dropdown(self, name, label, options, default):
        """
        Add a dropdown field.

        Args:
            name (str): The name of the dropdown.
            label (str): The label for the dropdown.
            options (list): The list of options.
            default (str): The default value.
        """
        lbl = tk.Label(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        combo = ttk.Combobox(self, values=options, state="readonly")
        combo.set(default)
        combo.grid(row=self.row_index,columnspan=2, column=1, padx=5, pady=5, sticky="w")

        self.inputs[name] = {"type": "dropdown", "widget": combo}
        self.row_index += 1

    def check_transparent(self, var, color_entry, pick_button, color_preview):
        if var.get():
            color_entry.config(state="disabled")
            pick_button.config(state="disabled")
            color_preview.config(bg="white")
        else:
            color_entry.config(state="normal")
            pick_button.config(state="normal")
            color_preview.config(bg=color_entry.get())

    def pick_color(self, color_entry, color_preview):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            color_entry.delete(0, tk.END)
            color_entry.insert(0, color_code)
            color_preview.config(bg=color_code)

    def add_color_picker(self, name, label, default):
        """
        Add a color picker.

        Args:
            name (str): The name of the color picker.
            label (str): The label for the color picker.
            default (str): The default color.
        """
        if default == "transparent":
            default = "#00000000"
            var = tk.BooleanVar(value=True)
        else:
            var = tk.BooleanVar(value=False)
        lbl = tk.Label(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        color_preview = tk.Label(self, bg=default, width=2, height=1)
        color_preview.grid(row=self.row_index, column=1, padx=5, pady=5, sticky="w")

        color_entry = tk.Entry(self)
        color_entry.insert(0, default)
        color_entry.grid(row=self.row_index, column=2, padx=5, pady=5, sticky="w")

        pick_button = tk.Button(self, text="Pick", command=lambda: self.pick_color(color_entry, color_preview))
        pick_button.grid(row=self.row_index, column=3, padx=5, pady=5, sticky="w")

        
        chk = tk.Checkbutton(self, text="Transparent", variable=var, command=lambda: self.check_transparent(var, color_entry, pick_button, color_preview))
        chk.grid(row=self.row_index, column=4, padx=5, pady=5, sticky="w")

        self.inputs[name] = {"type": "color", "entry": color_entry, "transparent_var": var}
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
            elif details["type"] == "dropdown":
                options[name] = details["widget"].get()
            elif details["type"] == "color":
                if "value" in details:
                    options[name] = details["value"]
                else:
                    options[name] = "transparent"

        self.apply_callback(options)
        self.destroy()

    def add_conditional_setting(self, name, condition):
        """
        Add a conditional setting that is displayed based on another setting.

        Args:
            name (str): The name of the conditional setting.
            condition (function): The condition function that returns a boolean.
        """
        if condition():
            if self.inputs[name]["type"] == "number":
                self.add_number_input(
                    name,
                    self.inputs[name]["label"],
                    self.inputs[name]["default"],
                    self.inputs[name]["min"],
                    self.inputs[name]["max"],
                )
            elif self.inputs[name]["type"] == "text":
                self.add_text_input(
                    name, self.inputs[name]["label"], self.inputs[name]["default"]
                )
            elif self.inputs[name]["type"] == "checkbox":
                self.add_checkbox(
                    name, self.inputs[name]["label"], self.inputs[name]["default"]
                )
            elif self.inputs[name]["type"] == "dropdown":
                self.add_dropdown(
                    name,
                    self.inputs[name]["label"],
                    self.inputs[name]["options"],
                    self.inputs[name]["default"],
                )
            elif self.inputs[name]["type"] == "color":
                self.add_color_picker(
                    name, self.inputs[name]["label"], self.inputs[name]["default"]
                )


# Example usage
if __name__ == "__main__":
    def apply_options(options):
        print(options)

    root = tk.Tk()
    current_options = {
        "canvas_width": {"type": "number", "label": "Width:", "default": 900, "min": 1, "max": 2540},
        "canvas_height": {"type": "number", "label": "Height:", "default": 900, "min": 1, "max": 2540},
        "template": {"type": "text", "label": "Filename Template:", "default": "{slug}_{sku}_{width}x{height}"},
        "delete_images": {"type": "checkbox", "label": "Delete image when done", "default": False},
        "background_color": {"type": "color", "label": "Background Color:", "default": "#FFFFFF"},
        "image_format": {"type": "dropdown", "label": "Image Format:", "options": ["JPEG", "PNG", "GIF"], "default": "JPEG"}
    }

    app = OptionsWindow(root, apply_options, current_options)

    root.mainloop()
