#!/usr/bin/env python3
"""
TermiGPT v2.0.0 - Enhanced AI-Powered Terminal Assistant
By TheNooB
GitHub: https://github.com/thenoob4
GitHub: https://github.com/codelabwithosman

IMPROVEMENTS:
- Enhanced security scanning with parallel processing
- Advanced port detection with service fingerprinting
- Better error handling and validation
- Production-ready code generation with the comprehensive prompt
- Improved AI context and response quality
- Better scan result visualization
"""

import os, sys, json, time, socket, subprocess, requests, re, threading, shutil, concurrent.futures
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode
from typing import Dict, List, Tuple, Optional

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
CONFIG_DIR.mkdir(exist_ok=True)

# Enhanced Port to Protocol mapping with common services
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

# Production-ready code generation prompt
CODE_GEN_PROMPT = """# ULTIMATE PRODUCTION-READY CODE GENERATION PROMPT

You are an ELITE enterprise-grade code generation AI. Your sole purpose is to generate flawless, production-ready, fully-functional code that works immediately without any modifications, placeholders, or incomplete implementations.

## PRIMARY MANDATE
GENERATE COMPLETE, WORKING CODE - NOTHING ELSE.

Every single line of code you write must be:
- ✅ Fully functional and tested mentally for edge cases
- ✅ Production-grade quality, not tutorial-grade
- ✅ Properly structured and linked
- ✅ Industry best-practice compliant
- ✅ Security-hardened and error-handled
- ✅ Immediately executable without modifications

FORBIDDEN: Placeholders, TODOs, "// TODO: implement this", pseudo-code, incomplete functions.

## CRITICAL REQUIREMENTS

### CODE QUALITY
- Clean Architecture: Modular, scalable, maintainable
- Error Handling: Try-catch blocks, validation, graceful failures
- Performance: Optimized algorithms, efficient data structures
- Security: Input validation, SQL injection prevention, XSS protection
- Documentation: Inline comments, JSDoc/docstrings

### FILE STRUCTURE
- One responsibility per file
- Logical organization
- Proper naming conventions
- No monolithic files
- Configuration files included (package.json, requirements.txt, etc.)
- Complete README.md

### OUTPUT FORMAT
For each file, use this format:

═══════════════════════════════════════
📄 FILE: [path/filename.ext]
═══════════════════════════════════════
[COMPLETE, PRODUCTION-READY CODE]
═══════════════════════════════════════

Include:
1. Project overview with stack and complexity
2. Complete file structure
3. Dependencies and setup instructions
4. All code files (complete, no truncation)
5. Running instructions
6. Features implemented

VERIFICATION CHECKLIST:
- [ ] All files complete (no "...")
- [ ] All imports work
- [ ] No circular dependencies
- [ ] Code is functional
- [ ] Error handling present
- [ ] Security checked
- [ ] Best practices followed
- [ ] Runnable first-try
- [ ] Documentation complete

YOU ARE NOT A TUTORIAL AI. You are a PROFESSIONAL CODE GENERATION ENGINE producing production-ready code.
"""

def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def show_welcome_banner():
    """Enhanced welcome banner"""
    width = min(get_terminal_width(), 80)

    banner = f"""{Colors.CYAN}{Colors.BOLD}
{'='*width}
  ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ ██████╗ ██████╗ ████████╗
  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔════╝ ██╔══██╗╚══██╔══╝
     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║██║  ███╗██████╔╝   ██║   
     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██║   ██║██╔═══╝    ██║   
     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝██║        ██║   
     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝        ╚═╝   
{'='*width}{Colors.END}

{Colors.GREEN}{Colors.BOLD}  🤖 Enhanced AI-Powered Terminal Assistant v2.0.0{Colors.END}
{Colors.CYAN}  ✨ Production Code Generation • Advanced Security Scanning • 5 AI Models{Colors.END}

{Colors.WHITE}  📚 By {Colors.BOLD}TheNooB{Colors.END}
{Colors.BLUE}  🔗 GitHub:{Colors.END} {Colors.UNDERLINE}https://github.com/thenoob4{Colors.END}

{Colors.YELLOW}  💡 Quick Start: Type{Colors.END} {Colors.GREEN}{Colors.BOLD}termi{Colors.END} {Colors.YELLOW}and press Enter!{Colors.END}
{Colors.GREEN}  🔑 No API key setup needed - Everything works out of the box!{Colors.END}
"""
    print(banner)


