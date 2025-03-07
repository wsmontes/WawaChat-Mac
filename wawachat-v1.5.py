import torch
import tkinter as tk
from tkinter import ttk, messagebox
from transformers import pipeline
import threading
import time
import os
import sys
import json

# Try to import optional dependencies with graceful fallbacks
try:
    import huggingface_hub
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    print("Warning: huggingface_hub not installed. Some features may be limited.")

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not installed. Please install with: pip install python-dotenv")
    print("Continuing without .env support...")

# Default model list - can be expanded
DEFAULT_MODELS = [
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "facebook/opt-125m",
    "microsoft/phi-1_5",
    "google/gemma-2b"
]

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Get Hugging Face token from environment variable instead of hardcoding it
if HUGGINGFACE_AVAILABLE:
    huggingface_token = os.environ.get("HUGGINGFACE_TOKEN")
    if huggingface_token:
        huggingface_hub.login(token=huggingface_token)
    else:
        print("Warning: HUGGINGFACE_TOKEN not found in environment variables.")
        print("Some models may not be available. Set this in a .env file or as an environment variable.")

# Import the model manager module
try:
    from model_manager_ui import ModelManagerUI
    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    MODEL_MANAGER_AVAILABLE = False
    print("Warning: Model Manager UI modules not found. Model management features will be disabled.")

