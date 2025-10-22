import asyncio
import websockets
import json
import sys
import subprocess
import os
from pathlib import Path
from .sarif_parser import SARIFParser
from .config_manager import ConfigManager

# Simple color constants for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# Quiet minimal output and spinner until completion
QUIET = True

def qprint(*args, **kwargs):
    if not QUIET:
        print(*args, **kwargs)

def get_git_repo_info():
    """Get current git repository information"""
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

def get_branch_name():
    """Get branch name from user input or use current branch"""
    git_info = get_git_repo_info()
    if not git_info:
        print('❌ No git repository detected. Please run this command in a git repository.')
        return None, None
        
    current_branch = git_info['current_branch']
    remote_url = git_info['remote_url']
    
    if not remote_url:
        print('❌ No remote URL configured. Please set up git remote origin.')
        return None, None
    
    # Convert SSH URL to HTTPS format if needed
    if remote_url.startswith('git@'):
        remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
        if not remote_url.endswith('.git'):
            remote_url += '.git'
    elif not remote_url.startswith('http'):
        remote_url = remote_url.replace('git@', 'https://').replace(':', '/')
        if not remote_url.endswith('.git'):
            remote_url += '.git'
    elif remote_url.startswith('https://') and not remote_url.endswith('.git'):
        remote_url += '.git'
    
    # Ask for branch name
    print(f'Repository: {remote_url}')
    print(f'Branch: {current_branch}')
    
    branch_input = input(f'Enter branch name to scan (or press Enter for "{current_branch}"): ').strip()
    branch_name = branch_input if branch_input else current_branch
    
    return remote_url, branch_name

def parse_detailed_vulnerabilities(msg_data):
    """Parse detailed vulnerability information from scan results"""
    print('\n🔍 DETAILED VULNERABILITY ANALYSIS:')
    print('=' * 50)
    
    # Parse OSS License information if available
    if 'ossLicenseCounts' in msg_data:
        print('\n📄 OPEN SOURCE LICENSE ANALYSIS:')
        print('=' * 50)
        
        for license_info in msg_data['ossLicenseCounts']:
            file_name = license_info.get('fileName', 'Unknown')
            total_count = license_info.get('totalCount', 0)
            denied_count = license_info.get('deniedCount', 0)
            allowed_count = license_info.get('allowedCount', 0)
            
            print(f'📁 {file_name}:')
            print(f'   Total Dependencies: {total_count}')
            print(f'   ❌ Denied Licenses: {denied_count}')
            print(f'   ✅ Allowed Licenses: {allowed_count}')
            if denied_count > 0:
                print(f'   ⚠️  {denied_count} dependencies have denied licenses!')
            print('   ' + '-' * 40)
    
    # Parse build policy results
    if 'response' in msg_data and 'results' in msg_data['response']:
        results = msg_data['response']['results']
        
        for category, data in results.items():
            if 'failureBuildPolicyResults' in data and data['failureBuildPolicyResults']:
                print(f'\n🚨 {category}:')
                for finding in data['failureBuildPolicyResults']:
                    rule = finding.get('rule', {})
                    message = finding.get('message', 'No description')
                    count = finding.get('count', 0)
                    
                    print(f'   📋 Rule: {rule.get("operand", "Unknown")} {rule.get("operator", "")} {rule.get("value", "")}')
                    print(f'   📝 Description: {message}')
                    print(f'   🔢 Count: {count}')
                    print('   ' + '-' * 40)
    
    # Note: The actual detailed vulnerability data (file paths, line numbers, etc.) 
    # would typically be in a SARIF format or similar detailed results structure
    # that might be available in other parts of the response or through separate API calls
    print('\n💡 For detailed file-level vulnerability information, check the CloudDefense dashboard')
    print('   or use the web interface for complete SARIF results with file paths and line numbers.')