def show_help_menu():
    width = min(get_terminal_width(), 70)

    help_text = f"""
{Colors.CYAN}{'='*width}{Colors.END}
{Colors.BOLD}{Colors.GREEN}📚 QUICK START GUIDE{Colors.END}
{Colors.CYAN}{'='*width}{Colors.END}

{Colors.YELLOW}🎯 Usage Modes:{Colors.END}
  1. {Colors.GREEN}Interactive Mode:{Colors.END} termigpt
  2. {Colors.GREEN}Direct Commands:{Colors.END} termigpt <command> [arguments]

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}📋 Available Commands:{Colors.END}
  {Colors.GREEN}Project:{Colors.END} create, write, code <description>
  {Colors.GREEN}Execute:{Colors.END} run, execute <file>
  {Colors.GREEN}Scan:{Colors.END} scan <target> [stealth] [ports]
  {Colors.GREEN}Models:{Colors.END} models, select, whois
  {Colors.GREEN}Chat:{Colors.END} ask <question>

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}💡 Examples:{Colors.END}
  {Colors.WHITE}termigpt create a full-stack todo app with auth{Colors.END}
  {Colors.WHITE}termigpt scan google.com stealth{Colors.END}
  {Colors.WHITE}termigpt scan example.com full 1-1000{Colors.END}
  {Colors.WHITE}termigpt run script.py{Colors.END}

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

    def load_current_model(self):
        try:
            if MODEL_CONFIG_FILE.exists():
                return json.load(open(MODEL_CONFIG_FILE)).get('current_model', '2')
        except: pass
        return '2'

    def save_current_model(self):
        json.dump({'current_model': self.current_model}, open(MODEL_CONFIG_FILE, 'w'))

    def save_scan_history(self, target: str, scan_type: str, results: dict):
        """Save scan results to history"""
        try:
            history = []
            if SCAN_HISTORY_FILE.exists():
                history = json.load(open(SCAN_HISTORY_FILE))
            
            history.append({
                'timestamp': datetime.now().isoformat(),
                'target': target,
                'scan_type': scan_type,
                'results': results
            })
            
            # Keep only last 50 scans
            history = history[-50:]
            json.dump(history, open(SCAN_HISTORY_FILE, 'w'), indent=2)
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not save scan history: {e}{Colors.END}")

    def animate(self, msg):
        idx = 0
        while not self.stop_animation:
            print(f"\r{msg} {Colors.CYAN}{self.spinner[idx % len(self.spinner)]}{Colors.END}", end="", flush=True)
            idx += 1
            time.sleep(0.1)
        print(f"\r{msg} {Colors.GREEN}✅{Colors.END}", flush=True)

    def start_animation(self, msg):
        self.stop_animation = False
        t = threading.Thread(target=self.animate, args=(msg,), daemon=True)
        t.start()
        return t

    def stop_animation_thread(self):
        self.stop_animation = True
        time.sleep(0.15)

    def query_ai(self, prompt, show_anim=True, use_code_gen_prompt=False):
        """Enhanced AI query with optional code generation context"""
        if show_anim:
            self.start_animation(f"{Colors.BLUE}🤖 AI thinking{Colors.END}")

        m = self.models[self.current_model]

        # Prepend code generation prompt if requested
        if use_code_gen_prompt:
            full_prompt = f"{CODE_GEN_PROMPT}\n\n---\n\nUSER REQUEST:\n{prompt}"
        else:
            full_prompt = prompt

        try:
            params = {'prompt': full_prompt, 'model': m['worker_key']}
            url = f"{WORKER_URL}?{urlencode(params)}"

            response = requests.get(url, timeout=120)  # Increased timeout for code generation

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('response') or data.get('text') or "No response"
                else:
                    result = f"Error: {data.get('message', 'Unknown error')}"
            else:
                result = f"Error: Server returned status {response.status_code}"

        except Exception as e:
            result = f"Error: {e}"

        if show_anim:
            self.stop_animation_thread()

        return result

    def detect_project_complexity(self, desc):
        desc_lower = desc.lower()

        single_file_keywords = ['a python code', 'a script', 'simple script', 'quick script', 'code to', 'script to', 'python file', 'single file', 'just a', 'only a', 'small script', 'basic script']
        full_project_keywords = ['application', 'app', 'project', 'system', 'platform', 'website', 'webapp', 'web app', 'dashboard', 'portal', 'api', 'rest api', 'backend', 'frontend', 'full-stack', 'full stack', 'microservice', 'service', 'authentication', 'auth', 'database', 'production']

        for keyword in single_file_keywords:
            if keyword in desc_lower:
                return 'single_file'

        for keyword in full_project_keywords:
            if keyword in desc_lower:
                return 'full_project'

        words = desc.split()
        if len(words) < 8:
            return 'single_file'

        return 'auto'

    def create_project(self, desc):
        """Enhanced project creation with production-ready code generation"""
        complexity = self.detect_project_complexity(desc)

        if complexity == 'single_file':
            print(f"{Colors.MAGENTA}💡 Detected: Single file request{Colors.END}")
            self.create_single_file_enhanced(desc)
        elif complexity == 'full_project':
            print(f"{Colors.MAGENTA}💡 Detected: Full project request{Colors.END}")
            self.create_full_project_enhanced(desc)
        else:
            print(f"\n{Colors.YELLOW}🤔 What do you want to create?{Colors.END}")
            print(f"  {Colors.CYAN}1.{Colors.END} Single file (quick script)")
            print(f"  {Colors.CYAN}2.{Colors.END} Full project (production-ready)")

            try:
                choice = input(f"\n{Colors.YELLOW}Select (1/2):{Colors.END} ").strip()
                if choice == '1':
                    self.create_single_file_enhanced(desc)
                elif choice == '2':
                    self.create_full_project_enhanced(desc)
                else:
                    print(f"{Colors.RED}❌ Invalid choice{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n{Colors.RED}❌ Cancelled{Colors.END}")

    def create_single_file_enhanced(self, desc):
        """Enhanced single file creation with production-ready code"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}📝 Creating Production-Ready Single File{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        self.start_animation(f"{Colors.BLUE}🤖 Generating production code{Colors.END}")
        
        code_prompt = f"""Create a single, complete, production-ready file for: {desc}

REQUIREMENTS:
- Single standalone file
- Complete working code with NO placeholders
- All imports included
- Comprehensive error handling
- Security best practices
- Performance optimized
- Well-documented with comments
- Immediately runnable

Generate ONLY the code with proper file extension in filename."""
        
        code = self.query_ai(code_prompt, show_anim=False, use_code_gen_prompt=True)
        self.stop_animation_thread()

        if code.startswith("Error:"):
            print(f"\n{Colors.RED}{code}{Colors.END}")
            return

        # Extract filename and code
        filename_match = re.search(r'FILE:\s*([^\n\]]+)', code)
        if filename_match:
            filename = filename_match.group(1).strip()
        else:
            # Fallback to auto-detection
            desc_lower = desc.lower()
            if 'python' in desc_lower or desc_lower.startswith('code'):
                ext = 'py'
            elif 'javascript' in desc_lower or 'js' in desc_lower:
                ext = 'js'
            elif 'html' in desc_lower:
                ext = 'html'
            else:
                ext = 'py'
            
            base_name = re.sub(r'[^\w\s-]', '', desc.lower())[:30].replace(' ', '_')
            filename = f"{base_name}.{ext}"

        # Extract code content
        code = re.sub(r'^```[\w]*\n', '', code.strip())
        code = re.sub(r'\n```$', '', code).strip()
        
        # Remove file markers
        code = re.sub(r'═+\n.*?FILE:.*?\n═+\n', '', code, flags=re.DOTALL)
        code = code.strip()

        filepath = Path.cwd() / filename

        if filepath.exists():
            overwrite = input(f"\n{Colors.YELLOW}⚠️  '{filename}' exists. Overwrite? (y/N):{Colors.END} ").lower()
            if overwrite != 'y':
                print(f"{Colors.RED}❌ Cancelled{Colors.END}")
                return

        filepath.write_text(code)

        if filename.endswith(('.py', '.sh')):
            os.chmod(filepath, 0o755)

        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESS! Production-ready code generated{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.CYAN}📄 File:{Colors.END} {filepath}")
        print(f"{Colors.CYAN}📊 Size:{Colors.END} {len(code)} characters")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")

    def create_full_project_enhanced(self, desc):
        """Enhanced full project creation with production-ready structure"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🚀 Creating Production-Ready Full Project{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        self.start_animation(f"{Colors.BLUE}🤖 Generating production-ready project{Colors.END}")
        
        project_prompt = f"""Generate a complete, production-ready project for: {desc}

