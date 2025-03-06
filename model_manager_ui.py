import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from model_manager import ModelManager

class ModelManagerUI:
    """UI component for managing Hugging Face models cache"""
    
    def __init__(self, parent):
        self.parent = parent
        self.model_manager = ModelManager()
        self.create_window()
        self.load_models()
    
    def create_window(self):
        # Create a new top-level window
        self.window = tk.Toplevel(self.parent)
        self.window.title("Model Cache Manager")
        self.window.geometry("800x500")
        self.window.minsize(600, 400)
        
        # Make it modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Create the main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.window, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create the information frame
        info_frame = ttk.LabelFrame(main_frame, text="Cache Information", padding="5")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Cache directory and size info
        ttk.Label(info_frame, text="Cache Directory:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.cache_dir_label = ttk.Label(info_frame, text=self.model_manager.cache_dir)
        self.cache_dir_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Total Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_size_label = ttk.Label(info_frame, text="Calculating...")
        self.total_size_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Create the models list frame
        models_frame = ttk.LabelFrame(main_frame, text="Downloaded Models", padding="5")
        models_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a treeview for the models list
        self.tree = ttk.Treeview(models_frame, columns=("size", "revision", "modified"), show="headings")
        self.tree.heading("size", text="Size (MB)")
        self.tree.heading("revision", text="Revision")
        self.tree.heading("modified", text="Last Modified")
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.column("revision", width=150)
        self.tree.column("modified", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add a scrollbar to the treeview
        scrollbar = ttk.Scrollbar(models_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Create the buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add the action buttons
        ttk.Button(buttons_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.load_models).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Export Info", command=self.export_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear Cache", command=self.clear_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Update the status
        self.status_var.set("Ready")
    
    def load_models(self):
        """Load model information in a background thread to keep UI responsive"""
        self.status_var.set("Loading models...")
        self.tree.delete(*self.tree.get_children())  # Clear the treeview
        
        def update_ui_with_models(models):
            for model in models:
                self.tree.insert("", tk.END, text=model["repo_id"], 
                               values=(model["size_mb"], model["revision"], model["last_modified"]),
                               tags=(model["repo_id"], model["revision"]))
            self.status_var.set(f"Loaded {len(models)} models")
        
        def update_cache_size(size):
            self.total_size_label.config(text=f"{size} MB")
        
        def load_data():
            # Get the cache size
            size = self.model_manager.get_total_cache_size()
            self.window.after(0, lambda: update_cache_size(size))
            
            # Get the models list
            models = self.model_manager.get_downloaded_models()
            self.window.after(0, lambda: update_ui_with_models(models))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def delete_selected(self):
        """Delete the selected model from the cache"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a model to delete")
            return
        
        item = self.tree.item(selection[0])
        repo_id = item["text"]
        revision = item["values"][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {repo_id}?"):
            self.status_var.set(f"Deleting {repo_id}...")
            
            def do_delete():
                success, msg = self.model_manager.delete_model(repo_id, revision)
                if success:
                    self.window.after(0, lambda: self.tree.delete(selection[0]))
                self.window.after(0, lambda: self.status_var.set(msg))
                self.window.after(1000, self.load_models)  # Reload after a delay
            
            threading.Thread(target=do_delete, daemon=True).start()
    
    def export_info(self):
        """Export model information to a JSON file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Model Information"
        )
        if filepath:
            self.status_var.set("Exporting model information...")
            
            def do_export():
                success, msg = self.model_manager.export_models_info(filepath)
                self.window.after(0, lambda: self.status_var.set(msg))
            
            threading.Thread(target=do_export, daemon=True).start()
    
    def clear_cache(self):
        """Clear the entire model cache"""
        if messagebox.askyesno("Confirm Clear Cache", 
                             "Are you sure you want to clear the entire cache? This will delete all downloaded models."):
            self.status_var.set("Clearing cache...")
            
            def do_clear():
                success, msg = self.model_manager.clear_entire_cache()
                self.window.after(0, lambda: self.status_var.set(msg))
                self.window.after(1000, self.load_models)  # Reload after a delay
            
            threading.Thread(target=do_clear, daemon=True).start()

# For testing the UI directly
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    app = ModelManagerUI(root)
    root.mainloop()
