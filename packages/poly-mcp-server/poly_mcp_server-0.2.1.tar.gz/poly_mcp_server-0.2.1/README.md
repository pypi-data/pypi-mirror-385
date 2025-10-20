# Poly MCP Server

Version: 0.2.0

A Model Context Protocol (MCP) server providing:
- Wordit Edutem usage statistics export to Excel

## Installation

```bash
uvx poly-mcp-server@0.2.0
```

Or install locally:
```bash
uv pip install poly-mcp-server
```

## Available Tools

### wordit_edutem_usage

Export Wordit Edutem usage statistics to Excel file.

**Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format (e.g., '2025-09-01')
- `end_date` (optional): End date in YYYY-MM-DD format. If omitted, uses the last day of start_date's month
- `campus_name` (optional): Campus name filter (e.g., '강남캠퍼스'). If omitted, queries all campuses
- `output_path` (optional): Excel file save path (default: ./output)

**Example:**
```json
{
  "start_date": "2025-09-01",
  "end_date": "2025-09-07",
  "campus_name": "강남캠퍼스",
  "output_path": "./output"
}
```

## Environment Variables

Required for database connection:
- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_DB`: PostgreSQL database name (required)
- `POSTGRES_USER`: PostgreSQL username (required)
- `POSTGRES_PASSWORD`: PostgreSQL password (required)

## MCP Configuration

### VSCode Settings

Add to `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "poly-mcp": {
      "command": "uvx",
      "args": ["poly-mcp-server@0.2.0"],
      "env": {
        "POSTGRES_HOST": "your-host",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "your-db",
        "POSTGRES_USER": "your-user",
        "POSTGRES_PASSWORD": "your-password"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

#### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

#### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Linux
Location: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "poly-mcp": {
      "command": "uvx",
      "args": ["poly-mcp-server@0.2.0"],
      "env": {
        "POSTGRES_HOST": "your-host",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "your-db",
        "POSTGRES_USER": "your-user",
        "POSTGRES_PASSWORD": "your-password"
      }
    }
  }
}
```

## Development

### Local Setup

```bash
git clone <repository-url>
cd poly-mcp-server

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=poly_mcp_server
```

### Run Server

```bash
# Using uv
uv run poly-mcp-server

# Or as Python module
uv run python -m poly_mcp_server.server

# Show help
uv run poly-mcp-server --help
```

## License

MIT

## Contributing

Bug reports and feature requests are welcome via GitHub Issues.