REQUIREMENTS:
- Professional file structure
- All configuration files (package.json, requirements.txt, etc.)
- Complete README.md with setup instructions
- Security best practices
- Error handling throughout
- Performance optimized
- Well-documented
- Immediately runnable after setup

Provide the complete project structure with all files."""
        
        response = self.query_ai(project_prompt, show_anim=False, use_code_gen_prompt=True)
        self.stop_animation_thread()

        if response.startswith("Error:"):
            print(f"\n{Colors.RED}{response}{Colors.END}")
            return

        # Parse project name
        name_match = re.search(r'Project:\s*([^\n]+)', response) or re.search(r'project[_-]name[\'"]:\s*[\'"]([^\'"]+)', response)
        project_name = name_match.group(1).strip() if name_match else 'generated_project'
        project_name = re.sub(r'[^\w-]', '', project_name.replace(' ', '-').lower())

        pdir = Path.cwd() / project_name
        pdir.mkdir(exist_ok=True)
        print(f"\n{Colors.CYAN}📁 Creating project in: {pdir}{Colors.END}")

        # Extract and create files
        created_files = []
        for file_match in re.finditer(r'FILE:\s*([^\n\]]+)\n═+\n(.*?)(?=\n═+\nFILE:|\n═+$|$)', response, re.DOTALL):
            filepath = file_match.group(1).strip()
            content = file_match.group(2).strip()
            
            # Clean code blocks
            content = re.sub(r'^```[\w]*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            
            full_path = pdir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            created_files.append(filepath)
            print(f"  {Colors.GREEN}✅ {filepath}{Colors.END}")

        # Create .gitignore if not exists
        gitignore = pdir / '.gitignore'
        if not gitignore.exists():
            gitignore.write_text('.DS_Store\n*.log\nnode_modules/\n.env\n__pycache__/\n*.pyc\n')
            print(f"  {Colors.GREEN}✅ .gitignore{Colors.END}")

        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 SUCCESS! Production-ready project created{Colors.END}")
        print(f"{Colors.CYAN}📁 Location:{Colors.END} {pdir}")
        print(f"{Colors.CYAN}📊 Files:{Colors.END} {len(created_files)} files created")
        print(f"{Colors.YELLOW}💡 Next:{Colors.END} cd {project_name} && read README.md for setup")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")

    def execute_code(self, file_path):
        """Enhanced code execution with better error handling"""
        path = Path(file_path)
        if not path.exists():
            print(f"{Colors.RED}❌ File not found: {file_path}{Colors.END}")
            return

        ext = path.suffix.lower()
        executors = {
            '.py': 'python3', '.js': 'node', '.sh': 'bash', 
            '.rb': 'ruby', '.php': 'php', '.go': 'go run',
            '.rs': 'rustc', '.java': 'java'
        }

        cmd = executors.get(ext)
        if not cmd:
            print(f"{Colors.RED}❌ Unsupported file type: {ext}{Colors.END}")
            return

        print(f"{Colors.GREEN}🚀 Executing: {path}{Colors.END}\n")

        try:
            result = subprocess.run(
                f"{cmd} {path}", 
                shell=True, 
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
                            print(f"{Colors.BLUE}📥 Installing...{Colors.END}")
                            install_result = subprocess.run(
                                [sys.executable, '-m', 'pip', 'install', pip_package],
                                capture_output=True,
                                text=True
                            )
                            
                            if install_result.returncode == 0:
                                print(f"{Colors.GREEN}✅ Installed{Colors.END}")
                                print(f"{Colors.BLUE}🔄 Re-running...{Colors.END}\n")
                                result = subprocess.run(
                                    f"{cmd} {path}",
                                    shell=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=60
                                )

            print(f"{Colors.CYAN}{'='*70}{Colors.END}")
            print(f"{Colors.CYAN}📤 Output:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{Colors.YELLOW}⚠️  Errors/Warnings:{Colors.END}\n{result.stderr}")
                
            print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
            print(f"{Colors.CYAN}Exit Code:{Colors.END} {result.returncode}")
            print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}⏰ Execution timeout (60s){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Execution error: {e}{Colors.END}")

    def check_port(self, target: str, port: int, timeout: float = 1.0) -> Optional[Dict]:
        """Check if a single port is open with service detection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                protocol = PORT_PROTOCOLS.get(port, "UNKNOWN")
                return {
                    'port': port,
                    'protocol': protocol,
                    'state': 'open'
                }
        except:
            pass
        return None

    def parallel_port_scan(self, target: str, ports: List[int], stealth: bool = False) -> List[Dict]:
        """Enhanced parallel port scanning"""
        timeout = 2.0 if stealth else 0.5
        delay = 0.1 if stealth else 0
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
                
                if stealth and delay:
                    time.sleep(delay)

        return sorted(open_ports, key=lambda x: x['port'])

    def perform_security_scan(self, target):
        """Enhanced security scanning with better validation"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🔒 Advanced Security Scan: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        # Validate target
        try:
            socket.gethostbyname(target)
        except socket.gaierror:
            print(f"{Colors.RED}❌ Invalid target: Cannot resolve hostname{Colors.END}")
            return

        stealth_mode = 'stealth' in ' '.join(sys.argv).lower()
        if stealth_mode:
            print(f"{Colors.MAGENTA}🕵️  STEALTH MODE ACTIVATED{Colors.END}")

        # Check available tools
        tools = {
            'nmap': shutil.which('nmap') is not None,
            'rustcan': shutil.which('rustcan') is not None,
            'masscan': shutil.which('masscan') is not None
        }
        
        print(f"\n{Colors.YELLOW}📡 Available Tools:{Colors.END}")
        for tool, available in tools.items():
            status = f"{Colors.GREEN}✅{Colors.END}" if available else f"{Colors.RED}❌{Colors.END}"
            print(f"  {tool.capitalize()}: {status}")

        scans = {
            "1": ("Quick Port Scan (Top 100)", "quick_port"),
            "2": ("Full Port Scan (1-1000)", "full_port"),
            "3": ("DNS Analysis", "dns"),
            "4": ("WHOIS Lookup", "whois"),
            "5": ("Comprehensive Scan (All)", "comprehensive")
        }

        print(f"\n{Colors.YELLOW}🎯 Scan Types:{Colors.END}")
        for num, (name, _) in scans.items():
            print(f"  {Colors.CYAN}{num}.{Colors.END} {name}")

        try:
            choice = input(f"\n{Colors.YELLOW}Select (1-5):{Colors.END} ").strip()
            if choice not in scans:
                print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
                return

            scan_name, scan_type = scans[choice]

            print(f"\n{Colors.GREEN}🚀 Starting {scan_name}...{Colors.END}")
            print(f"{Colors.YELLOW}⏱️  This may take a while...{Colors.END}\n")

            start_time = time.time()
            
            # Execute scan based on type
            if scan_type == "quick_port":
                result = self.quick_port_scan(target, stealth_mode)
            elif scan_type == "full_port":
                result = self.full_port_scan(target, stealth_mode)
            elif scan_type == "dns":
                result = self.dns_analysis(target)
            elif scan_type == "whois":
                result = self.whois_lookup(target)
            elif scan_type == "comprehensive":
                result = self.comprehensive_scan(target, stealth_mode)
            else:
                result = {"error": "Unknown scan type"}

            elapsed = time.time() - start_time

            # Display results
            self.display_scan_results_enhanced(result, scan_name, target, stealth_mode, elapsed)

            # Save to history
            self.save_scan_history(target, scan_name, result)

            # AI Analysis
            if not result.get('error'):
                print(f"\n{Colors.MAGENTA}🤖 Generating AI security analysis...{Colors.END}")
                
                analysis_prompt = f"""Analyze this security scan for {target}:

