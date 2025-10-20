#!/usr/bin/env python3
"""
TermiGPT v2.0.1 - AI-Powered Security Research Terminal Assistant
By TheNooB
GitHub: https://github.com/thenoob4

Professional tool for cybersecurity researchers, penetration testers, and students.
"""

import os, sys, json, time, socket, subprocess, requests, re, threading, shutil, concurrent.futures, shlex, platform
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
SESSION_FILE = CONFIG_DIR / "session_history.json"
CONFIG_DIR.mkdir(exist_ok=True)

# Port to Protocol mapping
PORT_PROTOCOLS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    445: "SMB", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    8080: "HTTP-ALT", 8443: "HTTPS-ALT", 27017: "MongoDB"
}

# Project structure templates
PROJECT_STRUCTURES = {
    "react": {
        "plain": """my-app/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── index.js
│   ├── App.js
│   ├── App.css
│   ├── components/
│   ├── pages/
│   ├── assets/
│   └── utils/
├── package.json
├── .gitignore
└── README.md""",
        "typescript": """my-app/
├── public/
│   └── index.html
├── src/
│   ├── index.tsx
│   ├── App.tsx
│   ├── components/
│   ├── types/
│   ├── hooks/
│   └── utils/
├── tsconfig.json
├── package.json
└── .gitignore"""
    },
    "nextjs": """my-app/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── api/
│   └── dashboard/
├── components/
├── lib/
├── public/
├── styles/
│   └── globals.css
├── next.config.js
├── package.json
└── tsconfig.json""",
    "vue": """my-app/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── components/
│   ├── views/
│   ├── router/
│   ├── store/
│   └── assets/
├── public/
├── vite.config.js
└── package.json""",
    "fullstack": """my-fullstack-app/
├── backend/
│   ├── server.js
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── config/
│   └── middleware/
├── frontend/
│   ├── index.html
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
├── .env
├── package.json
└── README.md""",
    "mern": """mern-app/
├── backend/
│   ├── server.js
│   ├── routes/
│   ├── models/
│   ├── controllers/
│   └── config/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
├── package.json
└── .env"""
}

# Enhanced code generation prompt with structure awareness
CODE_GEN_PROMPT = """You are an ELITE full-stack code generator creating PRODUCTION-READY applications.

CRITICAL REQUIREMENTS:
1. Generate COMPLETE, WORKING code with NO placeholders
2. Follow MODERN industry-standard folder structures
3. Create ALL necessary files for immediate deployment
4. Include proper configuration files (package.json, tsconfig.json, etc.)
5. Add comprehensive error handling and validation

OUTPUT FORMAT - MANDATORY:

[FILE: path/filename.ext]
<complete production code>
[/FILE]

STRUCTURE GUIDELINES:
- React: Include index.html, index.js/tsx, App.js/tsx, package.json, components/, pages/, assets/
- Next.js: Use app/ router with layout.tsx, page.tsx, globals.css, next.config.js
- Vue: Include main.js, App.vue, components/, views/, router/, vite.config.js
- Full-stack: Separate backend/ and frontend/ with proper API structure
- HTML/CSS/JS: Include index.html, css/, js/, assets/ folders

VERIFICATION CHECKLIST:
- [ ] ALL files wrapped in [FILE:][/FILE] tags
- [ ] Complete folder structure (no missing directories)
- [ ] All configuration files included
- [ ] No "TODO" or placeholders
- [ ] Proper imports and dependencies
- [ ] README with setup instructions
- [ ] .gitignore file included
- [ ] Package manager files (package.json, requirements.txt, etc.)

Generate the COMPLETE, DEPLOYMENT-READY project now."""

def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def show_welcome_banner():
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

{Colors.RED}{Colors.BOLD}  🛡️  AI-Powered Security Research Terminal v2.0.1{Colors.END}
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

{Colors.YELLOW}🎯 CORE COMMANDS:{Colors.END}
  {Colors.GREEN}Code Generation:{Colors.END}
    create/code/write <desc>     Generate complete projects
    
  {Colors.GREEN}Execution:{Colors.END}
    run/execute <file>            Execute scripts
    
  {Colors.GREEN}Security Operations:{Colors.END}
    recon <target>                Full reconnaissance
    enum <target>                 Subdomain enumeration
    portscan <target>             Port scanning
    scan <target>                 Security assessment
    
  {Colors.GREEN}AI & Models:{Colors.END}
    models                        List AI models
    select                        Change model
    ask <question>                AI query
    
