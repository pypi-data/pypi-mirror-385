# Clipboard MCP Server

A Model Context Protocol (MCP) server that provides system clipboard read and write capabilities for AI assistants like Claude.

## Features

- **read_clipboard**: Read text content from the system clipboard
- **write_clipboard**: Write text content to the system clipboard
- Cross-platform support (Linux, macOS, Windows, WSL)
- Lightweight with minimal dependencies

## Installation

### Option 1: pip (Recommended)

```bash
pip install clipboard-mcp
```

*Consider using a virtual environment to avoid dependency conflicts:*
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install clipboard-mcp
```

### Option 2: uv (Lightweight, for trying it out)

Run directly with uv (no pip installation required):

```bash
# One-time execution
uv run --from clipboard-mcp clipboard-mcp

# Or clone and run from source
git clone https://github.com/gabiteodoru/clipboard-mcp.git
cd clipboard-mcp
uv run clipboard-mcp
```

### Option 3: From Source

```bash
git clone https://github.com/gabiteodoru/clipboard-mcp.git
cd clipboard-mcp
pip install -e .
```

### Platform-Specific Setup

The installation will display instructions for your platform. Here's what you need:

#### Linux (X11)
Install clipboard utilities:
```bash
sudo apt install xclip xsel
```

For other distributions:
```bash
# Fedora/RHEL
sudo dnf install xclip xsel

# Arch Linux
sudo pacman -S xclip xsel
```

#### Linux (Wayland)
```bash
sudo apt install wl-clipboard
```

#### macOS
No additional dependencies needed - uses built-in `pbcopy`/`pbpaste`.

#### Windows/WSL
No additional dependencies needed - uses built-in `clip.exe` and PowerShell.

## Usage

### With Claude CLI

After pip installation:
```bash
claude mcp add --scope user clipboard-mcp clipboard-mcp
```

With uv (no installation):
```bash
claude mcp add --scope user clipboard-mcp "uv run --from clipboard-mcp clipboard-mcp"
```

Or from source directory:
```bash
claude mcp add --scope user clipboard-mcp "uv run /path/to/clipboard-mcp"
```

### With Claude Desktop

Add to your Claude Desktop configuration file.

**Configuration file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**After pip installation:**
```json
{
  "mcpServers": {
    "clipboard": {
      "command": "clipboard-mcp"
    }
  }
}
```

**With uv (no installation):**
```json
{
  "mcpServers": {
    "clipboard": {
      "command": "uv",
      "args": [
        "run",
        "--from",
        "clipboard-mcp",
        "clipboard-mcp"
      ]
    }
  }
}
```

**From source directory:**
```json
{
  "mcpServers": {
    "clipboard": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/clipboard-mcp",
        "run",
        "clipboard-mcp"
      ]
    }
  }
}
```

### Available Tools

Once configured, Claude will have access to these tools:

- **read_clipboard()** - Reads the current clipboard content
- **write_clipboard(text)** - Writes text to the clipboard

### Example Interactions

With this MCP server running, you can ask Claude to:

- "Read what's in my clipboard"
- "Copy this code snippet to my clipboard"
- "Save this output to my clipboard so I can paste it elsewhere"

## How It Works

This MCP server uses the [pyperclip](https://github.com/asweigart/pyperclip) library to interact with your system clipboard. It provides a secure bridge between Claude and your clipboard through the Model Context Protocol.

## Troubleshooting

### Linux: "Failed to read clipboard" errors

**Problem**: Missing system clipboard utilities

**Solution**: Install the required tools:
```bash
# For X11
sudo apt install xclip xsel

# For Wayland
sudo apt install wl-clipboard

# Or use PyQt5 as fallback (larger dependency)
pip install PyQt5
```

### Linux: Running in a headless environment

**Problem**: No display server available (e.g., SSH session, Docker)

**Solution**: Clipboard operations require a display server. For headless environments, consider:
- Using X11 forwarding: `ssh -X user@host`
- Running a virtual display with Xvfb
- Using alternative data transfer methods

### Verification

Test the installation manually:

```bash
# Test reading clipboard (copy something first)
python -c "import pyperclip; print(pyperclip.paste())"

# Test writing to clipboard
python -c "import pyperclip; pyperclip.copy('Hello from Python')"
```

### Getting Help

If you encounter issues:
1. Check that dependencies are installed for your platform
2. Verify pyperclip works independently (see verification above)
3. [Open an issue](https://github.com/gabiteodoru/clipboard-mcp/issues) with details about your platform and error messages

## Requirements

- Python 3.8 or higher
- [mcp](https://pypi.org/project/mcp/) - Model Context Protocol SDK
- [pyperclip](https://pypi.org/project/pyperclip/) - Cross-platform clipboard library

### Platform-Specific Requirements

| Platform | Requirements | Status |
|----------|-------------|--------|
| macOS | Built-in (pbcopy/pbpaste) | ✅ No setup needed |
| Windows | Built-in (clip.exe, PowerShell) | ✅ No setup needed |
| Linux X11 | xclip or xsel | ⚠️ Manual install required |
| Linux Wayland | wl-clipboard | ⚠️ Manual install required |
| WSL | Windows clipboard tools | ✅ Usually pre-installed |

## Security & Privacy

- This server only accesses clipboard content when explicitly requested by Claude
- No clipboard data is stored or transmitted except when you ask Claude to read/write
- All operations are local to your machine

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [GitHub Repository](https://github.com/gabiteodoru/clipboard-mcp)
- [Issue Tracker](https://github.com/gabiteodoru/clipboard-mcp/issues)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
