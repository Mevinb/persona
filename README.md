# 🚀 NOVA - Personal AI Assistant

A fully local, modular personal AI assistant built in Python that gives you complete control over your AI experience.

## ✨ Features

- 🧠 **Local AI Brain**: Uses open-source LLMs (Mistral 7B) with memory-efficient quantization
- 🎙️ **Voice Interaction**: Speech-to-text with faster-whisper and text-to-speech with pyttsx3
- 💭 **Persistent Memory**: Remembers conversations, user preferences, and personal facts
- 🎯 **Smart Intent Detection**: Understands natural language commands for system tasks
- 🔧 **System Control**: Open applications, search web, set reminders, execute commands
- 🎨 **Customizable Personality**: Configurable tone, style, and behavioral traits
- 🔄 **Fine-tuning Ready**: LoRA-based fine-tuning to adapt to your communication style
- 💬 **Multiple Interfaces**: Text UI, voice mode, or hybrid interaction
- 🔐 **Privacy-First**: Runs entirely offline, no data leaves your system

## 📁 Project Structure

```
nova/
├── core/                      # Core AI components
│   ├── brain.py              # LLM loading and inference
│   ├── memory.py             # Conversation and persistent memory
│   ├── intents.py            # Intent recognition and actions
│   └── personality.yaml      # Assistant personality config
├── io/                       # Input/output modules  
│   ├── listener.py           # Speech-to-text (faster-whisper)
│   ├── speaker.py            # Text-to-speech (pyttsx3)
│   └── text_ui.py            # Command-line interface
├── data/                     # Configuration and databases
│   ├── config.yaml           # Main configuration
│   ├── memory.db             # SQLite conversation database
│   └── nova.log              # Application logs
├── fine_tune/                # Fine-tuning tools and data
│   ├── dataset.jsonl         # Training conversation examples
│   ├── fine_tuner.py         # LoRA fine-tuning scripts
│   └── README.md             # Fine-tuning documentation
└── main.py                   # Main application entry point
```

## 🛠️ Installation

### Prerequisites

- **Python 3.9+**
- **8GB+ RAM** (16GB recommended for optimal performance)
- **CUDA GPU** (optional but recommended for faster inference)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd personal-assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run NOVA**:
   ```bash
   python main.py
   ```

### GPU Setup (Recommended)

For faster inference, install PyTorch with CUDA support:

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 🚀 Usage

### Starting NOVA

```bash
# Text-only interface (default)
python main.py --interface text

# Voice-only interface
python main.py --interface voice

# Hybrid text + voice interface
python main.py --interface hybrid

# Debug mode
python main.py --debug
```

### Text Interface Commands

While in the text interface, you can use these commands:

- `/help` - Show available commands
- `/status` - Display system status
- `/memory` - View memory statistics
- `/history [n]` - Show conversation history
- `/settings` - Modify interface settings
- `/voice` - Toggle voice mode
- `/clear` - Clear screen
- `/save [filename]` - Save conversation
- `/exit` or `/quit` - Exit NOVA

### Natural Language Examples

```
You: Hello, what's your name?
Nova: Hi there! I'm Nova, your personal AI assistant...

You: Open Chrome
Nova: I'll open Chrome for you right now. *opens Chrome browser*

You: Set a reminder to call mom in 2 hours  
Nova: I'll set a reminder for you to call mom in 2 hours...

You: What's 15 * 8?
Nova: 15 * 8 = 120

You: My name is Alex and I'm a software developer
Nova: Nice to meet you, Alex! I'll remember that you're a software developer...
```

## ⚙️ Configuration

Edit `data/config.yaml` to customize NOVA's behavior:

### Key Settings

```yaml
# AI Model Settings
model:
  name: "mistralai/Mistral-7B-v0.1"
  temperature: 0.7
  quantization: true

# Voice Settings  
voice:
  enabled: true
  gender: "female"
  rate: 180

# Listening Settings
listening:
  wake_word: "nova"
  continuous_mode: false

# Memory Settings
memory:
  max_session_history: 50
  importance_threshold: 2
```