{Colors.YELLOW}💡 EXAMPLES:{Colors.END}
  {Colors.WHITE}termi create a React dashboard with TypeScript
  termi code a Next.js e-commerce app
  termi recon example.com
  termi run app.py{Colors.END}

{Colors.RED}⚠️  ETHICAL USE: Authorized testing only!{Colors.END}
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
        self.system_info = {'platform': platform.system(), 'is_linux': platform.system() == 'Linux'}

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
        if show_anim:
            self.start_animation(f"{Colors.BLUE}🤖 AI analyzing{Colors.END}")

        m = self.models[self.current_model]

        if use_code_gen_prompt:
            full_prompt = f"{CODE_GEN_PROMPT}\n\nUSER REQUEST: {prompt}\n\nGenerate the complete project with ALL necessary files."
        else:
            full_prompt = prompt

        try:
            params = {'prompt': full_prompt, 'model': m['worker_key']}
            url = f"{WORKER_URL}?{urlencode(params)}"
            response = requests.get(url, timeout=120)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('response') or data.get('text') or "No response"
                else:
                    result = f"{Colors.YELLOW}⚠️  System busy. Try: {Colors.CYAN}termi select{Colors.END}"
            else:
                result = f"{Colors.YELLOW}⚠️  Service unavailable. Try: {Colors.CYAN}termi select{Colors.END}"

        except:
            result = f"{Colors.YELLOW}⚠️  Connection issue. Check internet and try: {Colors.CYAN}termi select{Colors.END}"

        if show_anim:
            self.stop_animation_thread()

        return result

    def detect_framework(self, desc: str) -> Optional[str]:
        """Detect framework/stack from description"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ['next.js', 'nextjs', 'next js']):
            return 'nextjs'
        elif 'typescript' in desc_lower and 'react' in desc_lower:
            return 'react-ts'
        elif 'react' in desc_lower:
            return 'react'
        elif 'vue' in desc_lower:
            return 'vue'
        elif any(word in desc_lower for word in ['full-stack', 'fullstack', 'mern', 'backend', 'frontend']):
            return 'fullstack'
        
        return None

    def enhance_prompt_with_structure(self, user_prompt: str) -> str:
        """Enhance user prompt with structure requirements"""
        framework = self.detect_framework(user_prompt)
        
        structure_guide = ""
        if framework and framework in PROJECT_STRUCTURES:
            if framework == 'react-ts':
                structure_guide = f"\n\nUSE THIS FOLDER STRUCTURE:\n{PROJECT_STRUCTURES['react']['typescript']}"
            elif framework in PROJECT_STRUCTURES:
                structure_guide = f"\n\nUSE THIS FOLDER STRUCTURE:\n{PROJECT_STRUCTURES[framework]}"
        
        enhanced = f"""{user_prompt}{structure_guide}

MANDATORY REQUIREMENTS:
1. Create COMPLETE folder structure with ALL files
2. Include package.json with all dependencies
3. Include configuration files (tsconfig.json, vite.config.js, etc.)
4. Add globals.css or main styling file
5. Include README.md with setup instructions
6. Add .gitignore file
7. NO placeholders - complete working code only

