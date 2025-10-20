# WATBOT - WhatsApp & Instagram Automation Bot

## Quick Links

- 📚 **Documentation**: [README.md](README.md)
- 🚀 **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- 📦 **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- 💡 **Examples**: [examples/](examples/)

## Installation & Usage

### Method 1: Interactive (Easiest)
```bash
python start.py
```
Follow the prompts!

### Method 2: Python Script
```python
from watbot import WhatsAppBot

bot = WhatsAppBot()
bot.start()
```

### Method 3: Command Line
```bash
watbot start
```

### Method 4: Custom Config
```python
from watbot import WhatsAppBot, BotConfig

config = BotConfig()
config.whatsapp.monitor_contacts = ["Mom", "Dad"]
config.ai.personality = "friendly and helpful"

bot = WhatsAppBot(config=config)
bot.start()
```

## Features

✅ **Implemented**
- WhatsApp automation with AI responses
- Context-aware conversations
- Multiple contact monitoring
- Debug mode
- Headless/headed browser support
- Custom AI personalities
- Session persistence
- Config file support
- CLI interface
- Python library API

🚧 **Coming Soon**
- Instagram automation
- Advanced analytics
- Web dashboard
- Multi-language support
- Scheduled messages
- Custom triggers

## Project Structure

```
watbot/                    # Python package
├── __init__.py           # Package init
├── config.py             # Configuration
├── whatsapp_bot.py       # WhatsApp wrapper
└── cli.py                # Command-line interface

examples/                  # Usage examples
├── whatsapp_examples.py  # Python examples
└── config_example.json   # Config template

smart_whatsapp_bot.js     # Node.js automation
gemini_bot.py             # AI responses
start.py                  # Interactive launcher
test_watbot.py            # Test suite
```

## Development

```bash
# Clone repo
git clone https://github.com/nithin434/woat.git
cd woat

# Install dependencies
npm install
pip install -e .

# Run tests
python test_watbot.py

# Start bot
python start.py
```

## Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/nithin434/woat/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/nithin434/woat/discussions)
- 📧 Email: nithin@example.com
- ⭐ Star the repo if you like it!

## License

MIT License - see [LICENSE](LICENSE)

---

Made with ❤️ by [Nithin Jambula](https://github.com/nithin434)
