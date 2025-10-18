"""
MCPOSprint - MCP Server for Thermal Printer Task Card Generation

A modular MCP server for generating and printing task cards from markdown and Notion.
Optimized for thermal printers with direct USB ESC/POS printing.
"""

__version__ = "1.0.0"
__author__ = "MCPOSprint Team"

from .core.config import Config
from .core.printer import TaskCardPrinter
from .parsers.markdown import MarkdownParser
from .parsers.notion import NotionParser
from .generators.card import CardGenerator
from .printers.escpos_printer import EscposPrinter

__all__ = [
    'Config',
    'TaskCardPrinter', 
    'MarkdownParser',
    'NotionParser',
    'CardGenerator',
    'EscposPrinter'
] 