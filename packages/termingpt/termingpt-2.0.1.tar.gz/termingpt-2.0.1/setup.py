#!/usr/bin/env python3
"""
TermiGPT v2.0.1 - Complete Setup with Post-Install Banner
"""

import os
import sys
import subprocess
import shutil
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    
    def run(self):
        """Run standard install and show welcome banner"""
        
        # Check if Termux
        def is_termux():
            return os.path.exists('/data/data/com.termux/files/usr')
        
        def check_command(cmd):
            return shutil.which(cmd) is not None
        
        # Install system dependencies on Termux
        if is_termux():
            print("\n" + "="*60)
            print("🤖 Detected: Termux/Android")
            print("="*60)
            
            required = {
                'rustc': 'rust',
                'clang': 'clang',
                'pkg-config': 'pkg-config',
                'openssl': 'openssl'
            }
            
            missing = [pkg for cmd, pkg in required.items() if not check_command(cmd)]
            
            if missing:
                print(f"\n📦 Installing {len(missing)} system package(s)...")
                print("⏱️  This may take 5-10 minutes...")
                
                subprocess.run(['pkg', 'update', '-y'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
                
                for pkg in missing:
                    print(f"  Installing {pkg}...", end=' ', flush=True)
                    subprocess.run(
                        ['pkg', 'install', '-y', pkg],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print("✅")
        
        # Run standard install
        install.run(self)
        
        # Show post-install banner
        self.show_success_banner()
    
    def show_success_banner(self):
        """Display installation success banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ████████╗███████╗██████╗ ███╗   ███╗██╗ ██████╗ ██████╗ ████████╗ ║
║   ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║██╔════╝ ██╔══██╗╚══██╔══╝ ║
║      ██║   █████╗  ██████╔╝██╔████╔██║██║██║  ███╗██████╔╝   ██║    ║
║      ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║   ██║██╔═══╝    ██║    ║
║      ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║╚██████╔╝██║        ██║    ║
║      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝        ╚═╝    ║
║                                                                      ║
║                    🤖 v2.0.1 | By TheNooB                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

✅ Installation Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK START

  Just type:    termi

  Then press Enter to start interactive mode!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 COMMANDS

  termi                           → Interactive mode
  termi create <description>      → Generate code
  termi code <description>        → Generate code
  termi write <description>       → Generate code
  termi run <file>                → Execute code
  termi scan <target>             → Security scan
  termi models                    → List AI models
  termi select                    → Change model
  termi ask <question>            → Ask anything
  termi help                      → Show help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 EXAMPLES

  termi create a todo app with React
  termi code a Python REST API with Flask
  termi write a login page with HTML CSS JavaScript
  termi scan google.com
  termi scan example.com stealth
  termi run my_script.py
  termi ask "explain async/await in Python"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ FEATURES

  🤖 5 AI Models        → GPT-4o, GPT-4o Mini, GPT-4 Turbo, 
                           Perplexity AI, Mistral Large
  
  💻 Code Generation    → Production-ready code for any language
                           Supports: Python, JavaScript, React, Vue,
                           HTML/CSS, Node.js, Flask, Django, and more
  
  🔒 Security Scanning  → Port scanning, DNS analysis, WHOIS lookup
                           Stealth mode available
  
  🚀 Code Execution     → Run Python, JavaScript, Shell scripts
                           Auto-install missing dependencies
  

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 RESOURCES

  GitHub:   https://github.com/thenoob4/termingpt
  Issues:   https://github.com/thenoob4/termingpt/issues
  Author:   TheNooB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💫 Ready to create something amazing? Type: termi

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(banner)

# Read README for PyPI description
this_directory = Path(__file__).parent
long_description = ""
readme_file = this_directory / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="termingpt",
    version="2.0.1",
    author="TheNooB",
    author_email="codelearh@gmail.com",
    description="AI-powered terminal assistant with production-ready code generation and security scanning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thenoob4/termingpt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="ai chatgpt gpt-4 code-generator terminal security-scanner cli assistant termux",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "termi=termingpt.main:main",
            "termingpt=termingpt.main:main",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/thenoob4/termingpt/issues",
        "Source": "https://github.com/thenoob4/termingpt",
        "Documentation": "https://github.com/thenoob4/termingpt#readme",
    },
)
