# WawaChat

A lightweight desktop chat application powered by TinyLlama for local AI conversation.

![WawaChat Screenshot](screenshot.png)

## Features

- Chat interface powered by TinyLlama LLM
- Customizable generation parameters
- Cross-platform desktop application
- Runs locally for privacy

## Installation

### Prerequisites

- Python 3.8 or higher
- GPU recommended for faster inference (but CPU works too)

### Setup

#### Option 1: Using the setup script (recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wawachat.git
cd wawachat
```

2. Run the setup script:
```bash
# For macOS/Linux
chmod +x setup.sh
./setup.sh

# For Windows
./setup.sh
```

3. Edit the `.env` file to add your Hugging Face token:
```
HUGGINGFACE_TOKEN=your_token_here
```

4. Run the application:
```bash
python wawachat-v1.5.py
```

#### Option 2: Manual setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wawachat.git
cd wawachat
```

2. Create and activate a virtual environment (optional but recommended):
```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Hugging Face token:
```
HUGGINGFACE_TOKEN=your_token_here
```

5. Run the application:
```bash
python wawachat-v1.5.py
```

## Usage

1. Type your message in the input box and press Enter to send
2. The AI will respond in the conversation window
3. Adjust generation parameters in the side panel as needed
4. Use the Clear button to reset the conversation

## Configuration

Adjust the following parameters to customize the AI's responses:

- **Max new tokens**: Maximum number of tokens to generate
- **Temperature**: Controls randomness (higher = more random)
- **Top P**: Controls diversity via nucleus sampling
- **Num Beams**: Number of beams for beam search
- **Truncation**: Whether to truncate input tokens
- **Do Sample**: Whether to use sampling
- **Early Stopping**: Whether to stop generation when all beams are finished

## Troubleshooting

### ModuleNotFoundError: No module named 'dotenv'
This error occurs when the python-dotenv package is not installed. Fix it by running:
```bash
pip install python-dotenv
```

### Other missing dependencies
If you encounter other missing dependencies, make sure to install all requirements:
```bash
pip install -r requirements.txt
```

### The model is loading very slowly
TinyLlama is a large language model. The first time you run the application, it will download the model which may take some time depending on your internet connection. Subsequent runs will be faster.

## License

MIT

## Acknowledgments

- [TinyLlama](https://github.com/jzhang38/TinyLlama) for the language model
- [Hugging Face](https://huggingface.co/) for model hosting
