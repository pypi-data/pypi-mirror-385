#!/usr/bin/env python3
"""
TermiGPT v2.0.0 - AI-Powered Security Research Terminal Assistant
By TheNooB
GitHub: https://github.com/thenoob4

Professional tool for cybersecurity researchers, penetration testers, and students.
Combines AI intelligence with security automation for reconnaissance, exploitation, and reporting.
"""

import os, sys, json, time, socket, subprocess, requests, re, threading, shutil, concurrent.futures, shlex, platform
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode
from typing import Dict, List, Tuple, Optional
import tempfile

# ANSI Color Codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"

# Cloudflare Worker URL
WORKER_URL = "https://noobt.insta-acc-sec.workers.dev/ask"

# Configuration
CONFIG_DIR = Path.home() / ".termigpt"
MODEL_CONFIG_FILE = CONFIG_DIR / "current_model.json"
SCAN_HISTORY_FILE = CONFIG_DIR / "scan_history.json"
SESSION_FILE = CONFIG_DIR / "session_history.json"
TOOLS_CONFIG_FILE = CONFIG_DIR / "installed_tools.json"
CONFIG_DIR.mkdir(exist_ok=True)

# Port to Protocol mapping
PORT_PROTOCOLS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 119: "NNTP", 123: "NTP", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 161: "SNMP", 162: "SNMP-TRAP", 389: "LDAP", 443: "HTTPS",
    445: "SMB", 465: "SMTPS", 514: "SYSLOG", 587: "SMTP", 636: "LDAPS",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "ORACLE", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-ALT",
    8443: "HTTPS-ALT", 9200: "Elasticsearch", 27017: "MongoDB", 27018: "MongoDB",
    5672: "RabbitMQ", 11211: "Memcached", 2181: "Zookeeper", 9092: "Kafka"
}

# Security tools database
SECURITY_TOOLS = {
    "recon": {
        "subfinder": {
            "desc": "Fast subdomain discovery tool",
            "install": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
            "check": "subfinder"
        },
        "amass": {
            "desc": "In-depth DNS enumeration and network mapping",
            "install": "go install -v github.com/OWASP/Amass/v3/...@master",
            "check": "amass"
        },
        "httpx": {
            "desc": "Fast HTTP probe utility",
            "install": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
            "check": "httpx"
        },
        "nuclei": {
            "desc": "Fast vulnerability scanner",
            "install": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
            "check": "nuclei"
        }
    },
    "scanning": {
        "nmap": {
            "desc": "Network exploration tool and security scanner",
            "install": "sudo apt install nmap -y || brew install nmap",
            "check": "nmap"
        },
        "masscan": {
            "desc": "Fast TCP port scanner",
            "install": "sudo apt install masscan -y || brew install masscan",
            "check": "masscan"
        },
        "rustscan": {
            "desc": "Modern fast port scanner",
            "install": "cargo install rustscan",
            "check": "rustscan"
        }
    },
    "exploitation": {
        "metasploit": {
            "desc": "Penetration testing framework",
            "install": "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall",
            "check": "msfconsole"
        },
        "sqlmap": {
            "desc": "Automatic SQL injection tool",
            "install": "git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git ~/tools/sqlmap",
            "check": "sqlmap"
        }
    },
    "wireless": {
        "aircrack-ng": {
            "desc": "WiFi security auditing tools",
            "install": "sudo apt install aircrack-ng -y || brew install aircrack-ng",
            "check": "aircrack-ng"
        }
    },
    "web": {
        "gobuster": {
            "desc": "Directory/file & DNS busting tool",
            "install": "go install github.com/OJ/gobuster/v3@latest",
            "check": "gobuster"
        },
        "ffuf": {
            "desc": "Fast web fuzzer",
            "install": "go install github.com/ffuf/ffuf@latest",
            "check": "ffuf"
        },
        "wpscan": {
            "desc": "WordPress security scanner",
            "install": "gem install wpscan",
            "check": "wpscan"
        }
    }
}

# Production-ready code generation prompt
CODE_GEN_PROMPT = """You are an ELITE security-focused code generator for cybersecurity professionals.

CRITICAL REQUIREMENTS:
1. Generate COMPLETE, WORKING CODE with NO placeholders
2. Include security best practices and error handling
3. Add comments explaining security implications
4. Use proper pentesting/security libraries when applicable

OUTPUT FORMAT - Use this EXACT format:

[FILE: filename.ext]
<complete code here>
[/FILE]

RULES:
- Wrap EVERY file in [FILE: path][/FILE] tags
- Include ALL necessary files (README, requirements, configs)
- Code must be production-ready and immediately executable
- For security tools, include ethical use disclaimers
- Add proper error handling and logging

Generate the COMPLETE project now."""

