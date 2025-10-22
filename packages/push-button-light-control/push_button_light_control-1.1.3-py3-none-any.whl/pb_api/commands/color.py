from typing import List, Tuple
import math
import time
from .base import BaseCommand
from ..core.protocol import PushButtonProtocol
from ..core.constants import *

class ColorCommand(BaseCommand):
    """
    Color configuration commands for Push Button Light devices
    Uses DC values directly (0-63) - CORRECTED VERSION
    """
    
    def execute(self, device_id: int, color_values: List[int]) -> bool:
        """
        Execute color setting (implements abstract method)
        Uses SETTING command for color (DC values)
        """
        return self.set_color_values(device_id, color_values)
    
    def set_color_values(self, device_id: int, dc_values: List[int]) -> bool:
        """
        Set DC values for all LEDs (0-63 directly) - CORRECTED VERSION
        Uses SETTING command for color (DC values)
        """
        if len(dc_values) != 12:
            raise ValueError("DC values must contain exactly 12 values")
        if any(not (0 <= dc <= 63) for dc in dc_values):
            raise ValueError("DC values must be between 0-63")
        
        # CORRECTION: Use SETTING command for color (DC values)
        # Note: For setting command, we use 0x00 for LED states since DC values control color, not on/off
        packet = PushButtonProtocol.encode_setting_command(device_id, dc_values)
        response = self.device.send_command(packet)
        
        print(f"[DEBUG COLOR] Setting Command: dc_values={dc_values}")
        print(f"[DEBUG COLOR] Response: {response}")

        # Check for success
        if response.get('type') == 'command_response':
            return response.get('response_code') == ACK_SUCCESS
        elif response.get('type') == 'setting_response':
            return True
        elif response.get('type') == 'firmware_ack':
            print(f"[WARNING] Got firmware_ack for color, but continuing")
            return True
            
        return False
    
    def set_led_color(self, device_id: int, led_position: int, color_name: str) -> bool:
        """
        Set color for specific LED using predefined color presets
        Uses DC values directly (0-63)
        """
        if color_name not in COLOR_PRESETS_DC:  # Changed to DC version
            available_colors = ", ".join(COLOR_PRESETS_DC.keys())
            raise ValueError(f"Unknown color: {color_name}. Available: {available_colors}")
        
        color_values = COLOR_PRESETS_DC[color_name]
        
        # Use DC values directly (0-63)
        dc_g = color_values['G']
        dc_b = color_values['B']
        dc_r = color_values['R']
        
        # Create DC values array for all LEDs
        dc_array = [0] * 12
        base_index = led_position * 3
        dc_array[base_index] = dc_g      # Green
        dc_array[base_index + 1] = dc_b  # Blue
        dc_array[base_index + 2] = dc_r  # Red
        
        return self.set_color_values(device_id, dc_array)
    
    def set_all_leds_color(self, device_id: int, color_name: str) -> bool:
        """
        Set same color for all LEDs using DC values directly
        """
        if color_name not in COLOR_PRESETS_DC:  # Changed to DC version
            available_colors = ", ".join(COLOR_PRESETS_DC.keys())
            raise ValueError(f"Unknown color: {color_name}. Available: {available_colors}")
        
        color_values = COLOR_PRESETS_DC[color_name]
        
        # Use DC values directly (0-63)
        dc_g = color_values['G']
        dc_b = color_values['B']
        dc_r = color_values['R']
        
        # Create DC values array for all LEDs (same for all)
        dc_array = []
        for _ in range(4):  # 4 LEDs
            dc_array.extend([dc_g, dc_b, dc_r])  # G, B, R for each LED
        
        return self.set_color_values(device_id, dc_array)
    
    def set_custom_rgb_dc(self, device_id: int, led_position: int, red_dc: int, green_dc: int, blue_dc: int) -> bool:
        """
        Set custom RGB DC values for specific LED (0-63 directly)
        
        Args:
            device_id: Target device ID
            led_position: LED position (0-3)
            red_dc: Red DC value (0-63)
            green_dc: Green DC value (0-63)
            blue_dc: Blue DC value (0-63)
        """
        if not all(0 <= value <= 63 for value in [red_dc, green_dc, blue_dc]):
            raise ValueError("DC values must be between 0-63")
        
        # Create DC values array
        dc_array = [0] * 12
        base_index = led_position * 3
        dc_array[base_index] = green_dc    # Green
        dc_array[base_index + 1] = blue_dc # Blue  
        dc_array[base_index + 2] = red_dc  # Red
        
        return self.set_color_values(device_id, dc_array)
    
    def set_custom_rgb_percentage(self, device_id: int, led_position: int, red_percent: int, green_percent: int, blue_percent: int) -> bool:
        """
        Set custom RGB using percentages (converts to DC values 0-63)
        
        Args:
            device_id: Target device ID
            led_position: LED position (0-3)
            red_percent: Red percentage (0-100)
            green_percent: Green percentage (0-100)
            blue_percent: Blue percentage (0-100)
        """
        if not all(0 <= value <= 100 for value in [red_percent, green_percent, blue_percent]):
            raise ValueError("Percentage values must be between 0-100")
        
        # Convert percentages to DC values (0-63)
        dc_r = int(red_percent * DC_MAX / 100)
        dc_g = int(green_percent * DC_MAX / 100)
        dc_b = int(blue_percent * DC_MAX / 100)
        
        return self.set_custom_rgb_dc(device_id, led_position, dc_r, dc_g, dc_b)
    
    def set_all_leds_rgb_dc(self, device_id: int, red_dc: int, green_dc: int, blue_dc: int) -> bool:
        """
        Set same RGB DC values for all LEDs (0-63 directly)
        
        Args:
            device_id: Target device ID
            red_dc: Red DC value (0-63)
            green_dc: Green DC value (0-63) 
            blue_dc: Blue DC value (0-63)
        """
        if not all(0 <= value <= 63 for value in [red_dc, green_dc, blue_dc]):
            raise ValueError("DC values must be between 0-63")
        
        # Create DC values array for all LEDs (same for all)
        dc_array = []
        for _ in range(4):  # 4 LEDs
            dc_array.extend([green_dc, blue_dc, red_dc])  # G, B, R for each LED
        
        return self.set_color_values(device_id, dc_array)
    
    def smooth_color_transition(self, device_id: int, start_color: Tuple[int, int, int], 
                              end_color: Tuple[int, int, int], duration: float = 3.0, 
                              steps: int = 30) -> bool:
        """
        Smoothly transition between two RGB colors using DC values
        
        Args:
            device_id: Target device ID
            start_color: Tuple of (red, green, blue) DC values (0-63)
            end_color: Tuple of (red, green, blue) DC values (0-63)
            duration: Total transition time in seconds
            steps: Number of intermediate steps
        """
        start_r, start_g, start_b = start_color
        end_r, end_g, end_b = end_color
        
        step_delay = duration / steps
        
        for step in range(steps + 1):
            # Calculate intermediate values
            progress = step / steps
            current_r = int(start_r + (end_r - start_r) * progress)
            current_g = int(start_g + (end_g - start_g) * progress)
            current_b = int(start_b + (end_b - start_b) * progress)
            
            # Set the current color
            success = self.set_all_leds_rgb_dc(device_id, current_r, current_g, current_b)
            if not success:
                return False
            
            time.sleep(step_delay)
        
        return True
    
    def rainbow_cycle(self, device_id: int, cycles: int = 3, duration_per_cycle: float = 5.0) -> bool:
        """
        Create a beautiful rainbow color cycle effect
        
        Args:
            device_id: Target device ID
            cycles: Number of rainbow cycles
            duration_per_cycle: Duration of each cycle in seconds
        """
        steps = 36  # 10 degree steps for smooth rainbow
        step_delay = duration_per_cycle / steps
        
        for cycle in range(cycles):
            for step in range(steps):
                # Calculate hue (0-360 degrees)
                hue = (step * 360 / steps) % 360
                
                # Convert HSV to RGB
                r, g, b = self._hsv_to_rgb_dc(hue, 1.0, 1.0)
                
                # Set color
                success = self.set_all_leds_rgb_dc(device_id, r, g, b)
                if not success:
                    return False
                
                time.sleep(step_delay)
        
        return True
    
    def breathing_effect(self, device_id: int, base_color: Tuple[int, int, int], 
                        breaths: int = 5, breath_duration: float = 2.0) -> bool:
        """
        Create a breathing effect with a base color
        
        Args:
            device_id: Target device ID
            base_color: Tuple of (red, green, blue) DC values (0-63)
            breaths: Number of breath cycles
            breath_duration: Duration of each breath cycle in seconds
        """
        base_r, base_g, base_b = base_color
        steps = 36
        step_delay = breath_duration / steps
        
        for breath in range(breaths):
            # Breathe in (fade up)
            for step in range(steps):
                progress = step / steps
                # Use sine wave for smooth breathing
                brightness = math.sin(progress * math.pi)
                
                current_r = int(base_r * brightness)
                current_g = int(base_g * brightness)
                current_b = int(base_b * brightness)
                
                success = self.set_all_leds_rgb_dc(device_id, current_r, current_g, current_b)
                if not success:
                    return False
                
                time.sleep(step_delay)
            
            # Breathe out (fade down)
            for step in range(steps, 0, -1):
                progress = step / steps
                brightness = math.sin(progress * math.pi)
                
                current_r = int(base_r * brightness)
                current_g = int(base_g * brightness)
                current_b = int(base_b * brightness)
                
                success = self.set_all_leds_rgb_dc(device_id, current_r, current_g, current_b)
                if not success:
                    return False
                
                time.sleep(step_delay)
        
        return True
    
    def color_wave(self, device_id: int, wave_colors: List[Tuple[int, int, int]], 
                  wave_duration: float = 8.0) -> bool:
        """
        Create a flowing wave through multiple colors
        
        Args:
            device_id: Target device ID
            wave_colors: List of RGB color tuples to cycle through
            wave_duration: Total duration of one complete wave cycle
        """
        if len(wave_colors) < 2:
            raise ValueError("Need at least 2 colors for wave effect")
        
        segments = len(wave_colors)
        segment_steps = 25
        total_steps = segments * segment_steps
        step_delay = wave_duration / total_steps
        
        # Create extended color list for seamless looping
        extended_colors = wave_colors + [wave_colors[0]]
        
        for start_idx in range(segments):
            start_color = extended_colors[start_idx]
            end_color = extended_colors[start_idx + 1]
            
            # Smooth transition between these two colors
            for step in range(segment_steps + 1):
                progress = step / segment_steps
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                
                success = self.set_all_leds_rgb_dc(device_id, r, g, b)
                if not success:
                    return False
                
                time.sleep(step_delay)
        
        return True
    
    def random_color_transition(self, device_id: int, transitions: int = 10, 
                              transition_duration: float = 2.0) -> bool:
        """
        Transition between random colors smoothly
        
        Args:
            device_id: Target device ID
            transitions: Number of random transitions
            transition_duration: Duration of each transition
        """
        import random
        
        # Start with a random color
        current_color = (
            random.randint(0, 63),
            random.randint(0, 63), 
            random.randint(0, 63)
        )
        
        for transition in range(transitions):
            # Generate next random color
            next_color = (
                random.randint(0, 63),
                random.randint(0, 63),
                random.randint(0, 63)
            )
            
            # Smooth transition to next color
            success = self.smooth_color_transition(
                device_id, current_color, next_color, transition_duration
            )
            if not success:
                return False
            
            current_color = next_color
        
        return True
    
    def temperature_colors(self, device_id: int, temperature: str = "warm") -> bool:
        """
        Set colors based on temperature presets
        
        Args:
            device_id: Target device ID
            temperature: "warm", "cool", "daylight", "candle"
        """
        temperature_presets = {
            "warm": (63, 20, 45),      # Warm white
            "cool": (40, 40, 63),      # Cool white  
            "daylight": (50, 45, 55),  # Daylight
            "candle": (63, 10, 15),    # Candle light
        }
        
        if temperature not in temperature_presets:
            available = ", ".join(temperature_presets.keys())
            raise ValueError(f"Unknown temperature: {temperature}. Available: {available}")
        
        r, g, b = temperature_presets[temperature]
        return self.set_all_leds_rgb_dc(device_id, r, g, b)
    
    def _hsv_to_rgb_dc(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """
        Convert HSV color to RGB DC values (0-63)
        
        Args:
            h: Hue (0-360 degrees)
            s: Saturation (0-1)
            v: Value/Brightness (0-1)
            
        Returns:
            Tuple of (red, green, blue) DC values (0-63)
        """
        # Convert HSV to RGB (0-1 range)
        h = h / 360.0
        i = math.floor(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if i % 6 == 0: r, g, b = v, t, p
        elif i % 6 == 1: r, g, b = q, v, p
        elif i % 6 == 2: r, g, b = p, v, t
        elif i % 6 == 3: r, g, b = p, q, v
        elif i % 6 == 4: r, g, b = t, p, v
        else: r, g, b = v, p, q
        
        # Convert to DC values (0-63)
        r_dc = int(r * 44)
        g_dc = int(g * 44)
        b_dc = int(b * 44)
        
        return r_dc, g_dc, b_dc