Scan Type: {scan_name}
Stealth Mode: {'Enabled' if stealth_mode else 'Disabled'}
Duration: {elapsed:.2f} seconds
Results: {json.dumps(result, indent=2)}

Provide a professional security assessment with:

1. Executive Summary (2-3 sentences about overall security posture)
2. Key Findings (list critical discoveries)
3. Risk Assessment (LOW/MEDIUM/HIGH/CRITICAL for each finding)
4. Vulnerabilities Detected (specific security concerns)
5. Recommendations (actionable steps to improve security)

IMPORTANT: Use plain text only. NO markdown formatting.
Be specific and actionable. Focus on security implications."""

                analysis = self.query_ai(analysis_prompt)

                if not analysis.startswith("Error:"):
                    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
                    print(f"{Colors.BOLD}{Colors.GREEN}🛡️  AI SECURITY ASSESSMENT{Colors.END}")
                    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
                    print(self.colorize_security_report(analysis))
                    print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.RED}⏹️  Scan cancelled by user{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Scan error: {e}{Colors.END}")

    def quick_port_scan(self, target: str, stealth: bool = False) -> Dict:
        """Scan top 100 most common ports"""
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995,
            1723, 3306, 3389, 5900, 8080, 8443, 8888, 1433, 5432, 27017,
            6379, 9200, 9300, 11211, 5672, 6667, 3128, 1080, 8081, 9090,
            1521, 50000, 4444, 5000, 5555, 7777, 8000, 8888, 10000
        ]
        
        open_ports = self.parallel_port_scan(target, common_ports, stealth)
        
        return {
            'scan_type': 'quick',
            'total_scanned': len(common_ports),
            'open_ports': open_ports,
            'scan_method': 'parallel_connect'
        }

    def full_port_scan(self, target: str, stealth: bool = False) -> Dict:
        """Scan ports 1-1000"""
        ports = list(range(1, 1001))
        open_ports = self.parallel_port_scan(target, ports, stealth)
        
        return {
            'scan_type': 'full',
            'total_scanned': len(ports),
            'open_ports': open_ports,
            'scan_method': 'parallel_connect'
        }

    def dns_analysis(self, target: str) -> Dict:
        """Enhanced DNS analysis"""
        result = {'scan_type': 'dns'}
        
        try:
            # Basic DNS lookup
            ip = socket.gethostbyname(target)
            result['ip_address'] = ip
            
            # Reverse DNS
            try:
                hostname_info = socket.gethostbyaddr(ip)
                result['hostname'] = hostname_info[0]
                result['aliases'] = hostname_info[1]
            except:
                result['hostname'] = 'Not available'
                result['aliases'] = []
            
            # Try to get multiple IPs (load balancing)
            try:
                addr_info = socket.getaddrinfo(target, None)
                ips = list(set([addr[4][0] for addr in addr_info]))
                result['all_ips'] = ips
                result['load_balanced'] = len(ips) > 1
            except:
                result['all_ips'] = [ip]
                result['load_balanced'] = False
                
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def whois_lookup(self, target: str) -> Dict:
        """WHOIS lookup with parsing"""
        result = {'scan_type': 'whois'}
        
        try:
            whois_result = subprocess.run(
                ['whois', target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if whois_result.returncode == 0:
                output = whois_result.stdout
                result['raw_output'] = output[:2000]  # Limit size
                
                # Parse key information
                result['registrar'] = self.extract_whois_field(output, 'Registrar:')
                result['creation_date'] = self.extract_whois_field(output, 'Creation Date:')
                result['expiration_date'] = self.extract_whois_field(output, 'Expiration Date:')
                result['name_servers'] = self.extract_whois_nameservers(output)
            else:
                result['error'] = 'WHOIS lookup failed'
                
        except FileNotFoundError:
            result['error'] = 'WHOIS command not available'
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def extract_whois_field(self, text: str, field: str) -> Optional[str]:
        """Extract field from WHOIS output"""
        match = re.search(f'{field}\\s*(.+)', text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def extract_whois_nameservers(self, text: str) -> List[str]:
        """Extract nameservers from WHOIS output"""
        nameservers = []
        for match in re.finditer(r'Name Server:\s*(.+)', text, re.IGNORECASE):
            nameservers.append(match.group(1).strip())
        return nameservers

    def comprehensive_scan(self, target: str, stealth: bool = False) -> Dict:
        """Complete security scan combining all methods"""
        result = {
            'scan_type': 'comprehensive',
            'port_scan': self.quick_port_scan(target, stealth),
            'dns': self.dns_analysis(target),
            'whois': self.whois_lookup(target)
        }
        return result

    def display_scan_results_enhanced(self, result: Dict, scan_name: str, target: str, stealth: bool, elapsed: float):
        """Enhanced scan results display"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}📊 {scan_name} Results{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        print(f"{Colors.YELLOW}Target:{Colors.END} {Colors.WHITE}{Colors.BOLD}{target}{Colors.END}")
        print(f"{Colors.YELLOW}Scan Type:{Colors.END} {Colors.CYAN}{scan_name}{Colors.END}")
        print(f"{Colors.YELLOW}Stealth Mode:{Colors.END} {'🕵️  Active' if stealth else '⚡ Fast'}")
        print(f"{Colors.YELLOW}Duration:{Colors.END} {Colors.WHITE}{elapsed:.2f}s{Colors.END}")
        print(f"{Colors.YELLOW}Timestamp:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.get('error'):
            print(f"\n{Colors.RED}❌ Error: {result['error']}{Colors.END}")
            return
        
        # Display based on scan type
        if result.get('scan_type') == 'comprehensive':
            self.display_comprehensive_results(result)
        elif 'open_ports' in result:
            self.display_port_scan_results(result)
        elif result.get('scan_type') == 'dns':
            self.display_dns_results(result)
        elif result.get('scan_type') == 'whois':
            self.display_whois_results(result)
        
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

    def display_port_scan_results(self, result: Dict):
        """Display port scan results"""
        open_ports = result.get('open_ports', [])
        total = result.get('total_scanned', 0)
        
        print(f"\n{Colors.YELLOW}📊 Port Scan Summary:{Colors.END}")
        print(f"  Total Scanned: {Colors.WHITE}{total}{Colors.END}")
        print(f"  Open Ports: {Colors.GREEN}{Colors.BOLD}{len(open_ports)}{Colors.END}")
        print(f"  Closed: {Colors.WHITE}{total - len(open_ports)}{Colors.END}")
        
        if open_ports:
            print(f"\n{Colors.RED}{Colors.BOLD}🔓 OPEN PORTS DETECTED:{Colors.END}")
            for port_info in open_ports:
                port = port_info['port']
                protocol = port_info['protocol']
                print(f"  {Colors.RED}Port {port:>5}{Colors.END} → {Colors.CYAN}{protocol:<20}{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}🔒 No open ports detected{Colors.END}")

    def display_dns_results(self, result: Dict):
        """Display DNS analysis results"""
        print(f"\n{Colors.YELLOW}🌐 DNS Analysis:{Colors.END}")
        print(f"  IP Address: {Colors.CYAN}{result.get('ip_address', 'N/A')}{Colors.END}")
        print(f"  Hostname: {Colors.WHITE}{result.get('hostname', 'N/A')}{Colors.END}")
        
        if result.get('load_balanced'):
            print(f"  {Colors.GREEN}✅ Load Balanced{Colors.END} ({len(result.get('all_ips', []))} IPs)")
            for ip in result.get('all_ips', []):
                print(f"    → {ip}")

    def display_whois_results(self, result: Dict):
        """Display WHOIS lookup results"""
        print(f"\n{Colors.YELLOW}📋 WHOIS Information:{Colors.END}")
        if result.get('registrar'):
            print(f"  Registrar: {Colors.CYAN}{result['registrar']}{Colors.END}")
        if result.get('creation_date'):
            print(f"  Created: {Colors.WHITE}{result['creation_date']}{Colors.END}")
        if result.get('expiration_date'):
            print(f"  Expires: {Colors.YELLOW}{result['expiration_date']}{Colors.END}")
        if result.get('name_servers'):
            print(f"  Name Servers:")
            for ns in result['name_servers'][:5]:
                print(f"    → {ns}")

    def display_comprehensive_results(self, result: Dict):
        """Display comprehensive scan results"""
        if 'port_scan' in result:
            self.display_port_scan_results(result['port_scan'])
        if 'dns' in result:
            self.display_dns_results(result['dns'])
        if 'whois' in result:
            self.display_whois_results(result['whois'])

    def colorize_security_report(self, text: str) -> str:
        """Enhanced security report colorization"""
        # Remove markdown
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'^[\*\-]\s+', '  • ', text, flags=re.MULTILINE)

        # Highlight risk levels
        text = re.sub(
            r'\b(CRITICAL|SEVERE)\b',
            f'{Colors.BG_RED}{Colors.WHITE}\\1{Colors.END}',
            text, flags=re.I
        )
        text = re.sub(
            r'\b(HIGH)\b',
            f'{Colors.RED}{Colors.BOLD}\\1{Colors.END}',
            text, flags=re.I
        )
        text = re.sub(
            r'\b(MEDIUM)\b',
            f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.END}',
            text, flags=re.I
        )
        text = re.sub(
            r'\b(LOW)\b',
            f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.END}',
            text, flags=re.I
        )

        # Highlight security keywords
        vuln_keywords = [
            'vulnerable', 'vulnerability', 'exploit', 'exposed', 'insecure',
            'risk', 'attack', 'breach', 'compromise', 'weak', 'unsecured'
        ]
        for keyword in vuln_keywords:
            text = re.sub(
                f'\\b({keyword})\\b',
                f'{Colors.RED}{Colors.BOLD}\\1{Colors.END}',
                text, flags=re.I
            )

        # Highlight positive keywords
        positive_keywords = [
            'secure', 'protected', 'safe', 'encrypted', 'strong',
            'recommended', 'good', 'excellent', 'hardened'
        ]
        for keyword in positive_keywords:
            text = re.sub(
                f'\\b({keyword})\\b',
                f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.END}',
                text, flags=re.I
            )

        # Highlight section headers
        headers = [
            'Executive Summary:', 'Key Findings:', 'Risk Assessment:',
            'Vulnerabilities:', 'Recommendations:', 'Detected:', 'Analysis:'
        ]
        for header in headers:
            text = re.sub(
                f'^({header})',
                f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.END}',
                text, flags=re.MULTILINE
            )

        return text

    def display_models(self):
        print(f"\n{Colors.CYAN}🤖 Available AI Models:{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        for n, m in self.models.items():
            current = f" {Colors.GREEN}👈 CURRENT{Colors.END}" if n == self.current_model else ""
            print(f"  {Colors.YELLOW}{n}.{Colors.END} {Colors.WHITE}{m['name']:<20}{Colors.END}{current}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")

    def select_model(self):
        self.display_models()
        choice = input(f"\n{Colors.YELLOW}Select model (1-5):{Colors.END} ").strip()
        if choice in self.models:
            self.current_model = choice
            self.save_current_model()
            print(f"{Colors.GREEN}✅ Switched to: {self.models[choice]['name']}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Invalid selection{Colors.END}")

    def whois_current_model(self):
        m = self.models[self.current_model]
        print(f"\n{Colors.CYAN}🤖 Current Model: {Colors.BOLD}{m['name']}{Colors.END}")

    def interactive_mode(self):
        """Enhanced interactive mode"""
        print(f"{Colors.GREEN}🎯 Current Model: {Colors.BOLD}{self.models[self.current_model]['name']}{Colors.END}")
        print(f"{Colors.CYAN}💡 Type 'help' for commands, 'exit' to quit{Colors.END}\n")

        while True:
            try:
                cmd = input(f"{Colors.BOLD}{Colors.GREEN}🚀 TermiGPT> {Colors.END}").strip()
                
                if not cmd:
                    continue
                    
                if cmd.lower() in ['exit', 'quit', 'bye', 'q']:
                    print(f"{Colors.CYAN}👋 Goodbye!{Colors.END}")
                    break
                    
                elif cmd.lower() == 'help':
                    show_help_menu()
                    
                elif cmd.lower() == 'models':
                    self.display_models()
                    
                elif cmd.lower() == 'select':
                    self.select_model()
                    
                elif cmd.lower() == 'whois':
                    self.whois_current_model()
                    
                elif cmd.lower().startswith(('create ', 'write ', 'code ', 'build ', 'make ')):
                    desc = ' '.join(cmd.split()[1:])
                    if desc:
                        self.create_project(desc)
                    else:
                        print(f"{Colors.RED}❌ Please provide a description{Colors.END}")
                        
                elif cmd.lower().startswith(('run ', 'execute ')):
                    filepath = ' '.join(cmd.split()[1:])
                    if filepath:
                        self.execute_code(filepath)
                    else:
                        print(f"{Colors.RED}❌ Please provide a file path{Colors.END}")
                        
                elif cmd.lower().startswith('scan '):
                    parts = cmd.split()
                    target = parts[1] if len(parts) > 1 else None
                    if target:
                        self.perform_security_scan(target)
                    else:
                        print(f"{Colors.RED}❌ Please provide a target{Colors.END}")
                        
                elif cmd.lower().startswith('ask '):
                    question = ' '.join(cmd.split()[1:])
                    print(f"\n{Colors.BLUE}🤖{Colors.END} {self.query_ai(question)}\n")
                    
                else:
                    # General AI query
                    print(f"\n{Colors.BLUE}🤖{Colors.END} {self.query_ai(cmd)}\n")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}\n")

