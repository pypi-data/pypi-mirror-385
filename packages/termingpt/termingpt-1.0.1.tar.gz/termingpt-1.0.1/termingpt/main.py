# File: termigpt-package/termigpt/main.py

#!/usr/bin/env python3
"""
TermiGPT v1.0.0 - AI-Powered Terminal Assistant
By TheNooB
GitHub: https://github.com/thenoob4
GitHub: https://github.com/codelabwithosman

Uses Cloudflare Worker: https://noobt.insta-acc-sec.workers.dev/ask
No API keys needed in code - all handled by worker!
"""

import os, sys, json, time, socket, subprocess, requests, re, threading, shutil
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

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
    8443: "HTTPS-ALT", 27017: "MongoDB", 27018: "MongoDB"
}

def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def show_welcome_banner():
    width = min(get_terminal_width(), 70)

    banner = f"""{Colors.CYAN}{Colors.BOLD}
{'='*width}
{Colors.GREEN}TermiGPT v1.0.0{Colors.CYAN} - AI-Powered Terminal Assistant
{'='*width}{Colors.END}

{Colors.WHITE}By {Colors.BOLD}TheNooB{Colors.END}
{Colors.BLUE}GitHub:{Colors.END} {Colors.UNDERLINE}https://github.com/thenoob4{Colors.END}
{Colors.BLUE}GitHub:{Colors.END} {Colors.UNDERLINE}https://github.com/codelabwithosman{Colors.END}

{Colors.YELLOW}✨ Smart Detection • Auto-Install • Security Scanning • Stealth Mode{Colors.END}
{Colors.GREEN}🔑 No setup needed - Ready to use!{Colors.END}
"""
    print(banner)

