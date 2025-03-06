import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os

class PreferencesDialog:
    def __init__(self, parent, credentials_manager):
        self.parent = parent
        self.credentials_manager = credentials_manager
        self.create_dialog()
        
    def create_dialog(self):
        """Create the preferences dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("WawaChat Preferences")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make it modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create API Keys tab
        api_frame = ttk.Frame(notebook, padding=10)
        notebook.add(api_frame, text="API Keys")
        
        # Create About tab
        about_frame = ttk.Frame(notebook, padding=10)
        notebook.add(about_frame, text="About")
        
        # Setup API keys tab
        self.setup_api_keys_tab(api_frame)
        
        # Setup About tab
        self.setup_about_tab(about_frame)
        
        # Center the dialog
        self.dialog.update_idletasks()
        w = self.dialog.winfo_width()
        h = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - w) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - h) // 2
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    def setup_api_keys_tab(self, parent):
        """Setup the API Keys tab content"""
        # Hugging Face section
        hf_frame = ttk.LabelFrame(parent, text="Hugging Face API", padding=10)
        hf_frame.pack(fill=tk.X, pady=5)
        
        # Current status
        current_key = self.credentials_manager.get_api_key()
        status_text = "API Key: " + ("Configured" if current_key else "Not Configured")
        ttk.Label(hf_frame, text=status_text).pack(anchor=tk.W)
        
        # API Key entry
        key_frame = ttk.Frame(hf_frame)
        key_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(key_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W)
        
        self.api_key_var = tk.StringVar(value=current_key if current_key else "")
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=40, show="•")
        self.api_key_entry.grid(row=0, column=1, padx=5)
        
        # Toggle visibility button
        self.show_key = tk.BooleanVar(value=False)
        ttk.Checkbutton(key_frame, text="Show", variable=self.show_key, 
                      command=self._toggle_key_visibility).grid(row=0, column=2)
        
        # Help text and link
        help_frame = ttk.Frame(hf_frame)
        help_frame.pack(fill=tk.X, pady=5)
        
        help_text = ("An API key is required to download models from Hugging Face.\n"
                   "If you don't have one, you can get it from your Hugging Face account settings.")
        ttk.Label(help_frame, text=help_text, wraplength=400, justify=tk.LEFT).pack(anchor=tk.W)
        
        link_text = "Click here to get your Hugging Face API key"
        link_label = ttk.Label(help_frame, text=link_text, foreground="blue", cursor="hand2")
        link_label.pack(anchor=tk.W, pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://huggingface.co/settings/tokens"))
        
        # Storage options
        storage_frame = ttk.LabelFrame(parent, text="Storage Options", padding=10)
        storage_frame.pack(fill=tk.X, pady=10)
        
        self.use_keyring = tk.BooleanVar(value=self.credentials_manager.config.get("use_keyring", True))
        ttk.Radiobutton(storage_frame, text="Store API key securely in system keyring (recommended)",
                      variable=self.use_keyring, value=True).pack(anchor=tk.W)
        ttk.Radiobutton(storage_frame, text="Store API key in configuration file (less secure)",
                      variable=self.use_keyring, value=False).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save_api_key).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Remove Key", command=self._delete_api_key).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Test Connection", command=self._test_api_key).pack(side=tk.RIGHT, padx=5)
    
    def setup_about_tab(self, parent):
        """Setup the About tab content"""
        # App info
        app_frame = ttk.Frame(parent)
        app_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(app_frame, text="WawaChat", font=("Helvetica", 16, "bold")).pack(pady=(20, 5))
        ttk.Label(app_frame, text="A lightweight desktop AI chat application").pack()
        ttk.Label(app_frame, text="Powered by TinyLlama and Hugging Face").pack(pady=(0, 20))
        
        # Version info
        version_frame = ttk.Frame(app_frame)
        version_frame.pack(fill=tk.X)
        
        ttk.Label(version_frame, text="Version:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(version_frame, text="1.0.0").grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(version_frame, text="Author:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Label(version_frame, text="Wagner Silva Montes").grid(row=1, column=1, sticky=tk.W)
        
        # Links
        link_frame = ttk.Frame(app_frame)
        link_frame.pack(fill=tk.X, pady=20)
        
        github_link = ttk.Label(link_frame, text="GitHub Repository", foreground="blue", cursor="hand2")
        github_link.pack()
        github_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/yourusername/wawachat"))
        
        # Copyright
        ttk.Label(app_frame, text="© 2023 All rights reserved").pack(side=tk.BOTTOM, pady=10)
    
    def _toggle_key_visibility(self):
        """Toggle visibility of the API key in the entry field"""
        if self.show_key.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="•")
    
    def _save_api_key(self):
        """Save the API key"""
        api_key = self.api_key_var.get().strip()
        
        # Update keyring preference first
        self.credentials_manager.set_keyring_preference(self.use_keyring.get())
        
        # Then save the API key
        success, message = self.credentials_manager.set_api_key(api_key)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def _delete_api_key(self):
        """Delete the stored API key"""
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the API key?"):
            success, message = self.credentials_manager.delete_api_key()
            if success:
                self.api_key_var.set("")
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
    
    def _test_api_key(self):
        """Test the API key by trying to authenticate with Hugging Face"""
        api_key = self.api_key_var.get().strip()
        
        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key first")
            return
            
        # Display a busy cursor
        self.dialog.config(cursor="watch")
        self.dialog.update()
        
        try:
            import huggingface_hub
            
            try:
                # Temporarily login to test the token
                huggingface_hub.login(token=api_key)
                
                # Check if login worked by trying to get user info
                user_info = huggingface_hub.whoami()
                
                messagebox.showinfo("Success", f"API key is valid! Logged in as: {user_info['name']}")
            except Exception as e:
                messagebox.showerror("Error", f"API key validation failed: {str(e)}")
        except ImportError:
            messagebox.showerror("Error", "Hugging Face Hub package is not installed")
        finally:
            # Restore normal cursor
            self.dialog.config(cursor="")
