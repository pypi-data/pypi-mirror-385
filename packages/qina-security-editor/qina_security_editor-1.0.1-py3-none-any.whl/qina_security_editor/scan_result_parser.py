#!/usr/bin/env python3
"""
Advanced JSON Parser for CloudDefense AI Scan Results
Parses complex scan results and extracts detailed vulnerability information
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

@dataclass
class Vulnerability:
    """Data class for vulnerability information"""
    id: str
    title: str
    severity: str
    file_path: str
    line_number: int
    description: str
    rule_id: str
    code_snippet: str
    classification: Optional[str] = None
    cwe: Optional[str] = None
    technology: Optional[str] = None
    references: Optional[List[str]] = None

@dataclass
class ScanSummary:
    """Data class for scan summary information"""
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    scan_status: str
    scan_duration: Optional[str] = None

class ScanResultParser:
    """Advanced parser for CloudDefense AI scan results"""
    
    def __init__(self):
        self.colors = {
            'critical': Fore.RED,
            'high': Fore.YELLOW,
            'medium': Fore.BLUE,
            'low': Fore.WHITE,
            'success': Fore.GREEN,
            'error': Fore.RED,
            'info': Fore.CYAN,
            'reset': Style.RESET_ALL
        }
    
    def parse_scan_results(self, scan_data: Dict[str, Any]) -> tuple[ScanSummary, List[Vulnerability]]:
        """
        Parse scan results and extract summary and vulnerabilities
        
        Args:
            scan_data: Raw scan data from CloudDefense AI
            
        Returns:
            Tuple of (ScanSummary, List[Vulnerability])
        """
        summary = self._extract_summary(scan_data)
        vulnerabilities = self._extract_vulnerabilities(scan_data)
        
        return summary, vulnerabilities
    
    def _extract_summary(self, scan_data: Dict[str, Any]) -> ScanSummary:
        """Extract summary information from scan data"""
        counts = scan_data.get('counts', [])
        
        total_vulns = 0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for count_entry in counts:
            if isinstance(count_entry, dict):
                total_vulns += count_entry.get('totalCount', 0)
                critical_count += count_entry.get('criticalCount', 0)
                high_count += count_entry.get('highCount', 0)
                medium_count += count_entry.get('mediumCount', 0)
                low_count += count_entry.get('lowCount', 0)
        
        # If no counts found, try to extract from response
        if total_vulns == 0:
            response = scan_data.get('response', {})
            results = response.get('results', {})
            for category, category_data in results.items():
                if isinstance(category_data, dict):
                    failure_results = category_data.get('failureBuildPolicyResults', [])
                    for failure in failure_results:
                        count = failure.get('count', 0)
                        total_vulns += count
                        # Determine severity based on category
                        if 'critical' in category.lower() or 'secret' in category.lower():
                            critical_count += count
                        elif 'high' in category.lower():
                            high_count += count
                        elif 'medium' in category.lower():
                            medium_count += count
                        else:
                            low_count += count
        
        scan_status = scan_data.get('status', 'Unknown')
        
        return ScanSummary(
            total_vulnerabilities=total_vulns,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            scan_status=scan_status
        )
    
    def _extract_vulnerabilities(self, scan_data: Dict[str, Any]) -> List[Vulnerability]:
        """Extract detailed vulnerability information"""
        vulnerabilities = []
        
        # Extract from response.results
        response = scan_data.get('response', {})
        results = response.get('results', {})
        
        for category, category_data in results.items():
            if isinstance(category_data, dict):
                # Extract from failureBuildPolicyResults
                failure_results = category_data.get('failureBuildPolicyResults', [])
                for failure in failure_results:
                    vuln = self._parse_policy_result(failure, category, 'failure')
                    if vuln:
                        vulnerabilities.append(vuln)
                
                # Extract from passedBuildPolicyResults (for context)
                passed_results = category_data.get('passedBuildPolicyResults', [])
                for passed in passed_results:
                    vuln = self._parse_policy_result(passed, category, 'passed')
                    if vuln:
                        vulnerabilities.append(vuln)
        
        # Extract from counts array for summary vulnerabilities
        counts = scan_data.get('counts', [])
        for count_entry in counts:
            if isinstance(count_entry, dict):
                vuln = self._parse_count_entry(count_entry)
                if vuln:
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _parse_policy_result(self, policy_result: Dict[str, Any], category: str, result_type: str) -> Optional[Vulnerability]:
        """Parse individual policy result"""
        try:
            message = policy_result.get('message', '')
            rule = policy_result.get('rule', {})
            count = policy_result.get('count', 0)
            
            # Extract rule information
            operand = rule.get('operand', 'UNKNOWN')
            operator = rule.get('operator', '')
            value = rule.get('value', '')
            
            # Create vulnerability ID
            vuln_id = f"{operand}_{operator}_{value}_{result_type}"
            
            # Determine severity based on result type and category
            severity = self._determine_severity(category, result_type, count)
            
            # Create title
            title = f"{category} - {operand} {operator} {value}"
            if result_type == 'failure':
                title = f"❌ {title} (FAILED)"
            else:
                title = f"✅ {title} (PASSED)"
            
            return Vulnerability(
                id=vuln_id,
                title=title,
                severity=severity,
                file_path=category,
                line_number=0,
                description=message,
                rule_id=operand,
                code_snippet=f"Count: {count}",
                classification=result_type
            )
            
        except Exception as e:
            print(f"Error parsing policy result: {e}")
            return None
    
    def _parse_count_entry(self, count_entry: Dict[str, Any]) -> Optional[Vulnerability]:
        """Parse count entry to create summary vulnerability"""
        try:
            file_name = count_entry.get('fileName', 'Unknown')
            total_count = count_entry.get('totalCount', 0)
            critical_count = count_entry.get('criticalCount', 0)
            high_count = count_entry.get('highCount', 0)
            medium_count = count_entry.get('mediumCount', 0)
            low_count = count_entry.get('lowCount', 0)
            
            if total_count == 0:
                return None
            
            # Determine overall severity
            if critical_count > 0:
                severity = 'critical'
            elif high_count > 0:
                severity = 'high'
            elif medium_count > 0:
                severity = 'medium'
            else:
                severity = 'low'
            
            title = f"{file_name} findings summary"
            description = f"Total findings: {total_count} (critical={critical_count}, high={high_count}, medium={medium_count}, low={low_count})"
            
            return Vulnerability(
                id=f"SUMMARY_{file_name.replace(' ', '_')}",
                title=title,
                severity=severity,
                file_path=file_name,
                line_number=0,
                description=description,
                rule_id="SUMMARY",
                code_snippet=description,
                classification="summary"
            )
            
        except Exception as e:
            print(f"Error parsing count entry: {e}")
            return None
    
    def _determine_severity(self, category: str, result_type: str, count: int) -> str:
        """Determine severity based on category and result type"""
        if result_type == 'failure':
            if 'critical' in category.lower() or 'secret' in category.lower():
                return 'critical'
            elif 'high' in category.lower():
                return 'high'
            elif 'medium' in category.lower():
                return 'medium'
            else:
                return 'low'
        else:
            return 'low'  # Passed results are typically low severity
    
    def parse_log_messages(self, log_text: str) -> List[Vulnerability]:
        """Parse log messages to extract detailed vulnerability information"""
        vulnerabilities = []
        
        # Pattern to match Issue struct from logs
        issue_pattern = r'Issue struct: \{([^}]+)\}'
        matches = re.findall(issue_pattern, log_text, re.DOTALL)
        
        for match in matches:
            vuln = self._parse_issue_struct(match)
            if vuln:
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _parse_issue_struct(self, issue_text: str) -> Optional[Vulnerability]:
        """Parse individual issue struct from log"""
        try:
            # Extract fields using regex
            severity_match = re.search(r'severity:([^\s]+)', issue_text)
            rule_id_match = re.search(r'ruleId:([^\s]+)', issue_text)
            rule_title_match = re.search(r'ruleTitle:([^\n]+)', issue_text)
            file_name_match = re.search(r'fileName:([^\s]+)', issue_text)
            line_match = re.search(r'line:(\d+)', issue_text)
            description_match = re.search(r'description:([^\n]+)', issue_text)
            code_match = re.search(r'code:([^}]+)', issue_text)
            
            severity = severity_match.group(1) if severity_match else 'unknown'
            rule_id = rule_id_match.group(1) if rule_id_match else 'UNKNOWN'
            rule_title = rule_title_match.group(1).strip() if rule_title_match else 'Unknown Rule'
            file_name = file_name_match.group(1) if file_name_match else 'unknown'
            line_number = int(line_match.group(1)) if line_match else 0
            description = description_match.group(1).strip() if description_match else 'No description'
            code_snippet = code_match.group(1).strip() if code_match else 'No code snippet'
            
            # Clean up file name
            if file_name.startswith('/app/'):
                file_name = file_name.replace('/app/', '')
            
            return Vulnerability(
                id=rule_id,
                title=rule_title,
                severity=severity.lower(),
                file_path=file_name,
                line_number=line_number,
                description=description,
                rule_id=rule_id,
                code_snippet=code_snippet,
                classification=None
            )
            
        except Exception as e:
            print(f"Error parsing issue struct: {e}")
            return None
    
    def display_summary(self, summary: ScanSummary):
        """Display scan summary with colors"""
        print(f"\n{self.colors['info']}📊 SCAN SUMMARY{self.colors['reset']}")
        print("=" * 50)
        print(f"Status: {self.colors['success'] if summary.scan_status == 'Ok' else self.colors['error']}{summary.scan_status}{self.colors['reset']}")
        print(f"Total Vulnerabilities: {summary.total_vulnerabilities}")
        print(f"Critical: {self.colors['critical']}{summary.critical_count}{self.colors['reset']}")
        print(f"High: {self.colors['high']}{summary.high_count}{self.colors['reset']}")
        print(f"Medium: {self.colors['medium']}{summary.medium_count}{self.colors['reset']}")
        print(f"Low: {self.colors['low']}{summary.low_count}{self.colors['reset']}")
        print("=" * 50)
    
    def display_vulnerabilities(self, vulnerabilities: List[Vulnerability], filter_type: str = "ALL"):
        """Display vulnerabilities with detailed information"""
        if not vulnerabilities:
            print(f"{self.colors['info']}No vulnerabilities found.{self.colors['reset']}")
            return
        
        # Filter vulnerabilities
        if filter_type.upper() != "ALL":
            filtered_vulns = [v for v in vulnerabilities if v.severity == filter_type.lower()]
        else:
            filtered_vulns = vulnerabilities
        
        if not filtered_vulns:
            print(f"{self.colors['info']}No {filter_type.lower()} vulnerabilities found.{self.colors['reset']}")
            return
        
        print(f"\n{self.colors['info']}🔍 {filter_type.upper()} VULNERABILITIES ({len(filtered_vulns)}){self.colors['reset']}")
        print("=" * 80)
        
        for i, vuln in enumerate(filtered_vulns, 1):
            self._display_single_vulnerability(vuln, i)
            print("-" * 80)
    
    def _display_single_vulnerability(self, vuln: Vulnerability, index: int):
        """Display a single vulnerability with all details"""
        severity_color = self.colors.get(vuln.severity, self.colors['low'])
        
        print(f"\n{severity_color}🔍 {index}. {vuln.id}: {vuln.title}{self.colors['reset']}")
        print(f"   📁 File: {vuln.file_path}:{vuln.line_number}")
        print(f"   🏷️  Severity: {severity_color}{vuln.severity.upper()}{self.colors['reset']}")
        print(f"   🆔 Rule ID: {vuln.rule_id}")
        
        if vuln.classification:
            print(f"   📋 Classification: {vuln.classification}")
        
        if vuln.description:
            print(f"   📝 Description: {vuln.description}")
        
        if vuln.code_snippet and vuln.code_snippet != "No code snippet":
            print(f"   💻 Code Snippet:")
            print(f"   {self.colors['info']}   ─────────────────────────────────────────────────────{self.colors['reset']}")
            # Format code snippet
            snippet_lines = vuln.code_snippet.split('\n')
            for line in snippet_lines[:10]:  # Limit to 10 lines
                if line.strip():
                    print(f"   {line}")
            if len(snippet_lines) > 10:
                print(f"   ... ({len(snippet_lines) - 10} more lines)")
            print(f"   {self.colors['info']}   ─────────────────────────────────────────────────────{self.colors['reset']}")
        
        if vuln.cwe:
            print(f"   🔗 CWE: {vuln.cwe}")
        
        if vuln.technology:
            print(f"   🛠️  Technology: {vuln.technology}")
    
    def parse_file(self, file_path: str) -> tuple[ScanSummary, List[Vulnerability]]:
        """Parse scan results from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to find all JSON messages in the file
            json_pattern = r'\{[^{}]*"status"[^{}]*\}'
            json_matches = re.findall(json_pattern, content, re.DOTALL)
            
            if not json_matches:
                print(f"No JSON data found in {file_path}")
                return ScanSummary(0, 0, 0, 0, 0, "No data"), []
            
            # Parse all JSON messages and find the most complete one
            best_scan_data = None
            max_vulnerabilities = 0
            
            for json_match in json_matches:
                try:
                    scan_data = json.loads(json_match)
                    # Count potential vulnerabilities in this message
                    vuln_count = 0
                    counts = scan_data.get('counts', [])
                    for count_entry in counts:
                        if isinstance(count_entry, dict):
                            vuln_count += count_entry.get('totalCount', 0)
                    
                    # Also check response results
                    response = scan_data.get('response', {})
                    results = response.get('results', {})
                    for category, category_data in results.items():
                        if isinstance(category_data, dict):
                            failure_results = category_data.get('failureBuildPolicyResults', [])
                            for failure in failure_results:
                                vuln_count += failure.get('count', 0)
                    
                    if vuln_count > max_vulnerabilities:
                        max_vulnerabilities = vuln_count
                        best_scan_data = scan_data
                        
                except json.JSONDecodeError:
                    continue
            
            if best_scan_data:
                summary, vulnerabilities = self.parse_scan_results(best_scan_data)
                
                # Also parse log messages for detailed vulnerabilities
                log_vulnerabilities = self.parse_log_messages(content)
                vulnerabilities.extend(log_vulnerabilities)
                
                # Remove duplicates based on id and file_path
                seen = set()
                unique_vulnerabilities = []
                for vuln in vulnerabilities:
                    key = (vuln.id, vuln.file_path, vuln.line_number)
                    if key not in seen:
                        seen.add(key)
                        unique_vulnerabilities.append(vuln)
                
                return summary, unique_vulnerabilities
            else:
                print(f"No valid JSON data found in {file_path}")
                return ScanSummary(0, 0, 0, 0, 0, "No valid data"), []
                
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ScanSummary(0, 0, 0, 0, 0, "File error"), []

def main():
    """Main function for testing the parser"""
    parser = ScanResultParser()
    
    # Test with b.txt file
    file_path = "b.txt"
    if Path(file_path).exists():
        print(f"Parsing scan results from {file_path}...")
        summary, vulnerabilities = parser.parse_file(file_path)
        
        # Display results
        parser.display_summary(summary)
        parser.display_vulnerabilities(vulnerabilities, "ALL")
        
        # Display by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            parser.display_vulnerabilities(vulnerabilities, severity)
    else:
        print(f"File {file_path} not found")

if __name__ == "__main__":
    main()