def show_help_menu():
    width = min(get_terminal_width(), 70)

    help_text = f"""
{Colors.CYAN}{'='*width}{Colors.END}
{Colors.BOLD}{Colors.GREEN}📚 QUICK START GUIDE{Colors.END}
{Colors.CYAN}{'='*width}{Colors.END}

{Colors.YELLOW}🎯 Usage Modes:{Colors.END}

  1. {Colors.GREEN}Interactive Mode:{Colors.END}
     {Colors.WHITE}termigpt{Colors.END}

  2. {Colors.GREEN}Direct Commands:{Colors.END}
     {Colors.WHITE}termigpt <command> [arguments]{Colors.END}

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}📋 Available Commands:{Colors.END}

  {Colors.GREEN}Project:{Colors.END} create, write, code <description>
  {Colors.GREEN}Execute:{Colors.END} run, execute <file>
  {Colors.GREEN}Scan:{Colors.END} scan <target> [stealth]
  {Colors.GREEN}Models:{Colors.END} models, select, whois
  {Colors.GREEN}Chat:{Colors.END} ask <question>

{Colors.CYAN}{'-'*width}{Colors.END}

{Colors.YELLOW}💡 Examples:{Colors.END}

  {Colors.WHITE}termigpt create a todo app{Colors.END}
  {Colors.WHITE}termigpt code a python script to check weather{Colors.END}
  {Colors.WHITE}termigpt scan google.com{Colors.END}
  {Colors.WHITE}termigpt scan example.com stealth{Colors.END}
  {Colors.WHITE}termigpt run script.py{Colors.END}

{Colors.CYAN}{'='*width}{Colors.END}

{Colors.GREEN}🚀 Choose your mode:{Colors.END}
  • Type a {Colors.BOLD}command{Colors.END} from above
  • Or press {Colors.BOLD}Enter{Colors.END} for interactive mode
  • Type {Colors.BOLD}help{Colors.END} to see this menu again

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

    def query_ai(self, prompt, show_anim=True):
        if show_anim:
            self.start_animation(f"{Colors.BLUE}🤖 AI thinking{Colors.END}")

        m = self.models[self.current_model]

        try:
            params = {'prompt': prompt, 'model': m['worker_key']}
            url = f"{WORKER_URL}?{urlencode(params)}"

            response = requests.get(url, timeout=60)

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
        full_project_keywords = ['application', 'app', 'project', 'system', 'platform', 'website', 'webapp', 'web app', 'dashboard', 'portal', 'api', 'rest api', 'backend', 'frontend', 'full-stack', 'microservice', 'service', 'cms', 'blog', 'e-commerce', 'production', 'deploy', 'scalable', 'enterprise']

        for keyword in single_file_keywords:
            if keyword in desc_lower:
                return 'single_file'

        for keyword in full_project_keywords:
            if keyword in desc_lower:
                return 'full_project'

        words = desc.split()
        if len(words) < 8:
            return 'single_file'

        if any(word in desc_lower for word in ['database', 'authentication', 'docker', 'deployment', 'testing', 'ci/cd']):
            return 'full_project'

        return 'auto'

    def create_single_file(self, desc):
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}📝 Creating Single File: {desc}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        desc_lower = desc.lower()
        if 'python' in desc_lower or desc_lower.startswith('code'):
            ext, lang = 'py', 'Python'
        elif 'javascript' in desc_lower or 'js' in desc_lower:
            ext, lang = 'js', 'JavaScript'
        elif 'html' in desc_lower:
            ext, lang = 'html', 'HTML'
        elif 'bash' in desc_lower or 'shell' in desc_lower:
            ext, lang = 'sh', 'Shell'
        else:
            ext, lang = 'py', 'Python'

        base_name = re.sub(r'^(a|an|the)\s+', '', desc_lower)
        base_name = re.sub(r'\s*(code|script|file|program)\s*', '', base_name)
        base_name = re.sub(r'\s+to\s+', '_', base_name)
        base_name = re.sub(r'[^\w\s-]', '', base_name)
        base_name = re.sub(r'\s+', '_', base_name.strip())[:30]

        filename = f"{base_name}.{ext}"

        print(f"{Colors.YELLOW}📄 File:{Colors.END} {filename}")
        print(f"{Colors.YELLOW}🔤 Language:{Colors.END} {lang}\n")

        self.start_animation(f"{Colors.BLUE}🤖 Generating code{Colors.END}")
        code_prompt = f"Create a single, complete, production-ready {lang} file for: {desc}\n\nRequirements:\n- Single standalone file\n- Complete working code\n- Include all imports\n- Add helpful comments\n- Include error handling\n- Make it immediately runnable\n\nGenerate ONLY the code."
        code = self.query_ai(code_prompt, show_anim=False)
        self.stop_animation_thread()

        if code.startswith("Error:"):
            print(f"\n{Colors.RED}{code}{Colors.END}")
            return

        code = re.sub(r'^```[\w]*\n', '', code.strip())
        code = re.sub(r'\n```$', '', code).strip()

        filepath = Path.cwd() / filename

        if filepath.exists():
            overwrite = input(f"\n{Colors.YELLOW}⚠️  '{filename}' exists. Overwrite? (y/N):{Colors.END} ").lower()
            if overwrite != 'y':
                print(f"{Colors.RED}❌ Cancelled{Colors.END}")
                return

        filepath.write_text(code)

        if ext in ['py', 'sh']:
            os.chmod(filepath, 0o755)

        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESS!{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.CYAN}📄 File:{Colors.END} {filepath}")
        print(f"{Colors.CYAN}📊 Size:{Colors.END} {len(code)} characters")
        print(f"\n{Colors.YELLOW}🚀 Run it:{Colors.END}")

        if ext == 'py':
            print(f"{Colors.WHITE}   python3 {filename}{Colors.END}")
        elif ext == 'js':
            print(f"{Colors.WHITE}   node {filename}{Colors.END}")
        elif ext == 'sh':
            print(f"{Colors.WHITE}   ./{filename}{Colors.END}")

        print(f"{Colors.GREEN}{'='*70}{Colors.END}")

    def create_full_project(self, desc):
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🚀 Creating Full Project: {desc}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        self.start_animation(f"{Colors.BLUE}🧠 AI designing structure{Colors.END}")
        struct_prompt = f"Design file structure for: {desc}\nJSON only:\n{{'project_type':'html','project_name':'name','folders':['f1'],'files':{{'p/f.ext':'desc'}},'tech_stack':['t1'],'main_file':'index.html'}}"
        resp = self.query_ai(struct_prompt, show_anim=False)
        self.stop_animation_thread()

        if resp.startswith("Error:"):
            print(f"\n{Colors.RED}{resp}{Colors.END}")
            return

        try:
            struct = json.loads(re.search(r'\{.*\}', resp, re.DOTALL).group())
        except:
            struct = {"project_type":"html","project_name":"project","folders":["css","js"],"files":{"index.html":"Main","css/style.css":"CSS","js/script.js":"JS"},"tech_stack":["html","css","js"],"main_file":"index.html"}

        print(f"\n{Colors.YELLOW}📋 Structure:{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.WHITE}Type:{Colors.END} {Colors.BOLD}{struct['project_type'].upper()}{Colors.END}")
        print(f"{Colors.WHITE}Stack:{Colors.END} {Colors.CYAN}{','.join(struct['tech_stack'])}{Colors.END}")
        print(f"\n{Colors.YELLOW}Folders:{Colors.END}")
        for f in struct['folders']: print(f"  {Colors.BLUE}📂 {f}/{Colors.END}")
        print(f"\n{Colors.YELLOW}Files:{Colors.END}")
        for p,d in list(struct['files'].items())[:10]: print(f"  {Colors.GREEN}📄 {p:<30}{Colors.END} {Colors.WHITE}- {d}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        if input(f"\n{Colors.YELLOW}Proceed? (Y/n):{Colors.END} ").lower() == 'n':
            return print(f"{Colors.RED}❌ Cancelled{Colors.END}")

        name = re.sub(r'[^\w-]','',struct['project_name'].replace(' ','-'))
        pdir = Path.cwd() / name
        pdir.mkdir(exist_ok=True)
        print(f"\n{Colors.CYAN}📁 {pdir}{Colors.END}")

        print(f"\n{Colors.YELLOW}📦 Creating folders...{Colors.END}")
        for f in struct['folders']:
            (pdir/f).mkdir(parents=True,exist_ok=True)
            print(f"  {Colors.GREEN}✅ {f}/{Colors.END}")

        self.start_animation(f"{Colors.BLUE}🤖 Generating code{Colors.END}")
        code_prompt = f"Complete code for: {desc}\nStructure: {json.dumps(struct)}\nFormat: [FILE: path]\ncode\n[/FILE]"
        code = self.query_ai(code_prompt, show_anim=False)
        self.stop_animation_thread()

        if code.startswith("Error:"):
            print(f"\n{Colors.RED}{code}{Colors.END}")
            return

        print(f"\n{Colors.YELLOW}⚙️  Creating files...{Colors.END}")
        created = []
        for p,c in re.findall(r'\[FILE:\s*([^\]]+)\](.*?)\[/FILE\]', code, re.DOTALL|re.I):
            p = p.strip()
            c = re.sub(r'^```\w*\n','',c.strip())
            c = re.sub(r'\n```$','',c).strip()
            fp = pdir/p
            fp.parent.mkdir(parents=True,exist_ok=True)
            fp.write_text(c)
            created.append(p)
            print(f"  {Colors.GREEN}✅ {p}{Colors.END}")

        (pdir/'README.md').write_text(f'# {name}\n\n{desc}\n\nGenerated by TermiGPT v1.0.0')
        (pdir/'.gitignore').write_text('.DS_Store\n*.log\nnode_modules/\n.env\n')
        print(f"  {Colors.GREEN}✅ README.md{Colors.END}")
        print(f"  {Colors.GREEN}✅ .gitignore{Colors.END}")

        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 SUCCESS!{Colors.END}")
        print(f"{Colors.CYAN}📁 {pdir}{Colors.END}")
        print(f"{Colors.CYAN}📊 {len(list(pdir.rglob('*.*')))} files{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")

    def create_project(self, desc):
        complexity = self.detect_project_complexity(desc)

        if complexity == 'single_file':
            print(f"{Colors.MAGENTA}💡 Detected: Single file request{Colors.END}")
            self.create_single_file(desc)
        elif complexity == 'full_project':
            print(f"{Colors.MAGENTA}💡 Detected: Full project request{Colors.END}")
            self.create_full_project(desc)
        else:
            print(f"\n{Colors.YELLOW}🤔 What do you want to create?{Colors.END}")
            print(f"  {Colors.CYAN}1.{Colors.END} Single file (quick script)")
            print(f"  {Colors.CYAN}2.{Colors.END} Full project (complete structure)")

            try:
                choice = input(f"\n{Colors.YELLOW}Select (1/2):{Colors.END} ").strip()
                if choice == '1':
                    self.create_single_file(desc)
                elif choice == '2':
                    self.create_full_project(desc)
                else:
                    print(f"{Colors.RED}❌ Invalid choice{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n{Colors.RED}❌ Cancelled{Colors.END}")

    def execute_code(self, file_path):
        path = Path(file_path)
        if not path.exists():
            print(f"{Colors.RED}❌ File not found: {file_path}{Colors.END}")
            return

        ext = path.suffix.lower()
        executors = {'.py': 'python3', '.js': 'node', '.sh': 'bash', '.rb': 'ruby', '.php': 'php', '.go': 'go run'}

        cmd = executors.get(ext)
        if not cmd:
            print(f"{Colors.RED}❌ Unsupported: {ext}{Colors.END}")
            return

        print(f"{Colors.GREEN}🚀 Executing: {path}{Colors.END}")

        try:
            result = subprocess.run(f"{cmd} {path}", shell=True, capture_output=True, text=True, timeout=30)

            if result.returncode != 0 and ext == '.py':
                stderr = result.stderr

                if 'ModuleNotFoundError' in stderr or 'No module named' in stderr:
                    match = re.search(r"No module named ['"]([^'"]+)['"]", stderr)
                    if match:
                        module = match.group(1)
                        print(f"\n{Colors.YELLOW}⚠️  Missing Python module: {module}{Colors.END}")

                        pip_map = {'bs4': 'beautifulsoup4', 'cv2': 'opencv-python', 'PIL': 'Pillow', 'sklearn': 'scikit-learn', 'yaml': 'pyyaml'}
                        pip_package = pip_map.get(module, module)

                        try:
                            install = input(f"{Colors.CYAN}📦 Install '{pip_package}' now? (Y/n):{Colors.END} ").strip().lower()
                            if install != 'n':
                                print(f"{Colors.BLUE}📥 Installing {pip_package}...{Colors.END}")
                                install_result = subprocess.run([sys.executable, '-m', 'pip', 'install', pip_package], capture_output=True, text=True)

                                if install_result.returncode == 0:
                                    print(f"{Colors.GREEN}✅ Installed {pip_package}{Colors.END}")
                                    print(f"\n{Colors.BLUE}🔄 Re-running {path}...{Colors.END}")
                                    result = subprocess.run(f"{cmd} {path}", shell=True, capture_output=True, text=True, timeout=30)
                                else:
                                    print(f"{Colors.RED}❌ Failed to install{Colors.END}")
                        except KeyboardInterrupt:
                            print(f"\n{Colors.RED}❌ Installation cancelled{Colors.END}")
                            return

            print(f"\n{Colors.CYAN}📤 Output:{Colors.END}")
            print("-" * 50)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{Colors.YELLOW}⚠️  Errors:{Colors.END}\n{result.stderr}")
            print("-" * 50)

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}⏰ Timeout (30s){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")

    def check_scan_tools(self):
        tools = {}
        tools['nmap'] = subprocess.run(['which', 'nmap'], capture_output=True).returncode == 0
        tools['rustcan'] = subprocess.run(['which', 'rustcan'], capture_output=True).returncode == 0
        tools['masscan'] = subprocess.run(['which', 'masscan'], capture_output=True).returncode == 0
        return tools

    def perform_security_scan(self, target):
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🔒 Security Scan: {target}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        stealth_mode = 'stealth' in ' '.join(sys.argv).lower()
        if stealth_mode:
            print(f"{Colors.MAGENTA}🕵️  STEALTH MODE ACTIVATED{Colors.END}")

        tools = self.check_scan_tools()
        print(f"\n{Colors.YELLOW}📡 Available Tools:{Colors.END}")
        print(f"  Nmap: {Colors.GREEN+'✅'+Colors.END if tools['nmap'] else Colors.RED+'❌'+Colors.END}")
        print(f"  Rustcan: {Colors.GREEN+'✅'+Colors.END if tools['rustcan'] else Colors.RED+'❌'+Colors.END}")
        print(f"  Masscan: {Colors.GREEN+'✅'+Colors.END if tools['masscan'] else Colors.RED+'❌'+Colors.END}")

        scans = {
            "1": ("Port Scan", self.port_scan_enhanced),
            "2": ("DNS Lookup", self.dns_lookup),
            "3": ("WHOIS Lookup", self.whois_lookup),
            "4": ("Full Scan", self.full_scan_enhanced)
        }

        print(f"\n{Colors.YELLOW}🎯 Scan Types:{Colors.END}")
        for num, (name, _) in scans.items():
            print(f"  {Colors.CYAN}{num}.{Colors.END} {name}")

        try:
            choice = input(f"\n{Colors.YELLOW}Select (1-4):{Colors.END} ").strip()
            if choice not in scans:
                print(f"{Colors.RED}❌ Invalid{Colors.END}")
                return

            scan_name, scan_func = scans[choice]

            print(f"\n{Colors.GREEN}🚀 Starting {scan_name}...{Colors.END}")
            print(f"{Colors.YELLOW}⏱️  This may take a while...{Colors.END}\n")

            scan_result = [None]

            def run_scan():
                scan_result[0] = scan_func(target, stealth=stealth_mode)

            scan_thread = threading.Thread(target=run_scan, daemon=True)
            scan_thread.start()

            self.start_animation(f"{Colors.BLUE}🔍 Scanning {target}{Colors.END}")
            scan_thread.join(timeout=180)
            self.stop_animation_thread()

            if scan_result[0] is None:
                print(f"{Colors.RED}⏰ Scan timeout{Colors.END}")
                return

            result = scan_result[0]

            self.display_scan_results(result, scan_name, target, stealth_mode)

            print(f"\n{Colors.MAGENTA}🤖 AI analyzing scan results...{Colors.END}")

            analysis_prompt = f"""Analyze this security scan for {target}:

