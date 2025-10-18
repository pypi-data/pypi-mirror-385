"""ESC/POS printer interface for direct USB thermal printer communication"""

import usb.core
import usb.util
from escpos.printer import Usb
from PIL import Image
from typing import Optional, Dict, Any, List
from ..core.config import Config

class EscposPrinter:
    """ESC/POS printer interface for direct USB thermal printer communication"""
    
    def __init__(self, config: Config, ctx=None):
        self.config = config
        self.ctx = ctx
        self.device = None
        self._connect()
    
    def _connect(self):
        """Connect to USB thermal printer"""
        try:
            self.device = self._autodetect_usb_device()
        except Exception as e:
            self._log(f"⚠️ Failed to connect to USB printer: {e}")
            self.device = None
    
    def _log(self, message: str):
        """Log message to context if available, otherwise use file logger"""
        if self.ctx:
            self.ctx.info(message)
        else:
            # Use file-based logging only - NO stdout/stderr output for MCP compatibility
            import logging
            logger = logging.getLogger('mcposprint.printer')
            logger.info(message.replace('🖨️', '').replace('📖', '').replace('✅', '').replace('❌', '').replace('⚠️', '').strip())
    
    def _get_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices using pyusb"""
        try:
            devices = []
            # Find all USB devices
            for device in usb.core.find(find_all=True):
                try:
                    # Get device info
                    vendor_id = device.idVendor
                    product_id = device.idProduct
                    
                    # Try to get manufacturer and product strings
                    manufacturer = "Unknown"
                    product = "Unknown"
                    
                    try:
                        if device.manufacturer:
                            manufacturer = device.manufacturer
                    except (ValueError, usb.core.USBError):
                        pass
                    
                    try:
                        if device.product:
                            product = device.product
                    except (ValueError, usb.core.USBError):
                        pass
                    
                    description = f"{manufacturer} {product}".strip()
                    
                    devices.append({
                        'vendor_id': vendor_id,
                        'product_id': product_id,
                        'description': description,
                        'manufacturer': manufacturer,
                        'product': product
                    })
                    
                except (ValueError, usb.core.USBError):
                    # Skip devices we can't access
                    continue
            
            return devices
        except Exception as e:
            self._log(f"⚠️ Error listing USB devices: {e}")
            return []
    
    def _autodetect_usb_device(self):
        """Auto-detect USB thermal printer device"""
        devices = self._get_usb_devices()
        if not devices:
            raise RuntimeError("No USB devices found. Make sure USB printer is connected and you have permission to access USB devices.")

        # Common thermal printer vendor IDs
        thermal_vendors = {
            0x04b8: 'Epson',
            0x1504: 'Bixolon', 
            0x0519: 'Star Micronics',
            0x2730: 'Citizen',
            0x0483: 'STMicroelectronics',
            0x154f: 'SNBC'
        }
        
        # Look for known thermal printer vendors first
        preferred = None
        for device in devices:
            vendor_id = device['vendor_id']
            if vendor_id in thermal_vendors:
                preferred = device
                break
        
        # Fallback: look for printer-related keywords in description
        if not preferred:
            printer_keywords = ['printer', 'receipt', 'thermal', 'pos', 'epson', 'bixolon', 'star', 'citizen']
            for device in devices:
                description_lower = device['description'].lower()
                if any(keyword in description_lower for keyword in printer_keywords):
                    preferred = device
                    break
        
        # Last resort: use first device (not recommended but better than failing)
        selected = preferred or devices[0]
        
        vendor_name = thermal_vendors.get(selected['vendor_id'], selected['manufacturer'])
        self._log(f"🖨️ Connecting to printer: {vendor_name} ({hex(selected['vendor_id'])}:{hex(selected['product_id'])})")
        self._log(f"   Description: {selected['description']}")
        
        return Usb(selected['vendor_id'], selected['product_id'])
    
    def print_image(self, image: Image.Image, cut_after: bool = True, is_last_card: bool = False) -> bool:
        """Print PIL image to ESC/POS thermal printer"""
        if not self.device:
            self._log("❌ No printer device connected")
            return False
        
        try:
            # Convert to 1-bit black and white for thermal printing
            bw_img = image.convert("1")
            
            # Print the image
            self.device.image(bw_img)
            
            # Add some spacing and cut if requested
            if cut_after:
                # Add minimal line feeds before cutting
                self.device.text("\n\n")
                cut_mode = 'FULL' if is_last_card else 'PART'
                self.device.cut(mode=cut_mode)
            
            self._log("✓ Printed card successfully")
            return True
            
        except Exception as e:
            self._log(f"❌ ESC/POS print failed: {e}")
            return False
    
    def print_text_and_qr(self, text: str, qr_data: Optional[str] = None) -> bool:
        """Print text and optional QR code"""
        if not self.device:
            self._log("❌ No printer device connected")
            return False
        
        try:
            # Print text
            self.device.text(text + "\n")
            
            # Print QR code if provided
            if qr_data:
                self.device.qr(qr_data, size=6, model=2)
            
            # Cut paper
            self.device.cut()
            return True
            
        except Exception as e:
            self._log(f"❌ ESC/POS text/QR print failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test ESC/POS printer connection"""
        self._log("🔧 Testing ESC/POS printer connection...")
        
        if not self.device:
            self._log("❌ No printer device connected")
            return False
        
        try:
            self.device.text("Task Card Printer Test\nESC/POS connection successful!\n")
            self.device.cut()
            self._log("✅ ESC/POS test print successful!")
            return True
            
        except Exception as e:
            self._log(f"❌ ESC/POS test failed: {e}")
            return False
    
    def get_printer_status(self) -> Dict[str, Any]:
        """Get ESC/POS printer status information"""
        status = {
            'usb_device_found': self.device is not None,
            'printer_exists': self.device is not None,
            'printer_ready': self.device is not None,
            'print_command': 'escpos',
            'printer_type': 'usb',
            'error_messages': []
        }
        
        if not self.device:
            status['error_messages'].append("No USB printer device connected")
        
        # Try to list available USB devices for troubleshooting
        try:
            devices = self._get_usb_devices()
            if not devices:
                status['error_messages'].append("No USB devices found")
            else:
                self._log(f"📋 Found {len(devices)} USB device(s):")
                for i, device in enumerate(devices):
                    manufacturer = device.get('manufacturer', 'Unknown')
                    self._log(f"  {i+1}. {manufacturer} ({hex(device['vendor_id'])}:{hex(device['product_id'])}) - {device['description']}")
        except Exception as e:
            status['error_messages'].append(f"Failed to list USB devices: {e}")
        
        return status 