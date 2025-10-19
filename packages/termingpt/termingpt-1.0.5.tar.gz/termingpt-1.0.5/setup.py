# File: setup.py
# TerminGPT v1.0.5 - Complete Setup with Post-Install Banner

import os
import sys
import subprocess
import shutil
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

class CustomInstallCommand(install):
    """Custom installation with post-install banner and dependency management."""

    def run(self):
        """Check platform, install dependencies, and show success banner."""

        def is_termux():
            return os.path.exists('/data/data/com.termux/files/usr')

        def check_command_exists(command):
            return shutil.which(command) is not None

        def show_install_banner():
            """Show compact installation banner"""
            print("\n" + "="*60)
            print("  ╔╦╗╔═╗╦═╗╔╦╗╦╔╗╔╔═╗╔═╗╔╦╗")
            print("   ║ ║╣ ╠╦╝║║║║║║║║ ╦╠═╝ ║ ")
            print("   ╩ ╚═╝╩╚═╩ ╩╩╝╚╝╚═╝╩   ╩  v1.0.5")
            print("="*60)
            print("  🤖 AI Terminal Assistant • By TheNooB")
            print("  ✨ 5 AI Models • Code Gen • Security Scan")
            print("  🔗 github.com/thenoob4")
            print("="*60)

        def install_termux_deps():
            print("\n" + "="*60)
            print("🤖 Detected: Termux/Android")
            print("="*60)
            print("🔍 Checking system dependencies...\n")

            required_packages = {
                'rustc': 'rust',
                'clang': 'clang', 
                'pkg-config': 'pkg-config',
                'openssl': 'openssl',
            }

            missing = []
            for cmd, pkg in required_packages.items():
                if not check_command_exists(cmd):
                    missing.append(pkg)
                    print(f"  ❌ Missing: {pkg}")
                else:
                    print(f"  ✅ Found: {pkg}")

            if missing:
                print("\n" + "="*60)
                print(f"📦 Installing {len(missing)} missing package(s)...")
                print("="*60)
                print("⏱️  This may take 5-10 minutes (first time only)...")
                print("☕ Please be patient...\n")

                subprocess.run(['pkg', 'update', '-y'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)

                for pkg in missing:
                    print(f"📦 Installing {pkg}...", end=' ', flush=True)
                    result = subprocess.run(
                        ['pkg', 'install', '-y', pkg],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    if result.returncode == 0:
                        print("✅")
                    else:
                        print("⚠️  (continuing...)")

                print("\n✅ System dependencies installed!")
            else:
                print("\n✅ All system dependencies already installed!")

        # Detect platform
        if is_termux():
            install_termux_deps()

        print("="*60)
        print("📦 Installing Python packages...")
        print("="*60)

        # Run standard install
        install.run(self)

        # Show success banner
        print()
        show_install_banner()

        print("\n" + "="*60)
        print("✅ INSTALLATION COMPLETE!")
        print("="*60)
        print("\n🚀 Quick Start:")
        print("  ➤ Just type: \033[1;32mtermi\033[0m")
        print("\n💡 Examples:")
        print("  ➤ termi create a todo app")
        print("  ➤ termi ask \"explain async/await\"")
        print("  ➤ termi scan google.com")
        print("  ➤ termi models")
        print("\n📚 Help: termi help")
        print("🎯 5 AI Models: GPT-4o • GPT-4o Mini • Perplexity • Mistral")
        print("🔑 No API Key Setup Needed - Works out of the box!")
        print("\n" + "="*60)
        print("Thank you for installing TerminGPT! 🎉")
        print("="*60 + "\n")

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="termingpt",
    version="1.0.5",
    author="TheNooB",
    author_email="",
    description="AI-powered terminal assistant with 5 models, production-ready code generation, and security scanning",
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
        "Operating System :: Android",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords="ai chatgpt gpt-4 code-generator termux security-scanner openai cli terminal-assistant",
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
        'install': CustomInstallCommand,
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/thenoob4/termingpt/issues",
        "Source": "https://github.com/thenoob4/termingpt",
    },
)
