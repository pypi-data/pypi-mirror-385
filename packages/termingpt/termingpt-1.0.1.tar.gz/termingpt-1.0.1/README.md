# File: termigpt-package/README.md

# TermiGPT v1.0.0

AI-Powered Terminal Assistant for code generation, security scanning, and interactive AI chat.

## Features

✨ **Smart Project Detection** - Automatically detects if you want a single file or full project  
🤖 **5 AI Models** - GPT-4o, GPT-4o Mini, GPT-4 Turbo, Perplexity, Mistral  
🔒 **Security Scanning** - Port scanning with protocol detection, DNS lookup, WHOIS  
🕵️ **Stealth Mode** - Use nmap stealth scan techniques  
⚡ **Auto-Install** - Automatically installs missing Python modules  
📱 **Termux Ready** - Installs Rust and dependencies automatically on Android  

## Installation

```bash
pip install termigpt
```

## Usage

### Interactive Mode
```bash
termigpt
```

### Direct Commands
```bash
# Create projects
termigpt create a todo app
termigpt code a python script to check weather

# Execute code
termigpt run script.py

# Security scanning
termigpt scan google.com
termigpt scan example.com stealth

# AI Chat
termigpt ask "explain async/await"
```

## Available Commands

- `create`, `write`, `code` - Create projects/code
- `run`, `execute` - Execute code files
- `scan` - Security scanning
- `models` - List available AI models
- `select` - Change AI model
- `ask` - Ask AI questions

## Models

1. GPT-4o
2. GPT-4o Mini (default)
3. GPT-4 Turbo
4. Perplexity AI
5. Mistral Large

## Requirements

- Python 3.7+
- Internet connection
- (Optional) nmap, rustcan for advanced scanning

## No API Keys Needed!

TermiGPT uses a Cloudflare Worker backend - no API key configuration required!

## Author

**TheNooB**
- GitHub: https://github.com/thenoob4
- GitHub: https://github.com/codelabwithosman

## License

MIT License