After generating, verify completeness and enhance if needed."""
        
        return enhanced

    def create_project(self, desc):
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🚀 Generating Production-Ready Project{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        # Enhance prompt with structure
        enhanced_prompt = self.enhance_prompt_with_structure(desc)
        
        self.start_animation(f"{Colors.BLUE}🤖 Generating complete project{Colors.END}")
        response = self.query_ai(enhanced_prompt, show_anim=False, use_code_gen_prompt=True)
        self.stop_animation_thread()

        if "System busy" in response or "Service unavailable" in response:
            print(f"\n{response}\n")
            return

        # Extract files
        file_pattern = r'\[FILE:\s*([^\]]+)\]\s*(.*?)\s*\[/FILE\]'
        files = re.findall(file_pattern, response, re.DOTALL | re.IGNORECASE)

        if not files or len(files) < 3:
            print(f"{Colors.YELLOW}⚠️  Incomplete response. Requesting enhancement...{Colors.END}\n")
            
            # Second pass - request completeness
            enhance_prompt = f"The previous response was incomplete. Generate ALL files including:\n- All source files\n- package.json or equivalent\n- Configuration files\n- Styling files (globals.css, etc.)\n- README.md\n- .gitignore\n\nOriginal request: {desc}"
            
            self.start_animation(f"{Colors.BLUE}🤖 Enhancing project{Colors.END}")
            response = self.query_ai(enhance_prompt, show_anim=False, use_code_gen_prompt=True)
            self.stop_animation_thread()
            
            files = re.findall(file_pattern, response, re.DOTALL | re.IGNORECASE)

        if not files:
            print(f"{Colors.RED}❌ Could not generate project. Try: {Colors.CYAN}termi select{Colors.END} to switch models\n")
            return

        # Determine project name
        project_name = re.sub(r'[^\w\s-]', '', desc[:30]).replace(' ', '-').lower()
        pdir = Path.cwd() / project_name
        pdir.mkdir(exist_ok=True)
        
        print(f"{Colors.CYAN}📁 Project: {pdir}{Colors.END}\n")

        # Create all files
        created_files = []
        for filepath, content in files:
            filepath = filepath.strip()
            content = content.strip()
            
            # Clean code blocks
            content = re.sub(r'^```[\w]*\n', '', content)
            content = re.sub(r'\n```$', '', content)
            
            full_path = pdir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                full_path.write_text(content, encoding='utf-8')
                created_files.append(filepath)
                
                # Make scripts executable
                if filepath.endswith(('.sh', '.py')):
                    os.chmod(full_path, 0o755)
                
                print(f"  {Colors.GREEN}✅ {filepath}{Colors.END}")
            except Exception as e:
                print(f"  {Colors.RED}❌ {filepath}: {str(e)[:50]}{Colors.END}")

        # Ensure .gitignore exists
        gitignore = pdir / '.gitignore'
        if not gitignore.exists():
            gitignore.write_text('node_modules/\n.env\n*.log\n.DS_Store\n__pycache__/\n*.pyc\ndist/\nbuild/\n')
            print(f"  {Colors.GREEN}✅ .gitignore{Colors.END}")

        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESS! {len(created_files)} files created{Colors.END}")
        print(f"{Colors.CYAN}📁 Location:{Colors.END} {pdir}")
        print(f"{Colors.YELLOW}💡 Next:{Colors.END} cd {project_name} && cat README.md")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")

    def execute_code(self, file_path):
        path = Path(file_path)
        if not path.exists():
            print(f"{Colors.RED}❌ File not found: {file_path}{Colors.END}\n")
            return

        ext = path.suffix.lower()
        executors = {
            '.py': ['python3', str(path)],
            '.js': ['node', str(path)],
            '.sh': ['bash', str(path)],
            '.rb': ['ruby', str(path)],
            '.php': ['php', str(path)]
        }

        if ext not in executors:
            print(f"{Colors.RED}❌ Unsupported: {ext}{Colors.END}\n")
            return

        cmd = executors[ext]
        print(f"{Colors.GREEN}🚀 Executing: {path}{Colors.END}\n")

        try:
            # Execute and capture output in real-time
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            print(f"{Colors.CYAN}{'='*70}{Colors.END}")
            print(f"{Colors.CYAN}📤 OUTPUT:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*70}{Colors.END}")

            # Read output in real-time
            stdout_lines = []
            stderr_lines = []
            
            for line in process.stdout:
                print(line, end='')
                stdout_lines.append(line)

            process.wait()

            # Read any stderr
            stderr_output = process.stderr.read()
            if stderr_output:
                stderr_lines = stderr_output.split('\n')

            # Handle missing modules
            if process.returncode != 0 and ext == '.py' and stderr_output:
                if 'ModuleNotFoundError' in stderr_output or 'No module named' in stderr_output:
                    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", stderr_output)
                    if match:
                        module = match.group(1)
                        print(f"\n{Colors.YELLOW}⚠️  Missing module: {module}{Colors.END}")
                        
                        pip_map = {
                            'bs4': 'beautifulsoup4', 'cv2': 'opencv-python',
                            'PIL': 'Pillow', 'sklearn': 'scikit-learn'
                        }
                        pkg = pip_map.get(module, module)
                        
                        install = input(f"{Colors.CYAN}📦 Install '{pkg}'? (Y/n):{Colors.END} ").strip().lower()
                        if install != 'n':
                            print(f"{Colors.BLUE}📥 Installing...{Colors.END}")
                            subprocess.run([sys.executable, '-m', 'pip', 'install', pkg],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            print(f"{Colors.GREEN}✅ Installed. Re-running...{Colors.END}\n")
                            
                            # Re-run
                            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                            for line in process.stdout:
                                print(line, end='')
                            process.wait()
                            stderr_output = process.stderr.read()

            # Show output summary
            if not stdout_lines and not stderr_output:
                print(f"{Colors.YELLOW}(no output produced){Colors.END}")

            if stderr_output and process.returncode != 0:
                print(f"\n{Colors.RED}❌ ERRORS:{Colors.END}")
                print(stderr_output)

            print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
            print(f"{Colors.CYAN}Exit Code:{Colors.END} {process.returncode}")
            print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        except Exception as e:
            print(f"{Colors.RED}❌ Execution error: {e}{Colors.END}\n")

    def reconnaissance_hardcoded(self, target):
        """Hardcoded reconnaissance using actual tools"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🔍 RECONNAISSANCE: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        results = {
            'target': target,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dns': {},
            'whois': '',
            'subdomains': [],
            'open_ports': []
        }

        # DNS Lookup
        print(f"{Colors.YELLOW}[1/4] DNS Lookup{Colors.END}")
        try:
            ip = socket.gethostbyname(target)
            results['dns']['ip'] = ip
            print(f"  {Colors.GREEN}✓{Colors.END} IP: {Colors.CYAN}{ip}{Colors.END}")
            
            try:
                hostname = socket.gethostbyaddr(ip)
                results['dns']['hostname'] = hostname[0]
                print(f"  {Colors.GREEN}✓{Colors.END} Hostname: {Colors.CYAN}{hostname[0]}{Colors.END}")
            except:
                pass
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.END} Could not resolve")
            results['dns']['error'] = str(e)

        # WHOIS
        print(f"\n{Colors.YELLOW}[2/4] WHOIS Lookup{Colors.END}")
        if shutil.which('whois'):
            try:
                result = subprocess.run(['whois', target], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    results['whois'] = result.stdout
                    lines = result.stdout.split('\n')[:10]
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
            except:
                print(f"  {Colors.YELLOW}⚠️  Timeout{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠️  whois not installed{Colors.END}")

        # Subdomain enumeration
        print(f"\n{Colors.YELLOW}[3/4] Subdomain Enumeration{Colors.END}")
        if shutil.which('subfinder'):
            try:
                result = subprocess.run(['subfinder', '-d', target, '-silent'], 
                                      capture_output=True, text=True, timeout=30)
                subdomains = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
                results['subdomains'] = subdomains
                for sub in subdomains[:10]:
                    print(f"  {Colors.GREEN}✓{Colors.END} {sub}")
                if len(subdomains) > 10:
                    print(f"  {Colors.CYAN}... and {len(subdomains) - 10} more{Colors.END}")
            except:
                print(f"  {Colors.YELLOW}⚠️  Timeout{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠️  subfinder not installed{Colors.END}")

        # Port scan
        print(f"\n{Colors.YELLOW}[4/4] Port Scan (Top 20){Colors.END}")
        common_ports = [21, 22, 23, 25, 80, 110, 143, 443, 445, 3306, 3389, 5432, 5900, 8080, 8443, 9200, 27017, 5672, 6379, 11211]
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                if sock.connect_ex((target, port)) == 0:
                    protocol = PORT_PROTOCOLS.get(port, "UNKNOWN")
                    results['open_ports'].append({'port': port, 'protocol': protocol})
                    print(f"  {Colors.GREEN}✓{Colors.END} Port {port}/{protocol} - {Colors.RED}OPEN{Colors.END}")
                sock.close()
            except:
                pass

        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}✅ Reconnaissance complete{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        # AI Summary
        self.generate_ai_summary(results, "reconnaissance")

    def enumerate_subdomains_hardcoded(self, target):
        """Hardcoded subdomain enumeration"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🌐 SUBDOMAIN ENUMERATION: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        results = {
            'target': target,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'subdomains': [],
            'method': 'subfinder'
        }

        if shutil.which('subfinder'):
            print(f"{Colors.BLUE}Running subfinder...{Colors.END}\n")
            try:
                result = subprocess.run(['subfinder', '-d', target, '-silent'],
                                      capture_output=True, text=True, timeout=60)
                subdomains = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
                results['subdomains'] = subdomains
                
                for sub in subdomains:
                    print(f"  {Colors.GREEN}✓{Colors.END} {sub}")
                
                print(f"\n{Colors.GREEN}Found {len(subdomains)} subdomains{Colors.END}")
            except:
                print(f"{Colors.YELLOW}⚠️  Timeout{Colors.END}")
                results['error'] = 'timeout'
        else:
            print(f"{Colors.YELLOW}⚠️  subfinder not installed{Colors.END}")
            print(f"{Colors.CYAN}Install: go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest{Colors.END}")
            results['error'] = 'tool_not_installed'

        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}\n")

        # AI Summary
        if results['subdomains']:
            self.generate_ai_summary(results, "subdomain_enumeration")

    def portscan_hardcoded(self, target):
        """Hardcoded port scanning with progress"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}🔓 PORT SCAN: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        results = {
            'target': target,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_scanned': 1000,
            'open_ports': [],
            'scan_duration': 0
        }

        ports = list(range(1, 1001))
        open_ports = []

        print(f"{Colors.YELLOW}Scanning 1000 ports...{Colors.END}\n")
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_port = {
                executor.submit(self.check_port, target, port): port 
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result:
                    open_ports.append(result)
                    results['open_ports'].append(result)
                    print(f"  {Colors.GREEN}✓{Colors.END} Port {result['port']}/{result['protocol']} - {Colors.RED}OPEN{Colors.END}")

        results['scan_duration'] = round(time.time() - start_time, 2)

        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}✅ Scan complete in {results['scan_duration']}s{Colors.END}")
        print(f"{Colors.GREEN}Found {len(open_ports)} open ports{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        # AI Summary
        self.generate_ai_summary(results, "port_scan")

    def generate_ai_summary(self, results, scan_type):
        """Generate professional AI summary of scan results"""
        print(f"{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.MAGENTA}{Colors.BOLD}🤖 AI SECURITY ANALYSIS{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.END}\n")

        # Build analysis prompt based on scan type
        if scan_type == "reconnaissance":
            prompt = f"""Analyze this reconnaissance scan and provide a professional security assessment:

Target: {results['target']}
Timestamp: {results['timestamp']}

DNS Information:
{json.dumps(results['dns'], indent=2)}

Subdomains Found: {len(results['subdomains'])}
Top Subdomains: {', '.join(results['subdomains'][:10])}

Open Ports Detected:
{json.dumps(results['open_ports'], indent=2)}

Provide:
1. Executive Summary (2-3 sentences)
2. Attack Surface Analysis
3. High-Priority Findings
4. Security Recommendations
5. Next Steps for deeper testing

Format in plain text, be specific and actionable."""

        elif scan_type == "subdomain_enumeration":
            prompt = f"""Analyze these enumerated subdomains for security implications:

Target: {results['target']}
Total Subdomains: {len(results['subdomains'])}
Subdomains: {', '.join(results['subdomains'][:20])}

Provide:
1. Attack Surface Assessment
2. High-Value Targets (admin, api, dev, staging, test subdomains)
3. Potential Information Disclosure Risks
4. Subdomain Takeover Possibilities
5. Recommended Next Steps

Be specific about which subdomains pose higher risk."""

        elif scan_type == "port_scan":
            prompt = f"""Analyze this port scan for security vulnerabilities:

Target: {results['target']}
Ports Scanned: {results['total_scanned']}
Open Ports: {len(results['open_ports'])}
Duration: {results['scan_duration']}s

Open Services:
{json.dumps(results['open_ports'], indent=2)}

Provide:
1. Critical Findings (databases, admin ports)
2. Risk Assessment for each open service
3. Common Vulnerabilities for detected services
4. Hardening Recommendations
5. Penetration Testing Next Steps

Use plain text format."""

        self.start_animation(f"{Colors.BLUE}🤖 Analyzing results{Colors.END}")
        analysis = self.query_ai(prompt, show_anim=False)
        self.stop_animation_thread()

        if "System busy" not in analysis and "Service unavailable" not in analysis:
            # Colorize the analysis
            analysis = self.colorize_security_analysis(analysis)
            print(analysis)
        else:
            print(f"{Colors.YELLOW}⚠️  AI analysis unavailable. Results saved above.{Colors.END}")

        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.END}\n")

    def colorize_security_analysis(self, text: str) -> str:
        """Colorize AI security analysis for better readability"""
        # Remove markdown
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)

        # Highlight risk levels
        text = re.sub(r'\b(CRITICAL|SEVERE)\b', f'{Colors.BG_RED}{Colors.WHITE}\\1{Colors.END}', text, flags=re.I)
        text = re.sub(r'\b(HIGH)\b', f'{Colors.RED}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)
        text = re.sub(r'\b(MEDIUM)\b', f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)
        text = re.sub(r'\b(LOW)\b', f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)

        # Highlight security keywords
        vuln_keywords = ['vulnerable', 'vulnerability', 'exploit', 'exposed', 'risk', 'attack', 'breach', 'weak', 'insecure']
        for keyword in vuln_keywords:
            text = re.sub(f'\\b({keyword})\\b', f'{Colors.RED}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)

        # Highlight positive keywords
        positive_keywords = ['secure', 'protected', 'recommended', 'good', 'strong', 'hardened']
        for keyword in positive_keywords:
            text = re.sub(f'\\b({keyword})\\b', f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)

        # Highlight section headers
        headers = ['Executive Summary:', 'Attack Surface:', 'Findings:', 'Recommendations:', 'Next Steps:', 'Assessment:', 'Analysis:']
        for header in headers:
            text = re.sub(f'^({header})', f'{Colors.CYAN}{Colors.BOLD}\\1{Colors.END}', text, flags=re.MULTILINE)

        return text

    def execute_code(self, file_path):
        """Enhanced code execution with multiple fallback methods"""
        path = Path(file_path)
        if not path.exists():
            print(f"{Colors.RED}❌ File not found: {file_path}{Colors.END}\n")
            return

        ext = path.suffix.lower()
        
        print(f"{Colors.GREEN}🚀 Executing: {path}{Colors.END}\n")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.CYAN}📤 OUTPUT:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}\n")

        try:
            if ext == '.py':
                # Python - use subprocess.run for better output handling
                result = subprocess.run(
                    ["python3", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Print output immediately
                if result.stdout:
                    print(result.stdout)
                
                # Handle missing modules
                if result.returncode != 0 and result.stderr:
                    if 'ModuleNotFoundError' in result.stderr or 'No module named' in result.stderr:
                        match = re.search(r"No module named ['\"]([^'\"]+)['\"]", result.stderr)
                        if match:
                            module = match.group(1)
                            print(f"\n{Colors.YELLOW}⚠️  Missing module: {module}{Colors.END}")
                            
                            pip_map = {'bs4': 'beautifulsoup4', 'cv2': 'opencv-python', 'PIL': 'Pillow', 'sklearn': 'scikit-learn'}
                            pkg = pip_map.get(module, module)
                            
                            install = input(f"{Colors.CYAN}📦 Install '{pkg}'? (Y/n):{Colors.END} ").strip().lower()
                            if install != 'n':
                                print(f"{Colors.BLUE}📥 Installing...{Colors.END}")
                                subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], 
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                print(f"{Colors.GREEN}✅ Installed. Re-running...{Colors.END}\n")
                                
                                # Re-run
                                result = subprocess.run(["python3", str(path)], capture_output=True, text=True, timeout=60)
                                if result.stdout:
                                    print(result.stdout)
                    else:
                        print(f"\n{Colors.RED}❌ ERRORS:{Colors.END}")
                        print(result.stderr)
                
                exit_code = result.returncode
                
            elif ext == '.sh':
                # Shell script
                result = subprocess.run(["bash", str(path)], capture_output=True, text=True, timeout=60)
                if result.stdout:
                    print(result.stdout)
                if result.stderr and result.returncode != 0:
                    print(f"\n{Colors.RED}❌ ERRORS:{Colors.END}")
                    print(result.stderr)
                exit_code = result.returncode
                
            elif ext == '.js':
                # JavaScript
                result = subprocess.run(["node", str(path)], capture_output=True, text=True, timeout=60)
                if result.stdout:
                    print(result.stdout)
                if result.stderr and result.returncode != 0:
                    print(f"\n{Colors.RED}❌ ERRORS:{Colors.END}")
                    print(result.stderr)
                exit_code = result.returncode
                
            else:
                print(f"{Colors.RED}❌ Unsupported file type: {ext}{Colors.END}")
                exit_code = 1

            # Show summary
            if not result.stdout and not result.stderr:
                print(f"{Colors.YELLOW}(script executed but produced no output){Colors.END}")

            print(f"\n{Colors.CYAN}{'-'*70}{Colors.END}")
            print(f"{Colors.CYAN}Exit Code:{Colors.END} {exit_code}")
            if exit_code == 0:
                print(f"{Colors.GREEN}✅ Execution successful{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Execution failed{Colors.END}")
            print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        except subprocess.TimeoutExpired:
            print(f"\n{Colors.RED}⏰ Execution timeout (60s){Colors.END}\n")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Execution error: {e}{Colors.END}\n")

    def check_port(self, target, port, timeout=0.5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            if sock.connect_ex((target, port)) == 0:
                protocol = PORT_PROTOCOLS.get(port, "UNKNOWN")
                sock.close()
                return {'port': port, 'protocol': protocol}
        except:
            pass
        return None

    def display_models(self):
        print(f"\n{Colors.CYAN}🤖 Available Models:{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        for n, m in self.models.items():
            current = f" {Colors.GREEN}👈 CURRENT{Colors.END}" if n == self.current_model else ""
            print(f"  {Colors.YELLOW}{n}.{Colors.END} {Colors.WHITE}{m['name']:<20}{Colors.END}{current}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

    def select_model(self):
        self.display_models()
        choice = input(f"{Colors.YELLOW}Select (1-5):{Colors.END} ").strip()
        if choice in self.models:
            self.current_model = choice
            self.save_current_model()
            print(f"{Colors.GREEN}✅ Switched to: {self.models[choice]['name']}{Colors.END}\n")
        else:
            print(f"{Colors.RED}❌ Invalid{Colors.END}\n")

    def show_history(self):
        if not self.session_history:
            print(f"{Colors.YELLOW}No command history{Colors.END}\n")
            return

        print(f"\n{Colors.CYAN}📜 Command History:{Colors.END}")
        for idx, cmd in enumerate(self.session_history[-20:], 1):
            print(f"  {idx}. {cmd}")
        print()

    def get_identity_response(self):
        return f"""{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║           TermiGPT - Security Research Assistant             ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.BOLD}What I Am:{Colors.END}
AI-powered terminal assistant for cybersecurity professionals,
penetration testers, and security students.

{Colors.BOLD}Capabilities:{Colors.END}
  🔍 Reconnaissance & OSINT
  💻 Production Code Generation  
  🎯 Vulnerability Assessment
  📊 VAPT Reporting
  🛠️  Security Tool Integration
  🧠 Learning & Training

{Colors.BOLD}Powered By:{Colors.END} 5 AI Models
{Colors.BOLD}Focus:{Colors.END} Ethical hacking, authorized security testing

{Colors.RED}⚠️  For authorized, ethical security testing only.{Colors.END}

Type '{Colors.CYAN}help{Colors.END}' for commands.
"""

    def interactive_mode(self):
        print(f"\n{Colors.GREEN}🎯 Model: {Colors.BOLD}{self.models[self.current_model]['name']}{Colors.END}")
        print(f"{Colors.CYAN}💡 Type 'help' for commands, 'exit' to quit{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  For authorized security testing only{Colors.END}\n")

        while True:
            try:
                cmd = input(f"{Colors.BOLD}{Colors.GREEN}termi> {Colors.END}").strip()
                
                if not cmd:
                    continue
                
                self.session_history.append(cmd)
                cmd_lower = cmd.lower()
                    
                if cmd_lower in ['exit', 'quit', 'bye', 'q']:
                    print(f"{Colors.CYAN}👋 Goodbye!{Colors.END}")
                    break
                
                elif cmd_lower == 'clear':
                    os.system('clear' if self.system_info['is_linux'] else 'cls')
                    
                elif cmd_lower == 'help':
                    show_help_menu()
                    
                elif cmd_lower == 'history':
                    self.show_history()
                    
                elif cmd_lower == 'models':
                    self.display_models()
                    
                elif cmd_lower == 'select':
                    self.select_model()
                
                elif cmd_lower in ['who are you', 'what are you', 'capabilities', 'what can you do']:
                    print(self.get_identity_response())
                
                elif cmd_lower.startswith('recon '):
                    target = cmd.split(maxsplit=1)[1]
                    self.reconnaissance_hardcoded(target)
                
                elif cmd_lower.startswith('enum '):
                    target = cmd.split()[-1]
                    self.enumerate_subdomains_hardcoded(target)
                
                elif cmd_lower.startswith('portscan '):
                    target = cmd.split(maxsplit=1)[1]
                    self.portscan_hardcoded(target)
                
                elif cmd_lower.startswith('scan '):
                    target = cmd.split(maxsplit=1)[1]
                    self.portscan_hardcoded(target)
                
                elif any(cmd_lower.startswith(p) for p in ['create ', 'write ', 'code ', 'generate ', 'build ', 'make ']):
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
                print(f"{Colors.RED}❌ Error: {e}{Colors.END}\n")
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
                cmd_lower = user_input.lower()
                
                if cmd_lower in ['help', 'h']:
                    show_help_menu()
                elif cmd_lower == 'models':
                    app.display_models()
                elif cmd_lower in ['who are you', 'what are you', 'capabilities']:
                    print(app.get_identity_response())
                elif cmd_lower.startswith('recon '):
                    target = user_input.split(maxsplit=1)[1]
                    app.reconnaissance_hardcoded(target)
                elif cmd_lower.startswith('enum '):
                    target = user_input.split()[-1]
                    app.enumerate_subdomains_hardcoded(target)
                elif cmd_lower.startswith(('portscan ', 'scan ')):
                    target = user_input.split(maxsplit=1)[1]
                    app.portscan_hardcoded(target)
                elif any(cmd_lower.startswith(p) for p in ['create ', 'write ', 'code ', 'generate ', 'build ']):
                    app.create_project(user_input)
                elif cmd_lower.startswith(('run ', 'execute ')):
                    filepath = ' '.join(user_input.split()[1:])
                    app.execute_code(filepath)
                else:
                    result = app.query_ai(user_input)
                    print(f"\n{result}\n")
                
                # Enter interactive mode after command
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
        elif len(sys.argv) > 2:
            full_input = ' '.join(sys.argv[1:])
            
            if cmd == 'recon':
                app.reconnaissance_hardcoded(sys.argv[2])
            elif cmd == 'enum':
                app.enumerate_subdomains_hardcoded(sys.argv[2])
            elif cmd in ['scan', 'portscan']:
                app.portscan_hardcoded(sys.argv[2])
            elif cmd in ['run', 'execute']:
                app.execute_code(' '.join(sys.argv[2:]))
            elif cmd in ['create', 'code', 'write', 'generate', 'build', 'make']:
                app.create_project(' '.join(sys.argv[2:]))
            elif cmd == 'ask':
                result = app.query_ai(' '.join(sys.argv[2:]))
                print(f"\n{result}\n")
            else:
                result = app.query_ai(full_input)
                print(f"\n{result}\n")
        else:
            result = app.query_ai(sys.argv[1])
            print(f"\n{result}\n")

if __name__ == "__main__":
    main()
