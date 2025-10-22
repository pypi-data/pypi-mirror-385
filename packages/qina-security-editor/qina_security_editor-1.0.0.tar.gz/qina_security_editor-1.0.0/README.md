# QINA Security Editor

A powerful code monitoring and vulnerability scanning terminal application that provides real-time security analysis for your development workflow.

## Features

- 🔍 **Real-time Code Monitoring** - Automatically detects file changes and triggers scans
- 🛡️ **Vulnerability Scanning** - Comprehensive security analysis using CloudDefense AI
- 📊 **Detailed Results** - Rich vulnerability reports with severity classification
- 🔧 **Git Integration** - Branch scanning and diff analysis
- ⚡ **Fast Performance** - Optimized for developer productivity
- 🎨 **Beautiful Terminal UI** - Color-coded output and intuitive interface

## Installation

```bash
pip install qina-security-editor
```

## Quick Start

1. **Run the application:**
   ```bash
   qina
   ```

2. **Set up your credentials** (first time only):
   - The app will guide you through CloudDefense AI login
   - Enter your API key when prompted

3. **Environment Configuration** (optional):
   ```bash
   # QA Environment (default)
   export CLOUDDEFENSE_API_KEY=your_api_key
   
   # Production Environment
   export CLOUDDEFENSE_API_BASE_URL=https://console.clouddefenseai.com
   export CLOUDDEFENSE_WS_BASE_URL=wss://console.clouddefenseai.com
   export CLOUDDEFENSE_API_KEY=your_api_key
   ```

4. **Start monitoring:**
   ```bash
   /start [path]  # Start monitoring a directory (default: current)
   ```

4. **Run scans:**
   ```bash
   scan          # Scan monitored files
   scan branch   # Scan current git branch
   ```

## Commands

### Core Commands
- `scan` - Run file upload scan
- `scan branch` - Run branch scan
- `git diff` - Analyze git diff changes
- `parse results` - Parse and display scan results

### Monitoring Commands
- `/start [path]` - Start monitoring directory
- `/stop` - Stop monitoring
- `add file <path>` - Manually add file to monitoring
- `list files` - List monitored files

### Filtering Commands
- `show critical` - Show critical vulnerabilities
- `show high` - Show high priority vulnerabilities
- `show medium` - Show medium priority vulnerabilities
- `show low` - Show low priority vulnerabilities

### Utility Commands
- `/status` - Show current status
- `/clear` - Clear scan results
- `/help` - Show help
- `/exit` - Exit application

## Configuration

The application stores configuration in `~/.config/qina_security_editor/config.json`:

```json
{
  "api_key": "your_api_key",
  "team_id": "your_team_id"
}
```

## Environment Variables

- `CLOUDDEFENSE_API_KEY` - Your CloudDefense AI API key
- `CLOUDDEFENSE_TEAM_ID` - Your team ID
- `CLOUDDEFENSE_CLIENT_ID` - Client ID (optional)

## Requirements

- Python 3.8+
- Git repository (for branch scanning)
- CloudDefense AI account

## Support

- 📧 Email: support@clouddefenseai.com
- 🐛 Issues: [GitHub Issues](https://github.com/clouddefenseai/qina-security-editor/issues)
- 📖 Documentation: [GitHub README](https://github.com/clouddefenseai/qina-security-editor#readme)

## License

MIT License - see LICENSE file for details.