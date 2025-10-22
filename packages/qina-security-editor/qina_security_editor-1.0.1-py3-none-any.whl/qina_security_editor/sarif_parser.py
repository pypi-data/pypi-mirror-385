#!/usr/bin/env python3
"""
SARIF Parser for CloudDefense Scan Results
Extracts detailed vulnerability information from SARIF format data
"""

import json
import re
from typing import Dict, List, Any, Optional


class SARIFParser:
    """Parser for SARIF format vulnerability data from CloudDefense scans"""
    
    def __init__(self):
        self.severity_mapping = {
            'CRITICAL': 'critical',
            'HIGH': 'high', 
            'MEDIUM': 'medium',
            'LOW': 'low',
            'error': 'high',
            'warning': 'medium',
            'note': 'low'
        }
    
    def parse_scan_results(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse scan results and extract detailed vulnerability information"""
        detailed_findings = []

        # 1) Prefer the final detailed_findings block if present (already normalized by service)
        if isinstance(scan_results.get('detailed_findings'), list) and scan_results['detailed_findings']:
            normalized: List[Dict[str, Any]] = []
            for f in scan_results['detailed_findings']:
                try:
                    normalized.append(self._normalize_existing_finding(f))
                except Exception:
                    # Skip any malformed entries
                    continue
            if normalized:
                return normalized
        
        # First, try to extract from the detailed SARIF data in messages
        if 'all_messages' in scan_results:
            for message in scan_results['all_messages']:
                if 'message' in message and isinstance(message['message'], str):
                    msg_text = message['message']
                    # Check if it contains scan_metadata (SARIF data)
                    if 'scan_metadata' in msg_text:
                        try:
                            # Find the JSON part in the message
                            json_start = msg_text.find('{')
                            if json_start != -1:
                                json_part = msg_text[json_start:]
                                message_data = json.loads(json_part)
                                findings = self._extract_from_sarif_message(message_data)
                                detailed_findings.extend(findings)
                        except json.JSONDecodeError:
                            continue
                    else:
                        # Try to parse the message as JSON (it might be direct JSON)
                        try:
                            message_data = json.loads(msg_text)
                            findings = self._extract_from_sarif_message(message_data)
                            detailed_findings.extend(findings)
                        except json.JSONDecodeError:
                            continue
        
        # Also extract from the basic newVulnerability array as fallback
        if 'newVulnerability' in scan_results:
            for vuln in scan_results['newVulnerability']:
                finding = {
                    'id': vuln.get('name', 'unknown'),
                    'title': vuln.get('name', 'Vulnerability'),
                    'file': vuln.get('filePath', 'unknown'),
                    'line': 0,  # Will be updated if we find SARIF data
                    'severity': 'medium',  # Default, will be updated if we find SARIF data
                    'description': '',
                    'rule_id': vuln.get('name', ''),
                    'type': 'newVulnerability',
                    'code_snippet': '',
                    'cwe': [],
                    'references': []
                }
                detailed_findings.append(finding)
        
        return detailed_findings

    def _normalize_existing_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize an existing finding object to the expected schema.

        Ensures the following keys are present and clean:
        title, file, line, severity, description, rule_id, code_snippet, language, cwe, references
        """
        title = finding.get('title') or finding.get('name') or finding.get('rule_id') or 'Finding'
        file_path = finding.get('file') or finding.get('filePath') or 'unknown'
        if isinstance(file_path, str) and file_path.startswith('/app/'):
            file_path = file_path.replace('/app/', '')
        line_number = 0
        try:
            line_number = int(finding.get('line') or 0)
        except Exception:
            line_number = 0
        # Prefer explicit severity; if absent, map from issue_severity or level
        severity = finding.get('severity')
        if not severity:
            issue_severity = finding.get('issue_severity')
            if isinstance(issue_severity, str):
                severity = self.severity_mapping.get(issue_severity, 'medium')
            else:
                severity = 'medium'
        # Normalize severity to lower-case canonical
        if isinstance(severity, str):
            upper = severity.upper()
            severity = self.severity_mapping.get(upper, severity.lower())
        description = finding.get('description') or finding.get('message') or ''
        rule_id = finding.get('rule_id') or finding.get('id') or ''
        code_snippet = finding.get('code_snippet') or ''
        language = finding.get('language') or 'unknown'
        cwe = finding.get('cwe') or []
        references = finding.get('references') or []

        # Clean snippet formatting similar to SARIF path
        if isinstance(code_snippet, str):
            code_snippet = self._clean_code_snippet(code_snippet)

        return {
            'id': rule_id or title,
            'title': title,
            'file': file_path,
            'line': line_number,
            'severity': severity,
            'description': description,
            'rule_id': rule_id,
            'code_snippet': code_snippet,
            'language': language,
            'type': finding.get('type', 'sarif_result'),
            'cwe': cwe if isinstance(cwe, list) else [cwe],
            'references': references if isinstance(references, list) else [references],
            'issue_severity': finding.get('issue_severity')
        }
    
    def _extract_from_sarif_message(self, message_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract findings from SARIF message data"""
        findings = []
        
        if 'language_results' in message_data:
            for lang_result in message_data['language_results']:
                language = lang_result.get('language', 'unknown')
                
                if 'sarif_report' in lang_result:
                    sarif_data = lang_result['sarif_report']
                    findings.extend(self._extract_from_sarif_report(sarif_data, language))
        
        return findings
    
    def _extract_from_sarif_report(self, sarif_data: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """Extract findings from SARIF report data"""
        findings = []
        
        # Handle different SARIF structures
        if 'results' in sarif_data:
            # Direct results array
            for result in sarif_data['results']:
                finding = self._parse_sarif_result(result, language)
                if finding:
                    findings.append(finding)
        
        elif 'runs' in sarif_data:
            # SARIF runs structure
            for run in sarif_data['runs']:
                if 'results' in run:
                    for result in run['results']:
                        finding = self._parse_sarif_result(result, language)
                        if finding:
                            findings.append(finding)
        
        # Handle the specific structure we see in the data
        elif 'vulnerabilities' in sarif_data:
            # This is the structure we see in the actual data
            vulnerabilities = sarif_data['vulnerabilities']
            if isinstance(vulnerabilities, list):
                for vuln in vulnerabilities:
                    if 'results' in vuln:
                        for result in vuln['results']:
                            finding = self._parse_sarif_result(result, language)
                            if finding:
                                findings.append(finding)
        
        return findings
    
    def _parse_sarif_result(self, result: Dict[str, Any], language: str) -> Optional[Dict[str, Any]]:
        """Parse individual SARIF result"""
        try:
            # Extract basic information
            rule_id = result.get('ruleId', 'UNKNOWN')
            
            # Extract message/description
            message = result.get('message', {})
            if isinstance(message, dict):
                description = message.get('text', '')
            else:
                description = str(message)
            
            # Extract severity from properties
            properties = result.get('properties', {})
            issue_severity = properties.get('issue_severity', 'MEDIUM')
            
            # Map severity
            severity = self.severity_mapping.get(issue_severity, 'medium')
            
            # Also check the level field as fallback
            level = result.get('level', 'note').lower()
            if severity == 'medium' and level in self.severity_mapping:
                severity = self.severity_mapping[level]
            
            # Extract location information
            locations = result.get('locations', [])
            file_path = 'unknown'
            line_number = 0
            code_snippet = ''
            
            if locations:
                loc = locations[0]
                if 'physicalLocation' in loc:
                    phys_loc = loc['physicalLocation']
                    
                    # Extract file path
                    if 'artifactLocation' in phys_loc:
                        file_path = phys_loc['artifactLocation'].get('uri', 'unknown')
                    
                    # Extract line number and code snippet
                    if 'region' in phys_loc:
                        region = phys_loc['region']
                        line_number = region.get('startLine', 0)
                        
                        # Extract code snippet
                        if 'snippet' in region:
                            snippet = region['snippet']
                            if 'text' in snippet:
                                code_snippet = snippet['text']
                                # Clean up the snippet
                                code_snippet = self._clean_code_snippet(code_snippet)
            
            # Clean up file path
            if file_path.startswith('/app/'):
                file_path = file_path.replace('/app/', '')
            
            # Extract CWE and references
            cwe = properties.get('cwe', [])
            references = properties.get('references', [])
            
            return {
                'id': rule_id,
                'title': rule_id.replace('-', ' ').title(),
                'file': file_path,
                'line': line_number,
                'severity': severity,
                'description': description,
                'rule_id': rule_id,
                'code_snippet': code_snippet,
                'language': language,
                'type': 'sarif_result',
                'cwe': cwe,
                'references': references,
                'issue_severity': issue_severity
            }
            
        except Exception as e:
            print(f"Error parsing SARIF result: {e}")
            return None
    
    def _clean_code_snippet(self, snippet: str) -> str:
        """Clean up code snippet for better readability"""
        if not snippet:
            return ''
        
        # Remove extra whitespace and newlines
        snippet = snippet.strip()
        
        # Replace escaped newlines with actual newlines
        snippet = snippet.replace('\\n', '\n')
        
        # Remove extra spaces
        lines = snippet.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def display_parsed_results(self, findings: List[Dict[str, Any]]) -> None:
        """Display parsed findings in a formatted way"""
        if not findings:
            print("No detailed findings found.")
            return
        
        print(f"\n🔍 PARSED VULNERABILITY DETAILS:")
        print("=" * 80)
        
        for i, finding in enumerate(findings, 1):
            print(f"{i}. {finding['title']}")
            print(f"   File: {finding['file']}:{finding['line']}")
            print(f"   Severity: {finding['severity']} (from: {finding.get('issue_severity', 'N/A')})")
            print(f"   Type: {finding['type']}")
            print(f"   Language: {finding.get('language', 'unknown')}")
            
            if finding.get('description'):
                print(f"   Description: {finding['description']}")
            
            if finding.get('code_snippet'):
                print(f"   Code Snippet:")
                for line in finding['code_snippet'].split('\n'):
                    print(f"     {line}")
            
            if finding.get('cwe'):
                print(f"   CWE: {', '.join(finding['cwe'])}")
            
            if finding.get('references'):
                refs = finding['references'] if isinstance(finding['references'], list) else [finding['references']]
                if refs:
                    print("   References:")
                    for ref in refs:
                        print(f"     - {ref}")
            
            print("-" * 40)


def main():
    """Test the parser with the upload-scan-response.txt file"""
    parser = SARIFParser()
    
    # Read the scan results file
    try:
        with open('upload-scan-response.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the JSON content
        # Find the JSON part (skip the header)
        json_start = content.find('{')
        if json_start == -1:
            print("No JSON data found in file")
            return
        
        json_content = content[json_start:]
        scan_data = json.loads(json_content)
        
        # Extract scan results
        if 'scan_results' in scan_data:
            scan_results = scan_data['scan_results']
            
            # Parse the results
            findings = parser.parse_scan_results(scan_results)
            
            # Display parsed results only
            parser.display_parsed_results(findings)
            
        else:
            print("No scan_results found in the data")
            
    except Exception as e:
        print(f"Error reading or parsing file: {e}")


if __name__ == "__main__":
    main()
