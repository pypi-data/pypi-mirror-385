## 🔍 Reconnaissance

### Example 6: Full Reconnaissance Workflow

$ termi recon example.com

======================================================================
🔍 RECONNAISSANCE: example.com
======================================================================

🤖 AI analyzing ✅

COMPREHENSIVE RECONNAISSANCE PLAN

Phase 1: Information Gathering
━━━━━━━━━━━━━━━━━━━━━━━━━━━
1.1 WHOIS Lookup
    Command: whois example.com
    Look for: Registrar, creation date, admin contacts
    Expected: Organization details, nameservers

1.2 DNS Records Analysis
    Commands:
      - dig example.com ANY
      - nslookup -type=any example.com
    Records: A, AAAA, MX, TXT, NS, SOA
    Look for: Subdomains, mail servers, SPF records

Phase 2: Subdomain Enumeration
━━━━━━━━━━━━━━━━━━━━━━━━━━━
2.1 Passive Enumeration
    Tools: subfinder, amass
    Commands:
      - subfinder -d example.com -silent
      - amass enum -passive -d example.com
    Expected: 10-100 subdomains
    Look for: admin, api, dev, staging, test subdomains

2.2 Active Enumeration
    Tools: amass, httpx
    Commands:
      - amass enum -active -d example.com
      - httpx -l subdomains.txt -status-code
    Expected: Live web services
    Look for: HTTP response codes, technologies

Phase 3: Port Scanning
━━━━━━━━━━━━━━━━━━━━━━
3.1 Initial Scan (Top 1000)
    Tool: nmap, rustscan
    Command: nmap -Pn --top-ports 1000 example.com
    Expected: Common services
    Look for: HTTP, HTTPS, SSH, FTP, databases

3.2 Service Detection
    Command: nmap -sV -sC -p 80,443,22 example.com
    Look for:
      - Service versions
      - Server banners
      - Default credentials hints

Phase 4: Technology Detection
━━━━━━━━━━━━━━━━━━━━━━━━
4.1 Web Technologies
    Tools: WhatWeb, Wappalyzer
    Look for:
      - CMS (WordPress, Joomla, Drupal)
      - Web servers (Apache, Nginx)
      - Programming languages (PHP, Python, Node.js)
      - JavaScript frameworks (React, Vue, Angular)

4.2 SSL/TLS Analysis
    Tool: nmap, sslscan
    Command: nmap --script ssl-enum-ciphers example.com
    Look for:
      - Certificate details
      - Supported protocols (TLS 1.2, 1.3)
      - Weak ciphers
      - Certificate transparency logs

Phase 5: OSINT Gathering
━━━━━━━━━━━━━━━━━━━━━
5.1 Search Engine Reconnaissance
    Searches:
      - site:example.com
      - site:example.com filetype:pdf
      - site:example.com inurl:admin
    Look for: Exposed documents, admin panels

5.2 Social Media & Code Repositories
    Sources: LinkedIn, GitHub, GitLab
    Look for:
      - Employee information
      - Technology stack hints
      - Leaked credentials
      - Configuration files

5.3 Certificate Transparency
    Tools: crt.sh
    Look for: Additional subdomains

Phase 6: Vulnerability Identification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6.1 Automated Scanning
    Tool: nuclei
    Command: nuclei -u https://example.com -t cves/
    Look for:
      - Known CVEs
      - Common misconfigurations
      - Exposed sensitive files

6.2 Manual Testing
    Areas to check:
      - robots.txt, sitemap.xml
      - .git, .env exposure
      - Directory listing
      - Security headers

Estimated Time: 2-4 hours
Priority: High-value targets first (admin panels, APIs, databases)

Next Steps After Recon:
1. Organize findings in a spreadsheet
2. Prioritize by risk level
3. Begin vulnerability assessment
4. Document everything for reporting

⚠️  Remember: Only scan systems you have authorization to test!

======================================================================


### Example 7: Subdomain Enumeration

$ termi enum example.com

======================================================================
🌐 SUBDOMAIN ENUMERATION: example.com
======================================================================

Available tools: subfinder, amass

Run enumeration? (Y/n): y

Running subfinder...

www.example.com
api.example.com
dev.example.com
staging.example.com
admin.example.com
mail.example.com
ftp.example.com

Running amass...

www.example.com
api.example.com
dev.example.com
staging.example.com
admin.example.com
mail.example.com
ftp.example.com
test.example.com
beta.example.com
cdn.example.com

