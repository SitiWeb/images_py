import customtkinter as ctk
from tkinter import colorchooser, messagebox


class OptionsWindow(ctk.CTkToplevel):
    def __init__(self, parent, apply_callback, current_options):
        super().__init__(parent)
        self.title("Options")
        self.geometry("500x500")

        self.apply_callback = apply_callback
        self.options = current_options
        self.inputs = {}

        self.setup_ui()
        self.attributes('-topmost', True)  # Ensure the window stays on top
        self.lift()  # Bring the window to the front

    def setup_ui(self):
        """
        Set up the UI components.
        """
        self.row_index = 0
        for name, details in self.options.items():
            self.create_option(name, details)

        self.create_apply_button()

    def create_option(self, name, details):
        """
        Create an option based on its type.
        """
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
        lbl = ctk.CTkLabel(self, text=label)
        lbl.grid(row=self.row_index, columnspan=1, column=0, padx=5, pady=5, sticky="w")

        entry = ctk.CTkEntry(self)
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
        lbl = ctk.CTkLabel(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        entry = ctk.CTkEntry(self)
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
        var = ctk.BooleanVar(value=default)
        chk = ctk.CTkCheckBox(self, text=label, variable=var)
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
        lbl = ctk.CTkLabel(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        combo = ctk.CTkComboBox(self, values=options, state="readonly")
        combo.set(default)
        combo.grid(row=self.row_index, columnspan=2, column=1, padx=5, pady=5, sticky="w")

        self.inputs[name] = {"type": "dropdown", "widget": combo}
        self.row_index += 1

    def pick_color(self, button):
        self.attributes('-topmost', False)  # Temporarily disable topmost to allow colorchooser to be on top
        color_code = colorchooser.askcolor(parent=self, title="Choose color")[1]
        self.attributes('-topmost', True)  # Re-enable topmost for this window

        if color_code:
            button.configure(fg_color=color_code)
            self.inputs[button.name]["color"] = color_code

    def add_color_picker(self, name, label, default):
        """
        Add a color picker.

        Args:
            name (str): The name of the color picker.
            label (str): The label for the color picker.
            default (str): The default color.
        """
        lbl = ctk.CTkLabel(self, text=label)
        lbl.grid(row=self.row_index, column=0, padx=5, pady=5, sticky="w")

        color_button = ctk.CTkButton(self, text="", width=30, command=lambda: self.pick_color(color_button))
        color_button.name = name
        color_button.configure(fg_color=default)
        color_button.grid(row=self.row_index, column=1, padx=5, pady=5, sticky="w")

        chk_var = ctk.BooleanVar(value=(default == "transparent"))
        chk = ctk.CTkCheckBox(self, text="Transparent", variable=chk_var, command=lambda: self.check_transparent(chk_var, color_button))
        chk.grid(row=self.row_index, column=2, padx=5, pady=5, sticky="w")

        self.inputs[name] = {"type": "color", "button": color_button, "transparent_var": chk_var, "color": default}
        self.row_index += 1

    def check_transparent(self, var, button):
        if var.get():
            button.configure(state="disabled", fg_color="#ffffff")
        else:
            button.configure(state="normal")

    def create_apply_button(self):
        """
        Create the apply button.
        """
        apply_button = ctk.CTkButton(
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
                if details["transparent_var"].get():
                    options[name] = "transparent"
                else:
                    options[name] = details["color"]

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
            self.create_option(name, self.inputs[name])


# Example usage
if __name__ == "__main__":
    def apply_options(options):
        print(options)

    root = ctk.CTk()
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
