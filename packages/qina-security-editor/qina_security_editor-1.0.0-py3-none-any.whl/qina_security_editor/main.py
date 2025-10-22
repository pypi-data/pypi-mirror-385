#!/usr/bin/env python3
"""
QINA Security Terminal Tool
A code monitoring and vulnerability scanning terminal application
"""

import os
import sys
import json
import time
import shutil
import requests
import threading
import subprocess
import zipfile
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, Back, Style, init
import tempfile
import itertools
from .scan_result_parser import ScanResultParser
from .js_scan_service import JSScanService
from .sarif_parser import SARIFParser
from .config_manager import ConfigManager
from .auth_service import AuthService
from .findings_manager import FindingsManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class Colors:
    """Color constants for terminal output"""
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL

class FileWatcher(FileSystemEventHandler):
    """Handles file system events for code monitoring"""
    
    def __init__(self, qina_app):
        self.qina_app = qina_app
        self.last_scan_time = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Filter for code files
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs'}
        file_path = Path(event.src_path)
        
        if file_path.suffix.lower() in code_extensions:
            self.qina_app.add_changed_file(file_path)
            
    def on_created(self, event):
        if not event.is_directory:
            self.on_modified(event)

class QinaApp:
    """Main QINA Security Terminal Application"""
    
    def __init__(self):
        self.tmp_dir = Path("/tmp/qina_security_scan")
        self.changed_files = set()
        self.last_scan_results = None
        self.observer = None
        self.monitoring_active = False
        self.monitor_path = None  # path provided via /start; used for scan scope
        self.api_endpoint = "http://localhost:8080/api/blahblah"  # Placeholder API
        # Legacy API fields retained for compatibility with config; not used for scan/upload/branch
        # Get URLs from config manager (environment-based)
        api_base = self.config_manager.get_api_base_url()
        self.branch_scan_api = f"{api_base}/api/ide/scan/branch"
        self.file_upload_api = f"{api_base}/api/ide/file/upload"
        self.config = ConfigManager()
        self.auth_service = AuthService(self.config)
        # Load from config if present; may be None
        self.api_key = self.config.get_api_key()
        self.team_id = self.config.get_team_id()
        # Disable legacy ~/.qina config flow; use ConfigManager/AuthService only
        self.git_repo_info = self.detect_git_repo()
        self.setup_tmp_directory()
        self.scan_parser = ScanResultParser()
        self.js_scan_service = JSScanService(self.api_key, self.team_id)
        self.findings_manager = FindingsManager(self.tmp_dir)

        # Run auth flow at startup if credentials are missing
        if not (self.api_key and self.team_id):
            try:
                creds = self.auth_service.ensure_credentials()
                self.api_key = creds.get('api_key')
                self.team_id = creds.get('team_id')
                # propagate to JS service
                self.js_scan_service.api_key = self.api_key
                self.js_scan_service.team_id = self.team_id
                print(f"{Colors.GREEN}✓ Credentials configured (team {self.team_id})")
            except Exception as e:
                print(f"{Colors.RED}✗ Authentication setup failed: {e}")
        
    def process_command(self, command: str):
        """Process a single command string (used by TUI and CLI)."""
        cmd = command.strip().lower()
        if cmd == 'scan':
            return self.run_try_py()
        if cmd == 'git diff':
            return self.send_git_diff_to_api()
        if cmd == 'scan branch':
            return self.run_f_py()
        if cmd.startswith('scan branch '):
            branch_name = cmd.replace('scan branch ', '', 1).strip()
            return self.run_f_py(branch_name)
        if cmd == 'git remote':
            self.show_git_remote_info()
            return None
        if cmd == 'upload':
            return self.run_try_py()
        if cmd == 'upload all':
            return self.run_try_py()
        if cmd.startswith('upload file '):
            return self.run_try_py()
        if cmd.startswith('add file '):
            file_path = cmd.replace('add file ', '', 1).strip()
            return self.add_file_to_monitoring(file_path)
        if cmd == 'list files':
            return self.list_monitored_files()
        if cmd == 'parse results':
            return self.parse_scan_results()
        if cmd.startswith('parse results '):
            file_path = cmd.replace('parse results ', '', 1).strip()
            return self.parse_scan_results(file_path)
        # show <filter>
        if cmd.startswith('show '):
            filt = cmd.replace('show ', '', 1)
            if filt in ['critical', 'high', 'medium', 'low', 'must fix', 'good to fix', 'false positive']:
                self.filter_vulnerabilities(filt)
                return None
        # passthrough old single word filters for compatibility
        if cmd in ['critical', 'high', 'medium', 'low', 'must fix', 'good to fix', 'false positive']:
            self.filter_vulnerabilities(cmd)
            return None
        if cmd == '/help':
            self.display_help()
            return None
        if cmd == '/status':
            self.display_status()
            return None
        if cmd.startswith('/start'):
            path = cmd.split(' ', 1)[1] if len(cmd.split()) > 1 else '.'
            self.start_monitoring(path)
            return None
        if cmd == '/stop':
            self.stop_monitoring()
            return None
        if cmd == '/clear':
            self.last_scan_results = None
            self.findings_manager.clear_findings()
            print(f"{Colors.GREEN}✓ Scan results cleared")
            return None
        if cmd == '/exit':
            # Signal exit by returning a sentinel
            return '__EXIT__'
        if cmd == '':
            return None
        print(f"{Colors.RED}Unknown command: {command}. Type '/help' for available commands.")
        return None

    def normalize_api_results(self, raw):
        """Normalize various API shapes into internal vulnerabilities format."""
        def map_classification(value):
            if not value:
                return None
            v = str(value).lower().replace('_', ' ')
            if 'false positive' in v:
                return 'false positive'
            if v in ['must fix', 'good to fix', 'critical', 'high', 'medium', 'low']:
                return v
            return v

        vulns = []
        if not raw:
            return { 'vulnerabilities': vulns }

        # If already in our expected format
        if isinstance(raw, dict) and 'vulnerabilities' in raw:
            # Ensure fields and normalize
            for v in raw.get('vulnerabilities', []):
                vulns.append({
                    'id': v.get('id') or v.get('finding_id') or v.get('rule_id') or 'UNKNOWN',
                    'title': v.get('title') or v.get('message') or v.get('rule_id') or 'Finding',
                    'severity': (v.get('severity') or 'low').lower(),
                    'classification': map_classification(v.get('classification')),
                    'file': v.get('file') or v.get('normalized_path') or v.get('path') or 'unknown',
                    'line': v.get('line') or v.get('start_line') or 0,
                    'description': v.get('description') or v.get('code_snippet_from_tool') or ''
                })
            return { 'vulnerabilities': vulns }

        # Semgrep-like: dict single finding
        if isinstance(raw, dict) and ('finding_id' in raw or 'normalized_path' in raw):
            raw = [raw]

        # List of findings
        if isinstance(raw, list):
            for item in raw:
                classification = (
                    item.get('classification') or
                    (item.get('llm_analysis') or {}).get('classification')
                )
                vulns.append({
                    'id': item.get('finding_id') or item.get('id') or item.get('rule_id') or 'UNKNOWN',
                    'title': item.get('message') or item.get('title') or item.get('rule_id') or 'Finding',
                    'severity': (item.get('severity') or 'low').lower(),
                    'classification': map_classification(classification),
                    'file': item.get('normalized_path') or item.get('file') or item.get('path') or 'unknown',
                    'line': item.get('start_line') or item.get('line') or 0,
                    'description': item.get('code_snippet_from_tool') or (item.get('tree_sitter_context') or {}).get('raw_snippet_for_line') or item.get('description') or ''
                })
            return { 'vulnerabilities': vulns }

        # Fallback: wrap as is
        return { 'vulnerabilities': vulns }

    def detect_git_repo(self):
        """Detect if current directory is a git repository and get branch info"""
        try:
            # Check if .git directory exists
            if not Path('.git').exists():
                return None
                
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            
            # Get remote origin URL
            try:
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      capture_output=True, text=True, check=True)
                remote_url = result.stdout.strip()
            except subprocess.CalledProcessError:
                remote_url = None
                
            return {
                'is_git_repo': True,
                'current_branch': current_branch,
                'remote_url': remote_url
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
            
    def get_git_diff(self):
        """Get git diff of changes since last push"""
        if not self.git_repo_info:
            return None
            
        try:
            # Get diff since last push (or last commit if no push)
            result = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            try:
                # Fallback to diff of working directory
                result = subprocess.run(['git', 'diff'], 
                                      capture_output=True, text=True, check=True)
                return result.stdout
            except subprocess.CalledProcessError:
                return None

    def run_try_py(self):
        """Run file upload scan using the new JavaScript service."""
        try:
            # Ensure credentials
            if not (self.api_key and self.team_id):
                creds = self.auth_service.ensure_credentials()
                self.api_key = creds.get('api_key')
                self.team_id = creds.get('team_id')
                # update service
                self.js_scan_service.api_key = self.api_key
                self.js_scan_service.team_id = self.team_id
            print(f"{Colors.CYAN}🔄 Running file upload scan using JavaScript service...")
            
            # Use the JavaScript service for file upload scan
            scan_path = Path(self.monitor_path) if self.monitor_path else None
            results = self._run_async_scan(self.js_scan_service.run_scan(scan_path))
            
            if 'error' in results:
                print(f"{Colors.RED}✗ Scan failed: {results['error']}")
                return False
            
            # Save results
            self.js_scan_service.save_results(results, 'upload-scan-response.txt')
            
            # Display complete raw results first
            if results.get('scan_results'):
                # Display detailed findings if available
                if results['scan_results'].get('detailed_findings'):
                    # Save detailed findings to temporary file
                    self.findings_manager.save_findings(results['scan_results']['detailed_findings'])
                    
                    print(f"\n{Colors.YELLOW}📋 DETAILED FINDINGS:")
                    print("=" * 80)
                    for i, finding in enumerate(results['scan_results']['detailed_findings'], 1):
                        sev = str(finding.get('severity', '')).lower()
                        if sev in ('critical', 'high'):
                            sev_color = Colors.RED
                        elif sev == 'medium':
                            sev_color = Colors.YELLOW
                        elif sev == 'low':
                            sev_color = Colors.CYAN
                        else:
                            sev_color = Colors.WHITE

                        title_line = f"{i}. {finding['title']}"
                        print(f"{sev_color}{title_line}{Colors.RESET}")
                        print(f"   File: {finding['file']}:{finding['line']}")
                        print(f"   Severity: {sev_color}{finding['severity']}{Colors.RESET}")
                        print(f"   Type: {finding['type']}")
                        if finding.get('language'):
                            print(f"   Language: {finding['language']}")
                        if finding.get('rule_id'):
                            print(f"   Rule: {finding['rule_id']}")
                        if finding.get('description'):
                            print(f"   Description: {finding['description']}")
                        if finding.get('code_snippet'):
                            print("   Code Snippet:")
                            for line in str(finding['code_snippet']).split('\n'):
                                print(f"     {line}")
                        if finding.get('cwe'):
                            try:
                                cwe_list = finding['cwe'] if isinstance(finding['cwe'], list) else [finding['cwe']]
                                if cwe_list:
                                    print(f"   CWE: {', '.join(map(str, cwe_list))}")
                            except Exception:
                                pass
                        if finding.get('references'):
                            try:
                                ref_list = finding['references'] if isinstance(finding['references'], list) else [finding['references']]
                                if ref_list:
                                    print("   References:")
                                    for ref in ref_list:
                                        print(f"     - {ref}")
                            except Exception:
                                pass
                        print("-" * 40)
                
                # Also display the summary for now
                self._display_scan_results(results['scan_results'])
            
            print(f"{Colors.GREEN}✅ File upload scan completed successfully!")
            return True

        except Exception as e:
            # Detect invalid API key message and clear config
            if 'invalid api key' in str(e).lower():
                print(f"{Colors.RED}✗ Invalid API key detected. Clearing saved config.")
                self.auth_service.handle_invalid_api_key()
            print(f"{Colors.RED}✗ Failed to run scan: {e}")
            return False

    def run_f_py(self, branch_name=None):
        """Run branch scan using the original f.py script."""
        try:
            # Ensure credentials
            if not (self.api_key and self.team_id):
                creds = self.auth_service.ensure_credentials()
                self.api_key = creds.get('api_key')
                self.team_id = creds.get('team_id')
            print(f"{Colors.CYAN}🔄 Running branch scan using f.py...")
            
            # Get repository information
            if not self.git_repo_info:
                print(f"{Colors.RED}✗ No git repository detected. Please run this command in a git repository.")
                return False
            
            repo_url = self.git_repo_info['remote_url']
            if not repo_url:
                print(f"{Colors.RED}✗ No remote URL configured. Please set up git remote origin.")
                return False
            
            # Convert SSH URL to HTTPS format if needed
            if repo_url.startswith('git@'):
                repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
                if not repo_url.endswith('.git'):
                    repo_url += '.git'
            elif not repo_url.startswith('http'):
                repo_url = repo_url.replace('git@', 'https://').replace(':', '/')
                if not repo_url.endswith('.git'):
                    repo_url += '.git'
            elif repo_url.startswith('https://') and not repo_url.endswith('.git'):
                repo_url += '.git'
            
            # Use current branch if no branch specified
            if not branch_name:
                branch_name = self.git_repo_info['current_branch']
            
            print(f"{Colors.WHITE}Repository: {repo_url}")
            print(f"{Colors.WHITE}Branch: {branch_name}")
            
            # Run the original f.py script for branch scan
            script_path = str(Path(__file__).with_name('f.py'))
            return_code = subprocess.call([sys.executable, script_path])
            
            if return_code == 0:
                print(f"{Colors.GREEN}✅ Branch scan completed successfully!")
                # Note: f.py now handles result parsing and display internally
                return True
            else:
                print(f"{Colors.RED}✗ Branch scan failed with return code: {return_code}")
                return False
            
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to run branch scan: {e}")
            return False
                
    def _run_async_scan(self, coro):
        """Helper method to run async functions from sync code"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                # No event loop running, we can use asyncio.run
                return asyncio.run(coro)
        except RuntimeError:
            # No event loop exists, create a new one
            return asyncio.run(coro)
        except Exception as e:
            print(f"{Colors.RED}Error running async scan: {e}")
            return {'error': str(e)}

    def _parse_and_display_branch_results(self):
        """Parse and display branch scan results from f.py output"""
        try:
            # Check for branch scan response file
            output_file = Path('branch-scan-response.txt')
            if not output_file.exists():
                print(f"{Colors.YELLOW}⚠️ No branch scan results file found")
                return
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Title
            print(f"\n{Colors.CYAN}🔍 BRANCH SCAN RESULTS:")
            print("=" * 80)
            
            # Try to parse JSON messages from the file
            json_messages = []
            for line in content.split('\n'):
                if line.strip().startswith('{'):
                    try:
                        message = json.loads(line)
                        json_messages.append(message)
                    except json.JSONDecodeError:
                        continue
            
            if json_messages:
                # Use the last (most complete) message
                latest_message = json_messages[-1]

                # Use SARIF parser if detailed_findings available, else try all_messages
                detailed_findings = []
                try:
                    parser = SARIFParser()
                    if 'detailed_findings' in latest_message:
                        detailed_findings = [parser._normalize_existing_finding(f) for f in latest_message['detailed_findings']]
                    else:
                        # Build a minimal scan_results-like dict for parser
                        scan_like = {
                            'all_messages': latest_message.get('all_messages', []),
                            'newVulnerability': latest_message.get('newVulnerability', [])
                        }
                        detailed_findings = parser.parse_scan_results(scan_like)
                except Exception:
                    detailed_findings = []

                # Show detailed findings (colored), no raw JSON
                if detailed_findings:
                    # Convert detailed findings to the format expected by FindingsManager
                    findings_data = []
                    for finding in detailed_findings:
                        findings_data.append({
                            'id': finding.get('id', 'UNKNOWN'),
                            'title': finding.get('title', 'Unknown Finding'),
                            'severity': finding.get('severity', 'unknown'),
                            'file': finding.get('file', 'unknown'),
                            'line': finding.get('line', 0),
                            'type': finding.get('type', 'unknown'),
                            'language': finding.get('language'),
                            'rule_id': finding.get('rule_id'),
                            'description': finding.get('description'),
                            'code_snippet': finding.get('code_snippet'),
                            'cwe': finding.get('cwe'),
                            'references': finding.get('references')
                        })
                    
                    # Save detailed findings to temporary file
                    self.findings_manager.save_findings(findings_data)
                    
                    print(f"\n{Colors.YELLOW}📋 DETAILED FINDINGS:")
                    print("=" * 80)
                    for i, finding in enumerate(detailed_findings, 1):
                        sev = str(finding.get('severity', '')).lower()
                        if sev in ('critical', 'high'):
                            sev_color = Colors.RED
                        elif sev == 'medium':
                            sev_color = Colors.YELLOW
                        elif sev == 'low':
                            sev_color = Colors.CYAN
                        else:
                            sev_color = Colors.WHITE

                        title_line = f"{i}. {finding.get('title', 'Finding')}"
                        print(f"{sev_color}{title_line}{Colors.RESET}")
                        print(f"   File: {finding.get('file','unknown')}:{finding.get('line',0)}")
                        print(f"   Severity: {sev_color}{finding.get('severity','unknown')}{Colors.RESET}")
                        print(f"   Type: {finding.get('type','unknown')}")
                        if finding.get('language'):
                            print(f"   Language: {finding['language']}")
                        if finding.get('rule_id'):
                            print(f"   Rule: {finding['rule_id']}")
                        if finding.get('description'):
                            print(f"   Description: {finding['description']}")
                        if finding.get('code_snippet'):
                            print("   Code Snippet:")
                            for line in str(finding['code_snippet']).split('\n'):
                                print(f"     {line}")
                        if finding.get('cwe'):
                            try:
                                cwe_list = finding['cwe'] if isinstance(finding['cwe'], list) else [finding['cwe']]
                                if cwe_list:
                                    print(f"   CWE: {', '.join(map(str, cwe_list))}")
                            except Exception:
                                pass
                        if finding.get('references'):
                            try:
                                ref_list = finding['references'] if isinstance(finding['references'], list) else [finding['references']]
                                if ref_list:
                                    print("   References:")
                                    for ref in ref_list:
                                        print(f"     - {ref}")
                            except Exception:
                                pass
                        print("-" * 40)

                # Display summary if available
                if 'counts' in latest_message:
                    print(f"\n{Colors.CYAN}📊 Branch Scan Summary:")
                    print("=" * 50)
                    
                    total_findings = 0
                    for count in latest_message['counts']:
                        file_name = count.get('fileName', 'Unknown')
                        total = count.get('totalCount', 0)
                        critical = count.get('criticalCount', 0)
                        high = count.get('highCount', 0)
                        medium = count.get('mediumCount', 0)
                        low = count.get('lowCount', 0)
                        
                        print(f"📁 {file_name}:")
                        print(f"   Total: {total} | Critical: {critical} | High: {high} | Medium: {medium} | Low: {low}")
                        total_findings += total
                    
                    print(f"\n🎯 Total findings: {total_findings}")
                    print("=" * 50)
                
                # Display status
                status = latest_message.get('status', 'Unknown')
                message = latest_message.get('message', '')
                
                if status in ['Ok', 'ok']:
                    print(f"{Colors.GREEN}✅ Branch Scan Status: {status}")
                elif status == 'Failed':
                    print(f"{Colors.YELLOW}⚠️ Branch Scan Status: {status}")
                else:
                    print(f"{Colors.WHITE}📊 Branch Scan Status: {status}")
                
                if message:
                    print(f"{Colors.WHITE}Message: {message}")
            else:
                # If no JSON found, display raw content
                print(content)
                print("=" * 80)
                
        except Exception as e:
            print(f"{Colors.RED}Error parsing branch scan results: {e}")

    def _display_scan_results(self, scan_results):
        """Display scan results in a formatted way"""
        try:
            if not scan_results:
                return
            
            # Extract counts if available
            counts = scan_results.get('counts', [])
            if counts:
                print(f"\n{Colors.CYAN}📊 Scan Results Summary:")
                print("=" * 50)
                
                total_findings = 0
                for count in counts:
                    file_name = count.get('fileName', 'Unknown')
                    total = count.get('totalCount', 0)
                    critical = count.get('criticalCount', 0)
                    high = count.get('highCount', 0)
                    medium = count.get('mediumCount', 0)
                    low = count.get('lowCount', 0)
                    
                    print(f"📁 {file_name}:")
                    print(f"   Total: {total} | Critical: {critical} | High: {high} | Medium: {medium} | Low: {low}")
                    total_findings += total
                
                print(f"\n🎯 Total findings: {total_findings}")
                print("=" * 50)
            
            # Display status
            status = scan_results.get('status', 'Unknown')
            message = scan_results.get('message', '')
            
            if status in ['Ok', 'ok', 'Completed']:
                print(f"{Colors.GREEN}✅ Scan Status: {status}")
            elif status == 'Failed':
                print(f"{Colors.YELLOW}⚠️ Scan Status: {status}")
            else:
                print(f"{Colors.WHITE}📊 Scan Status: {status}")
            
            if message:
                print(f"{Colors.WHITE}Message: {message}")
            
            # Display infrastructure note if present
            infrastructure_note = scan_results.get('infrastructure_note', '')
            if infrastructure_note:
                print(f"{Colors.YELLOW}ℹ️  {infrastructure_note}")
                
        except Exception as e:
            print(f"{Colors.RED}Error displaying scan results: {e}")
                
    # Removed internal scan_branch; delegated to f.py

    # Removed internal _run_ws_branch_scan; delegated to f.py

    def _parse_sarif_to_findings(self, sarif_obj):
        """Parse SARIF JSON object into a list of normalized-like findings dicts."""
        findings = []
        try:
            runs = sarif_obj.get('runs', []) if isinstance(sarif_obj, dict) else []
            for run in runs:
                tool = (run.get('tool') or {}).get('driver') or {}
                rules = { (r.get('id') or ''): r for r in (tool.get('rules') or []) }
                for res in run.get('results', []) or []:
                    rule_id = res.get('ruleId') or res.get('rule', {}).get('id') or 'UNKNOWN'
                    message = (res.get('message') or {}).get('text') or 'Finding'
                    level = (res.get('level') or '').lower()
                    severity = {
                        'error': 'high',
                        'warning': 'medium',
                        'note': 'low'
                    }.get(level, 'low')
                    locations = res.get('locations') or []
                    file_path = 'unknown'
                    line_no = 0
                    if locations:
                        loc0 = locations[0] or {}
                        phys = (loc0.get('physicalLocation') or {})
                        art = (phys.get('artifactLocation') or {})
                        file_path = art.get('uri') or file_path
                        region = phys.get('region') or {}
                        line_no = region.get('startLine') or line_no
                    # Prefer rule shortDescription/name if present
                    rule = rules.get(rule_id) or {}
                    title = (rule.get('shortDescription') or {}).get('text') or rule.get('name') or message
                    findings.append({
                        'id': rule_id,
                        'title': title,
                        'severity': severity,
                        'classification': None,
                        'file': file_path,
                        'line': line_no,
                        'description': message
                    })
        except Exception:
            pass
        return findings
            
    def send_git_diff_to_api(self):
        """Send git diff to API for analysis"""
        if not self.git_repo_info:
            print(f"{Colors.RED}✗ No git repository detected. Please run this command in a git repository.")
            return None
            
        git_diff = self.get_git_diff()
        if not git_diff:
            print(f"{Colors.YELLOW}⚠ No changes detected in git repository.")
            return None
            
        try:
            print(f"{Colors.CYAN}🔄 Analyzing git diff changes...")
            
            # Prepare files data from git diff
            files_data = []
            current_file = None
            current_content = []
            
            for line in git_diff.split('\n'):
                if line.startswith('diff --git'):
                    # Save previous file if exists
                    if current_file and current_content:
                        files_data.append({
                            'name': current_file,
                            'content': '\n'.join(current_content),
                            'path': current_file,
                            'type': 'git_diff'
                        })
                    
                    # Extract filename from diff header
                    parts = line.split()
                    if len(parts) >= 4:
                        current_file = parts[3].replace('b/', '')
                        current_content = []
                elif line.startswith('+') and not line.startswith('+++'):
                    current_content.append(line[1:])  # Remove the + prefix
                elif line.startswith(' ') and current_file:
                    current_content.append(line[1:])  # Remove the space prefix
            
            # Add the last file
            if current_file and current_content:
                files_data.append({
                    'name': current_file,
                    'content': '\n'.join(current_content),
                    'path': current_file,
                    'type': 'git_diff'
                })
            
            if not files_data:
                print(f"{Colors.YELLOW}⚠ No file changes found in git diff.")
                return None
            
            payload = {
                'files': files_data,
                'timestamp': datetime.now().isoformat(),
                'scan_type': 'git_diff',
                'git_info': self.git_repo_info
            }
            
            # Mock response for demonstration (replace with actual API call)
            mock_response = self.generate_mock_response()
            self.last_scan_results = mock_response
            
            print(f"{Colors.GREEN}✅ Git diff analysis completed!")
            self.display_scan_summary()
            
            return mock_response
            
        except Exception as e:
            print(f"{Colors.RED}✗ Git diff analysis error: {e}")
            return None
            
    def show_git_remote_info(self):
        """Show git remote information and help fix URL format"""
        if not self.git_repo_info:
            print(f"{Colors.RED}✗ No git repository detected.")
            return
            
        print(f"{Colors.CYAN}📁 Git Repository Information:")
        print(f"{Colors.WHITE}  Current Branch: {self.git_repo_info['current_branch']}")
        print(f"{Colors.WHITE}  Remote URL: {self.git_repo_info['remote_url']}")
        
        if self.git_repo_info['remote_url']:
            if self.git_repo_info['remote_url'].startswith('git@'):
                print(f"{Colors.YELLOW}⚠ SSH URL detected. Converting to HTTPS format...")
                # Convert SSH to HTTPS
                https_url = self.git_repo_info['remote_url']
                if https_url.startswith('git@github.com:'):
                    https_url = https_url.replace('git@github.com:', 'https://github.com/')
                else:
                    https_url = https_url.replace('git@', 'https://').replace(':', '/')
                
                # Ensure .git extension is present
                if not https_url.endswith('.git'):
                    https_url += '.git'
                
                print(f"{Colors.GREEN}✅ HTTPS URL: {https_url}")
                print(f"{Colors.YELLOW}💡 To fix permanently, run: git remote set-url origin {https_url}")
            elif self.git_repo_info['remote_url'].startswith('https://'):
                print(f"{Colors.GREEN}✅ HTTPS URL format is correct.")
            else:
                print(f"{Colors.RED}✗ Unknown URL format. Please configure HTTPS remote URL.")
        else:
            print(f"{Colors.RED}✗ No remote URL configured.")
            print(f"{Colors.YELLOW}💡 To add remote: git remote add origin <repository-url>")
        
    def create_zip_from_tmp(self):
        """Create a zip file from the tmp directory (silent)"""
        try:
            zip_path = Path("/tmp/qina_security_scan.zip")
            
            # Remove existing zip file if it exists
            if zip_path.exists():
                zip_path.unlink()
            
            # Create zip file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.tmp_dir.rglob('*'):
                    if file_path.is_file():
                        # Add file to zip with relative path
                        arcname = file_path.relative_to(self.tmp_dir)
                        zipf.write(file_path, arcname)
            return zip_path
            
        except Exception as e:
            print(f"{Colors.RED}✗ Error creating zip file: {e}")
            return None

    # Removed internal upload_entire_repository; delegated to try.py
            
    # Removed internal upload_specific_file; delegated to try.py
            
    # Removed internal upload_zip_to_api; delegated to try.py

    # Removed internal _ws_first_upload_flow; delegated to try.py
            
    # Removed internal manual_upload; delegated to try.py
        
    def setup_tmp_directory(self):
        """Create temporary directory for changed files"""
        try:
            if self.tmp_dir.exists():
                shutil.rmtree(self.tmp_dir)
            self.tmp_dir.mkdir(parents=True, exist_ok=True)
            print(f"{Colors.GREEN}✓ Temporary directory created: {self.tmp_dir}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error creating tmp directory: {e}")
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded from scans"""
        # Exclude the findings file and other temporary files
        exclude_patterns = [
            'detailed_findings.json',
            '*.log',
            '*.tmp',
            '__pycache__',
            '.git'
        ]
        
        file_name = file_path.name
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern == file_name:
                return True
        
        return False
            
    def add_changed_file(self, file_path):
        """Add a changed file to the monitoring list"""
        if file_path.exists() and file_path.is_file():
            # Check if file should be excluded
            if self.should_exclude_file(file_path):
                return
            
            self.changed_files.add(file_path)
            # Copy file to tmp directory
            try:
                dest_path = self.tmp_dir / file_path.name
                shutil.copy2(file_path, dest_path)
                print(f"{Colors.CYAN}📁 File monitored: {file_path.name}")
            except Exception as e:
                print(f"{Colors.RED}✗ Error copying file {file_path}: {e}")
                
    def add_file_to_monitoring(self, file_path):
        """Manually add a file to monitoring (useful when inotify is not available)"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"{Colors.RED}✗ File not found: {file_path}")
                return None
                
            if not file_path.is_file():
                print(f"{Colors.RED}✗ Path is not a file: {file_path}")
                return None
                
            # Add to changed files and copy to tmp directory
            self.add_changed_file(file_path)
            print(f"{Colors.GREEN}✅ Added {file_path.name} to monitoring")
            print(f"{Colors.CYAN}💡 Use 'scan' to scan monitored files")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}✗ Error adding file to monitoring: {e}")
            return None
            
    def list_monitored_files(self):
        """List all currently monitored files"""
        if not self.changed_files:
            print(f"{Colors.YELLOW}⚠️  No files currently monitored")
            print(f"{Colors.CYAN}💡 Use 'add file <path>' to add files manually")
            return None
            
        print(f"{Colors.CYAN}📁 Currently monitored files ({len(self.changed_files)}):")
        for file_path in self.changed_files:
            print(f"   {Colors.WHITE}• {file_path.name}")
        print(f"{Colors.CYAN}💡 Use 'scan' to scan these files")
        return True
                
    def start_monitoring(self, path="."):
        """Start monitoring the specified path for file changes"""
        try:
            if self.observer:
                self.stop_monitoring()
                
            # Persist monitor path for scan scoping
            self.monitor_path = os.path.abspath(path)

            self.observer = Observer()
            event_handler = FileWatcher(self)
            self.observer.schedule(event_handler, path, recursive=True)
            self.observer.start()
            self.monitoring_active = True
            print(f"{Colors.GREEN}🔍 Code monitoring started for: {os.path.abspath(path)}")
        except OSError as e:
            if e.errno == 24:  # inotify instance limit reached
                print(f"{Colors.RED}✗ Error starting file monitoring: {e}")
                print(f"{Colors.YELLOW}💡 Solution: Increase inotify limits with:")
                print(f"{Colors.CYAN}   echo fs.inotify.max_user_instances=1024 | sudo tee -a /etc/sysctl.conf")
                print(f"{Colors.CYAN}   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf")
                print(f"{Colors.CYAN}   sudo sysctl -p")
                print(f"{Colors.YELLOW}💡 Or restart your system to reset inotify instances")
                print(f"{Colors.YELLOW}⚠️  Monitoring disabled - you can still use 'scan' command manually")
            else:
                print(f"{Colors.RED}✗ Error starting file monitoring: {e}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error starting file monitoring: {e}")
            
    def stop_monitoring(self):
        """Stop file monitoring"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            self.monitoring_active = False
            print(f"{Colors.YELLOW}⏹ Code monitoring stopped")
        # Do not clear monitor_path on stop; keep it for subsequent scans unless /start is called again
            
    # Removed internal send_to_api; 'scan' delegated to try.py

    def _spinner(self, message: str, stop_event: threading.Event):
        """Simple CLI spinner until stop_event is set."""
        spinner_cycle = itertools.cycle(['⠋','⠙','⠸','⠴','⠦','⠇'])
        while not stop_event.is_set():
            frame = next(spinner_cycle)
            print(f"\r{Colors.CYAN}{message} {frame}{Colors.RESET}", end='', flush=True)
            time.sleep(0.1)
        print("\r" + " " * (len(message) + 4) + "\r", end='', flush=True)

    # === Auth and config management ===
    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self.api_key = data.get('apiKey', self.api_key)
                self.team_id = data.get('teamId', self.team_id)
        except Exception:
            pass

    def save_config(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            data = {
                'apiKey': self.api_key,
                'teamId': self.team_id,
                'updatedAt': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def verify_and_check_api_key(self):
        """Verify and check the API key at startup. Uses provided QA endpoints."""
        if not self.api_key:
            return
        payload = { 'apiKey': self.api_key }
        try:
            # Verify
            requests.post('http://qa.clouddefense.ai/api/ide/auth/verify', json=payload, timeout=10)
            # Check
            requests.post('http://qa.clouddefense.ai/api/ide/auth/check', json=payload, timeout=10)
            # Persist key locally after successful contact
            self.save_config()
        except Exception:
            # Stay silent on failures; tool remains usable for local mock flows
            pass
            
    def generate_mock_response(self):
        """Generate mock vulnerability response for demonstration"""
        return {
            'scan_id': 'scan_' + str(int(time.time())),
            'timestamp': datetime.now().isoformat(),
            'total_vulnerabilities': 24,
            'vulnerabilities': [
                {
                    'id': 'VULN_001',
                    'title': 'SQL Injection vulnerability',
                    'severity': 'critical',
                    'classification': 'critical',
                    'file': 'database.py',
                    'line': 45,
                    'description': 'Unsanitized user input in SQL query'
                },
                {
                    'id': 'VULN_002',
                    'title': 'Cross-Site Scripting (XSS)',
                    'severity': 'high',
                    'classification': 'high',
                    'file': 'templates.js',
                    'line': 123,
                    'description': 'Unescaped user data in HTML output'
                },
                {
                    'id': 'VULN_003',
                    'title': 'Hardcoded credentials',
                    'severity': 'critical',
                    'classification': 'must fix',
                    'file': 'config.py',
                    'line': 12,
                    'description': 'Hardcoded API key found in source code'
                },
                {
                    'id': 'VULN_004',
                    'title': 'Weak password policy',
                    'severity': 'medium',
                    'classification': 'good to fix',
                    'file': 'auth.py',
                    'line': 78,
                    'description': 'Password complexity requirements too weak'
                },
                {
                    'id': 'VULN_005',
                    'title': 'Unused import statement',
                    'severity': 'low',
                    'classification': 'false positive',
                    'file': 'utils.py',
                    'line': 5,
                    'description': 'Import statement not used in code'
                }
            ]
        }
        
    def display_scan_summary(self):
        """Display scan results summary"""
        if not self.last_scan_results:
            return
            
        vulns = self.last_scan_results['vulnerabilities']
        
        # Count vulnerabilities by severity
        counts = {
            'critical': len([v for v in vulns if v['severity'] == 'critical']),
            'high': len([v for v in vulns if v['severity'] == 'high']),
            'medium': len([v for v in vulns if v['severity'] == 'medium']),
            'low': len([v for v in vulns if v['severity'] == 'low'])
        }
        
        total = sum(counts.values())
        print(f"{Colors.GREEN}Found {total} vulnerabilities • {Colors.RED}{counts['critical']} critical {Colors.YELLOW}• {counts['high']} high {Colors.BLUE}• {counts['medium']} medium {Colors.WHITE}• {counts['low']} low")
        
    def filter_vulnerabilities(self, filter_type):
        """Filter vulnerabilities based on type"""
        if not self.findings_manager.has_findings():
            print(f"{Colors.RED}✗ No scan results available. Run 'scan' first to perform a scan.")
            return
        
        if filter_type in ['critical', 'high', 'medium', 'low']:
            filtered_findings = self.findings_manager.get_findings_by_severity(filter_type)
        elif filter_type in ['must fix', 'good to fix', 'false positive']:
            # Note: classification filtering not yet implemented in FindingsManager
            print(f"{Colors.YELLOW}⚠️ Classification filtering not yet implemented. Showing all findings.")
            filtered_findings = self.findings_manager.findings
        else:
            filtered_findings = self.findings_manager.findings
        
        self.display_detailed_findings(filtered_findings, filter_type.upper())
    
    def display_detailed_findings(self, findings, filter_name):
        """Display detailed findings with full information"""
        if not findings:
            print(f"{Colors.YELLOW}No {filter_name.lower()} vulnerabilities found.")
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== {filter_name} VULNERABILITIES ({len(findings)}) ==={Colors.RESET}")
        print("=" * 80)
        
        for i, finding in enumerate(findings, 1):
            severity_color = {
                'critical': Colors.RED,
                'high': Colors.YELLOW,
                'medium': Colors.BLUE,
                'low': Colors.WHITE
            }.get(finding.severity.lower(), Colors.WHITE)
            
            print(f"\n{severity_color}🔍 {i}. {finding.title}{Colors.RESET}")
            print(f"   📁 File: {finding.file}:{finding.line}")
            print(f"   🏷️  Severity: {severity_color}{finding.severity.upper()}{Colors.RESET}")
            print(f"   🆔 Type: {finding.type}")
            
            if finding.language:
                print(f"   🌐 Language: {finding.language}")
            if finding.rule_id:
                print(f"   📋 Rule: {finding.rule_id}")
            if finding.description:
                print(f"   📝 Description: {finding.description}")
            if finding.code_snippet:
                print("   💻 Code Snippet:")
                print(f"   {Colors.CYAN}   ─────────────────────────────────────────────────────{Colors.RESET}")
                for line in str(finding.code_snippet).split('\n'):
                    if line.strip():
                        print(f"     {line}")
                print(f"   {Colors.CYAN}   ─────────────────────────────────────────────────────{Colors.RESET}")
            if finding.cwe:
                print(f"   🔗 CWE: {finding.cwe}")
            if finding.references:
                print("   📚 References:")
                for ref in finding.references:
                    print(f"     - {ref}")
            print("-" * 80)
        
    def display_vulnerabilities(self, vulnerabilities, filter_name):
        """Display filtered vulnerabilities"""
        if not vulnerabilities:
            print(f"{Colors.YELLOW}No {filter_name.lower()} vulnerabilities found.")
            return
            
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== {filter_name} VULNERABILITIES ({len(vulnerabilities)}) ==={Colors.RESET}")
        
        for vuln in vulnerabilities:
            severity_color = {
                'critical': Colors.RED,
                'high': Colors.YELLOW,
                'medium': Colors.BLUE,
                'low': Colors.WHITE
            }.get(vuln['severity'], Colors.WHITE)
            
            print(f"\n{severity_color}🔍 {vuln['id']}: {vuln['title']}")
            print(f"   📁 File: {vuln['file']}:{vuln['line']}")
            if vuln.get('description'):
                snippet = str(vuln['description']).strip()
                if len(snippet) > 300:
                    snippet = snippet[:300] + '…'
                print(f"   🧩 Snippet:\n{Colors.WHITE}   ─────────────────────────────────────────────────────")
                for line in snippet.splitlines():
                    print(f"   {line}")
                print(f"{Colors.WHITE}   ─────────────────────────────────────────────────────")
            print(f"   🏷️  Classification: {vuln.get('classification') or 'N/A'}")
    
    def parse_scan_results(self, file_path: str = None):
        """Parse and display detailed scan results using the advanced parser"""
        try:
            if not file_path:
                # Try to find the most recent scan result file
                possible_files = [
                    'upload-scan-response.txt',
                    'branch-scan-response.txt',
                    'b.txt'
                ]
                
                for file_name in possible_files:
                    if Path(file_name).exists():
                        file_path = file_name
                        break
                
                if not file_path:
                    print(f"{Colors.RED}✗ No scan result files found. Run a scan first.")
                    return None
            
            if not Path(file_path).exists():
                print(f"{Colors.RED}✗ File not found: {file_path}")
                return None
            
            print(f"{Colors.CYAN}🔄 Parsing scan results from: {file_path}")
            
            # Parse the file using the advanced parser
            summary, vulnerabilities = self.scan_parser.parse_file(file_path)
            
            # Display results using the parser's display methods
            self.scan_parser.display_summary(summary)
            self.scan_parser.display_vulnerabilities(vulnerabilities, "ALL")
            
            # Store the parsed results for filtering
            self.last_scan_results = {
                'vulnerabilities': [
                    {
                        'id': v.id,
                        'title': v.title,
                        'severity': v.severity,
                        'file': v.file_path,
                        'line': v.line_number,
                        'description': v.description,
                        'classification': v.classification
                    } for v in vulnerabilities
                ]
            }
            
            print(f"\n{Colors.GREEN}✅ Scan results parsed successfully!")
            print(f"{Colors.CYAN}💡 Use 'show <severity>' to filter by severity (critical, high, medium, low)")
            
            return {
                'summary': summary,
                'vulnerabilities': vulnerabilities
            }
            
        except Exception as e:
            print(f"{Colors.RED}✗ Error parsing scan results: {e}")
            return None
            
    def display_header(self):
        """Display the application header"""
        # Clear screen for better presentation
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Get terminal width for dynamic box sizing
        try:
            terminal_width = os.get_terminal_size().columns
        except:
            terminal_width = 120
            
        # Create box borders
        top_border = "┌" + "─" * (terminal_width - 2) + "┐"
        bottom_border = "└" + "─" * (terminal_width - 2) + "┘"
        side_border = "│"
        
        def create_boxed_line(content, color=""):
            # Calculate padding to center content or align left
            content_length = len(content.encode('unicode_escape').decode('unicode_escape'))
            # Remove ANSI color codes for length calculation
            import re
            clean_content = re.sub(r'\x1b\[[0-9;]*m', '', content)
            clean_length = len(clean_content)
            
            padding_total = terminal_width - 4 - clean_length  # -4 for borders and spaces
            padding_left = 1
            padding_right = max(1, padding_total - padding_left)
            
            return f"{side_border} {content}{' ' * padding_right} {side_border}"
        
        # Top header with tabs in a box
        header = f"""
{Colors.WHITE}{top_border}
{create_boxed_line(f"{Colors.GREEN}🛡️  QINA Security Editor    {Colors.CYAN}📊 Security Analysis ✕")}
{create_boxed_line("")}
{create_boxed_line(f"{Colors.GREEN}📟 QINA Security Terminal")}
{Colors.WHITE}{bottom_border}

{Colors.GREEN}✓ Temporary directory created: {self.tmp_dir}

{Colors.GREEN}★ Welcome to QINA Security Editor!

{Colors.WHITE}/help for help, /status for your current security scan setup

{Colors.WHITE}cwd: {os.getcwd()}
        """
        
        # Add git repository information
        if self.git_repo_info:
            git_info = f"""
{Colors.CYAN}📁 Git Repository: {self.git_repo_info['current_branch']}
{Colors.WHITE}   Remote: {self.git_repo_info['remote_url'] or 'No remote configured'}
            """
            print(git_info)
        else:
            print(f"{Colors.YELLOW}⚠ No git repository detected")
            
        print(header)
        
    def display_help(self):
        """Display help information"""
        help_text = f"""
{Colors.CYAN}QINA Security Terminal Commands:
{Colors.WHITE}
  scan                  - Run file upload scan using JavaScript service
  git diff              - Analyze git diff changes since last push
  scan branch           - Run branch scan using f.py script
  scan branch <name>    - Run branch scan for specific branch using f.py
  git remote            - Show git remote information and fix URL format
  upload                - Run file upload scan (same as 'scan')
  upload file <path>    - Run file upload scan (same as 'scan')
  add file <path>       - Manually add file to monitoring (when inotify unavailable)
  list files            - List currently monitored files
  parse results         - Parse and display detailed scan results
  parse results <file>  - Parse specific scan result file
  show critical         - Show critical vulnerabilities
  show high             - Show high priority vulnerabilities  
  show medium           - Show medium priority vulnerabilities
  show low              - Show low priority vulnerabilities
  show must fix         - Show must fix vulnerabilities
  show good to fix      - Show good to fix vulnerabilities
  show false positive   - Show false positive vulnerabilities
  /status              - Show current monitoring status
  /start [path]        - Start monitoring path (default: current dir)
  /stop                - Stop file monitoring
  /clear               - Clear scan results
  /help                - Show this help
  /exit                - Exit QINA terminal
        """
        print(help_text)
        
    def display_status(self):
        """Display current status"""
        git_status = ""
        if self.git_repo_info:
            git_status = f"  Git Repository: {self.git_repo_info['current_branch']} ({self.git_repo_info['remote_url'] or 'No remote'})"
        else:
            git_status = "  Git Repository: Not detected"
            
        upload_status = ""
        if hasattr(self, 'last_upload_result') and self.last_upload_result:
            upload_status = f"  Last Upload: {self.last_upload_result.get('fileName', 'Unknown')}"
        else:
            upload_status = "  Last Upload: None"
            
        status = f"""
{Colors.CYAN}Current Status:
{Colors.WHITE}  Monitoring: {'🟢 Active' if self.monitoring_active else '🔴 Inactive'}
  Changed Files: {len(self.changed_files)}
  Last Scan: {'Available' if self.last_scan_results else 'None'}
{upload_status}
  Temp Directory: {self.tmp_dir}
{git_status}
        """
        print(status)
        
    def run(self):
        """Main application loop"""
        self.display_header()
        
        # Auto-start monitoring current directory
        self.start_monitoring()
        
        # Show usage warning and auto-update message
        print(f"{Colors.YELLOW}⚠ Approaching QINA usage limit - /scan to use best available scan model")
        print(f"{Colors.RED}🔄 Auto-update failed Try qina security-update npm -g @qina-security-ai/qina-security-editor")
        
        try:
            while True:
                try:
                    command = input(f"\n{Colors.GREEN}> ")
                    result = self.process_command(command)
                    if result == '__EXIT__':
                        break
                        
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Use '/exit' to quit.")
                except EOFError:
                    break
                    
        finally:
            self.stop_monitoring()
            print(f"\n{Colors.GREEN}👋 QINA Security Terminal closed.")

def main():
    """Entry point"""
    try:
        app = QinaApp()
        # Non-interactive CLI execution: python3 main.py <command> [args...]
        if len(sys.argv) > 1:
            # Join remaining args to support multi-word commands, e.g., "scan branch" or "show critical"
            cli_command = ' '.join(sys.argv[1:])
            result = app.process_command(cli_command)
            if result == '__EXIT__':
                return
            # If command executed was not starting monitoring, avoid leaving observer running
            if app.monitoring_active:
                app.stop_monitoring()
            return
        # Default: interactive terminal UI
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user.")
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()