def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def show_welcome_banner():
    """Professional security research welcome banner"""
    width = min(get_terminal_width(), 80)

    banner = f"""{Colors.CYAN}{Colors.BOLD}
{'='*width}
  ████████╗███████╗██████╗ ███╗   ███╗██╗ ██████╗ ██████╗ ████████╗
  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║██╔════╝ ██╔══██╗╚══██╔══╝
     ██║   █████╗  ██████╔╝██╔████╔██║██║██║  ███╗██████╔╝   ██║   
     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║   ██║██╔═══╝    ██║   
     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║╚██████╔╝██║        ██║   
     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝        ╚═╝   
{'='*width}{Colors.END}

{Colors.RED}{Colors.BOLD}  🛡️  AI-Powered Security Research Terminal v2.0.0{Colors.END}
{Colors.YELLOW}  For Cybersecurity Researchers, Penetration Testers & Students{Colors.END}

{Colors.WHITE}  📚 By {Colors.BOLD}TheNooB{Colors.END}
{Colors.BLUE}  🔗 GitHub:{Colors.END} {Colors.UNDERLINE}https://github.com/thenoob4{Colors.END}

{Colors.GREEN}  ⚠️  ETHICAL USE ONLY - For authorized security testing{Colors.END}
"""
    print(banner)

def show_help_menu():
    width = min(get_terminal_width(), 75)

    help_text = f"""
{Colors.CYAN}{'='*width}{Colors.END}
{Colors.BOLD}{Colors.RED}🛡️  SECURITY RESEARCH COMMAND CENTER{Colors.END}
{Colors.CYAN}{'='*width}{Colors.END}

{Colors.YELLOW}🎯 USAGE MODES:{Colors.END}
  {Colors.GREEN}Interactive:{Colors.END}  termi
  {Colors.GREEN}Direct:{Colors.END}       termi <command> [arguments]
  {Colors.GREEN}Pipe Input:{Colors.END}   cat file.txt | termi -p "analyze"
  {Colors.GREEN}Session:{Colors.END}      termi --continue  (resume last session)

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}📋 CORE COMMANDS:{Colors.END}
  {Colors.GREEN}Code Generation:{Colors.END}
    create/code/write <desc>     Generate security tools/scripts
    
  {Colors.GREEN}Execution:{Colors.END}
    run/execute <file>            Execute scripts with output
    
  {Colors.GREEN}Reconnaissance:{Colors.END}
    recon <target>                Full reconnaissance workflow
    enum <target>                 Subdomain enumeration
    portscan <target>             Advanced port scanning
    
  {Colors.GREEN}Security Scanning:{Colors.END}
    scan <target> [mode]          Security assessment
    vuln-scan <target>            Vulnerability scanning
    
  {Colors.GREEN}Tool Management:{Colors.END}
    install-tool <category>       Install security tools
    list-tools                    Show available tools
    check-tools                   Verify installed tools
    
  {Colors.GREEN}Reporting:{Colors.END}
    report <scan-data>            Generate VAPT report
    export <format>               Export findings (pdf/json/html)
    
  {Colors.GREEN}AI & Models:{Colors.END}
    models                        List AI models
    select                        Change active model
    ask <question>                General AI query
    
  {Colors.GREEN}Session Management:{Colors.END}
    history                       Show command history
    sessions                      List saved sessions
    clear                         Clear current session

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}💡 SECURITY EXAMPLES:{Colors.END}
  {Colors.WHITE}# Reconnaissance
  termi recon example.com
  termi enum subdomains of target.com
  
  # Generate payloads
  termi create a PowerShell reverse shell for 192.168.1.10:4444
  termi code a Python port scanner with threading
  
  # Scanning
  termi scan target.com comprehensive
  termi vuln-scan https://example.com
  
  # Tool installation
  termi install-tool recon
  termi install-tool scanning
  
  # Reporting
  termi report generate from last scan
  termi export findings as pdf
  
  # Learning
  termi ask "explain nmap -sV -A -T4 flags"
  termi ask "what is CVE-2024-1234"
  
  # File analysis
  cat nmap-output.xml | termi -p "analyze and find vulnerabilities"{Colors.END}

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}🔧 ADVANCED FEATURES:{Colors.END}
  • AI-powered reconnaissance automation
  • Payload generation for various platforms
  • VAPT-style report generation with CVEs
  • OSINT & threat intelligence integration
  • Tool-specific guidance (Nmap, Metasploit, etc.)
  • Adaptive to skill level (beginner to advanced)
  • Session persistence & command history
  • Multi-model AI support (5 models)

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.RED}⚠️  ETHICAL USE DISCLAIMER:{Colors.END}
{Colors.YELLOW}This tool is for authorized security testing only.
Unauthorized access to systems is illegal.
Always obtain proper authorization before testing.{Colors.END}

{Colors.CYAN}{'='*width}{Colors.END}
"""
    print(help_text)