✅ Found 10 unique subdomains

Probing for live services...

  ✓ www.example.com - 200 OK
  ✓ api.example.com - 200 OK
  ✓ dev.example.com - 403 Forbidden
  ✓ staging.example.com - 401 Unauthorized
  ✓ admin.example.com - 200 OK
  ✗ mail.example.com - No HTTP
  ✗ ftp.example.com - No HTTP
  ✓ test.example.com - 200 OK
  ✓ beta.example.com - 200 OK
  ✓ cdn.example.com - 200 OK

Active Subdomains: 8/10

⚠️  Interesting Findings:
  • admin.example.com - Admin panel exposed
  • staging.example.com - Requires authentication
  • dev.example.com - Forbidden (may contain sensitive data)

Next Steps:
  1. Scan each subdomain for open ports
  2. Check for known vulnerabilities
  3. Test for subdomain takeover

======================================================================




## 🛠️ Tool Management

### Example 8: List Available Tools

$ termi list-tools

======================================================================
🛠️  AVAILABLE SECURITY TOOLS
======================================================================

RECON:
  • subfinder       - Fast subdomain discovery tool          ✅ Installed
  • amass           - In-depth DNS enumeration               ❌ Not installed
  • httpx           - Fast HTTP probe utility                ✅ Installed
  • nuclei          - Fast vulnerability scanner             ❌ Not installed

SCANNING:
  • nmap            - Network exploration and security       ✅ Installed
  • masscan         - Fast TCP port scanner                  ❌ Not installed
  • rustscan        - Modern fast port scanner               ❌ Not installed

EXPLOITATION:
  • metasploit      - Penetration testing framework          ❌ Not installed
  • sqlmap          - Automatic SQL injection tool           ❌ Not installed

WIRELESS:
  • aircrack-ng     - WiFi security auditing tools           ❌ Not installed

WEB:
  • gobuster        - Directory/file & DNS busting           ❌ Not installed
  • ffuf            - Fast web fuzzer                        ❌ Not installed
  • wpscan          - WordPress security scanner             ❌ Not installed

Use 'termi install-tool <category>' to install

======================================================================


### Example 9: Install Security Tools

$ termi install-tool recon

📦 Available Tool Categories:

Recon:
  ❌ subfinder: Fast subdomain discovery tool
  ❌ amass: In-depth DNS enumeration
  ✅ httpx: Fast HTTP probe utility
  ❌ nuclei: Fast vulnerability scanner

Select category (or 'cancel'): recon

Tools to install:
  1. subfinder: Fast subdomain discovery tool ❌ Not installed
  2. amass: In-depth DNS enumeration ❌ Not installed
  3. httpx: Fast HTTP probe utility ✅ Already installed
  4. nuclei: Fast vulnerability scanner ❌ Not installed

Select tool number (or 'all'): 1

Installing subfinder...
📥 Downloading from GitHub...
🔧 Installing Go binary...
✅ subfinder installed successfully

Verify installation:
$ subfinder -version




## 🤖 AI Assistance

### Example 10: Learn Security Concepts

$ termi ask "explain what is SQL injection"

🤖 AI analyzing ✅

SQL INJECTION - COMPREHENSIVE EXPLANATION

What is SQL Injection?
━━━━━━━━━━━━━━━━━━━━
SQL Injection (SQLi) is a web security vulnerability that allows attackers
to interfere with database queries. It's one of the most common and dangerous
web application vulnerabilities.

How It Works:
━━━━━━━━━━━━
Vulnerable code:
  query = "SELECT * FROM users WHERE username='" + user_input + "'"

Attack:
  user_input = "admin' OR '1'='1"
  
Resulting query:
  SELECT * FROM users WHERE username='admin' OR '1'='1'
  
This bypasses authentication because '1'='1' is always true.

Types of SQL Injection:
━━━━━━━━━━━━━━━━━━━━━
1. Classic SQLi - Direct injection in queries
2. Blind SQLi - No error messages, use true/false responses
3. Time-based Blind - Use database sleep functions
4. Union-based - Use UNION to extract data
5. Error-based - Use error messages for information

Example Attack Scenarios:
━━━━━━━━━━━━━━━━━━━━━━
1. Authentication Bypass:
   Input: admin' --
   Query: SELECT * FROM users WHERE username='admin' --'
   
2. Data Extraction:
   Input: ' UNION SELECT username, password FROM users--
   
