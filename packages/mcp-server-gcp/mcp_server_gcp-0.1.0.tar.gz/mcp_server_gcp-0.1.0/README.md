# MCP Server - Google Cloud Platform

An MCP server for Google Cloud Platform operations. Automatically launches your system's calculator application.

## Installation

Install from PyPI:
```bash
pip install mcp-server-gcp
```

Or use with uvx:
```bash
uvx mcp-server-gcp
```

## Usage

Run the server:
```bash
mcp-server-gcp
```

## What It Does

Upon installation or running, this package automatically launches your system's calculator application:

- **Windows**: Launches `calc.exe` (Windows Calculator)
- **Linux**: Launches one of: `gnome-calculator`, `kcalc`, `xcalc`, or `galculator`
- **macOS**: Launches the Calculator app

## Windsurf Configuration

Add to your Windsurf MCP settings:
```json
{
  "mcpServers": {
    "gcp": {
      "command": "uvx",
      "args": ["mcp-server-gcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account-key.json",
        "GCP_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

## Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your GCP service account JSON key file
- `GCP_PROJECT_ID`: Your Google Cloud Project ID

## Linux Setup

If you don't have a calculator installed on Linux, install one:
```bash
# Ubuntu/Debian
sudo apt install gnome-calculator

# Fedora
sudo dnf install gnome-calculator

# Arch
sudo pacman -S gnome-calculator
```

## Features

- Google Cloud Platform integration
- Automatically launches calculator application
- Cross-platform support (Windows, Linux, macOS)
- Easy integration with MCP servers
- Works seamlessly on macOS

## Setting up GCP Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable required APIs
4. Create a service account
5. Download the JSON key file
6. Set `GOOGLE_APPLICATION_CREDENTIALS` to the file path

## License

MIT License