class WawaChatApplication:
    def __init__(self):
        # Load configuration
        self.config = self.load_config()
        
        # Create the main window first
        self.window = tk.Tk()
        self.window.title("WawaChat")
        
        # Initialize all variables needed for UI and theme before UI setup
        self.pipe = None
        self.model_initialized = threading.Event()
        self.selected_model = tk.StringVar(self.window)
        self.selected_model.set(self.config.get("model", DEFAULT_MODELS[0]))
        self.theme_mode = self.config.get("theme", "light")
        self.chat_history = []
        self.download_progress = 0
        self.download_status = "Idle"
        
        # Complete the rest of the UI setup
        self.initialize_ui()
        
        # Set up model change handler after UI is initialized
        self.selected_model.trace_add("write", self.on_model_changed)
        
        # Start model initialization
        self.update_status("Initializing model...")
        threading.Thread(target=self.initialize_model, daemon=True).start()

    def load_config(self):
        """Load configuration from file or return default config"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        # Default config
        return {
            "model": DEFAULT_MODELS[0],
            "theme": "light"
        }

    def save_config(self):
        """Save current configuration to file"""
        config = {
            "model": self.selected_model.get(),
            "theme": self.theme_mode
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            self.update_status(f"Error saving config: {e}")

    def on_model_changed(self, *args):
        """Handle model selection change"""
        new_model = self.selected_model.get()
        if self.pipe is not None and new_model != self.config.get("model"):
            self.update_status(f"Model changed to {new_model}. Restart required to apply.")
            # Save the new selection
            self.config["model"] = new_model
            self.save_config()

    def initialize_ui(self):
        # Don't create Tk instance again, just continue with UI setup
        # Set app icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.window.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Set window size
        window_width = 815
        window_height = 450
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate position for the window to be centered
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)

        # Set the window's position to the center of the screen
        self.window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.window.resizable(True, True)

        # Create main container frames
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(10, 5), pady=10)
        
        self.settings_frame = tk.Frame(self.main_frame, width=200)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 10), pady=10)
        self.settings_frame.pack_propagate(False)

        # Conversation UI components
        self.setup_conversation_ui()

        # Settings UI components
        self.setup_settings_ui()
        
        # Apply theme after all UI elements are created
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        if self.theme_mode == "dark":
            bg_color = "#2d2d2d"
            fg_color = "#ffffff"
            text_bg = "#3d3d3d"
            button_bg = "#555555"
            button_fg = "#ffffff"
        else:  # light mode
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            text_bg = "#ffffff"
            button_bg = "#e0e0e0"
            button_fg = "#000000"
        
        # Apply to main window and frames
        self.window.config(bg=bg_color)
        self.main_frame.config(bg=bg_color)
        self.chat_frame.config(bg=bg_color)
        self.settings_frame.config(bg=bg_color)
        
        # Apply to conversation elements
        self.conversation_history.config(bg=text_bg, fg=fg_color)
        self.new_message_input.config(bg=text_bg, fg=fg_color)
        
        # Special handling for ttk widgets
        # For ttk widgets, we need to use a style
        style = ttk.Style()
        
        # Configure the ttk.Label style
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        
        # Apply to status bar (ttk.Label)
        self.status_bar.configure(style='TLabel')
        
        # Update settings widgets if they exist
        for widget in self.settings_frame.winfo_children():
            try:
                if isinstance(widget, tk.Label):
                    # Regular tk.Label supports bg color and fg color
                    widget.config(bg=bg_color, fg=fg_color)
                elif isinstance(widget, ttk.Label):
                    # ttk.Label styling is handled by the style above
                    pass
                elif isinstance(widget, tk.Entry):
                    # Regular tk.Entry supports bg color and fg color
                    widget.config(bg=text_bg, fg=fg_color)
                elif isinstance(widget, ttk.Entry):
                    # Can't directly style ttk.Entry this way
                    pass
                elif isinstance(widget, tk.Button):
                    widget.config(bg=button_bg, fg=button_fg)
                elif isinstance(widget, tk.Checkbutton):
                    widget.config(bg=bg_color, fg=fg_color, selectcolor=button_bg)
                elif isinstance(widget, tk.Frame):
                    widget.config(bg=bg_color)
            except tk.TclError:
                # Skip widgets that don't support the attempted configuration
                pass
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()
        # Update theme in config
        self.config["theme"] = self.theme_mode
        self.save_config()

    def setup_conversation_ui(self):
        # Conversation frame and text box
        conversation_frame = tk.Frame(self.chat_frame)
        conversation_frame.pack(pady=10, expand=True, fill=tk.BOTH)
        conversation_frame.pack_propagate(False)

        self.conversation_history = tk.Text(conversation_frame, height=20, width=50)
        self.conversation_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.conversation_history.config(state=tk.DISABLED)

        # Scrollbar
        conversation_scrollbar = tk.Scrollbar(conversation_frame)
        conversation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversation_history.config(yscrollcommand=conversation_scrollbar.set)
        conversation_scrollbar.config(command=self.conversation_history.yview)

        # Input frame and entry
        input_frame = tk.Frame(self.chat_frame)
        input_frame.pack(pady=5, padx=5, anchor='e')

        self.new_message_input = tk.Entry(input_frame, width=50)
        self.new_message_input.pack(side=tk.LEFT, fill=tk.X, padx=(0, 5), pady=5, expand=True)
        self.new_message_input.bind("<Return>", self.send_message)

        # Status bar
        self.status_bar = ttk.Label(self.chat_frame, text="Loading...", relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2, padx=2)

    def setup_settings_ui(self):
        def add_setting(setting_name, default_value, row, setting_type="entry"):
            ttk.Label(self.settings_frame, text=setting_name).grid(row=row, column=1, sticky='w', pady=2)

            if setting_type == "entry":
                entry = tk.Entry(self.settings_frame)
                entry.insert(0, str(default_value))
                entry.grid(row=row, column=2, pady=2)
                return entry
            elif setting_type == "select":
                var = tk.StringVar(self.settings_frame)
                var.set(str(default_value))
                select = ttk.Combobox(self.settings_frame, textvariable=var, values=("True", "False"))
                select.grid(row=row, column=2, pady=2)
                return var

        # Model selection dropdown
        ttk.Label(self.settings_frame, text="Model:").grid(row=0, column=1, sticky='w', pady=2)
        model_dropdown = ttk.Combobox(self.settings_frame, textvariable=self.selected_model, values=DEFAULT_MODELS)
        model_dropdown.grid(row=0, column=2, pady=2, sticky='ew')
        
        # Allow custom model input
        model_dropdown['values'] = DEFAULT_MODELS
        model_dropdown.bind('<KeyRelease>', lambda e: self.selected_model.set(model_dropdown.get()))
        
        # Add a separator after model selection
        ttk.Separator(self.settings_frame, orient='horizontal').grid(
            row=1, column=1, columnspan=2, sticky='ew', pady=5)

        # Numeric and text parameters - starting from row 2 now
        self.settings = {
            "max_new_tokens": add_setting("Max new tokens", 50, 2),
            "temperature": add_setting("Temperature", 0.5, 3),
            "top_p": add_setting("Top P", 0.9, 4),
            "num_beams": add_setting("Num Beams", 2, 5),
        }

        # Boolean parameters with select dropdowns
        self.boolean_settings = {
            "truncation": add_setting("Truncation", "True", 6, "select"),
            "do_sample": add_setting("Do Sample", "True", 7, "select"),
            "early_stopping": add_setting("Early Stopping", "True", 8, "select"),
        }

        # Checkboxes for including/excluding parameters
        self.include_settings = {}
        row = 9
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

        # Add a separator before buttons
        row += 1
        ttk.Separator(self.settings_frame, orient='horizontal').grid(
            row=row, column=1, columnspan=2, sticky='ew', pady=10)
        row += 1

        # Button frame for controls
        button_frame = tk.Frame(self.settings_frame)
        button_frame.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)
        row += 1

        # Clear button
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_conversation)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle button
        theme_btn = tk.Button(button_frame, text="Toggle Theme", command=self.toggle_theme)
        theme_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add a Model Management button if available
        if MODEL_MANAGER_AVAILABLE:
            model_mgr_btn = tk.Button(self.settings_frame, text="Manage Model Cache", 
                                    command=self.open_model_manager)
            model_mgr_btn.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5)

    def initialize_model(self):
        """Initialize the model with Mac-optimized settings"""
        try:
            self.update_status("Downloading model (this may take a while)...")
            
            # Create a progress tracker using a separate thread
            progress_thread = threading.Thread(target=self.track_download_progress, daemon=True)
            progress_thread.start()
            
            try:
                # Initialize the pipeline with the selected model
                model_name = self.selected_model.get()
                
                # Mac-optimized model settings - FIXED: removed duplicate torch_dtype
                self.pipe = pipeline(
                    "text-generation", 
                    model=model_name, 
                    torch_dtype=torch.float32,  # float32 is more stable on Mac CPUs
                    device_map="cpu",  # Force CPU usage for maximum stability on Mac
                    model_kwargs={
                        "low_cpu_mem_usage": True,
                        "use_cache": True,
                        "offload_folder": None,  # Avoid disk offloading which can be slow on Mac
                        # Removed duplicate torch_dtype parameter that was causing the error
                    }
                )
                
                # Perform a warmup inference for faster subsequent generation
                self.warmup_model()
                
                # Stop the progress tracking
                self.download_status = "Complete"
                self.model_initialized.set()
                self.update_status(f"Model {model_name} ready.")
            except Exception as e:
                self.download_status = "Error"
                self.update_status(f"Error initializing model: {str(e)}")
                print(f"Model initialization error: {str(e)}")
        except Exception as e:
            self.download_status = "Error"
            self.update_status(f"Error in model initialization: {str(e)}")
            print(f"Critical error in model thread: {str(e)}")

    def warmup_model(self):
        """Perform a quick inference to initialize the model's caches"""
        try:
            # Simple warmup to prime internal caches and compile any operations
            _ = self.pipe("Hello", max_new_tokens=5, do_sample=False, num_beams=1)
            print("Model warmup completed")
        except Exception as e:
            print(f"Model warmup failed: {e}")

    def track_download_progress(self):
        """Track and display model download progress"""
        self.download_status = "Downloading"
        progress_chars = ["|", "/", "-", "\\"]
        i = 0
        
        while self.download_status == "Downloading":
            self.update_status(f"Downloading model {progress_chars[i]} (this may take a while)")
            i = (i + 1) % len(progress_chars)
            time.sleep(0.5)

    def open_model_manager(self):
        """Open the model manager window"""
        if MODEL_MANAGER_AVAILABLE:
            ModelManagerUI(self.window)
        else:
            messagebox.showwarning("Not Available", 
                                 "Model Manager is not available. Check console for details.")

    def send_message(self, event=None):
            new_message = self.new_message_input.get()
            if not new_message.strip():
                return

            self.new_message_input.delete(0, tk.END)
            self.update_conversation_history("You: " + new_message + "\n")
            self.update_status("Generating response...")
            threading.Thread(target=self.generate_and_display_response, args=(new_message,)).start()

    def update_conversation_history(self, message):
        def append_message():
            self.conversation_history.config(state=tk.NORMAL)
            self.conversation_history.insert(tk.END, message)
            self.conversation_history.config(state=tk.DISABLED)
            # Automatically scroll to the end to show the latest message
            self.conversation_history.yview(tk.END)

        # Schedule the update to be run in the main thread
        self.window.after(0, append_message)


    def generate_and_display_response(self, input_text):
        self.update_status("Generating response...")
        self.new_message_input.delete(0, tk.END)
        self.update_conversation_history("You: " + input_text + "\n")

        if not self.model_initialized.is_set():
            print("Model is not yet initialized. Please wait...")
            return

        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": input_text})

        # Offload the response generation to a background thread
        threading.Thread(target=self.process_response, daemon=True).start()

    def process_response(self):
        try:
            # Get the message that needs a response
            self.update_ui_with_status("Generating response...")
            
            # Set a timeout for the generation
            MAX_GENERATION_TIME = 30  # seconds
            
            # Retrieve UI settings in the main thread context
            generation_parameters = self.get_generation_parameters()
            
            # Use the tokenizer's chat template method to format the input text
            formatted_chat = self.pipe.tokenizer.apply_chat_template(
                self.chat_history, tokenize=False, add_generation_prompt=True
            )
            
            # Check if formatted_chat is a string
            if not isinstance(formatted_chat, str):
                raise TypeError("The chat history formatting did not return a string.")
            
            # Create a timer to update the UI during generation
            generation_start = time.time()
            
            def update_generation_status():
                elapsed = time.time() - generation_start
                if elapsed < MAX_GENERATION_TIME:
                    self.update_ui_with_status(f"Generating response... ({int(elapsed)}s)")
                    self.window.after(500, update_generation_status)
                else:
                    self.update_ui_with_status("Generation is taking longer than expected...")
            
            # Start the timer
            self.window.after(500, update_generation_status)
            
            # Run the model pipeline and get the response
            response = self.pipe(
                formatted_chat, 
                batch_size=1,  # Process one token at a time to reduce memory usage
                num_workers=1,  # Limit worker threads for Mac stability
                **generation_parameters
            )
            
            # Process the response
            response_text = response[0]['generated_text']
            
            # Add AI response to chat history
            ai_response = self.trim_response(response_text)
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Update the UI with the response
            self.update_ui_with_response(ai_response)
        except Exception as e:
            self.update_ui_with_status(f"Error: {str(e)}")
            print(f"Response generation error: {e}")

    def update_ui_with_response(self, response_text):
        """ Update the conversation history with the AI's response """
        def update():
            self.conversation_history.config(state=tk.NORMAL)
            self.conversation_history.insert(tk.END, "AI: " + response_text + "\n")
            self.conversation_history.config(state=tk.DISABLED)
            self.conversation_history.yview(tk.END)
            self.status_bar.config(text="Model ready.")
        
        # Schedule the update to be run in the main thread
        self.window.after(0, update)

    def update_ui_with_status(self, status_message):
        """ Update the status bar with the provided message """
        def update():
            self.status_bar.config(text=status_message)
        
        # Schedule the update to be run in the main thread
        self.window.after(0, update)

    def trim_response(self, response_text):
        """ Post-process the response to trim unwanted parts """
        # This is a placeholder; adjust the logic as needed for your application
        trimmed_response = response_text.split("</s>")[0]  # Example: Take content before the first end-of-string token
        return trimmed_response


    def get_conversation_history_text(self):
        """Retrieve text from the conversation history Text widget."""
        return self.conversation_history.get("1.0", tk.END).strip()

    def get_chat_history(self):
        # Placeholder: Implement according to how you manage chat history.
        # This should return a list of dictionaries with 'role' and 'content' keys.
        return self.chat_history  # Assuming self.chat_history is a list of message dictionaries.

    def update_status(self, message):
        def update_message():
            self.status_bar.config(text=message)
        
        self.window.after(0, update_message)

    def clear_conversation(self):
        self.conversation_history.config(state=tk.NORMAL)
        self.conversation_history.delete('1.0', tk.END)
        self.conversation_history.config(state=tk.DISABLED)

    def get_generation_parameters(self):
        """Collect generation parameters with Mac-optimized defaults"""
        parameters = {}
        
        # Mac-optimized generation defaults
        mac_defaults = {
            "max_new_tokens": 30,      # Shorter responses for better performance
            "temperature": 0.7,        # Balance between creativity and determinism
            "top_p": 0.92,             # Slightly higher than default for better quality/speed balance
            "num_beams": 1,            # Greedy decoding is much faster on Mac CPUs
            "repetition_penalty": 1.2, # Avoid repetitions without heavy penalties
            "use_cache": True,         # Enable KV-cache for faster generation
            "early_stopping": True,    # Stop when conditions are met
            "do_sample": False,        # Deterministic generation is faster
            "truncation": True,        # Enable truncation
            "pad_token_id": 0,         # Use 0 as padding token for compatibility
        }
        
        # Get values from UI with fallbacks to optimized defaults
        for key in self.settings.keys():
            if self.include_settings[key].get():
                try:
                    # Convert values to appropriate types
                    if key == "max_new_tokens" or key == "num_beams":
                        parameters[key] = int(self.settings[key].get())
                    else:
                        parameters[key] = float(self.settings[key].get())
                except (ValueError, TypeError):
                    parameters[key] = mac_defaults.get(key, 0)
        
        for key in self.boolean_settings.keys():
            if self.include_settings[key].get():
                parameters[key] = self.boolean_settings[key].get() == "True"
        
        # Enforce Mac-friendly limits regardless of user settings
        if parameters.get("max_new_tokens", 0) > 75:  # Cap token generation
            parameters["max_new_tokens"] = 75
        
        if parameters.get("num_beams", 1) > 2:  # Beam search is resource intensive
            parameters["num_beams"] = 2
        
        # Add optimization parameters not in the UI
        if "use_cache" not in parameters:
            parameters["use_cache"] = True
        
        return parameters

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = WawaChatApplication()
    app.run()