### Personality Customization

Modify `core/personality.yaml` to change NOVA's personality:

```yaml
traits:
  - "friendly"
  - "witty" 
  - "helpful"
  - "curious"

tone: "conversational"
style: "warm but professional"
```

## 🎯 Intent System

NOVA can understand and execute various types of commands:

### System Control
- "open chrome" → Opens Chrome browser
- "close notepad" → Closes Notepad
- "execute dir" → Runs directory listing

### Information
- "what time is it" → Shows current time
- "calculate 15 * 8" → Performs calculation
- "search for python tutorials" → Opens web search

### Memory & Preferences
- "remember my name is Alex" → Stores user fact
- "set my preferred language to English" → Saves preference

### File Operations
- "create file test.txt" → Creates new file
- "open document.pdf" → Opens file

## 🧠 Memory System

NOVA maintains several types of memory:

- **Session Memory**: Current conversation context
- **Conversation History**: Stored chat logs with importance ratings
- **User Facts**: Personal information (name, job, preferences)
- **Preferences**: System and behavior settings

Memory is automatically managed with configurable retention policies.

## 🔧 Fine-tuning

Customize NOVA's responses using LoRA fine-tuning:

1. **Add training examples** to `fine_tune/dataset.jsonl`
2. **Run fine-tuning**:
   ```bash
   cd fine_tune
   python fine_tuner.py
   ```
3. **Update config** to use your fine-tuned model

See `fine_tune/README.md` for detailed instructions.

## 🏗️ Architecture

### Core Components

- **Brain**: Manages LLM loading, inference, and response generation
- **Memory**: Handles conversation history and user data persistence  
- **Intents**: Detects user intentions and maps to system actions
- **Listener**: Speech-to-text using faster-whisper
- **Speaker**: Text-to-speech using pyttsx3
- **TextUI**: Command-line interface with rich features

### Key Design Principles

- **Modularity**: Each component is independent and replaceable
- **Privacy**: All processing happens locally
- **Efficiency**: Optimized for consumer hardware
- **Extensibility**: Easy to add new features and capabilities
- **User Control**: Comprehensive configuration options

## 🛡️ Privacy & Security

- ✅ **Fully Local**: No data sent to external services
- ✅ **Offline Capable**: Works without internet connection
- ✅ **Open Source**: Complete transparency and auditability
- ✅ **User Controlled**: You own and control all data
- ✅ **Configurable**: Adjust privacy settings to your comfort

## 🔮 Future Enhancements

- 📱 **GUI Interface**: Modern desktop application with customtkinter
- 🌐 **Web Interface**: Browser-based control panel
- 🔍 **Vector Search**: Advanced semantic memory with ChromaDB
- 📅 **Calendar Integration**: Advanced scheduling and reminders
- 🌍 **Multi-language**: Support for additional languages
- 🤖 **Plugin System**: Third-party extensions and integrations
- 📊 **Analytics**: Usage insights and optimization suggestions

## 🐛 Troubleshooting

### Common Issues

**Model loading fails**:
- Ensure you have enough RAM (8GB+)
- Try enabling quantization in config
- Check CUDA installation for GPU acceleration

**Voice recognition not working**:
- Install `portaudio` dependencies
- Check microphone permissions
- Verify audio device configuration

**Performance issues**:
- Enable GPU acceleration
- Reduce model size or enable quantization
- Close unnecessary applications

### Debug Mode

Run with `--debug` for detailed logging:
```bash
python main.py --debug
```

Check logs in `data/nova.log` for detailed error information.

## 📄 License

This project is open source. See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

- 📚 **Documentation**: Check this README and inline code comments
- 🐛 **Issues**: Open GitHub issues for bugs and feature requests
- 💬 **Discussions**: Join GitHub Discussions for questions and ideas

---

**Built with ❤️ for AI enthusiasts who value privacy and control.**#   p e r s o n a  
 