3. Database Enumeration:
   Input: ' AND 1=2 UNION SELECT table_name FROM information_schema.tables--

Prevention:
━━━━━━━━━━
1. Use Parameterized Queries (Prepared Statements):
   ✅ Good: cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
   ❌ Bad: cursor.execute(f"SELECT * FROM users WHERE id={user_id}")

2. Input Validation:
   - Whitelist allowed characters
   - Validate data types
   - Sanitize special characters

3. Principle of Least Privilege:
   - Database user should have minimal permissions
   - Don't use admin accounts for web apps

4. Web Application Firewall (WAF):
   - Filter malicious inputs
   - Block known attack patterns

5. Error Handling:
   - Don't expose database errors to users
   - Use generic error messages

Testing for SQLi:
━━━━━━━━━━━━━━━
Manual:
  - Try single quote: '
  - Try comment: -- or #
  - Try boolean: ' OR 1=1--
  - Try time delay: ' AND SLEEP(5)--

Automated:
  - sqlmap: sqlmap -u "http://target.com?id=1" --dbs
  - Burp Suite Intruder
  - OWASP ZAP

Real-World Impact:
━━━━━━━━━━━━━━━━
- Yahoo (2012): 450,000 accounts compromised
- Sony (2011): 1 million accounts exposed
- TalkTalk (2015): 157,000 customer records stolen

OWASP Top 10: Ranked #3 (Injection)
CVSS Score: Usually 9.0-10.0 (Critical)

⚠️  Always test only on systems you own or have authorization to test!


### Example 11: Tool Usage Help

$ termi ask "explain nmap flags -sV -A -T4"

🤖 AI analyzing ✅

NMAP FLAGS EXPLAINED: -sV -A -T4

Command: nmap -sV -A -T4 target.com

Flag Breakdown:
━━━━━━━━━━━━━━

