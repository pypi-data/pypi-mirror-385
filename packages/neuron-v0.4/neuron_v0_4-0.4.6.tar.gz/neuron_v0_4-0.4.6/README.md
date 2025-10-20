# Neuron AI Assistant 

A powerful local AI assistant with advanced identity protection, hardware optimization, and comprehensive conversation management.

**Created by:** Dev Patel  
**Version:** 0.4.6

##  Features

-  **Identity Protection**: Built-in safeguards against prompt injection and identity tampering
-  **Hardware Optimization**: Auto-detects CPU, GPU (CUDA), Apple Silicon (MPS), RAM, and VRAM
-  **Multiple Models**: Support for GPT4All (CPU-friendly) and Mistral 7B (GPU-optimized)
-  **Conversation Management**: Save, export, and manage chat history
-  **Config Security**: Cryptographic signing and automatic backups
-  **Error Recovery**: Automatic backup restoration and config migration
-  **Resource Management**: Dynamic token limits and OOM handling
-  **Diagnostic Tools**: Built-in system health checks

##  Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Disk Space**: 20GB free (for model downloads)
- **GPU** (Optional): NVIDIA with CUDA support for better performance

##  Installation

### Option 1: From PyPI (when published)
```bash
pip install neuron-ai-assistant
```

### Option 2: From Source
```bash
# Clone the repository
git clone https://github.com/devpatel/neuron-ai-assistant.git
cd neuron-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Or install with all features
pip install -e .[all]
```

### Option 3: GPU Support
```bash
# For NVIDIA GPU (CUDA 11.8)
pip install torch==2.0.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# For NVIDIA GPU (CUDA 12.1)
pip install torch==2.0.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### Option 4: CPU Only (Smaller)
```bash
pip install torch==2.0.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

##  Quick Start

### First Run
```bash
python neuron_assistant.py
```

On first run, you'll be asked to:
1. Enter your name
2. Select a model (GPT4All or Mistral)
3. Wait for model download (if needed)

### Using the Assistant
```python
# After installation
neuron
# or
neuron-assistant
```

## 💻 Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/clear` | Clear conversation history |
| `/save` | Save conversation to text file |
| `/export` | Export conversation to JSON |
| `/stats` | Show system statistics |
| `/tokens <n>` | Set max tokens (16-1024) |
| `/model` | Change AI model |
| `/migrate` | Fix/update old configs |
| `/diagnose` | Run system diagnostics |
| `/reset` | Reset assistant completely |
| `/exit` | Exit gracefully |

## 🔧 Configuration

The assistant creates these files automatically:
- `config.json` - User and model settings
- `config.sig` - Cryptographic signature
- `models/` - Downloaded AI models
- `backups/` - Config backups (last 5)
- `.neuron.lock` - Instance lock file

## Model Comparison

| Model | Size | RAM | VRAM | Speed | Quality |
|-------|------|-----|------|-------|---------|
| GPT4All-J | 3.5GB | 4GB | 0GB | Fast | Good |
| Mistral 7B | 14GB | 16GB | 12GB | Medium | Excellent |

##  Advanced Usage

### Set HuggingFace Token
```bash
export HF_TOKEN="your_token_here"
python neuron_assistant.py
```

### Custom Token Limit
```python
from neuron_assistant import NeuronAssistant

assistant = NeuronAssistant()
assistant.set_max_tokens(256)
```

### Programmatic Use
```python
from neuron_assistant import NeuronAssistant

# Initialize
assistant = NeuronAssistant(hf_token="optional_token")

# Chat
response = assistant.chat("Hello! How are you?")
print(response)

# Save conversation
assistant.save_history("my_chat.txt")
assistant.export_history_json("my_chat.json")
```

## 🐛 Troubleshooting

### Model Download Fails
```bash
# Check disk space
df -h

# Verify internet connection
ping huggingface.co

# Manual download location
ls models/
```

### Config Corrupted
```bash
# Run diagnostics
# In chat: /diagnose

# Migrate config
# In chat: /migrate

# Last resort - reset
# In chat: /reset
```

### Out of Memory
```bash
# Use smaller model (GPT4All)
# Reduce token limit: /tokens 64
# Clear history: /clear
```

### GPU Not Detected
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip install torch==2.0.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
```

## 🔒 Security Features

- **Creator Lock**: Hardcoded creator name prevents identity theft
- **Config Signing**: RSA signatures verify config integrity
- **Prompt Injection Detection**: Blocks manipulation attempts
- **Output Sanitization**: Removes references to other AI companies
- **Backup System**: Auto-backups before changes

##  License

MIT License - See LICENSE file for details

##  Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

##  Support

- **Issues**: [GitHub Issues](https://github.com/devpatel/neuron-ai-assistant/issues)
- **Email**: dev@example.com
- **Docs**: [Wiki](https://github.com/devpatel/neuron-ai-assistant/wiki)

##  Acknowledgments

- Built with [PyTorch](https://pytorch.org/)
- Uses [Transformers](https://huggingface.co/transformers)
- Supports [GPT4All](https://gpt4all.io/)
- Model: [Mistral AI](https://mistral.ai/)

##  Changelog

### v0.4.6 (Current)
- Advanced identity protection
- Config migration system
- Comprehensive diagnostics
- Improved error handling
- Backup/restore functionality

---

**Made with heart by Dev Patel**