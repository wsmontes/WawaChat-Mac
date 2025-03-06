import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import threading
import sys

class FirstRunWizard:
    def __init__(self, parent, credentials_manager, on_complete=None):
        self.parent = parent
        self.credentials_manager = credentials_manager
        self.on_complete_callback = on_complete
        
        # Current step in the wizard (0-based index)
        self.current_step = 0
        
        # Define the wizard steps
        self.steps = [
            {
                "title": "Welcome to WawaChat",
                "content": self._create_welcome_page,
            },
            {
                "title": "Hugging Face API Key",
                "content": self._create_api_key_page,
            },
            {
                "title": "Download Models",
                "content": self._create_models_page,
            },
            {
                "title": "Setup Complete",
                "content": self._create_complete_page,
            }
        ]
        
        self.create_wizard()
    
    def create_wizard(self):
        """Create the wizard dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("WawaChat Setup Wizard")
        self.dialog.geometry("600x450")
        self.dialog.resizable(False, False)
        
        # Make it modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Prevent closing with the X button
        self.dialog.protocol("WM_DELETE_WINDOW", self._handle_close)
        
        # Title bar
        self.title_bar = ttk.Frame(self.dialog, padding=10)
        self.title_bar.pack(fill=tk.X)
        
        self.title_label = ttk.Label(self.title_bar, text="", font=("Helvetica", 14, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        # Main content area
        self.content_frame = ttk.Frame(self.dialog, padding=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Bottom navigation bar
        self.nav_bar = ttk.Frame(self.dialog)
        self.nav_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        self.skip_button = ttk.Button(self.nav_bar, text="Skip", command=self._handle_skip)
        self.skip_button.pack(side=tk.LEFT)
        
        self.back_button = ttk.Button(self.nav_bar, text="Back", command=self._handle_back)
        self.back_button.pack(side=tk.RIGHT)
        
        self.next_button = ttk.Button(self.nav_bar, text="Next", command=self._handle_next)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Center the wizard
        self.dialog.update_idletasks()
        w = self.dialog.winfo_width()
        h = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - h) // 2
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        
        # Navigate to the first step
        self._navigate_to_step(0)
    
    def _navigate_to_step(self, step_index):
        """Navigate to the specified step in the wizard"""
        if step_index < 0 or step_index >= len(self.steps):
            return
            
        self.current_step = step_index
        
        # Update title
        self.title_label.config(text=self.steps[step_index]["title"])
        
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create new content
        self.steps[step_index]["content"](self.content_frame)
        
        # Update navigation buttons
        self._update_nav_buttons()
    
    def _update_nav_buttons(self):
        """Update the navigation buttons based on current step"""
        # Back button is disabled on the first step
        self.back_button.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        
        # Next button becomes Finish on the last step
        if self.current_step == len(self.steps) - 1:
            self.next_button.config(text="Finish")
        else:
            self.next_button.config(text="Next")
        
        # Skip button is only shown for API key step
        if self.current_step == 1:  # API Key step
            self.skip_button.pack(side=tk.LEFT)
        else:
            self.skip_button.pack_forget()
    
    def _handle_next(self):
        """Handle the Next/Finish button click"""
        if self.current_step == 1:  # API Key step
            # Try to save the API key if entered
            api_key = self.api_key_var.get().strip()
            if api_key:
                self.credentials_manager.set_api_key(api_key)
        
        if self.current_step == len(self.steps) - 1:
            # This is the last step, finish the wizard
            self._finish_wizard()
        else:
            # Navigate to the next step
            self._navigate_to_step(self.current_step + 1)
    
    def _handle_back(self):
        """Handle the Back button click"""
        self._navigate_to_step(self.current_step - 1)
    
    def _handle_skip(self):
        """Handle the Skip button click"""
        if self.current_step == 1:  # API Key step
            # Go to the next step without saving an API key
            self._navigate_to_step(self.current_step + 1)
    
    def _handle_close(self):
        """Handle the dialog close button (X) click"""
        if self.current_step == len(self.steps) - 1:
            # If on the last step, allow closing
            self._finish_wizard()
        else:
            # Otherwise, show a warning that setup is required
            if messagebox.askyesno(
                "Quit Setup", 
                "Setup is not complete. If you quit now, some features may not work properly. Quit anyway?"
            ):
                self._finish_wizard(completed=False)
    
    def _finish_wizard(self, completed=True):
        """Complete the wizard and mark first run as done"""
        if completed:
            self.credentials_manager.mark_first_run_completed()
        
        self.dialog.destroy()
        
        if self.on_complete_callback:
            self.on_complete_callback(completed)
    
    def _toggle_key_visibility(self):
        """Toggle visibility of the API key in the entry field"""
        if self.show_key.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="•")
    
    def _create_welcome_page(self, parent):
        """Create the welcome page content"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Try to load the logo if it exists
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((150, 150), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                logo = ImageTk.PhotoImage(img)
                
                logo_label = ttk.Label(frame, image=logo)
                logo_label.image = logo  # Keep a reference to prevent garbage collection
                logo_label.pack(pady=20)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        ttk.Label(frame, text="Welcome to WawaChat!", 
                font=("Helvetica", 16, "bold")).pack(pady=10)
        
        welcome_text = (
            "This wizard will help you set up WawaChat for first use.\n\n"
            "You'll need a Hugging Face account and API key to download models.\n\n"
            "Click 'Next' to continue."
        )
        ttk.Label(frame, text=welcome_text, wraplength=500, justify=tk.CENTER).pack(pady=20)
    
    def _create_api_key_page(self, parent):
        """Create the API key page content"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Hugging Face API Key", 
                font=("Helvetica", 14)).pack(pady=10)
        
        info_text = (
            "WawaChat uses Hugging Face to download AI models.\n"
            "You need an API key to access these models."
        )
        ttk.Label(frame, text=info_text, wraplength=500).pack(pady=10)
        
        # API Key entry
        key_frame = ttk.Frame(frame)
        key_frame.pack(pady=20)
        
        ttk.Label(key_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        current_key = self.credentials_manager.get_api_key()
        self.api_key_var = tk.StringVar(value=current_key if current_key else "")
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=40, show="•")
        self.api_key_entry.grid(row=0, column=1, padx=5)
        
        # Toggle visibility
        self.show_key = tk.BooleanVar(value=False)
        ttk.Checkbutton(key_frame, text="Show", variable=self.show_key, 
                      command=self._toggle_key_visibility).grid(row=0, column=2)
        
        # Get key button
        get_key_frame = ttk.Frame(frame)
        get_key_frame.pack(pady=10)
        
        ttk.Label(get_key_frame, text="Don't have an API key?").grid(row=0, column=0, padx=5)
        
        get_key_button = ttk.Button(get_key_frame, text="Get Key from Hugging Face", 
                                  command=lambda: webbrowser.open_new("https://huggingface.co/settings/tokens"))
        get_key_button.grid(row=0, column=1)
        
        # Skip info
        skip_text = "You can also skip this step and add your API key later in Preferences."
        ttk.Label(frame, text=skip_text, wraplength=500, foreground="gray").pack(pady=20)
    
    def _create_models_page(self, parent):
        """Create the models page content"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Download AI Models", 
                font=("Helvetica", 14)).pack(pady=10)
        
        info_text = (
            "When you start WawaChat, it will download the TinyLlama model.\n"
            "This will happen automatically on first use."
        )
        ttk.Label(frame, text=info_text, wraplength=500).pack(pady=10)
        
        # Model info
        model_info_frame = ttk.LabelFrame(frame, text="Default Model Information")
        model_info_frame.pack(pady=20, fill=tk.X)
        
        ttk.Label(model_info_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(model_info_frame, text="TinyLlama-1.1B-Chat-v1.0").grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(model_info_frame, text="Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(model_info_frame, text="~600 MB").grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(model_info_frame, text="First Download Time:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(model_info_frame, text="~1-3 minutes (depends on your internet speed)").grid(row=2, column=1, sticky=tk.W)
        
        # Storage location
        storage_frame = ttk.LabelFrame(frame, text="Storage Location")
        storage_frame.pack(pady=10, fill=tk.X)
        
        try:
            import huggingface_hub
            cache_dir = huggingface_hub.constants.HUGGINGFACE_HUB_CACHE
            ttk.Label(storage_frame, text=f"Models will be stored in:\n{cache_dir}", 
                   wraplength=500).pack(padx=5, pady=5)
        except:
            ttk.Label(storage_frame, text="Models will be stored in the default Hugging Face cache directory.",
                   wraplength=500).pack(padx=5, pady=5)
    
    def _create_complete_page(self, parent):
        """Create the setup complete page content"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Setup Complete!", 
                font=("Helvetica", 16, "bold")).pack(pady=20)
        
        complete_text = (
            "You've successfully set up WawaChat.\n\n"
            "Click 'Finish' to start using the application."
        )
        ttk.Label(frame, text=complete_text, wraplength=500, justify=tk.CENTER).pack(pady=20)
        
        # Tips
        tips_frame = ttk.LabelFrame(frame, text="Tips")
        tips_frame.pack(pady=10, fill=tk.X)
        
        tips = [
            "You can change your API key later in the Preferences menu",
            "Adjust model parameters in the side panel to customize responses",
            "First model download may take a few minutes"
        ]
        
        for i, tip in enumerate(tips):
            ttk.Label(tips_frame, text=f"• {tip}", wraplength=450).pack(anchor=tk.W, padx=5, pady=2)
