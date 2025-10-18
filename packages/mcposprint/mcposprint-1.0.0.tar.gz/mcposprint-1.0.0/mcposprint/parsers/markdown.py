"""Markdown parser for static task cards"""

from typing import List, Dict, Any
from pathlib import Path

class MarkdownParser:
    """Parser for markdown task card files"""
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse markdown file and return list of card data"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into card data structure"""
        lines = content.split('\n')
        cards = []
        current_card = None
        
        for line in lines:
            trimmed = line.strip()
            
            # Skip empty lines
            if not trimmed:
                continue
            
            # Check for card header (## format)
            if trimmed.startswith('## '):
                if current_card:
                    cards.append(current_card)
                current_card = {
                    'title': trimmed[3:].strip(),
                    'tasks': []
                }
            # Check for task items (- format)
            elif trimmed.startswith('- ') and current_card:
                task_text = trimmed[2:].strip()
                is_priority = False
                
                # Check if task starts with * (priority marker)
                if task_text.startswith('*'):
                    is_priority = True
                    task_text = task_text[1:].strip()
                
                current_card['tasks'].append({
                    'text': task_text,
                    'priority': is_priority
                })
        
        # Add the last card
        if current_card:
            cards.append(current_card)
        
        return cards
    
    @staticmethod
    def create_sample_markdown() -> str:
        """Create sample markdown content for testing"""
        return """## Morning Routine
- *Get dressed
- Brush teeth
- Make coffee
- Check calendar

## Work Tasks
- *Review emails
- Update project status
- *Prepare for 2pm meeting
- Submit timesheet

## Evening Tasks
- Grocery shopping
- *Take medication
- Plan tomorrow
- Read for 30 minutes""" 