async def main():
    # Get repository information
    repo_url, branch_name = get_branch_name()
    if not repo_url or not branch_name:
        return
    
    # Get credentials from config manager
    config = ConfigManager()
    cli_id = os.environ.get('CLOUDDEFENSE_CLIENT_ID', '123e4567-e89b-12d3-a456-426614174000')
    api_key = config.get_api_key()
    
    if not api_key:
        print('❌ No API key found in config')
        print('💡 Please run the main application first to set up your credentials')
        print('💡 Or set environment variable: export CLOUDDEFENSE_API_KEY=your_api_key')
        return
    
    # Use the actual repository URL for scanning
    # Environment-based URLs
    ws_base = os.environ.get('CLOUDDEFENSE_WS_BASE_URL', 'wss://qa.clouddefenseai.com')
    url = f'{ws_base}/ws/scan/{cli_id}/ide/branch?CLOUDDEFENSE_API_KEY={api_key}'
    
    qprint(f'Connecting to: {url}')
    print(f'Repository: {repo_url}')
    print(f'Branch: {branch_name}')
    
    # Initialize SARIF parser
    sarif_parser = SARIFParser()
    
    try:
        async with websockets.connect(url) as websocket:
            print('Connected successfully!')
            
            # Send branch scan message
            scan_message = {
                "url": repo_url,
                "type": "GITHUB",
                "branchName": branch_name,
                "isPublic": True,
                "isEnterprise": False
            }
            
            qprint(f'Sending branch scan request: {scan_message}')
            await websocket.send(json.dumps(scan_message))
            
            # Listen for messages with a spinner
            async def _spinner(stop_event: asyncio.Event):
                frames = ['|', '/', '-', '\\']
                idx = 0
                print('Processing...', end='', flush=True)
                while not stop_event.is_set():
                    print(f'\rProcessing... {frames[idx % len(frames)]}', end='', flush=True)
                    idx += 1
                    await asyncio.sleep(0.15)
                print('\r' + ' ' * 40 + '\r', end='', flush=True)

            stop_event = asyncio.Event()
            spinner_task = asyncio.create_task(_spinner(stop_event))

            message_count = 0
            all_messages = []
            scan_completed = False
            
            async for message in websocket:
                message_count += 1
                try:
                    msg_data = json.loads(message)
                    all_messages.append(msg_data)
                    status = msg_data.get('status', 'unknown')
                    msg_text = msg_data.get('message', '')
                    
                    # Check if this message contains scan_metadata (the detailed results)
                    if isinstance(msg_text, str) and 'scan_metadata' in msg_text:
                        stop_event.set()
                        await spinner_task
                        print('✅ Branch scan completed successfully!')
                        
                        # Parse the scan_metadata JSON from the message
                        try:
                            # Extract JSON from the message string
                            json_start = msg_text.find('{')
                            if json_start != -1:
                                json_part = msg_text[json_start:]
                                scan_metadata = json.loads(json_part)
                                
                                # Use SARIF parser to extract detailed findings
                                sarif_findings = sarif_parser.parse_scan_results({
                                    'all_messages': [{'message': json_part}],
                                    'newVulnerability': []
                                })
                                
                                if sarif_findings:
                                    print('\n🔍 BRANCH SCAN RESULTS:')
                                    print('=' * 80)
                                    sarif_parser.display_parsed_results(sarif_findings)
                                    
                                    # Display summary
                                    total_findings = len(sarif_findings)
                                    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                                    for finding in sarif_findings:
                                        severity = finding.get('severity', 'medium').lower()
                                        if severity in severity_counts:
                                            severity_counts[severity] += 1
                                    
                                    print(f'\n📊 Summary: {total_findings} total findings')
                                    print(f'   Critical: {severity_counts["critical"]}, High: {severity_counts["high"]}, Medium: {severity_counts["medium"]}, Low: {severity_counts["low"]}')
                                else:
                                    print('No detailed findings found in scan results.')
                                
                                scan_completed = True
                                break
                        except json.JSONDecodeError as e:
                            print(f'Error parsing scan metadata: {e}')
                            continue
                    
                    # Legacy completion handling (fallback)
                    elif status in ['Ok', 'ok'] and 'scan completed successfully' in msg_text.lower():
                        stop_event.set()
                        await spinner_task
                        print('✅ Branch scan completed successfully!')
                        
                        if 'response' in msg_data:
                            print('\nResults summary:')
                            print('=' * 50)
                            if 'counts' in msg_data:
                                counts = msg_data.get('counts', [])
                                total_findings = 0
                                for count in counts:
                                    file_name = count.get('fileName', 'Unknown')
                                    total = count.get('totalCount', 0)
                                    critical = count.get('criticalCount', 0)
                                    high = count.get('highCount', 0)
                                    medium = count.get('mediumCount', 0)
                                    low = count.get('lowCount', 0)
                                    print(f'{file_name}: Total={total} Critical={critical} High={high} Medium={medium} Low={low}')
                                    total_findings += total
                                print(f'\nTotal findings: {total_findings}')
                        scan_completed = True
                        break
                    elif status == 'Failed' and 'build policy' in msg_text.lower():
                        stop_event.set()
                        await spinner_task
                        print('⚠️ Build policy failed - scan completed with findings.')
                        if 'response' in msg_data:
                            print('\nResults summary:')
                            print('=' * 50)
                            if 'counts' in msg_data:
                                counts = msg_data.get('counts', [])
                                total_findings = 0
                                for count in counts:
                                    file_name = count.get('fileName', 'Unknown')
                                    total = count.get('totalCount', 0)
                                    critical = count.get('criticalCount', 0)
                                    high = count.get('highCount', 0)
                                    medium = count.get('mediumCount', 0)
                                    low = count.get('lowCount', 0)
                                    print(f'{file_name}: Total={total} Critical={critical} High={high} Medium={medium} Low={low}')
                                    total_findings += total
                                print(f'\nTotal findings: {total_findings}')
                        scan_completed = True
                        break
                    elif status in ['Failed', 'failed'] and 'build policy' not in msg_text.lower():
                        stop_event.set()
                        await spinner_task
                        print(f'❌ Scan failed: {msg_text}')
                        break
                    else:
                        # Suppress intermediate progress
                        pass
                        
                except json.JSONDecodeError:
                    print(f'📨 Message {message_count}: {message}')
            
            if not scan_completed:
                stop_event.set()
                await spinner_task
                print('⚠️ Scan completed but no detailed results found.')
                
    except websockets.exceptions.WebSocketException as err:
        print(f'WebSocket error: {err}')
    except Exception as err:
        print(f'Error: {err}')
    finally:
        qprint('Connection closed')

if __name__ == '__main__':
    asyncio.run(main())