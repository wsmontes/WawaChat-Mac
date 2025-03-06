import tkinter as tk
from tkinter import ttk

def setup_conversation_ui(self):
    """Set up the conversation UI components."""
    # Conversation frame and text box
    conversation_frame = tk.Frame(self.chat_frame)
    conversation_frame.pack(pady=10, expand=True, fill=tk.BOTH)
    conversation_frame.pack_propagate(False)

    self.conversation_history = tk.Text(conversation_frame, height=20, width=50, wrap=tk.WORD)
    self.conversation_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.conversation_history.config(state=tk.DISABLED)
    
    # Add syntax highlighting for user vs AI messages
    self.conversation_history.tag_configure("user_msg", foreground="blue")
    self.conversation_history.tag_configure("ai_msg", foreground="green")

    # Scrollbar
    conversation_scrollbar = tk.Scrollbar(conversation_frame)
    conversation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.conversation_history.config(yscrollcommand=conversation_scrollbar.set)
    conversation_scrollbar.config(command=self.conversation_history.yview)

    # Input frame and entry
    input_frame = tk.Frame(self.chat_frame)
    input_frame.pack(pady=5, padx=5, fill=tk.X)

    self.new_message_input = tk.Entry(input_frame)
    self.new_message_input.pack(side=tk.LEFT, fill=tk.X, padx=(0, 5), pady=5, expand=True)
    self.new_message_input.bind("<Return>", self.send_message)

    # Send button
    send_button = tk.Button(input_frame, text="Send", command=lambda: self.send_message(None))
    send_button.pack(side=tk.RIGHT, pady=5)

    # Status bar
    self.status_bar = ttk.Label(self.chat_frame, text="Loading...", relief=tk.SUNKEN, anchor="w")
    self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2, padx=2)
