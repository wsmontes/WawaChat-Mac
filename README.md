# WawaChat

A lightweight chat application powered by TinyLlama, providing a simple interface for conversational AI.

![WawaChat Screenshot](screenshots/wawachat_screenshot.png) <!-- Add a screenshot later -->

## Features

- Interactive chat interface with TinyLlama AI model
- Customizable generation parameters
- Real-time status updates
- Conversation history management
- Simple and intuitive user interface

## Requirements

- Python 3.8 or higher
- PyTorch
- Transformers
- Huggingface Hub

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/WawaChat.git
   cd WawaChat
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Hugging Face API token:
   - Create a `.env` file in the root directory (copy from `.env.example`)
   - Add your Hugging Face token:
     ```
     HUGGINGFACE_TOKEN=your_token_here
     ```
   - You can get your token from https://huggingface.co/settings/tokens

4. Run the application:
   ```
   python wawachat-v1.5.py
   ```

## Usage

1. Launch the application
2. Wait for the model to initialize ("Model ready" will appear in the status bar)
3. Type your message in the input field and press Enter
4. View the AI's response in the conversation window

## Configuration

You can adjust various parameters in the settings panel:
- Max new tokens: Controls the length of the generated response
- Temperature: Controls randomness (higher values = more random)
- Top P: Controls diversity via nucleus sampling
- Num Beams: Number of beams for beam search
- Various boolean parameters like truncation, sampling, and early stopping

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [TinyLlama](https://github.com/jzhang38/TinyLlama)
- Uses Hugging Face Transformers library