class TermiGPT:
    def __init__(self):
        self.models = {
            "1": {"name": "GPT-4o", "worker_key": "GPT-4o"},
            "2": {"name": "GPT-4o Mini", "worker_key": "GPT-4o Mini"},
            "3": {"name": "GPT-4 Turbo", "worker_key": "GPT-4 Turbo"},
            "4": {"name": "Perplexity", "worker_key": "Perplexity AI"},
            "5": {"name": "Mistral", "worker_key": "Mistral Large"}
        }
        self.current_model = self.load_current_model()
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.stop_animation = False
        self.session_history = []
        self.system_info = self.detect_system()

    def detect_system(self):
        """Detect operating system and capabilities"""
        return {
            'platform': platform.system(),
            'is_linux': platform.system() == 'Linux',
            'is_windows': platform.system() == 'Windows',
            'is_mac': platform.system() == 'Darwin',
            'has_sudo': shutil.which('sudo') is not None,
            'is_root': os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        }

    def load_current_model(self):
        try:
            if MODEL_CONFIG_FILE.exists():
                return json.load(open(MODEL_CONFIG_FILE)).get('current_model', '2')
        except: pass
        return '2'

    def save_current_model(self):
        json.dump({'current_model': self.current_model}, open(MODEL_CONFIG_FILE, 'w'))

    def animate(self, msg):
        idx = 0
        while not self.stop_animation:
            print(f"\r{msg} {Colors.CYAN}{self.spinner[idx % len(self.spinner)]}{Colors.END}", end="", flush=True)
            idx += 1
            time.sleep(0.1)
        print(f"\r{' ' * (len(msg) + 5)}\r", end="", flush=True)

    def start_animation(self, msg):
        self.stop_animation = False
        t = threading.Thread(target=self.animate, args=(msg,), daemon=True)
        t.start()
        return t

    def stop_animation_thread(self):
        self.stop_animation = True
        time.sleep(0.15)

    def query_ai(self, prompt, show_anim=True, use_code_gen_prompt=False):
        """Enhanced AI query with error handling"""
        if show_anim:
            self.start_animation(f"{Colors.BLUE}🤖 AI analyzing{Colors.END}")

        m = self.models[self.current_model]

        if use_code_gen_prompt:
            full_prompt = f"{CODE_GEN_PROMPT}\n\nUSER REQUEST: {prompt}"
        else:
            full_prompt = prompt

        try:
            params = {'prompt': full_prompt, 'model': m['worker_key']}
            url = f"{WORKER_URL}?{urlencode(params)}"

            response = requests.get(url, timeout=120)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('response') or data.get('text') or "No response received"
                else:
                    result = f"{Colors.YELLOW}⚠️  System is currently busy. Try another model with: {Colors.CYAN}termi select{Colors.END}"
            else:
                result = f"{Colors.YELLOW}⚠️  Service temporarily unavailable. Please try: {Colors.CYAN}termi select{Colors.END} to switch models"

        except requests.exceptions.ConnectionError:
            result = f"{Colors.YELLOW}⚠️  Network connection issue. Please check your internet and try again.{Colors.END}"
        except requests.exceptions.Timeout:
            result = f"{Colors.YELLOW}⚠️  Request timed out. System may be busy. Try: {Colors.CYAN}termi select{Colors.END} to switch models"
        except Exception as e:
            result = f"{Colors.YELLOW}⚠️  Service temporarily unavailable. Please try another model: {Colors.CYAN}termi select{Colors.END}"

        if show_anim:
            self.stop_animation_thread()

        return result

    def get_identity_response(self):
        """Professional identity for security context"""
        return f"""{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║           TermiGPT - Security Research Assistant             ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.BOLD}What I Am:{Colors.END}
I'm an AI-powered terminal assistant specifically designed for 
cybersecurity professionals, penetration testers, and security students.

{Colors.BOLD}My Capabilities:{Colors.END}

{Colors.GREEN}🔍 Reconnaissance & OSINT:{Colors.END}
  • Subdomain enumeration workflows
  • Port scanning and service detection
  • DNS analysis and WHOIS lookups
  • Network mapping and asset discovery

{Colors.GREEN}💻 Code & Payload Generation:{Colors.END}
  • Security tool development (Python, Bash, PowerShell)
  • Exploit code generation and modification
  • Reverse shells and payload crafting
  • Automation scripts for pentesting workflows

{Colors.GREEN}🎯 Vulnerability Assessment:{Colors.END}
  • Automated vulnerability scanning
  • CVE lookup and analysis
  • Risk assessment and severity rating
  • MITRE ATT&CK framework mapping

{Colors.GREEN}📊 Reporting & Documentation:{Colors.END}
  • VAPT-style professional reports
  • Executive summaries with technical details
  • Finding documentation with remediation steps
  • Export in multiple formats (PDF, JSON, HTML)

{Colors.GREEN}🛠️  Tool Management:{Colors.END}
  • Install and configure security tools
  • Tool-specific guidance (Nmap, Metasploit, Burp, etc.)
  • Command syntax help and flag explanations
  • Integration with popular pentesting frameworks

{Colors.GREEN}🧠 Learning & Training:{Colors.END}
  • Explain security concepts and techniques
  • Command usage examples and best practices
  • CVE and vulnerability explanations
  • Adaptive guidance for all skill levels

{Colors.BOLD}Powered By:{Colors.END} 5 AI Models (GPT-4o, Perplexity, Mistral, etc.)
{Colors.BOLD}Focus:{Colors.END} Ethical hacking, authorized security testing, research

{Colors.RED}⚠️  All features are for authorized, ethical security testing only.{Colors.END}

Type '{Colors.CYAN}help{Colors.END}' for commands or '{Colors.CYAN}ask <question>{Colors.END}' for anything else.
"""

    def check_tool_installed(self, tool_command):
        """Check if a tool is installed"""
        return shutil.which(tool_command) is not None

    def install_security_tool(self, category=None):
        """Install security tools by category"""
        if category and category in SECURITY_TOOLS:
            tools = SECURITY_TOOLS[category]
        elif not category:
            print(f"\n{Colors.YELLOW}📦 Available Tool Categories:{Colors.END}\n")
            for cat, tools in SECURITY_TOOLS.items():
                print(f"{Colors.CYAN}{cat.capitalize()}:{Colors.END}")
                for name, info in tools.items():
                    installed = "✅" if self.check_tool_installed(info['check']) else "❌"
                    print(f"  {installed} {name}: {info['desc']}")
                print()
            
            choice = input(f"{Colors.YELLOW}Select category (or 'cancel'):{Colors.END} ").strip().lower()
            if choice == 'cancel' or choice not in SECURITY_TOOLS:
                print(f"{Colors.RED}Cancelled{Colors.END}")
                return
            tools = SECURITY_TOOLS[choice]
        else:
            print(f"{Colors.RED}Unknown category: {category}{Colors.END}")
            return

        # List tools in category
        print(f"\n{Colors.CYAN}Tools to install:{Colors.END}")
        tool_list = list(tools.items())
        for idx, (name, info) in enumerate(tool_list, 1):
            installed = "✅ Already installed" if self.check_tool_installed(info['check']) else "❌ Not installed"
            print(f"  {idx}. {name}: {info['desc']} {installed}")

        selection = input(f"\n{Colors.YELLOW}Select tool number (or 'all'):{Colors.END} ").strip()

        if selection.lower() == 'all':
            to_install = tool_list
        elif selection.isdigit() and 1 <= int(selection) <= len(tool_list):
            to_install = [tool_list[int(selection) - 1]]
        else:
            print(f"{Colors.RED}Invalid selection{Colors.END}")
            return

        # Install selected tools
        for name, info in to_install:
            if self.check_tool_installed(info['check']):
                print(f"{Colors.GREEN}✅ {name} already installed{Colors.END}")
                continue

            print(f"\n{Colors.BLUE}Installing {name}...{Colors.END}")
            
            try:
                # Parse install command
                install_cmd = info['install']
                
                # Check if sudo needed
                needs_sudo = install_cmd.startswith('sudo')
                if needs_sudo and not self.system_info['has_sudo'] and not self.system_info['is_root']:
                    print(f"{Colors.YELLOW}⚠️  Requires sudo but not available{Colors.END}")
                    continue

                # Execute installation
                process = subprocess.Popen(
                    shlex.split(install_cmd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(timeout=300)
                
                if process.returncode == 0:
                    print(f"{Colors.GREEN}✅ {name} installed successfully{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ Installation failed for {name}{Colors.END}")
                    if stderr:
                        print(f"{Colors.YELLOW}Error: {stderr[:200]}{Colors.END}")
                        
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}❌ Installation timed out for {name}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error installing {name}: {e}{Colors.END}")

    def list_security_tools(self):
        """List all available security tools"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}🛠️  AVAILABLE SECURITY TOOLS{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        for category, tools in SECURITY_TOOLS.items():
            print(f"{Colors.YELLOW}{category.upper()}:{Colors.END}")
            for name, info in tools.items():
                status = f"{Colors.GREEN}✅ Installed{Colors.END}" if self.check_tool_installed(info['check']) else f"{Colors.RED}❌ Not installed{Colors.END}"
                print(f"  • {Colors.WHITE}{name:15}{Colors.END} - {info['desc']:40} {status}")
            print()

        print(f"{Colors.CYAN}Use '{Colors.WHITE}termi install-tool <category>{Colors.CYAN}' to install{Colors.END}\n")

    def is_code_generation_request(self, desc: str) -> bool:
        """Detect if user wants code generation"""
        desc_lower = desc.lower()
        
        code_keywords = [
            'create', 'write', 'code', 'generate', 'build', 'make', 'develop',
            'program', 'prepare', 'design', 'implement', 'craft', 'script'
        ]
        
        tech_keywords = [
            'python', 'bash', 'powershell', 'javascript', 'ruby', 'perl', 'go',
            'payload', 'exploit', 'shell', 'reverse', 'bind', 'script', 'tool',
            'scanner', 'fuzzer', 'brute', 'sql', 'xss', 'injection', 'api',
            'html', 'css', 'react', 'vue', 'node', 'flask', 'django', 'app'
        ]
        
        has_code_keyword = any(keyword in desc_lower for keyword in code_keywords)
        has_tech_keyword = any(keyword in desc_lower for keyword in tech_keywords)
        
        return has_code_keyword or has_tech_keyword

    def create_project(self, desc):
        """Generate security tools/scripts"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🔧 Generating Security Tool{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        # Add ethical use reminder
        print(f"\n{Colors.YELLOW}⚠️  Reminder: For authorized security testing only{Colors.END}\n")

        self.start_animation(f"{Colors.BLUE}🤖 Generating production code{Colors.END}")
        
        project_prompt = f"""Generate a COMPLETE, WORKING security tool/script for: {desc}

MANDATORY FORMAT - Use [FILE: path] tags for EVERY file:

[FILE: filename.ext]
<complete code>
[/FILE]

SECURITY REQUIREMENTS:
- Include ethical use disclaimer in README
- Add proper error handling
- Implement logging for actions
- Include usage examples
- Add safety checks where applicable

Generate the complete project NOW."""
        
        response = self.query_ai(project_prompt, show_anim=False, use_code_gen_prompt=True)
        self.stop_animation_thread()

        if "Service temporarily unavailable" in response or "System is currently busy" in response:
            print(f"\n{response}")
            return

        # Extract files
        file_pattern = r'\[FILE:\s*([^\]]+)\]\s*(.*?)\s*\[/FILE\]'
        files = re.findall(file_pattern, response, re.DOTALL | re.IGNORECASE)

        if not files:
            print(f"{Colors.RED}❌ Could not extract code from response{Colors.END}")
            return

        # Determine project name
        project_name = re.sub(r'[^\w\s-]', '', desc[:30]).replace(' ', '-').lower()
        
        pdir = Path.cwd() / project_name
        pdir.mkdir(exist_ok=True)
        
        print(f"\n{Colors.CYAN}📁 Project: {pdir}{Colors.END}\n")

        # Create all files
        created_files = []
        for filepath, content in files:
            filepath = filepath.strip()
            content = content.strip()
            
            content = re.sub(r'^```[\w]*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            
            full_path = pdir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                full_path.write_text(content, encoding='utf-8')
                created_files.append(filepath)
                
                # Make scripts executable
                if filepath.endswith(('.py', '.sh', '.rb', '.pl')):
                    os.chmod(full_path, 0o755)
                
                print(f"  {Colors.GREEN}✅ {filepath}{Colors.END}")
            except Exception as e:
                print(f"  {Colors.RED}❌ {filepath}: {e}{Colors.END}")

        # Create .gitignore if not exists
        gitignore_path = pdir / '.gitignore'
        if not gitignore_path.exists():
            gitignore_content = '.DS_Store\n*.log\n__pycache__/\n*.pyc\nvenv/\n*.swp\n'
            gitignore_path.write_text(gitignore_content)
            print(f"  {Colors.GREEN}✅ .gitignore{Colors.END}")

        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESS! {len(created_files)} files created{Colors.END}")
        print(f"{Colors.CYAN}📁 Location:{Colors.END} {pdir}")
        print(f"{Colors.YELLOW}💡 Next:{Colors.END} cd {project_name} && cat README.md")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")

    def execute_code(self, file_path):
        """Execute scripts with proper output handling"""
        path = Path(file_path)
        if not path.exists():
            print(f"{Colors.RED}❌ File not found: {file_path}{Colors.END}")
            return

        ext = path.suffix.lower()
        executors = {
            '.py': ['python3', str(path)],
            '.js': ['node', str(path)],
            '.sh': ['bash', str(path)],
            '.rb': ['ruby', str(path)],
            '.php': ['php', str(path)],
            '.pl': ['perl', str(path)]
        }

        if ext not in executors:
            print(f"{Colors.RED}❌ Unsupported file type: {ext}{Colors.END}")
            return

        cmd = executors[ext]
        print(f"{Colors.GREEN}🚀 Executing: {path}{Colors.END}\n")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Handle missing Python modules
            if result.returncode != 0 and ext == '.py':
                stderr = result.stderr
                if 'ModuleNotFoundError' in stderr or 'No module named' in stderr:
                    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", stderr)
                    if match:
                        module = match.group(1)
                        print(f"{Colors.YELLOW}⚠️  Missing module: {module}{Colors.END}")
                        
                        pip_map = {
                            'bs4': 'beautifulsoup4', 'cv2': 'opencv-python',
                            'PIL': 'Pillow', 'sklearn': 'scikit-learn', 'yaml': 'pyyaml'
                        }
                        pip_package = pip_map.get(module, module)
                        
                        install = input(f"{Colors.CYAN}📦 Install '{pip_package}'? (Y/n):{Colors.END} ").strip().lower()
                        if install != 'n':
                            print(f"{Colors.BLUE}📥 Installing {pip_package}...{Colors.END}")
                            subprocess.run(
                                [sys.executable, '-m', 'pip', 'install', pip_package],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            print(f"{Colors.GREEN}✅ Installed{Colors.END}")
                            print(f"{Colors.BLUE}🔄 Re-running...{Colors.END}\n")
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # Display output
            print(f"{Colors.CYAN}{'='*70}{Colors.END}")
            print(f"{Colors.CYAN}📤 OUTPUT:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
            
            if result.stdout:
                print(result.stdout)
            else:
                print(f"{Colors.YELLOW}(no output){Colors.END}")
                
            if result.stderr and result.returncode != 0:
                print(f"\n{Colors.RED}❌ ERRORS:{Colors.END}")
                print(result.stderr)
            elif result.stderr:
                print(f"\n{Colors.YELLOW}⚠️  WARNINGS:{Colors.END}")
                print(result.stderr)
                
            print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
            print(f"{Colors.CYAN}Exit Code:{Colors.END} {result.returncode}")
            print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}⏰ Execution timeout (60s){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")

    def reconnaissance(self, target):
        """AI-powered reconnaissance workflow"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🔍 RECONNAISSANCE: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        recon_prompt = f"""Provide a comprehensive reconnaissance plan for target: {target}

Include:
1. Subdomain enumeration techniques
2. Port scanning strategy
3. Service identification methods
4. DNS analysis approach
5. OSINT gathering techniques
6. Recommended tools for each phase
7. Expected findings and what to look for

Format as a step-by-step actionable plan."""

        result = self.query_ai(recon_prompt)
        print(f"\n{result}\n")

    def enumerate_subdomains(self, target):
        """Subdomain enumeration with AI guidance"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🌐 SUBDOMAIN ENUMERATION: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        # Check for tools
        tools_available = []
        if self.check_tool_installed('subfinder'):
            tools_available.append('subfinder')
        if self.check_tool_installed('amass'):
            tools_available.append('amass')

        if tools_available:
            print(f"{Colors.GREEN}Available tools: {', '.join(tools_available)}{Colors.END}\n")
            
            choice = input(f"{Colors.YELLOW}Run enumeration? (Y/n):{Colors.END} ").strip().lower()
            if choice != 'n':
                for tool in tools_available:
                    print(f"\n{Colors.BLUE}Running {tool}...{Colors.END}")
                    try:
                        if tool == 'subfinder':
                            result = subprocess.run(
                                ['subfinder', '-d', target, '-silent'],
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                        elif tool == 'amass':
                            result = subprocess.run(
                                ['amass', 'enum', '-d', target],
                                capture_output=True,
                                text=True,
                                timeout=120
                            )
                        
                        if result.stdout:
                            print(result.stdout)
                    except Exception as e:
                        print(f"{Colors.RED}Error running {tool}: {e}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}No enumeration tools installed.{Colors.END}")
            install = input(f"{Colors.CYAN}Install subfinder? (Y/n):{Colors.END} ").strip().lower()
            if install != 'n':
                self.install_security_tool('recon')

    def vulnerability_scan(self, target):
        """Vulnerability scanning with AI analysis"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🎯 VULNERABILITY SCAN: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        vuln_prompt = f"""Provide a vulnerability assessment plan for: {target}

Include:
1. Common vulnerabilities to check (OWASP Top 10)
2. Recommended scanning tools and commands
3. Manual testing techniques
4. What to look for in responses
5. Potential exploitation paths
6. Risk severity assessment criteria

Be specific and actionable."""

        result = self.query_ai(vuln_prompt)
        print(f"\n{result}\n")

    def generate_report(self, scan_data=None):
        """Generate VAPT-style report"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}📊 GENERATING VAPT REPORT{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        if not scan_data:
            scan_data = input(f"{Colors.YELLOW}Enter scan findings or path to scan file:{Colors.END} ").strip()

        report_prompt = f"""Generate a professional VAPT-style security report based on:

{scan_data}

Include:
1. Executive Summary (non-technical overview)
2. Methodology (tools and techniques used)
3. Findings (detailed with CVE references where applicable)
4. Risk Ratings (CRITICAL/HIGH/MEDIUM/LOW)
5. Remediation Recommendations (actionable steps)
6. Conclusion

Format as a professional security assessment report."""

        result = self.query_ai(report_prompt)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path.cwd() / f"vapt_report_{timestamp}.txt"
        report_file.write_text(result)
        
        print(f"\n{result}\n")
        print(f"{Colors.GREEN}✅ Report saved to: {report_file}{Colors.END}")

    def check_port(self, target: str, port: int, timeout: float = 1.0) -> Optional[Dict]:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                protocol = PORT_PROTOCOLS.get(port, "UNKNOWN")
                return {'port': port, 'protocol': protocol, 'state': 'open'}
        except:
            pass
        return None

    def parallel_port_scan(self, target: str, ports: List[int], stealth: bool = False) -> List[Dict]:
        """Parallel port scanning"""
        timeout = 2.0 if stealth else 0.5
        open_ports = []

        print(f"{Colors.YELLOW}🔍 Scanning {len(ports)} ports...{Colors.END}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=50 if not stealth else 10) as executor:
            future_to_port = {
                executor.submit(self.check_port, target, port, timeout): port 
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result:
                    open_ports.append(result)
                    print(f"  {Colors.GREEN}✓{Colors.END} Found: {result['port']}/{result['protocol']}")

        return sorted(open_ports, key=lambda x: x['port'])

    def perform_security_scan(self, target):
        """Enhanced security scanning"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🔒 SECURITY SCAN: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        try:
            socket.gethostbyname(target)
        except socket.gaierror:
            print(f"{Colors.RED}❌ Invalid target: Cannot resolve hostname{Colors.END}")
            return

        stealth_mode = 'stealth' in ' '.join(sys.argv).lower()

        scans = {
            "1": "Quick Scan (Top ports)",
            "2": "Full Scan (1-1000)",
            "3": "Comprehensive (1-65535)",
            "4": "DNS Analysis",
            "5": "Service Detection"
        }

        print(f"\n{Colors.YELLOW}🎯 Scan Types:{Colors.END}")
        for num, name in scans.items():
            print(f"  {Colors.CYAN}{num}.{Colors.END} {name}")

        choice = input(f"\n{Colors.YELLOW}Select (1-5):{Colors.END} ").strip()

        if choice == "1":
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]
            open_ports = self.parallel_port_scan(target, common_ports, stealth_mode)
            print(f"\n{Colors.GREEN}Found {len(open_ports)} open ports{Colors.END}")
        elif choice == "2":
            ports = list(range(1, 1001))
            open_ports = self.parallel_port_scan(target, ports, stealth_mode)
            print(f"\n{Colors.GREEN}Found {len(open_ports)} open ports{Colors.END}")
        elif choice == "3":
            confirm = input(f"{Colors.YELLOW}⚠️  Full scan may take 30+ minutes. Continue? (y/N):{Colors.END} ")
            if confirm.lower() == 'y':
                ports = list(range(1, 65536))
                open_ports = self.parallel_port_scan(target, ports, stealth_mode)
                print(f"\n{Colors.GREEN}Found {len(open_ports)} open ports{Colors.END}")
        elif choice == "4":
            try:
                ip = socket.gethostbyname(target)
                print(f"\n{Colors.GREEN}IP:{Colors.END} {ip}")
                try:
                    hostname = socket.gethostbyaddr(ip)
                    print(f"{Colors.GREEN}Hostname:{Colors.END} {hostname[0]}")
                except:
                    pass
            except:
                print(f"{Colors.RED}DNS lookup failed{Colors.END}")

    def display_models(self):
        print(f"\n{Colors.CYAN}🤖 Available AI Models:{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        for n, m in self.models.items():
            current = f" {Colors.GREEN}👈 CURRENT{Colors.END}" if n == self.current_model else ""
            print(f"  {Colors.YELLOW}{n}.{Colors.END} {Colors.WHITE}{m['name']:<20}{Colors.END}{current}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")

    def select_model(self):
        self.display_models()
        choice = input(f"\n{Colors.YELLOW}Select (1-5):{Colors.END} ").strip()
        if choice in self.models:
            self.current_model = choice
            self.save_current_model()
            print(f"{Colors.GREEN}✅ Switched to: {self.models[choice]['name']}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Invalid{Colors.END}")

    def show_history(self):
        """Show command history"""
        if not self.session_history:
            print(f"{Colors.YELLOW}No command history{Colors.END}")
            return

        print(f"\n{Colors.CYAN}📜 Command History:{Colors.END}")
        for idx, cmd in enumerate(self.session_history[-20:], 1):
            print(f"  {idx}. {cmd}")

    def interactive_mode(self):
        """Enhanced interactive mode that stays open"""
        print(f"\n{Colors.GREEN}🎯 Model: {Colors.BOLD}{self.models[self.current_model]['name']}{Colors.END}")
        print(f"{Colors.CYAN}💡 Type 'help' for commands, 'exit' to quit{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  For authorized security testing only{Colors.END}\n")

        while True:
            try:
                cmd = input(f"{Colors.BOLD}{Colors.GREEN}termi> {Colors.END}").strip()
                
                if not cmd:
                    continue
                
                # Save to history
                self.session_history.append(cmd)
                cmd_lower = cmd.lower()
                    
                if cmd_lower in ['exit', 'quit', 'bye', 'q']:
                    print(f"{Colors.CYAN}👋 Goodbye!{Colors.END}")
                    break
                
                elif cmd_lower == 'clear':
                    os.system('clear' if self.system_info['is_linux'] or self.system_info['is_mac'] else 'cls')
                    
                elif cmd_lower == 'help':
                    show_help_menu()
                    
                elif cmd_lower == 'history':
                    self.show_history()
                    
                elif cmd_lower == 'models':
                    self.display_models()
                    
                elif cmd_lower == 'select':
                    self.select_model()
                
                elif cmd_lower == 'list-tools':
                    self.list_security_tools()
                
                elif cmd_lower.startswith('install-tool'):
                    parts = cmd.split(maxsplit=1)
                    category = parts[1] if len(parts) > 1 else None
                    self.install_security_tool(category)
                
                elif cmd_lower.startswith('check-tools'):
                    self.list_security_tools()
                
                elif cmd_lower in ['who are you', 'what are you', 'capabilities', 'what can you do']:
                    print(self.get_identity_response())
                
                elif cmd_lower.startswith('recon '):
                    target = cmd.split(maxsplit=1)[1]
                    self.reconnaissance(target)
                
                elif cmd_lower.startswith('enum '):
                    target = cmd.split()[-1]
                    self.enumerate_subdomains(target)
                
                elif cmd_lower.startswith('vuln-scan '):
                    target = cmd.split(maxsplit=1)[1]
                    self.vulnerability_scan(target)
                
                elif cmd_lower.startswith('report'):
                    self.generate_report()
                
                elif self.is_code_generation_request(cmd):
                    desc = cmd
                    for prefix in ['create', 'write', 'code', 'generate', 'build', 'make']:
                        if cmd_lower.startswith(prefix):
                            desc = ' '.join(cmd.split()[1:])
                            break
                    self.create_project(desc)
                        
                elif cmd_lower.startswith(('run ', 'execute ')):
                    filepath = ' '.join(cmd.split()[1:])
                    if filepath:
                        self.execute_code(filepath)
                        
                elif cmd_lower.startswith('scan '):
                    parts = cmd.split()
                    if len(parts) > 1:
                        self.perform_security_scan(parts[1])
                
                elif cmd_lower.startswith('portscan '):
                    parts = cmd.split()
                    if len(parts) > 1:
                        self.perform_security_scan(parts[1])
                        
                elif cmd_lower.startswith('ask '):
                    question = ' '.join(cmd.split()[1:])
                    result = self.query_ai(question)
                    print(f"\n{result}\n")
                    
                else:
                    result = self.query_ai(cmd)
                    print(f"\n{result}\n")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Press Ctrl+C again or type 'exit' to quit{Colors.END}")
                continue
            except EOFError:
                print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
                continue

def main():
    show_welcome_banner()
    
    app = TermiGPT()

    # Handle piped input
    if not sys.stdin.isatty():
        piped_input = sys.stdin.read().strip()
        if len(sys.argv) > 1 and sys.argv[1] in ['-p', '--print']:
            prompt = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else "analyze this"
            full_prompt = f"{prompt}\n\nInput:\n{piped_input}"
            result = app.query_ai(full_prompt, show_anim=False)
            print(result)
        return

    if len(sys.argv) == 1:
        show_help_menu()
        try:
            user_input = input(f"{Colors.BOLD}{Colors.GREEN}termi> {Colors.END}").strip()
            
            if not user_input:
                app.interactive_mode()
            else:
                # Process single command then enter interactive mode
                cmd_lower = user_input.lower()
                
                if cmd_lower in ['help', 'h']:
                    show_help_menu()
                elif cmd_lower == 'models':
                    app.display_models()
                elif cmd_lower in ['who are you', 'what are you', 'capabilities']:
                    print(app.get_identity_response())
                elif app.is_code_generation_request(user_input):
                    app.create_project(user_input)
                elif cmd_lower.startswith(('run ', 'execute ')):
                    filepath = ' '.join(user_input.split()[1:])
                    app.execute_code(filepath)
                elif cmd_lower.startswith('scan '):
                    parts = user_input.split()
                    if len(parts) > 1:
                        app.perform_security_scan(parts[1])
                else:
                    result = app.query_ai(user_input)
                    print(f"\n{result}\n")
                
                # Always enter interactive mode after
                app.interactive_mode()
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
    else:
        # Direct command mode
        cmd = sys.argv[1].lower()
        
        if cmd in ['help', 'h', '--help', '-h']:
            show_help_menu()
        elif cmd in ['--continue', '-c']:
            app.interactive_mode()
        elif cmd == 'models':
            app.display_models()
        elif cmd == 'list-tools':
            app.list_security_tools()
        elif len(sys.argv) > 2:
            full_input = ' '.join(sys.argv[1:])
            
            if app.is_code_generation_request(full_input):
                app.create_project(full_input)
            elif cmd in ['run', 'execute']:
                app.execute_code(' '.join(sys.argv[2:]))
            elif cmd == 'scan':
                app.perform_security_scan(sys.argv[2])
            elif cmd == 'recon':
                app.reconnaissance(sys.argv[2])
            elif cmd == 'ask':
                result = app.query_ai(' '.join(sys.argv[2:]))
                print(result)
            else:
                result = app.query_ai(full_input)
                print(result)
        else:
            result = app.query_ai(sys.argv[1])
            print(result)

if __name__ == "__main__":
    main()