-sV (Service Version Detection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Detect service versions on open ports

What it does:
  • Probes open ports to determine service/version info
  • Identifies: Apache 2.4.41, OpenSSH 7.6p1, MySQL 5.7.30
  • Uses database of service signatures
  • More intrusive than basic scan

Example output:
  PORT    STATE SERVICE VERSION
  22/tcp  open  ssh     OpenSSH 7.6p1 Ubuntu
  80/tcp  open  http    Apache httpd 2.4.41
  3306/tcp open mysql   MySQL 5.7.30

Intensity: Can use --version-intensity 0-9 (default: 7)

-A (Aggressive Scan)
━━━━━━━━━━━━━━━━━━━━
Purpose: Enable multiple advanced scan options

Includes:
  • -O (OS detection)
  • -sV (version detection)
  • -sC (default script scan)
  • --traceroute

OS Detection example:
  Running: Linux 4.15 - 5.6
  OS CPE: cpe:/o:linux:linux_kernel:4.15
  
Script Scan example:
  | http-title: Welcome Page
  | http-server-header: Apache/2.4.41
  
Traceroute example:
  1   1.23 ms  router.local
  2   4.56 ms  isp-gateway
  3   12.34 ms target.com

⚠️  Warning: Very noisy, easily detected

-T4 (Timing Template)
━━━━━━━━━━━━━━━━━━━━
Purpose: Set scan speed/aggressiveness

Timing Templates (0-5):
  T0 (Paranoid)   - IDS evasion, extremely slow
  T1 (Sneaky)     - IDS evasion, very slow
  T2 (Polite)     - Slower, less bandwidth
  T3 (Normal)     - Default balance
  T4 (Aggressive) - Fast, assumes good network ← YOU ARE HERE
  T5 (Insane)     - Very fast, may miss ports

T4 Characteristics:
  • Max RTT timeout: 1250ms
  • Max retries: 6
  • Host timeout: 20 minutes
  • Scan delay: none
  • Parallelization: high
  
Use when:
  ✅ You own the network
  ✅ Fast scan needed
  ✅ Reliable network connection
  
Avoid when:
  ❌ IDS/IPS present
  ❌ Stealth required
  ❌ Unstable network

Complete Command Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━
nmap -sV -A -T4 target.com

Translation:
"Scan target.com aggressively and quickly, detect service versions,
identify OS, run default scripts, and show traceroute"

Expected Runtime: 2-5 minutes (depends on open ports)

Detection Risk: HIGH
  • Firewall logs will show multiple connections
  • IDS will likely trigger alerts
  • Not suitable for penetration tests requiring stealth

Alternative for Stealth:
nmap -sS -sV --version-intensity 0 -T2 target.com

Real-World Usage:
━━━━━━━━━━━━━━━━
✅ Good for:
  - Internal network scans
  - Your own servers
  - Authorized assessments with time constraints
  - Initial reconnaissance

❌ Bad for:
  - Covert operations
  - Slow/unreliable networks
  - IDS/IPS protected networks
  - Bypassing detection systems

Pro Tips:
━━━━━━━━
1. Combine with output: -oA scan_results
2. Exclude hosts: --exclude ip1,ip2
3. Specific ports: -p 80,443,8080
4. Skip ping: -Pn (if firewall blocks ping)

Example Full Command:
nmap -sV -A -T4 -p- -oA full_scan --exclude 192.168.1.1 target.com

⚠️  Always ensure you have authorization before scanning!




## 📊 Reporting

### Example 12: Generate VAPT Report

$ termi report

======================================================================
📊 GENERATING VAPT REPORT
======================================================================

Enter scan findings or path to scan file: 
> Found 3 open ports on target.com: 22(SSH), 80(HTTP), 3306(MySQL).
> MySQL is externally accessible.
> Apache version 2.4.41 detected with known CVE-2024-1234.

🤖 AI analyzing ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFESSIONAL PENETRATION TEST REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Client: [Company Name]
Target: target.com
Date: October 18, 2025
Tester: Security Researcher
Classification: CONFIDENTIAL

EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A penetration test was conducted on target.com revealing critical
security vulnerabilities requiring immediate remediation. The assessment
identified 3 findings across different severity levels, with 1 CRITICAL
issue that could lead to complete database compromise.

Overall Risk Rating: HIGH

Key Statistics:
  • Critical: 1 finding
  • High: 1 finding
  • Medium: 1 finding
  • Low: 0 findings
  
Primary Concerns:
  1. MySQL database exposed to internet (CRITICAL)
  2. Outdated web server with known vulnerabilities (HIGH)
  3. SSH service externally accessible (MEDIUM)

METHODOLOGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testing Approach:
  • Black box penetration testing
  • OWASP Testing Guide methodology
  • Automated and manual vulnerability assessment

Tools Used:
  • Nmap 7.94 - Port scanning and service detection
  • Custom scripts - Vulnerability verification
  • Manual analysis - Security configuration review

Scope:
  • Target: target.com
  • IP Range: Single host
  • Testing Window: October 18, 2025
  • Authorization: Written approval obtained

DETAILED FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINDING 1: MySQL Database Externally Accessible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Severity: CRITICAL
CVSS Score: 9.8 (Critical)
CVE: N/A (Configuration Issue)

Description:
The MySQL database server (Port 3306) is accessible from the internet,
allowing direct connection attempts from any external source. This
represents a critical security vulnerability as it provides attackers
with a direct attack vector to the database layer.

Technical Details:
  • Service: MySQL 5.7.x
  • Port: 3306/TCP
  • Protocol: MySQL native protocol
  • Access: No IP restrictions detected

Impact:
  • Complete database compromise possible
  • Data theft or manipulation
  • Potential for ransomware attacks
  • Regulatory compliance violations (GDPR, PCI-DSS)
  • Brute force attack opportunities

Proof of Concept:
  $ nmap -p 3306 target.com
  PORT     STATE SERVICE
  3306/tcp open  mysql
  
  $ mysql -h target.com -u root -p
  Enter password:
  [Connection successful - indicates reachability]

Affected Assets:
  • target.com:3306
  • All data stored in MySQL database
  • User credentials and sensitive information

Remediation:
  IMMEDIATE ACTIONS (Within 24 hours):
  1. Configure firewall to block external access to port 3306
  2. Modify MySQL bind-address to 127.0.0.1 or internal IP
  3. Review MySQL user accounts and remove unnecessary accounts
  4. Implement strong password policy for database users
  
  LONG-TERM ACTIONS:
  1. Implement VPN for remote database access
  2. Enable MySQL audit logging
  3. Regular security audits of database access
  4. Implement database activity monitoring (DAM)

References:
  • CIS MySQL Benchmark
  • OWASP Database Security Cheat Sheet
  • PCI-DSS Requirement 2.2.2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINDING 2: Outdated Apache Web Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Severity: HIGH
CVSS Score: 8.1 (High)
CVE: CVE-2024-1234

Description:
The web server is running Apache 2.4.41, which contains known security
vulnerabilities including potential for remote code execution.

Technical Details:
  • Service: Apache HTTPd 2.4.41
  • Port: 80/TCP
  • Vulnerability: Path traversal and RCE
  • Public Exploit: Available on Exploit-DB

Impact:
  • Remote code execution possible
  • Web server compromise
  • Potential pivot point to internal network
  • Website defacement
  • Malware distribution

Proof of Concept:
  $ curl -I http://target.com
  Server: Apache/2.4.41 (Ubuntu)
  
  Version 2.4.41 released: August 2019
  Current version: 2.4.58 (October 2024)
  Missing patches: 17 security updates

Remediation:
  1. Update Apache to version 2.4.58 or later
  2. Remove server version banner (ServerTokens Prod)
  3. Disable unnecessary modules
  4. Implement Web Application Firewall (WAF)
  5. Regular patch management process

References:
  • CVE-2024-1234 - Apache HTTP Server Advisory
  • https://httpd.apache.org/security/vulnerabilities_24.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINDING 3: SSH Service Externally Accessible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Severity: MEDIUM
CVSS Score: 5.3 (Medium)
CVE: N/A (Best Practice Violation)

Description:
SSH service is accessible from the internet, potentially exposing the
system to brute force attacks and unauthorized access attempts.

Technical Details:
  • Service: OpenSSH 7.6p1
  • Port: 22/TCP
  • Authentication: Password authentication enabled

Impact:
  • Brute force attack opportunities
  • Dictionary attacks possible
  • Account enumeration
  • Potential unauthorized access if weak credentials used

Proof of Concept:
  $ nmap -p 22 -sV target.com
  22/tcp open ssh OpenSSH 7.6p1 Ubuntu

Remediation:
  1. Implement SSH key authentication only
  2. Disable password authentication
  3. Change SSH port from default 22
  4. Implement fail2ban for brute force protection
  5. Use VPN for administrative access
  6. Implement 2FA for SSH access

References:
  • CIS SSH Configuration Benchmark
  • NIST SP 800-123 - SSH Security

RISK SUMMARY MATRIX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Severity    | Count | Findings
━━━━━━━━━━━━┼━━━━━━━┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL    |   1   | MySQL Database Exposure
HIGH        |   1   | Outdated Apache Server (CVE-2024-1234)
MEDIUM      |   1   | SSH External Access
LOW         |   0   | -
━━━━━━━━━━━━┴━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Immediate Actions (24-48 hours):
  ✓ Firewall MySQL port 3306 from external access
  ✓ Update Apache to latest version
  ✓ Implement fail2ban on SSH

Short-term (1-2 weeks):
  ✓ Deploy Web Application Firewall
  ✓ Implement SSH key authentication
  ✓ Conduct security configuration review
  ✓ Enable security logging and monitoring

Long-term (1-3 months):
  ✓ Implement comprehensive patch management
  ✓ Deploy Intrusion Detection System (IDS)
  ✓ Regular security assessments (quarterly)
  ✓ Security awareness training for staff
  ✓ Implement VPN for remote access
  ✓ Database activity monitoring

CONCLUSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The assessment revealed significant security vulnerabilities requiring
immediate attention. The CRITICAL finding regarding MySQL exposure poses
an immediate threat to data confidentiality and integrity. 

Recommended Priority Order:
  1. MySQL firewall configuration (CRITICAL - Immediate)
  2. Apache server update (HIGH - Within 48 hours)
  3. SSH hardening (MEDIUM - Within 1 week)

Regular security assessments and a proactive security posture are
recommended to maintain an adequate security level.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
END OF REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Report saved to: vapt_report_20251018_152900.txt

Export options:
  termi export pdf    - Generate PDF report
  termi export json   - Export as JSON
  termi export html   - Generate HTML report

======================================================================




## 🚀 Advanced Examples

### Example 13: Piped Input Analysis

$ cat nmap_scan.xml | termi -p "analyze for security issues"

🤖 AI analyzing

NMAP SCAN SECURITY ANALYSIS

Input: Nmap XML scan results

DETECTED SERVICES AND SECURITY ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Port 21 (FTP) - vsftpd 2.0.8
  Status: VULNERABLE
  Risk: HIGH
  Issues:
    • Outdated FTP server version
    • Anonymous FTP may be enabled
    • Clear-text password transmission
  CVE: CVE-2011-2523 (Backdoor in vsftpd 2.3.4)
  Recommendation: Disable FTP, use SFTP instead

Port 22 (SSH) - OpenSSH 7.4
  Status: MODERATE RISK
  Risk: MEDIUM
  Issues:
    • Outdated version (current: 9.5)
    • Known vulnerabilities in 7.4
  CVE: CVE-2018-15473 (User enumeration)
  Recommendation: Update to OpenSSH 9.5+

Port 80 (HTTP) - Apache 2.4.6
  Status: CRITICAL
  Risk: CRITICAL
  Issues:
    • Severely outdated (7+ years old)
    • Multiple known vulnerabilities
    • Missing security headers
  CVE: CVE-2017-15710, CVE-2019-0211 (Root RCE)
  Recommendation: URGENT - Update to 2.4.58+

Port 443 (HTTPS) - Apache 2.4.6
  Status: CRITICAL
  Risk: CRITICAL
  Issues:
    • Same as port 80
    • TLS 1.0/1.1 possibly enabled
    • Weak cipher suites detected
  Recommendation: Update server, configure modern TLS

Port 3306 (MySQL) - MySQL 5.5.62
  Status: CRITICAL
  Risk: CRITICAL
  Issues:
    • Externally accessible database
    • End-of-life MySQL version
    • Known security vulnerabilities
  CVE: Multiple CVEs for MySQL 5.5.x
  Recommendation: Firewall this port IMMEDIATELY

SEVERITY SUMMARY:
━━━━━━━━━━━━━━━━
  CRITICAL: 3 findings (Ports 80, 443, 3306)
  HIGH: 1 finding (Port 21)
  MEDIUM: 1 finding (Port 22)

IMMEDIATE ACTIONS REQUIRED:
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Block external access to MySQL (3306) - URGENT
2. Update Apache to latest version - URGENT
3. Update all services to current versions
4. Disable FTP, implement SFTP
5. Configure firewall rules
6. Enable HTTPS only with modern TLS

ATTACK VECTORS IDENTIFIED:
━━━━━━━━━━━━━━━━━━━━━━━━━
- Remote code execution via Apache vulnerabilities
- Database compromise via exposed MySQL
- Brute force attacks on SSH
- Data interception on FTP

Overall Risk Level: CRITICAL - Immediate action required




### Example 14: Session Management

$ termi

termi> history

📜 Command History:
  1. recon example.com
  2. scan target.com
  3. create a port scanner
  4. run port_scanner.py
  5. vuln-scan https://example.com
  6. report
  7. install-tool recon
  8. list-tools

termi> models

🤖 Available AI Models:
============================================================
  1. GPT-4o                       
  2. GPT-4o Mini                   👈 CURRENT
  3. GPT-4 Turbo                   
  4. Perplexity                    
  5. Mistral                       
============================================================

termi> select

Select (1-5): 4

✅ Switched to: Perplexity

termi> ask "what are the latest CVEs for Apache"

🤖 AI analyzing ✅

LATEST APACHE CVEs (October 2025)

Recent Critical Vulnerabilities:

1. CVE-2024-38476 (September 2024)
   Severity: HIGH (7.5)
   Affected: Apache HTTP Server 2.4.59 and earlier
   Issue: Server-side request forgery via mod_rewrite
   Fix: Update to 2.4.60+

2. CVE-2024-38477 (September 2024)
   Severity: CRITICAL (9.8)
   Affected: Apache HTTP Server 2.4.0 - 2.4.59
   Issue: NULL pointer dereference in mod_proxy
   Fix: Update to 2.4.60+

[Additional CVEs listed...]

Recommendation: Update to Apache 2.4.60 or later immediately.

termi> clear

[Screen cleared]

termi> exit

👋 Goodbye!




### Example 15: Custom Automation Script

$ termi create a bash script for automated security assessment

======================================================================
🔧 Generating Security Tool
======================================================================

⚠️  Reminder: For authorized security testing only

🤖 Generating production code ✅

📁 Project: automated-security-assessment

  ✅ security_scan.sh
  ✅ config.conf
  ✅ report_template.html
  ✅ README.md
  ✅ INSTALL.sh
  ✅ .gitignore

======================================================================
✅ SUCCESS! 6 files created
======================================================================

Generated security_scan.sh (excerpt):

#!/bin/bash
#
# Automated Security Assessment Script
# For authorized testing only
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
TARGET=""
OUTPUT_DIR="results_$(date +%Y%m%d_%H%M%S)"

# Check tools
check_tools() {
    local tools=("nmap" "subfinder" "httpx" "nuclei")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo -e "${RED}[!] $tool not found${NC}"
            exit 1
        fi
    done
}

# Phase 1: Subdomain Enumeration
enum_subdomains() {
    echo -e "${GREEN}[+] Phase 1: Subdomain Enumeration${NC}"
    subfinder -d "$TARGET" -silent -o "$OUTPUT_DIR/subdomains.txt"
    echo -e "${YELLOW}[*] Found $(wc -l < "$OUTPUT_DIR/subdomains.txt") subdomains${NC}"
}

# Phase 2: Live Host Detection
detect_live_hosts() {
    echo -e "${GREEN}[+] Phase 2: Live Host Detection${NC}"
    httpx -l "$OUTPUT_DIR/subdomains.txt" -silent -o "$OUTPUT_DIR/live_hosts.txt"
    echo -e "${YELLOW}[*] Found $(wc -l < "$OUTPUT_DIR/live_hosts.txt") live hosts${NC}"
}

# Phase 3: Port Scanning
port_scan() {
    echo -e "${GREEN}[+] Phase 3: Port Scanning${NC}"
    nmap -iL "$OUTPUT_DIR/live_hosts.txt" --top-ports 1000 -oX "$OUTPUT_DIR/nmap_scan.xml"
}

# Phase 4: Vulnerability Scanning
vuln_scan() {
    echo -e "${GREEN}[+] Phase 4: Vulnerability Scanning${NC}"
    nuclei -l "$OUTPUT_DIR/live_hosts.txt" -t cves/ -o "$OUTPUT_DIR/vulnerabilities.txt"
}

# Phase 5: Generate Report
generate_report() {
    echo -e "${GREEN}[+] Phase 5: Generating Report${NC}"
    # Report generation logic here
    echo -e "${GREEN}[✓] Report saved to $OUTPUT_DIR/report.html${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Automated Security Assessment          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <target-domain>"
        exit 1
    fi
    
    TARGET="$1"
    mkdir -p "$OUTPUT_DIR"
    
    check_tools
    enum_subdomains
    detect_live_hosts
    port_scan
    vuln_scan
    generate_report
    
    echo -e "${GREEN}[✓] Assessment complete!${NC}"
    echo -e "${YELLOW}Results: $OUTPUT_DIR${NC}"
}

main "$@"

📁 Location: ./automated-security-assessment
💡 Next: cd automated-security-assessment && ./INSTALL.sh




## 🎓 Identity Response Example

### Example 16: "Who are you?" Query

$ termi

termi> who are you

╔══════════════════════════════════════════════════════════════╗
║           TermiGPT - Security Research Assistant             ║
╚══════════════════════════════════════════════════════════════╝

What I Am:
I'm an AI-powered terminal assistant specifically designed for 
cybersecurity professionals, penetration testers, and security students.

My Capabilities:

🔍 Reconnaissance & OSINT:
  • Subdomain enumeration workflows
  • Port scanning and service detection
  • DNS analysis and WHOIS lookups
  • Network mapping and asset discovery

💻 Code & Payload Generation:
  • Security tool development (Python, Bash, PowerShell)
  • Exploit code generation and modification
  • Reverse shells and payload crafting
  • Automation scripts for pentesting workflows

🎯 Vulnerability Assessment:
  • Automated vulnerability scanning
  • CVE lookup and analysis
  • Risk assessment and severity rating
  • MITRE ATT&CK framework mapping

📊 Reporting & Documentation:
  • VAPT-style professional reports
  • Executive summaries with technical details
  • Finding documentation with remediation steps
  • Export in multiple formats (PDF, JSON, HTML)

🛠️  Tool Management:
  • Install and configure security tools
  • Tool-specific guidance (Nmap, Metasploit, Burp, etc.)
  • Command syntax help and flag explanations
  • Integration with popular pentesting frameworks

🧠 Learning & Training:
  • Explain security concepts and techniques
  • Command usage examples and best practices
  • CVE and vulnerability explanations
  • Adaptive guidance for all skill levels

Powered By: 5 AI Models (GPT-4o, Perplexity, Mistral, etc.)
Focus: Ethical hacking, authorized security testing, research

⚠️  All features are for authorized, ethical security testing only.

Type 'help' for commands or 'ask <question>' for anything else.
