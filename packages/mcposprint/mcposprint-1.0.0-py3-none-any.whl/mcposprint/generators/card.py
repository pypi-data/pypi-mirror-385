"""Card image generator using PIL"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List
from ..core.config import Config

class CardGenerator:
    """Generator for task card images"""
    
    def __init__(self, config: Config):
        self.config = config
        self._load_fonts()
        # Calculate proportional margins based on card size
        self.margin = max(20, self.config.card_width // 29)  # ~20px for 580px cards
        self.qr_size = int(max(192, self.config.card_width // 3) * 1.3)  # ~250px for 580px cards (30% bigger)
    
    def _load_fonts(self):
        """Load fonts with fallback to default"""
        try:
            # Reduce font sizes by 20%
            self.title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(self.config.title_font_size * 0.8))
            self.task_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(self.config.task_font_size * 0.8))
        except:
            self.title_font = ImageFont.load_default()
            self.task_font = ImageFont.load_default()
    
    def create_static_card_image(self, card_data: Dict[str, Any]) -> Image.Image:
        """Create PIL image for a static markdown task card (with header and ring hole)"""
        # Create white image with black border
        img = Image.new('RGB', (self.config.card_width, self.config.card_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw border (inset to prevent clipping)
        border_inset = self.config.border_width // 2
        draw.rectangle([border_inset, border_inset, 
                       self.config.card_width - border_inset - 1, 
                       self.config.card_height - border_inset - 1], 
                      outline='black', width=self.config.border_width)
        
        # Draw ring hole in top-left corner
        hole_x = self.margin
        hole_y = self.margin
        draw.ellipse([hole_x, hole_y, hole_x + self.config.ring_hole_size, hole_y + self.config.ring_hole_size], 
                    outline='black', width=2, fill='white')
        
        # Draw title background (black rectangle)
        title_rect = [self.config.border_width + 5, self.config.border_width + 5, 
                     self.config.card_width - self.config.border_width - 5, self.config.title_height]
        draw.rectangle(title_rect, fill='black')
        
        # Draw title text (white on black)
        self._draw_title(draw, card_data['title'])
        
        # Draw tasks
        self._draw_tasks(draw, card_data['tasks'])
        
        return img
    
    def create_notion_card_image(self, task_data: Dict[str, Any]) -> Image.Image:
        """Create PIL image for a Notion task card (no header, with QR code)"""
        # Create white image with black border
        img = Image.new('RGB', (self.config.card_width, self.config.card_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw border (inset to prevent clipping)
        border_inset = self.config.border_width // 2
        draw.rectangle([border_inset, border_inset, 
                       self.config.card_width - border_inset - 1, 
                       self.config.card_height - border_inset - 1], 
                      outline='black', width=self.config.border_width)
        
        # Load fonts with different sizes for Notion cards (proportional to card size)
        # Reduced by 20% from the original 20% bigger size
        notion_task_font_size = int(max(20, self.config.card_width // 29) * 3.9 * 0.8)  # 20% smaller ~75px for 580px cards
        notion_title_font_size = int(max(16, self.config.card_width // 36) * 3.6 * 0.8)  # 20% smaller ~54px for 580px cards
        
        try:
            task_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", notion_task_font_size)
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", notion_title_font_size)
        except:
            task_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw QR code in bottom-left corner (if QR data provided)
        qr_x = self.margin
        qr_y = self.config.card_height - self.qr_size - self.margin
        
        if task_data.get('qr_data'):
            qr_img = self._generate_qr_code(task_data['qr_data'])
            if qr_img:
                # Resize QR code to fit
                qr_img = qr_img.resize((self.qr_size, self.qr_size), Image.Resampling.LANCZOS)
                img.paste(qr_img, (qr_x, qr_y))
        
        # Draw task title (no header background) with improved wrapping
        title_text = task_data.get('title', 'Untitled Task')
        title_x = self.margin
        title_y = self.margin
        
        # Smart text wrapping based on actual text measurement
        def wrap_text(text, font, max_width):
            """Wrap text based on actual pixel width measurement"""
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Word is too long, force it anyway
                        lines.append(word)
                        current_line = ""
            
            if current_line:
                lines.append(current_line)
            
            return lines
        
        # Wrap title text (leave some margin on right)
        max_title_width = self.config.card_width - (2 * self.margin)  # margins on each side
        title_lines = wrap_text(title_text, title_font, max_title_width)
        
        # Draw wrapped title (max 3 lines with smaller text)
        line_height = max(68, self.config.card_width // 9)  # ~68px for 580px cards (smaller for 20% smaller text)
        for i, line in enumerate(title_lines[:3]):  # Allow up to 3 lines
            draw.text((title_x, title_y + i * line_height), line, fill='black', font=title_font)
        
        # Add ellipsis if title was truncated
        if len(title_lines) > 3:
            # Replace last few characters of 3rd line with ellipsis
            last_line = title_lines[2]
            if len(last_line) > 3:
                truncated_line = last_line[:-3] + "..."
                draw.text((title_x, title_y + 2 * line_height), truncated_line, fill='black', font=title_font)
        
        spacing = max(20, self.config.card_width // 29)  # ~20px for 580px cards (less spacing for smaller text)
        y_pos = title_y + min(len(title_lines), 3) * line_height + spacing
        
        # Draw due date if provided
        if task_data.get('due_date'):
            due_text = f"Due: {task_data['due_date']}"
            draw.text((title_x, y_pos), due_text, fill='red', font=task_font)
            y_pos += max(88, self.config.card_width // 7)  # ~88px for 580px cards (less spacing for smaller text)
        
        # Draw description/content if provided (leave space for QR code at bottom)
        if task_data.get('content'):
            content_text = task_data['content']
            max_chars = 45  # Increased from 35 since text is smaller
            
            if len(content_text) > max_chars:
                words = content_text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if len(test_line) <= max_chars:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # Draw wrapped content (leave space for QR code at bottom)
                content_line_height = max(88, self.config.card_width // 7)  # ~88px for 580px cards (smaller for 20% smaller text)
                qr_margin = max(60, self.config.card_width // 10)  # ~60px for 580px cards (more margin for bigger QR)
                
                for i, line in enumerate(lines[:4]):  # Allow up to 4 lines for content with smaller text
                    if y_pos > self.config.card_height - self.qr_size - qr_margin:  # Stop before QR code area
                        break
                    draw.text((title_x, y_pos + i * content_line_height), line, fill='black', font=task_font)
                    y_pos += content_line_height
            else:
                if y_pos < self.config.card_height - self.qr_size - qr_margin:  # Only draw if there's space above QR
                    draw.text((title_x, y_pos), content_text, fill='black', font=task_font)
        
        return img
    
    def _draw_title(self, draw: ImageDraw.Draw, title: str):
        """Draw title text with word wrapping"""
        # Handle long titles by wrapping
        if len(title) > 35:  # Increased from 30 since text is smaller
            words = title.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= 35:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw wrapped title
            y_offset = 0
            title_line_spacing = max(28, self.config.card_width // 21)  # ~28px for 580px cards (less spacing for smaller text)
            for i, line in enumerate(lines[:3]):  # Allow up to 3 lines
                bbox = draw.textbbox((0, 0), line, font=self.title_font)
                text_width = bbox[2] - bbox[0]
                text_x = (self.config.card_width - text_width) // 2
                text_y = self.config.border_width + max(12, self.config.card_width // 48) + y_offset
                draw.text((text_x, text_y), line, fill='white', font=self.title_font)
                y_offset += title_line_spacing
        else:
            # Single line title
            bbox = draw.textbbox((0, 0), title, font=self.title_font)
            text_width = bbox[2] - bbox[0]
            text_x = (self.config.card_width - text_width) // 2
            text_y = self.config.border_width + max(12, self.config.card_width // 48)  # Consistent with wrapped titles
            draw.text((text_x, text_y), title, fill='white', font=self.title_font)
    
    def _draw_tasks(self, draw: ImageDraw.Draw, tasks: List[Dict[str, Any]]):
        """Draw task list with checkboxes"""
        y_pos = self.config.title_height + self.margin * 2  # Extra margin after title
        
        # Sort tasks: priority first
        sorted_tasks = sorted(tasks, key=lambda x: not x['priority'])
        
        for task in sorted_tasks:
            if y_pos > self.config.card_height - max(60, self.config.card_width // 10):  # More space at bottom
                break
            
            # Draw checkbox (slightly smaller due to smaller text)
            checkbox_size = max(28, self.config.card_width // 21)  # ~28px for 580px cards (smaller for smaller text)
            checkbox_x = self.margin
            checkbox_y = y_pos
            draw.rectangle([checkbox_x, checkbox_y, 
                          checkbox_x + checkbox_size, checkbox_y + checkbox_size],
                         outline='black', width=2)
            
            # Draw task text
            task_text = task['text']
            
            # Add priority star
            if task['priority']:
                task_text = "★ " + task_text
            
            # Wrap text if too long
            text_margin = max(25, self.config.card_width // 23)  # ~25px for 580px cards
            wrapped_text = self._wrap_text(task_text, self.task_font, self.config.card_width - checkbox_x - checkbox_size - text_margin)
            
            text_spacing = max(15, self.config.card_width // 39)  # ~15px for 580px cards
            text_x = checkbox_x + checkbox_size + text_spacing
            text_y = checkbox_y + 2  # Align better with checkbox
            
            task_line_height = max(24, self.config.card_width // 24)  # ~24px for 580px cards (less spacing for smaller text)
            for line in wrapped_text[:3]:  # Allow up to 3 lines per task
                draw.text((text_x, text_y), line, fill='black', font=self.task_font)
                text_y += task_line_height
            
            # Adjusted spacing between tasks
            task_spacing = max(36, len(wrapped_text) * task_line_height) + task_line_height  # Adjusted spacing between tasks
            y_pos += task_spacing
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _generate_qr_code(self, url: str) -> Image.Image:
        """Generate QR code image"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=2,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            return qr.make_image(fill_color="black", back_color="white")
        except Exception as e:
            # Silently handle error - could add logging here if needed
            return None 