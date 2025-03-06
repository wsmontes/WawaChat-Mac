import tkinter as tk
from tkinter import ttk

def setup_settings_ui(self):
    """Set up the settings UI components."""
    # Title label
    ttk.Label(self.settings_frame, text="Model Parameters", font=("Helvetica", 12, "bold")).grid(
        row=0, column=1, columnspan=2, pady=(0, 10), sticky='w')

    def add_setting(setting_name, default_value, row, setting_type="entry"):
        ttk.Label(self.settings_frame, text=setting_name).grid(row=row, column=1, sticky='w', pady=2)

        if setting_type == "entry":
            entry = tk.Entry(self.settings_frame)
            entry.insert(0, str(default_value))
            entry.grid(row=row, column=2, pady=2, padx=5, sticky='ew')
            return entry
        elif setting_type == "select":
            var = tk.StringVar(self.settings_frame)
            var.set(str(default_value))
            select = ttk.Combobox(self.settings_frame, textvariable=var, values=("True", "False"))
            select.grid(row=row, column=2, pady=2, padx=5, sticky='ew')
            return var

    # Numeric and text parameters
    row_offset = 1
    self.settings = {
        "max_new_tokens": add_setting("Max new tokens", 50, row_offset),
        "temperature": add_setting("Temperature", 0.5, row_offset + 1),
        "top_p": add_setting("Top P", 0.9, row_offset + 2),
        "num_beams": add_setting("Num Beams", 2, row_offset + 3),
    }

    # Boolean parameters with select dropdowns
    self.boolean_settings = {
        "truncation": add_setting("Truncation", "True", row_offset + 4, "select"),
        "do_sample": add_setting("Do Sample", "True", row_offset + 5, "select"),
        "early_stopping": add_setting("Early Stopping", "True", row_offset + 6, "select"),
    }

    # Checkboxes for including/excluding parameters
    self.include_settings = {}
    row = row_offset + 7
    ttk.Separator(self.settings_frame, orient='horizontal').grid(
        row=row, column=1, columnspan=2, sticky='ew', pady=10)
    row += 1

    ttk.Label(self.settings_frame, text="Parameter Controls", font=("Helvetica", 10, "bold")).grid(
        row=row, column=1, columnspan=2, pady=(0, 5), sticky='w')
    row += 1

    for key in self.settings.keys():
        var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(self.settings_frame, text=f"Include {key}", var=var)
        chk.grid(row=row, column=1, columnspan=2, sticky='w')
        self.include_settings[key] = var
        row += 1

    for key in self.boolean_settings.keys():
        var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(self.settings_frame, text=f"Include {key}", var=var)
        chk.grid(row=row, column=1, columnspan=2, sticky='w')
        self.include_settings[key] = var
        row += 1

    # Separator
    ttk.Separator(self.settings_frame, orient='horizontal').grid(
        row=row, column=1, columnspan=2, sticky='ew', pady=10)
    row += 1

    # Button frame for controls
    button_frame = tk.Frame(self.settings_frame)
    button_frame.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)

    # Clear button
    clear_btn = tk.Button(button_frame, text="Clear Chat", command=self.clear_conversation)
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    # Theme toggle button
    theme_btn = tk.Button(button_frame, text="Toggle Theme", command=self.toggle_theme)
    theme_btn.pack(side=tk.RIGHT, padx=5)