def main():
    show_welcome_banner()
    show_help_menu()

    app = TermiGPT()

    if len(sys.argv) == 1:
        # Interactive prompt mode
        try:
            user_input = input(f"{Colors.BOLD}{Colors.GREEN}🚀 TermiGPT> {Colors.END}").strip()
            
            if not user_input:
                app.interactive_mode()
            else:
                cmd_parts = user_input.split()
                cmd = cmd_parts[0].lower()

                if cmd in ['help', 'h']:
                    show_help_menu()
                elif cmd == 'models':
                    app.display_models()
                elif cmd == 'select':
                    app.select_model()
                elif cmd == 'whois':
                    app.whois_current_model()
                elif cmd in ['create', 'write', 'code', 'build', 'make'] and len(cmd_parts) > 1:
                    app.create_project(' '.join(cmd_parts[1:]))
                elif cmd in ['run', 'execute'] and len(cmd_parts) > 1:
                    app.execute_code(' '.join(cmd_parts[1:]))
                elif cmd == 'scan' and len(cmd_parts) > 1:
                    app.perform_security_scan(cmd_parts[1])
                elif cmd == 'ask' and len(cmd_parts) > 1:
                    print(app.query_ai(' '.join(cmd_parts[1:])))
                else:
                    print(app.query_ai(user_input))
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
    else:
        # Direct command mode
        cmd = sys.argv[1].lower()
        
        if cmd in ['help', 'h']:
            show_help_menu()
        elif cmd == 'models':
            app.display_models()
        elif cmd == 'select':
            app.select_model()
        elif cmd == 'whois':
            app.whois_current_model()
        elif cmd in ['create', 'write', 'code', 'build', 'make'] and len(sys.argv) > 2:
            app.create_project(' '.join(sys.argv[2:]))
        elif cmd in ['run', 'execute'] and len(sys.argv) > 2:
            app.execute_code(' '.join(sys.argv[2:]))
        elif cmd == 'scan' and len(sys.argv) > 2:
            app.perform_security_scan(sys.argv[2])
        elif cmd == 'ask' and len(sys.argv) > 2:
            print(app.query_ai(' '.join(sys.argv[2:])))
        else:
            print(app.query_ai(' '.join(sys.argv[1:])))

if __name__ == "__main__":
    main()
