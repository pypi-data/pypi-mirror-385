# MCPOSprint - MCP Server for ESC/POS Printing over USB

Hi! This escalated quickly and became a whole thing. Full disclosure, AI helped me write a lot of this code, but I've tested it pretty throughly on a mac to confirm it works. 

This is a uv based MCP that lets you connect an MCP client to a usb connected ESC/POS printer. It has baked in tools for printing your tasks from notion with QR codes, and a template to print out markdown tasklists, as well as a generic print image tool you can use to print arbitrary images. I've only tested it with an EPSON_TM_T20III-17, so YMMV with other ESC/POS printers. 

## 🚀 Installation

MCPOSprint runs directly via `uvx`.

### Prerequisites - Install these first
- **Python 3.10+**
- **UV package manager**: Install from [astral.sh/uv](https://astral.sh/uv)
- **Thermal printer** : ESC/POS compatible USB printer
- **Notion API Token** (optional): If you want to print tasks from Notion. [You can see how to generate a token in Notion's docs](https://developers.notion.com/docs/authorization#set-up-the-auth-flow-for-a-public-integration)
- **libusb** for USB printer access
  - macOS: `brew install libusb`
  - Ubuntu/Debian: `sudo apt install libusb-1.0-0-dev`

## Getting Started

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Configure Your MCP Client** with MCPOSprint (see configuration section below)


## 🎯 MCP Client Setup

#### Minimal Configuration (Recommended)

You can add this to the mcp config file of whatever client you use

For most users, just configure your Notion credentials if you want them:

```json
{
  "mcpServers": {
    "mcposprint": {
      "command": "uvx",
      "args": ["mcposprint"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "NOTION_API_KEY": "your_notion_api_key_here",
        "TASKS_DATABASE_ID": "your_database_id_here"
      }
    }
  }
}
```

**Default settings used:**
- **OUTPUT_DIR**: `./images` (saved relative to Claude Desktop's working directory)
- **PRINTER_NAME**: `EPSON_TM_T20III-17`
- **CARD_WIDTH/HEIGHT**: `580` pixels (optimized for 58mm thermal printers)

#### Full Configuration (Advanced)

If you need to override defaults:

```json
{
  "mcpServers": {
    "mcposprint": {
      "command": "uvx", 
      "args": ["mcposprint"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "OUTPUT_DIR": "./my-custom-images",
        "PRINTER_NAME": "YOUR_PRINTER_NAME",
        "CARD_WIDTH": "580",
        "CARD_HEIGHT": "580", 
        "NOTION_API_KEY": "your_notion_api_key_here",
        "TASKS_DATABASE_ID": "your_database_id_here",
        "DEBUG": "false"
      }
    }
  }
}
```

**Configuration Notes:**
- **PATH**: Adjust for your system (macOS Homebrew path shown)
- **OUTPUT_DIR**: Where images are saved (relative to Claude Desktop's working directory)
- **PRINTER_NAME**: Use your actual thermal printer name
- **Notion credentials**: Optional - only needed for Notion integration

### Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OUTPUT_DIR` | `./images` | Where generated card images are saved |
| `PRINTER_NAME` | `EPSON_TM_T20III-17` | Your thermal printer name |
| `CARD_WIDTH` | `580` | Card width in pixels |
| `CARD_HEIGHT` | `580` | Card height in pixels |
| `NOTION_API_KEY` | _(none)_ | Your Notion integration API key |
| `TASKS_DATABASE_ID` | _(none)_ | Your Notion tasks database ID |
| `DEBUG` | `false` | Enable debug logging |

### Output Directory

Generated card images are saved to the `OUTPUT_DIR` (default: `./images`) relative to Claude Desktop's working directory. The directory is created automatically if it doesn't exist.

### Notion Setup

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Copy the API key to your `.env` file
3. Share your tasks database with the integration
4. Copy the database ID to your `.env` file

Database should have these properties:
- **Name** or **Task** (title)
- **Due Date** (date)
- **Priority** (select: High, Medium, Low)
- **Status** (status: Not Started, In Progress, Done)
- **Description** (rich text, optional)



### Usage with MCP Clients

Once connected, you can use these tools in your MCP client:

- **Generate cards from markdown**: Use `process_static_cards` tool
- **Fetch Notion tasks**: Use `process_notion_tasks` tool (with progress tracking)
- **Print existing images**: Use `print_only` tool
- **Test printer**: Use `test_printer_connection` tool
- **Run diagnostics**: Use `run_diagnostics` tool
- **Get printer specs**: Access `image://thermal-card-size` resource

### Markdown Format

```markdown
## Morning Routine
- *Get dressed
- Brush teeth
- Make coffee
- Check calendar

## Work Tasks
- *Review emails
- Update project status
- *Prepare for 2pm meeting
- Submit timesheet
```

- Use `## Title` for card headers
- Use `- Task` for regular tasks
- Use `- *Task` for priority tasks (marked with ★)

### Development Installation (Optional)

Only needed for contributing or customization:

```bash
# Clone the repository  
git clone https://github.com/your-username/mcposprint.git
cd mcposprint

# Install with uv
uv sync

# Start the MCP server
uv run mcposprint
```

## 🔧 MCP Tools

MCPOSprint provides 6 MCP tools for task card generation and printing:

### Available Tools

1. **`process_static_cards`** - Generate cards from markdown files
   - Parameters: `file` (string), `no_print` (boolean)
   - Returns: List of generated file paths

2. **`process_notion_tasks`** - Fetch and process Notion tasks (with progress tracking)
   - Parameters: `no_print` (boolean)
   - Returns: List of generated file paths
   - Features: Real-time progress updates via Context

3. **`print_only`** - Print existing image files from directory
   - Parameters: `directory` (string)
   - Returns: Success status message

4. **`test_printer_connection`** - Test thermal printer connectivity
   - Returns: Connection status message

5. **`run_diagnostics`** - Run comprehensive system diagnostics
   - Returns: Detailed diagnostic information

6. **`create_sample_files`** - Generate sample markdown file for testing
   - Returns: Success status message

### MCP Resources

- **`image://thermal-card-size`** - Thermal printer card specifications
  - Width: 384 pixels (48mm at 203 DPI)
  - Height: Variable (200-400 pixels)
  - Format: PNG, monochrome

## 🖨️ Printer Setup

### Supported Printers

#### AI Generated List of ESC/POS Compatible Thermal Printers
- **EPSON**: TM-T20III, TM-T88V, TM-T82, TM-T70
- **Star Micronics**: TSP143, TSP654, TSP100
- **Citizen**: CT-S310II, CT-S4000
- **Most USB thermal printers** supporting ESC/POS protocol

### Printer Setup via MCP Tools

Use the MCP tools to test and configure your printer:

```
# Test printer connection
Use: test_printer_connection

# Run full diagnostics
Use: run_diagnostics
```

## Architecture

The MCP server is modularized into clean components:

```
mcposprint/
├── core/
│   ├── config.py      # Configuration management
│   └── printer.py     # Main orchestration class
├── parsers/
│   ├── markdown.py    # Markdown file parser
│   └── notion.py      # Notion API integration
├── generators/
│   └── card.py        # PIL-based card image generation
└── printers/
    └── escpos_printer.py  # ESC/POS direct USB interface
```



## 🔍 Troubleshooting

### Common Issues

1. **Printer not found**
   - Use the `test_printer_connection` MCP tool
   - Use the `run_diagnostics` MCP tool for detailed information
   - Check USB connections and printer power

2. **Notion connection fails**
   - Use the `run_diagnostics` MCP tool to verify API configuration
   - Check that your API key is valid in `.env`
   - Verify database permissions in Notion
   - Ensure the database ID is correct

3. **MCP Server connection issues**
   - Verify the server is running: `uv run mcposprint`
   - Check your MCP client configuration
   - Ensure the working directory path is correct

### Real-time Progress Tracking

The `process_notion_tasks` tool provides real-time progress updates:
- ✅ API Success: Found X tasks
- Processing task 1/3: Task Name
- ✅ Generated: ./output/file.png
- ✅ Print Success: Task Name

This prevents client timeouts during long operations.

## Development

### Local Development
```bash
# Install in development mode with dev dependencies
uv sync --all-extras

# Run tests (when available)
pytest

# Format code
black mcposprint/
isort mcposprint/

# Type checking
mypy mcposprint/
```

### Running the MCP Server
```bash
# Start the server for development
uv run mcposprint

# Test with MCP inspector (if available)
# Connect your MCP client to localhost
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Changelog

### v1.0.0 - MCPOSprint Initial Release
- ✅ Full MCP server implementation with 6 tools
- ✅ Real-time progress tracking with Context support
- ✅ Async Notion task processing with timeout handling
- ✅ Thermal printer card generation and printing
- ✅ Static markdown card processing
- ✅ Modular architecture with clean separation
- ✅ Environment-based configuration
- ✅ ESC/POS direct USB printing support
- ✅ QR code generation for Notion tasks
- ✅ Comprehensive error handling and diagnostics
