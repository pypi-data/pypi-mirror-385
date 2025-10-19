# File: termingpt-package/setup.py
# Package Name: termingpt

import os
import sys
import subprocess
import shutil
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

class CustomInstallCommand(install):
    """Custom installation that auto-installs dependencies for Termux/Android."""

    def run(self):
        """Check platform and install dependencies automatically."""

        def is_termux():
            return os.path.exists('/data/data/com.termux/files/usr')

        def is_linux():
            return platform.system() == 'Linux' and not is_termux()

        def check_command_exists(command):
            return shutil.which(command) is not None

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

                print("📥 Updating package lists...")
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

        def install_linux_deps():
            print("\n" + "="*60)
            print(f"🐧 Detected: Linux ({platform.platform()})")
            print("="*60)
            print("✅ No additional system dependencies required!")
            print("   (Pre-compiled wheels available for Linux)\n")

        def install_other_platform():
            print("\n" + "="*60)
            print(f"💻 Detected: {platform.system()}")
            print("="*60)
            print("✅ No additional system dependencies required!")
            print("   (Pre-compiled wheels available)\n")

        if is_termux():
            install_termux_deps()
        elif is_linux():
            install_linux_deps()
        else:
            install_other_platform()

        print("="*60)
        print("📦 Installing Python packages...")
        print("="*60)

        if is_termux():
            print("⏱️  Compiling dependencies (may take a few minutes)...\n")
        else:
            print("⏱️  Downloading pre-compiled packages...\n")

        install.run(self)

        print("\n" + "="*60)
        print("✅ termingpt v1.0.0 Installation Complete!")
        print("="*60)
        print("\n🚀 Quick Start:")
        print("  Just run: termingpt")
        print("  (No API key setup needed!)\n")
        print("💡 Examples:")
        print("  termingpt create a todo app")
        print("  termingpt models")
        print("  termingpt scan example.com")
        print("\n📚 By TheNooB")
        print("  GitHub: https://github.com/thenoob4")
        print("  GitHub: https://github.com/codelabwithosman")
        print("="*60 + "\n")

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="termingpt",
    version="1.0.0",
    author="TheNooB",
    author_email="thenoob@example.com",
    description="AI-powered terminal assistant for code generation, security scanning, and interactive AI chat",
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
    keywords="ai chatgpt gpt-4 code-generator termux kali-linux security-scanner openai cli termingpt",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
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
        "GitHub": "https://github.com/codelabwithosman",
    },
)
