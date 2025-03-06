import torch
import tkinter as tk
from tkinter import ttk
from transformers import pipeline
import threading
import time
import huggingface_hub
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Hugging Face token from environment variable instead of hardcoding it
huggingface_token = os.environ.get("HUGGINGFACE_TOKEN")
if huggingface_token:
    huggingface_hub.login(token=huggingface_token)

class WawaChatApplication:
    def __init__(self):
        self.initialize_ui()
        self.pipe = None
        self.model_initialized = threading.Event()
        self.update_status("Initializing model...")
        threading.Thread(target=self.initialize_model, daemon=True).start()
        # Initialize chat history
        self.chat_history = []

    def initialize_ui(self):
        self.window = tk.Tk()
        self.window.title("WawaChat v1.5")
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
        self.chat_frame = tk.Frame(self.window)
        self.chat_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(10, 5), pady=10)
        
        self.settings_frame = tk.Frame(self.window, width=200)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 10), pady=10)
        self.settings_frame.pack_propagate(False)

        # Conversation UI components
        self.setup_conversation_ui()

        # Settings UI components
        self.setup_settings_ui()

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

        # Numeric and text parameters
        self.settings = {
            "max_new_tokens": add_setting("Max new tokens", 50, 0),
            "temperature": add_setting("Temperature", 0.5, 1),
            "top_p": add_setting("Top P", 0.9, 2),
            "num_beams": add_setting("Num Beams", 2, 3),
        }

        # Boolean parameters with select dropdowns
        self.boolean_settings = {
            "truncation": add_setting("Truncation", "True", 4, "select"),
            "do_sample": add_setting("Do Sample", "True", 5, "select"),
            "early_stopping": add_setting("Early Stopping", "True", 6, "select"),
        }

        # Checkboxes for including/excluding parameters
        self.include_settings = {}
        row = 7
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

        # Clear button
        clear_btn = tk.Button(self.settings_frame, text="Clear", command=self.clear_conversation)
        clear_btn.grid(row=row, columnspan=3, pady=10)


    def initialize_model(self):
        # Initialize the pipeline with TinyLlama settings
        self.pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")
        self.model_initialized.set()
        self.update_status("Model ready.")

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
        # Moved all UI component accesses to the main thread
        input_text = self.new_message_input.get()

        try:
            # Use the tokenizer's chat template method to format the input text
            formatted_chat = self.pipe.tokenizer.apply_chat_template(self.chat_history, tokenize=False, add_generation_prompt=True)

            # Collect settings from the UI and use them to generate the response
            generation_parameters = self.get_generation_parameters()

            response = self.pipe(formatted_chat, **generation_parameters)
            response_text = response[0]['generated_text']

            # Schedule the conversation history update to be run in the main thread
            self.window.after(0, lambda: self.update_conversation_history("AI: " + response_text + "\n"))
        except Exception as e:
            self.window.after(0, lambda: self.update_status("Error: " + str(e)))
        else:
            self.window.after(0, lambda: self.update_status("Model ready."))

    def get_generation_parameters(self):
        # Retrieve generation parameters from UI components
        # This function is called within the thread handling response generation
        parameters = {
            "max_new_tokens": int(self.settings['max_new_tokens'].get()),
            "temperature": float(self.settings['temperature'].get()),
            "top_p": float(self.settings['top_p'].get()),
            "num_beams": int(self.settings['num_beams'].get()),
        }
        # Add boolean settings if necessary, converting them from string to boolean
        parameters.update({
            "truncation": self.boolean_settings['truncation'].get() == 'True',
            "do_sample": self.boolean_settings['do_sample'].get() == 'True',
            "early_stopping": self.boolean_settings['early_stopping'].get() == 'True',
        })
        return parameters

    def process_response(self):
        try:
            # Retrieve UI settings in the main thread context
            generation_parameters = self.get_generation_parameters()

            # Use the tokenizer's chat template method to format the input text
            formatted_chat = self.pipe.tokenizer.apply_chat_template(self.chat_history, tokenize=False, add_generation_prompt=True)

            # Check if formatted_chat is a string
            if not isinstance(formatted_chat, str):
                raise TypeError("The chat history formatting did not return a string.")

            # Run the model pipeline and get the response
            response = self.pipe(formatted_chat, **generation_parameters)
            response_text = response[0]['generated_text']

            # Trim the response to the first section if it's too long or contains unwanted parts
            response_text = self.trim_response(response_text)

            # Update the UI with the response
            self.update_ui_with_response(response_text)

        except Exception as e:
            self.update_ui_with_status(f"Error: {str(e)}")

    def update_ui_with_response(self, response_text):
        """ Update the conversation history with the AI's response """
        # This function should only be called from the main thread using `self.window.after`
        self.conversation_history.insert(tk.END, "AI: " + response_text + "\n")
        self.conversation_history.yview(tk.END)
        self.status_bar.config(text="Model ready.")

    def update_ui_with_status(self, status_message):
        """ Update the status bar with the provided message """
        # This function should only be called from the main thread using `self.window.after`
        self.status_bar.config(text=status_message)

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

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = WawaChatApplication()
    app.run()