Scan Type: {scan_name}
Stealth Mode: {'Yes' if stealth_mode else 'No'}
Results: {result}

Provide a professional security assessment with:
1. Executive Summary (2-3 sentences)
2. Key Findings (list important discoveries)
3. Risk Assessment (LOW/MEDIUM/HIGH/CRITICAL)
4. Detected Vulnerabilities
5. Recommendations

IMPORTANT: Use ONLY plain text. NO markdown (no ##, no **, no bullets with -).
Use descriptive headers like 'Executive Summary:' without special formatting.
Keep it professional and concise."""

            analysis = self.query_ai(analysis_prompt)

            if not analysis.startswith("Error:"):
                print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}🛡️  PROFESSIONAL SECURITY REPORT{Colors.END}")
                print(f"{Colors.CYAN}{'='*70}{Colors.END}")

                analysis = self.colorize_findings(analysis)
                print(analysis)
                print(f"{Colors.CYAN}{'='*70}{Colors.END}")
            else:
                print(f"\n{Colors.RED}{analysis}{Colors.END}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.RED}⏹️  Cancelled{Colors.END}")

    def port_scan_enhanced(self, target, stealth=False):
        tools = self.check_scan_tools()
        results = []

        if tools['rustcan']:
            try:
                cmd = f"rustcan -a {target} --ulimit 5000"
                if stealth:
                    cmd += " -b 500"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and result.stdout:
                    results.append(f"[Rustcan] {result.stdout}")
            except:
                pass

        if tools['nmap']:
            try:
                if stealth:
                    cmd = f"nmap -sS -sV -T2 -f --top-ports 100 {target}"
                else:
                    cmd = f"nmap -sV -T4 --top-ports 1000 {target}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    results.append(f"[Nmap] {result.stdout}")
            except:
                pass

        if not results:
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]
            open_ports = []

            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2 if stealth else 1)
                    if sock.connect_ex((target, port)) == 0:
                        protocol = PORT_PROTOCOLS.get(port, "UNKNOWN")
                        open_ports.append(f"{port}/{protocol}")
                    sock.close()
                    if stealth:
                        time.sleep(0.5)
                except:
                    pass

            results.append(f"Open ports: {', '.join(open_ports) if open_ports else 'None detected'}")
            results.append(f"Scanned ports: {common_ports}")

        return "\n".join(results)

    def dns_lookup(self, target, stealth=False):
        try:
            ip = socket.gethostbyname(target)
            try:
                hostname = socket.gethostbyaddr(ip)
                return f"Domain: {target}\nIP: {ip}\nHostname: {hostname[0]}\nAliases: {hostname[1]}"
            except:
                return f"Domain: {target}\nIP: {ip}\nReverse DNS: Not available"
        except Exception as e:
            return f"DNS lookup failed: {e}"

    def whois_lookup(self, target, stealth=False):
        try:
            result = subprocess.run(['whois', target], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout[:1500] + "\n... (truncated)"
            else:
                return "WHOIS lookup failed"
        except:
            return "WHOIS command not available"

    def full_scan_enhanced(self, target, stealth=False):
        results = []
        results.append("=== PORT SCAN ===")
        results.append(self.port_scan_enhanced(target, stealth))
        results.append("\n=== DNS LOOKUP ===")
        results.append(self.dns_lookup(target, stealth))
        results.append("\n=== WHOIS ===")
        results.append(self.whois_lookup(target, stealth))
        return "\n".join(results)

    def display_scan_results(self, result, scan_name, target, stealth):
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}📊 {scan_name} Results{Colors.END}")
        if stealth:
            print(f"{Colors.MAGENTA}🕵️  Stealth Mode: Active{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

        print(f"{Colors.YELLOW}Host:{Colors.END} {Colors.WHITE}{Colors.BOLD}{target}{Colors.END}")
        print(f"{Colors.YELLOW}Scan Type:{Colors.END} {Colors.CYAN}{scan_name}{Colors.END}")
        print(f"{Colors.YELLOW}Timestamp:{Colors.END} {Colors.WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

        lines = result.split('\n')
        for line in lines:
            if 'Open ports:' in line or '[Rustcan]' in line or '[Nmap]' in line:
                ports = re.findall(r'(\d+)/(\w+)', line)
                if ports:
                    print(f"{Colors.GREEN}{Colors.BOLD}🔓 Open Ports:{Colors.END}")
                    for port, protocol in ports:
                        print(f"  {Colors.RED}Port {port}{Colors.END} - {Colors.CYAN}{protocol}{Colors.END}")
                elif 'None detected' in line:
                    print(f"{Colors.GREEN}🔒 No open ports detected{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}{line}{Colors.END}")
            elif 'Domain:' in line:
                print(f"{Colors.BLUE}{line}{Colors.END}")
            elif 'IP' in line or 'Hostname' in line:
                print(f"{Colors.CYAN}{line}{Colors.END}")
            elif 'Scanned ports' in line:
                print(f"\n{Colors.YELLOW}{line}{Colors.END}")
            elif line.startswith('==='):
                print(f"\n{Colors.MAGENTA}{Colors.BOLD}{line}{Colors.END}")
            elif line.strip() and not line.startswith('['):
                print(f"{Colors.WHITE}{line}{Colors.END}")

        print(f"{Colors.CYAN}{'='*70}{Colors.END}")

    def colorize_findings(self, text):
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'^[\*\-]\s+', '  • ', text, flags=re.MULTILINE)

        text = re.sub(r'\b(CRITICAL|HIGH)\b', f'{Colors.BG_RED}{Colors.WHITE}\\1{Colors.END}', text, flags=re.I)
        text = re.sub(r'\b(MEDIUM)\b', f'{Colors.BG_YELLOW}{Colors.WHITE}\\1{Colors.END}', text, flags=re.I)
        text = re.sub(r'\b(LOW)\b', f'{Colors.BG_GREEN}{Colors.WHITE}\\1{Colors.END}', text, flags=re.I)

        vuln_keywords = ['vulnerable', 'vulnerability', 'exploit', 'weak', 'insecure', 'risk', 'attack', 'exposed']
        for keyword in vuln_keywords:
            text = re.sub(f'\\b({keyword})\\b', f'{Colors.RED}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)

        positive_keywords = ['secure', 'protected', 'safe', 'recommended', 'good', 'strong']
        for keyword in positive_keywords:
            text = re.sub(f'\\b({keyword})\\b', f'{Colors.GREEN}{Colors.BOLD}\\1{Colors.END}', text, flags=re.I)

        text = re.sub(r'^(Executive Summary:|Key Findings:|Risk Assessment:|Vulnerabilities:|Recommendations:)',
                     f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.END}', text, flags=re.MULTILINE)

        return text

    def display_models(self):
        print(f"\n{Colors.CYAN}🤖 Available Models:{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        for n,m in self.models.items():
            c = f" {Colors.GREEN}👈 CURRENT{Colors.END}" if n==self.current_model else ""
            print(f"  {Colors.YELLOW}{n}.{Colors.END} {Colors.WHITE}{m['name']:<20}{Colors.END}{c}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")

    def select_model(self):
        self.display_models()
        c = input(f"\n{Colors.YELLOW}Select (1-5):{Colors.END} ").strip()
        if c in self.models:
            self.current_model = c
            self.save_current_model()
            print(f"{Colors.GREEN}✅ Changed to: {self.models[c]['name']}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Invalid{Colors.END}")

    def whois_current_model(self):
        m = self.models[self.current_model]
        print(f"\n{Colors.CYAN}🤖 Current: {Colors.BOLD}{m['name']}{Colors.END}")

    def interactive_mode(self):
        print(f"{Colors.GREEN}🎯 Model: {Colors.BOLD}{self.models[self.current_model]['name']}{Colors.END}")
        print(f"{Colors.CYAN}💡 Type 'help' for commands, 'exit' to quit{Colors.END}\n")

        while True:
            try:
                cmd = input(f"{Colors.BOLD}{Colors.GREEN}🚀 TermiGPT> {Colors.END}").strip()
                if not cmd: continue
                if cmd in ['exit','quit','bye']: 
                    print(f"{Colors.CYAN}👋 Goodbye!{Colors.END}")
                    break
                elif cmd=='help': 
                    show_help_menu()
                elif cmd=='models': self.display_models()
                elif cmd=='select': self.select_model()
                elif cmd=='whois': self.whois_current_model()
                elif cmd.startswith(('create ','write ','code ','develop ','build ','make ')):
                    desc = ' '.join(cmd.split()[1:])
                    if desc: self.create_project(desc)
                    else: print(f"{Colors.RED}❌ Provide description{Colors.END}")
                elif cmd.startswith(('run ','execute ')):
                    file = ' '.join(cmd.split()[1:])
                    if file: self.execute_code(file)
                    else: print(f"{Colors.RED}❌ Provide file path{Colors.END}")
                elif cmd.startswith('scan '):
                    parts = cmd.split()
                    target = parts[1] if len(parts) > 1 else None
                    if target: self.perform_security_scan(target)
                    else: print(f"{Colors.RED}❌ Provide target{Colors.END}")
                elif cmd.startswith('ask '):
                    print(f"\n{Colors.BLUE}🤖{Colors.END} {self.query_ai(' '.join(cmd.split()[1:]))}")
                else:
                    print(f"\n{Colors.BLUE}🤖{Colors.END} {self.query_ai(cmd)}")
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
                break

def main():
    show_welcome_banner()
    show_help_menu()

    app = TermiGPT()

    if len(sys.argv) == 1:
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
                elif cmd in ['create', 'write', 'code', 'develop', 'build', 'make'] and len(cmd_parts) > 1:
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
        cmd = sys.argv[1].lower()
        if cmd in ['help', 'h']:
            show_help_menu()
        elif cmd == 'models':
            app.display_models()
        elif cmd == 'select':
            app.select_model()
        elif cmd == 'whois':
            app.whois_current_model()
        elif cmd in ['create', 'write', 'code', 'develop', 'build', 'make'] and len(sys.argv) > 2:
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
