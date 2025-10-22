"""
QINA Security Editor Package

This package provides the QINA Security Editor - a code monitoring and vulnerability scanning terminal application.

## Main Components

- main.py - Main application entry point
- auth_service.py - Authentication and credential management
- config_manager.py - Configuration file management
- js_scan_service.py - JavaScript scan service wrapper
- sarif_parser.py - SARIF format parser
- scan_result_parser.py - Advanced scan result parser
- findings_manager.py - Findings storage and management

## Usage

```python
from qina_security_editor.main import main
main()
```

Or use the command-line entry point:

```bash
qina
```
"""

__version__ = "1.0.0"
__author__ = "CloudDefense AI"
__email__ = "support@clouddefenseai.com"