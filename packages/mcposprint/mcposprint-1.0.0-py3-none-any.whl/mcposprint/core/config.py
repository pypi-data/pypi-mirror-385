"""Configuration management for MCPOSprint"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Configuration class for MCPOSprint application"""
    
    # Printer configuration
    printer_name: str = os.getenv("PRINTER_NAME", "EPSON_TM_T20III-17")
    
    # Notion configuration
    notion_api_key: Optional[str] = os.getenv("NOTION_API_KEY")
    tasks_database_id: Optional[str] = os.getenv("TASKS_DATABASE_ID")
    
    # Card dimensions (optimized for 58mm thermal printers)
    # 58mm = ~580 pixels at 254 DPI (thermal printer resolution)
    # Can be overridden with CARD_WIDTH and CARD_HEIGHT environment variables
    card_width: int = int(os.getenv("CARD_WIDTH", "580"))
    card_height: int = int(os.getenv("CARD_HEIGHT", "580"))
    border_width: int = 4
    title_height: int = 80
    checkbox_size: int = 28
    task_margin: int = 8
    ring_hole_size: int = 12
    
    # Font configuration (scaled up for larger cards)
    title_font_size: int = int(28 * 1.2 * 1.4)  # 20% bigger + 40% more = 47px
    task_font_size: int = int(32 * 1.3 * 1.4)   # 30% bigger + 40% more = 58px
    
    # Application settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    output_dir: str = os.getenv("OUTPUT_DIR", os.path.expanduser("~/mcposprint-images"))
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    @property
    def has_notion_config(self) -> bool:
        """Check if Notion configuration is complete"""
        return bool(self.notion_api_key and self.tasks_database_id)
    
    @property
    def notion_headers(self) -> dict:
        """Get Notion API headers"""
        if not self.notion_api_key:
            raise ValueError("Notion API key not configured")
        
        return {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.printer_name:
            errors.append("PRINTER_NAME not configured")
        
        if self.card_width <= 0 or self.card_height <= 0:
            errors.append("Invalid card dimensions")
        
        return errors 