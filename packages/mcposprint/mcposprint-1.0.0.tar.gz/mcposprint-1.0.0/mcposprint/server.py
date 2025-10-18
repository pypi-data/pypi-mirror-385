
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP, Context
from mcposprint import TaskCardPrinter, Config, __version__
from pathlib import Path
import json
import os
import logging
from mcp import types

# Configure file-based logging
log_file = os.getenv("MCPOSPRINT_LOG_FILE", os.path.expanduser("~/Library/Logs/mcposprint.log"))
log_level = os.getenv("MCPOSPRINT_LOG_LEVEL", "INFO").upper()

# Ensure log directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Configure logging - NO stdout/stderr output
logging.basicConfig(
    filename=log_file,
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger('mcposprint')

mcp = FastMCP(f"MCPOSprint v{__version__}")

@mcp.tool()
def todo_list_cards_from_markdown(file: str, no_print: bool = False) -> list[str]:
    """Generate and optionally print task cards from a markdown file.
    
    Parses a markdown file with task lists (using ## headers and - bullets), generates
    PNG images for each section, and optionally sends them to your thermal printer.
    Priority tasks marked with * get a star symbol.
    
    Args:
        file: Path to markdown file (relative to current directory)
        no_print: If True, only generate images without printing (default: False)
        
    Returns:
        List of generated PNG file paths
        
    Example markdown format:
        ## Morning Tasks
        - *Get dressed (priority)
        - Brush teeth
        - Make coffee
    """
    try:
        config = Config()
        config_errors = config.validate()
        if config_errors:
            logger.warning(f"Configuration issues detected: {config_errors}")
        
        printer = TaskCardPrinter(config)  # No ctx for non-async functions
        print_cards = not no_print
        generated_files = printer.process_static_cards(file, print_cards=print_cards)
        return generated_files
    except Exception as e:
        logger.error(f"Error in todo_list_cards_from_markdown: {e}")
        raise ValueError(f"Failed to process markdown cards: {e}")

@mcp.tool()
async def task_cards_from_notion(no_print: bool = False, ctx: Context = None) -> list[str]:
    """Fetch today's tasks from Notion and generate thermal printer cards with QR codes.
    
    Connects to your Notion database, retrieves tasks with status "Today" or "In Progress", generates individual 
    task cards with QR codes linking back to Notion, and optionally prints them.
    Provides real-time progress updates to prevent client timeouts.
    
    Requires NOTION_API_KEY and TASKS_DATABASE_ID environment variables.
    
    Args:
        no_print: If True, only generate images without printing (default: False)
        
    Returns:
        List of generated PNG file paths
        
    Progress tracking includes:
        - API connection status
        - Task fetching progress
        - Individual card generation
        - Print success/failure for each card
    """
    config = Config()
    if not config.has_notion_config:
        raise ValueError("Notion not configured. Run --setup to create configuration files.")
    
    if ctx:
        ctx.info("Initializing Notion task processing...")
    
    printer = TaskCardPrinter(config, ctx)
    print_cards = not no_print
    
    try:
        if ctx:
            ctx.info("Fetching tasks from Notion API...")
        
        # Get tasks from Notion
        from mcposprint.parsers.notion import NotionParser
        notion_parser = NotionParser(config)
        tasks = notion_parser.get_todays_tasks()
        
        if ctx:
            ctx.info(f"✅ API Success: Found {len(tasks)} tasks")
            if len(tasks) == 0:
                ctx.info("No tasks found for today")
                return []
        
        generated_files = []
        
        # Process each task with progress reporting
        for i, task in enumerate(tasks):
            if ctx:
                await ctx.report_progress(i, len(tasks))
                ctx.info(f"Processing task {i+1}/{len(tasks)}: {task.get('title', 'Unknown')}")
            
            # Generate card for this task
            from mcposprint.generators.card import CardGenerator
            card_gen = CardGenerator(config)
            image = card_gen.create_notion_card_image(task)
            
            # Save the image
            import os
            output_dir = Path(config.output_dir)
            output_dir.mkdir(exist_ok=True)
            image_path = output_dir / f"notion_task_{i+1:02d}.png"
            image.save(image_path)
            generated_files.append(str(image_path))
            
            if ctx:
                ctx.info(f"✅ Generated: {image_path}")
            
            # Print if requested
            if print_cards:
                try:
                    from PIL import Image
                    img = Image.open(image_path)
                    is_last = (i == len(tasks) - 1)
                    success = printer.printer.print_image(img, cut_after=True, is_last_card=is_last)
                    
                    if ctx:
                        if success:
                            ctx.info(f"✅ Print Success: {task.get('title', 'Unknown')}")
                        else:
                            ctx.info(f"❌ Print Failed: {task.get('title', 'Unknown')}")
                except Exception as e:
                    if ctx:
                        ctx.info(f"❌ Print Error: {task.get('title', 'Unknown')} - {str(e)}")
        
        if ctx:
            ctx.info(f"✅ Processing complete: {len(generated_files)} cards generated")
            if print_cards:
                ctx.info("All cards sent to printer")
        
        return generated_files
        
    except Exception as e:
        if ctx:
            ctx.info(f"❌ Error: {str(e)}")
        raise

@mcp.tool()
def print_only(directory: str) -> str:
    """Send existing image files to the thermal printer without regenerating them.
    
    Scans a directory for PNG/JPG image files and sends them directly to your 
    thermal printer. Useful for reprinting previously generated cards or printing
    custom images you've created.
    
    Args:
        directory: Path to directory containing image files
        
    Returns:
        Success message with count of printed images
        
    Supported formats: PNG, JPG, JPEG
    Images are printed in alphabetical order with automatic paper cutting.
    """
    import glob
    config = Config()
    printer = TaskCardPrinter(config)
    print_dir = Path(directory)
    if not print_dir.exists():
        return f"Directory not found: {directory}"
    
    image_files = []
    for pattern in ['*.png', '*.jpg', '*.jpeg']:
        image_files.extend(glob.glob(str(print_dir / pattern)))
    
    if not image_files:
        return f"No image files found in: {directory}"
    
    image_files.sort()
    
    success_count = 0
    for i, image_file in enumerate(image_files):
        from PIL import Image
        try:
            img = Image.open(image_file)
            is_last = (i == len(image_files) - 1)
            success = printer.printer.print_image(img, cut_after=True, is_last_card=is_last)
            if success:
                success_count += 1
        except Exception as e:
            return f"Error printing {Path(image_file).name}: {e}"
            
    return f"Successfully printed {success_count}/{len(image_files)} images"

@mcp.tool()
def test_printer_connection() -> str:
    """Verify that your thermal printer is connected and responding.
    
    Attempts to establish a USB connection to your ESC/POS thermal printer
    and sends a basic test command. Use this to troubleshoot connection
    issues before printing actual content.
    
    Returns:
        Success/failure message with connection status
        
    Checks:
        - USB device detection
        - ESC/POS command response
        - Printer initialization
        
    If this fails, check:
        - Printer is powered on
        - USB cable is connected
        - PRINTER_NAME environment variable matches your device
        - libusb is installed on your system
    """
    config = Config()
    printer = TaskCardPrinter(config)
    success = printer.test_printer_connection()
    return "Printer connection successful" if success else "Printer connection failed"

@mcp.tool()
def run_diagnostics() -> dict:
    """Perform comprehensive system diagnostics for MCPOSprint setup.
    
    Runs a complete health check of your MCPOSprint installation, including
    configuration validation, printer connectivity, Notion API access, and
    system dependencies. Essential for troubleshooting setup issues.
    
    Returns:
        Detailed diagnostic report as JSON object
        
    Diagnostic checks include:
        - Environment variable configuration
        - Printer detection and connection
        - Notion API authentication and database access
        - Python package dependencies
        - Output directory permissions
        - System library availability (libusb, PIL, etc.)
        
    Use this when:
        - Setting up MCPOSprint for the first time
        - Troubleshooting printing or Notion connection issues
        - Verifying configuration after changes
    """
    config = Config()
    printer = TaskCardPrinter(config)
    diagnostics = printer.run_diagnostics()
    return diagnostics

@mcp.tool()
def info() -> dict:
    """Get MCPOSprint server information and system status.
    
    Returns version, dependency status, configuration issues, and operational health.
    Essential for troubleshooting and verifying proper setup.
    
    Returns:
        System information including version, dependencies, and configuration status
        
    Checks include:
        - Server version and build information
        - Required system dependencies (libusb, PIL, etc.)
        - Environment variable configuration
        - Log file accessibility
        - Basic printer connectivity
    """
    import sys
    import platform
    
    info_data = {
        "version": __version__,
        "server_name": f"MCPOSprint v{__version__}",
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependencies": {},
        "configuration": {},
        "log_file": log_file,
        "log_level": log_level
    }
    
    # Check dependencies
    try:
        import PIL
        info_data["dependencies"]["PIL"] = f"✅ {PIL.__version__}"
    except ImportError:
        info_data["dependencies"]["PIL"] = "❌ Not found"
    
    try:
        import escpos
        info_data["dependencies"]["python-escpos"] = "✅ Available"
    except ImportError:
        info_data["dependencies"]["python-escpos"] = "❌ Not found"
    
    try:
        import usb
        info_data["dependencies"]["pyusb"] = "✅ Available"
    except ImportError:
        info_data["dependencies"]["pyusb"] = "❌ Not found"
    
    # Check configuration
    config = Config()
    config_errors = config.validate()
    info_data["configuration"]["errors"] = config_errors
    info_data["configuration"]["notion_configured"] = config.has_notion_config
    info_data["configuration"]["output_dir"] = config.output_dir
    info_data["configuration"]["printer_name"] = config.printer_name
    
    # Check log file accessibility
    try:
        with open(log_file, 'a') as f:
            f.write(f"# Info check at {json.dumps({'timestamp': str(__import__('datetime').datetime.now())})}\n")
        info_data["log_status"] = "✅ Accessible"
    except Exception as e:
        info_data["log_status"] = f"❌ Error: {e}"
    
    return info_data

@mcp.tool()
def create_sample_files() -> str:
    """Generate a sample markdown file to test MCPOSprint functionality.
    
    Creates 'sample_cards.md' in the current directory with example task lists
    formatted for MCPOSprint. Perfect for testing your setup or learning
    the markdown format before creating your own task lists.
    
    Returns:
        Success message confirming file creation
        
    Generated file includes:
        - Multiple task sections (Morning, Work, Evening)
        - Examples of priority tasks (marked with *)
        - Proper formatting with ## headers and - bullets
        
    Use the generated file with process_static_cards tool to test printing.
    Configuration is handled via environment variables in your MCP client.
    """
    config = Config()
    printer = TaskCardPrinter(config)
    printer.create_sample_files()
    return "Sample markdown file created"

@mcp.resource("image://thermal-card-size")
def get_thermal_card_size() -> types.Resource:
    """Get detailed thermal printer card size specifications and constraints.
    
    Provides comprehensive technical specifications for designing images that will
    print correctly on ESC/POS thermal printers. Essential reference for custom
    image creation or understanding MCPOSprint's card generation parameters.
    """
    specs = {
        "width": {
            "pixels": 384,
            "mm": 48,
            "constraint": "fixed",
            "description": "Determined by thermal paper roll width"
        },
        "length": {
            "constraint": "unlimited", 
            "typical_range": [200, 600],
            "description": "Controls paper feed length - minimize for efficiency"
        },
        "dpi": 203,
        "dots_per_mm": 8,
        "format": "PNG",
        "color_mode": "monochrome",
        "margins": {
            "recommended": 8,
            "unit": "pixels",
            "all_sides": True
        },
        "notes": [
            "Length determines paper consumption",
            "Width cannot exceed hardware limit", 
            "ESC/POS commands control cutting and feeding"
        ]
    }
    
    return types.Resource(
        uri="image://thermal-card-size",
        name="Thermal Printer Card Specifications",
        mimeType="application/json",
        text=json.dumps(specs, indent=2)
    )
def main():
    """Entry point for script execution"""
    try:
        logger.info(f"Starting MCPOSprint v{__version__}")
        mcp.run()
    except Exception as e:
        logger.error(f"Fatal error in MCPOSprint server: {e}")
        raise
    finally:
        # Ensure all log messages are written
        for handler in logger.handlers:
            handler.flush()
        logging.shutdown()

if __name__ == "__main__":
    main()
