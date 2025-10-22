# UVX Installation Guide

## What is UVX?

UVX is a tool for running Python applications in isolated environments without manual installation. It's perfect for running MCP servers like Excel MCP Server.

## Prerequisites

- Python 3.9 or higher
- `uvx` installed (comes with `uv`)

### Installing UV/UVX

```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation Methods

### Method 1: Install from PyPI (Recommended)

Once the package is published to PyPI, you can install it directly:

```bash
uvx mcp-excel-supabase
```

This will:
- Download the package from PyPI
- Create an isolated environment
- Install all dependencies
- Make the `mcp-excel-supabase` command available

### Method 2: Install from GitHub

Install directly from the GitHub repository:

```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

This is useful for:
- Testing the latest development version
- Installing before PyPI publication
- Using a specific branch or commit

### Method 3: Install from Local Directory

For development or testing:

```bash
# Navigate to the project directory
cd /path/to/excel-mcp

# Install from local directory
uvx --from . mcp-excel-supabase
```

## Configuration

### Environment Variables

Create a `.env` file in your working directory:

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:

```env
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-service-role-key-here
```

Optional variables:

```env
DEFAULT_BUCKET=your-bucket-name
LOG_LEVEL=INFO
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**Location**:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:

```json
{
  "mcpServers": {
    "excel-supabase": {
      "command": "uvx",
      "args": ["mcp-excel-supabase"],
      "env": {
        "SUPABASE_URL": "https://yourproject.supabase.co",
        "SUPABASE_KEY": "your-service-role-key-here",
        "DEFAULT_BUCKET": "your-bucket-name",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Alternative (using .env file)**:

```json
{
  "mcpServers": {
    "excel-supabase": {
      "command": "uvx",
      "args": ["mcp-excel-supabase"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

This assumes you have a `.env` file in the specified `cwd` directory.

## Verification

### Test the Installation

```bash
# Run the server (it will start and wait for MCP connections)
uvx mcp-excel-supabase
```

You should see output indicating the server has started successfully.

### Test with Claude Desktop

1. Restart Claude Desktop after updating the configuration
2. Open a new conversation
3. Try using one of the Excel tools:

```
Can you parse this Excel file for me: data/sales.xlsx
```

If configured correctly, Claude will use the Excel MCP Server to process your request.

## Troubleshooting

### Issue: "Command not found: uvx"

**Solution**: Install UV/UVX first:

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: "Package not found on PyPI"

**Solution**: Use the GitHub installation method:

```bash
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

### Issue: "Missing environment variables"

**Solution**: Ensure your `.env` file exists and contains the required variables, or pass them via Claude Desktop configuration.

### Issue: "Permission denied"

**Solution**: On Unix systems, you may need to make the script executable:

```bash
chmod +x $(which mcp-excel-supabase)
```

### Issue: "Module not found" errors

**Solution**: Clear the UVX cache and reinstall:

```bash
# Clear cache
uv cache clean

# Reinstall
uvx mcp-excel-supabase
```

## Updating

### Update to Latest Version

```bash
# From PyPI
uvx --refresh mcp-excel-supabase

# From GitHub
uvx --refresh --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

### Check Current Version

```bash
uvx mcp-excel-supabase --version
```

## Uninstallation

UVX automatically manages isolated environments. To remove the package:

```bash
# Clear the UVX cache for this package
uv cache clean mcp-excel-supabase
```

## Advanced Usage

### Running with Custom Python Version

```bash
uvx --python 3.11 mcp-excel-supabase
```

### Running with Additional Dependencies

```bash
uvx --with pandas --with numpy mcp-excel-supabase
```

### Running in Verbose Mode

```bash
uvx --verbose mcp-excel-supabase
```

## Best Practices

1. **Use Environment Variables**: Store sensitive credentials in `.env` files, not in configuration files
2. **Regular Updates**: Keep the package updated to get the latest features and security fixes
3. **Isolated Environments**: UVX automatically creates isolated environments, preventing dependency conflicts
4. **Version Pinning**: For production use, consider pinning to a specific version:

```bash
uvx mcp-excel-supabase==1.0.0
```

## Support

For issues and questions:

- GitHub Issues: https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues
- Documentation: https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/README.md

## See Also

- [API Reference](api.md)
- [Examples](examples/)
- [Troubleshooting Guide](troubleshooting.md)
- [Security Policy](../SECURITY.md)

