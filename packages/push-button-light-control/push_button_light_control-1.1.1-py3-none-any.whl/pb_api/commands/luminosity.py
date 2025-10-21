from typing import List
from .base import BaseCommand
from ..core.protocol import PushButtonProtocol
from ..core.constants import *

class LuminosityCommand(BaseCommand):
    """
    Luminosity control commands for Push Button Light devices
    Uses percentage values (0-100) for luminosity
    """
    
    def execute(self, device_id: int, led_states: int, luminosity_values: List[int]) -> bool:
        """
        Execute luminosity setting (implements abstract method)
        """
        return self.set_luminosity_values(device_id, led_states, luminosity_values)
    
    def set_luminosity_values(self, device_id: int, led_states: int, luminosity_values: List[int]) -> bool:
        """
        Set luminosity values for all LEDs (percentage 0-100)
        """
        if len(luminosity_values) != 12:
            raise ValueError("Luminosity values must contain exactly 12 values")
        if any(not (0 <= gs <= 100) for gs in luminosity_values):
            raise ValueError("Luminosity values must be between 0-100")
        
        packet = PushButtonProtocol.encode_operating_command(device_id, led_states, luminosity_values)
        response = self.device.send_command(packet)
        
        # Check for success - accept both single ACK and operating response
        if response.get('type') == 'command_response':
            return response.get('response_code') == ACK_SUCCESS
        elif response.get('type') == 'operating_response':
            return True
        return False
    
    def set_led_luminosity(self, device_id: int, led_position: int, luminosity: int) -> bool:
        """
        Set luminosity for specific LED (percentage 0-100)
        
        Args:
            device_id: Target device ID
            led_position: LED position (0-3)
            luminosity: Luminosity percentage (0-100)
        """
        if not (0 <= luminosity <= 100):
            raise ValueError("Luminosity must be between 0-100")
        
        # Create luminosity values array
        luminosity_array = [0] * 12
        base_index = led_position * 3
        luminosity_array[base_index] = luminosity      # Green
        luminosity_array[base_index + 1] = luminosity  # Blue  
        luminosity_array[base_index + 2] = luminosity  # Red
        
        # Enable only the target LED
        led_states = PushButtonProtocol.create_led_states(
            ur=(led_position == LED_UR),
            ul=(led_position == LED_UL),
            lr=(led_position == LED_LR), 
            ll=(led_position == LED_LL)
        )
        
        return self.set_luminosity_values(device_id, led_states, luminosity_array)
    
    def set_all_luminosity(self, device_id: int, luminosity: int, all_leds_on: bool = True) -> bool:
        """
        Set same luminosity for all LEDs
        """
        luminosity_array = [luminosity] * 12
        led_states = 0x0F if all_leds_on else 0x00
        
        return self.set_luminosity_values(device_id, led_states, luminosity_array)
    
    def set_luminosity_preset(self, device_id: int, preset_name: str) -> bool:
        """
        Set luminosity preset
        """
        if preset_name not in GS_PRESETS:  # Use GS_PRESETS instead of LUMINOSITY_PRESETS
            available_presets = ", ".join(GS_PRESETS.keys())
            raise ValueError(f"Unknown preset: {preset_name}. Available: {available_presets}")
        
        luminosity = GS_PRESETS[preset_name]
        all_leds_on = (preset_name != "OFF")
        
        return self.set_all_luminosity(device_id, luminosity, all_leds_on)
    
    def fade_luminosity(self, device_id: int, start_luminosity: int, end_luminosity: int, 
                       steps: int = 10, delay: float = 0.1) -> bool:
        """
        Gradually fade luminosity between values
        """
        import time
        
        if not all(0 <= value <= 100 for value in [start_luminosity, end_luminosity]):
            raise ValueError("Luminosity values must be between 0-100")
        
        step_size = (end_luminosity - start_luminosity) / steps
        
        for i in range(steps + 1):
            current_luminosity = int(start_luminosity + (step_size * i))
            success = self.set_all_luminosity(device_id, current_luminosity)
            if not success:
                return False
            time.sleep(delay)
        
        return True