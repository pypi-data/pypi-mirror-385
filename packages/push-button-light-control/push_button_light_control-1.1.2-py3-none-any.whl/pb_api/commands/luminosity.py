from typing import List
from .base import BaseCommand
from ..core.protocol import PushButtonProtocol
from ..core.constants import *

class LuminosityCommand(BaseCommand):
    """
    Luminosity control commands for Push Button Light devices
    Uses percentage values (0-100) for luminosity - CORRECTED VERSION
    """
    
    def execute(self, device_id: int, led_states: int, luminosity_values: List[int]) -> bool:
        """
        Execute luminosity setting (implements abstract method)
        """
        return self.set_luminosity_values(device_id, led_states, luminosity_values)
    
    def set_luminosity_values(self, device_id: int, led_states: int, luminosity_values: List[int]) -> bool:
        """
        Set luminosity values for all LEDs (percentage 0-100) - CORRECTED VERSION
        Uses OPERATING command for luminosity (brightness)
        """
        if len(luminosity_values) != 12:
            raise ValueError("Luminosity values must contain exactly 12 values")
        if any(not (0 <= gs <= 100) for gs in luminosity_values):
            raise ValueError("Luminosity values must be between 0-100")
        
        # CORRECTION: Use OPERATING command for luminosity (brightness)
        packet = PushButtonProtocol.encode_operating_command(device_id, led_states, luminosity_values)
        response = self.device.send_command(packet)
        
        print(f"[DEBUG LUMINOSITY] Operating Command: led_states=0x{led_states:02x}, lum_values={luminosity_values}")
        print(f"[DEBUG LUMINOSITY] Response: {response}")

        # Check for success
        if response.get('type') == 'command_response':
            return response.get('response_code') == ACK_SUCCESS
        elif response.get('type') == 'operating_response':
            return True
        elif response.get('type') == 'firmware_ack':
            print(f"[WARNING] Got firmware_ack for luminosity, but continuing")
            return True
            
        print(f"[ERROR] Unexpected response for luminosity: {response.get('type')}")
        return False
    
    def set_led_luminosity(self, device_id: int, led_position: int, luminosity: int) -> bool:
        """
        Set luminosity for specific LED (percentage 0-100) - CORRECTED VERSION
        
        Args:
            device_id: Target device ID
            led_position: LED position (0-3)
            luminosity: Luminosity percentage (0-100)
        """
        if not (0 <= luminosity <= 100):
            raise ValueError("Luminosity must be between 0-100")
        
        print(f"[DEBUG] Setting LED {led_position} luminosity to {luminosity}%")
        
        # Create luminosity values array - CORRECTED MAPPING
        luminosity_array = [0] * 12
        
        # Map LED positions to array indices correctly
        # Each LED has 3 channels (G, B, R) in the order: UR, UL, LR, LL
        led_mapping = {
            0: 0,  # UR starts at index 0
            1: 3,  # UL starts at index 3  
            2: 6,  # LR starts at index 6
            3: 9   # LL starts at index 9
        }
        
        if led_position not in led_mapping:
            raise ValueError(f"Invalid LED position: {led_position}. Must be 0-3")
        
        base_index = led_mapping[led_position]
        luminosity_array[base_index] = luminosity      # Green
        luminosity_array[base_index + 1] = luminosity  # Blue  
        luminosity_array[base_index + 2] = luminosity  # Red
        
        # CORRECTED BIT MAPPING - Match protocol documentation
        # LED states: | 0000 | UR | UL | LR | LL |
        led_state_bits = {
            0: 0x08,  # UR = bit 3 (1000) - CORRECT
            1: 0x04,  # UL = bit 2 (0100) - CORRECT  
            2: 0x02,  # LR = bit 1 (0010) - CORRECT
            3: 0x01   # LL = bit 0 (0001) - CORRECT
        }
        
        led_states = led_state_bits.get(led_position, 0x00)
        
        print(f"[DEBUG] LED {led_position} -> base_index={base_index}, led_states=0x{led_states:02x}")
        print(f"[DEBUG] Luminosity array: {luminosity_array}")
        
        return self.set_luminosity_values(device_id, led_states, luminosity_array)
    
    def set_all_luminosity(self, device_id: int, luminosity: int, all_leds_on: bool = True) -> bool:
        """
        Set same luminosity for all LEDs - CORRECTED VERSION
        """
        luminosity_array = [luminosity] * 12
        led_states = 0x0F if all_leds_on else 0x00  # All LEDs on = 0x0F (1111)
        
        print(f"[DEBUG] Setting all LEDs luminosity to {luminosity}%, led_states=0x{led_states:02x}")
        
        return self.set_luminosity_values(device_id, led_states, luminosity_array)
    
    def set_luminosity_preset(self, device_id: int, preset_name: str) -> bool:
        """
        Set luminosity preset
        """
        if preset_name not in GS_PRESETS:
            available_presets = ", ".join(GS_PRESETS.keys())
            raise ValueError(f"Unknown preset: {preset_name}. Available: {available_presets}")
        
        luminosity = GS_PRESETS[preset_name]
        all_leds_on = (preset_name != "OFF")
        
        return self.set_all_luminosity(device_id, luminosity, all_leds_on)
    
    def test_luminosity_functions(self, device_id: int):
        """
        Comprehensive test of all luminosity functions
        """
        print("\n🎯 Testing Luminosity Functions")
        print("=" * 40)
        
        tests = [
            ("set_all_luminosity OFF", lambda: self.set_all_luminosity(device_id, 0)),
            ("set_all_luminosity 50%", lambda: self.set_all_luminosity(device_id, 50)),
            ("set_all_luminosity 100%", lambda: self.set_all_luminosity(device_id, 100)),
            ("set_led_luminosity UR 80%", lambda: self.set_led_luminosity(device_id, 0, 80)),
            ("set_led_luminosity UL 60%", lambda: self.set_led_luminosity(device_id, 1, 60)),
            ("set_led_luminosity LR 40%", lambda: self.set_led_luminosity(device_id, 2, 40)),
            ("set_led_luminosity LL 20%", lambda: self.set_led_luminosity(device_id, 3, 20)),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔧 Testing: {test_name}")
            success = test_func()
            print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
            import time
            time.sleep(1.0)
        
        return True