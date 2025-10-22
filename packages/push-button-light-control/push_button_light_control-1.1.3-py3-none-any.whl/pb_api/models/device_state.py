from dataclasses import dataclass
from typing import Dict, List
from ..core.constants import *

@dataclass
class LEDState:
    """Represents the state of a single LED"""
    position: int
    enabled: bool = False
    color: str = "WHITE"
    g_lumin: int = 0
    b_lumin: int = 0
    r_lumin: int = 0
    g_dc: int = 0
    b_dc: int = 0
    r_dc: int = 0
    
    @property
    def position_name(self) -> str:
        """Get position name"""
        positions = {LED_UR: "UR", LED_UL: "UL", LED_LR: "LR", LED_LL: "LL"}
        return positions.get(self.position, "UNKNOWN")

@dataclass
class ColorPreset:
    """Represents a color preset"""
    name: str
    g_value: int
    b_value: int
    r_value: int
    display_color: str = "#000000"
    
    @classmethod
    def from_name(cls, color_name: str):
        """Create color preset from name"""
        if color_name not in COLOR_PRESETS:
            raise ValueError(f"Unknown color: {color_name}")
        
        values = COLOR_PRESETS[color_name]
        display_color = LIGHT_COLORS.get(color_name, "#000000")
        
        return cls(
            name=color_name,
            g_value=values['G'],
            b_value=values['B'],
            r_value=values['R'],
            display_color=display_color
        )

@dataclass
class DeviceState:
    """Represents the complete state of a device"""
    device_id: int
    control_mode: str = "UART_MODE"
    leds: Dict[str, LEDState] = None
    gs_max: int = 4095
    gs_day: int = 2047
    gs_night: int = 819
    
    def __post_init__(self):
        if self.leds is None:
            self.leds = {}
            # Initialize all LED positions
            for pos, pos_name in [(LED_UR, "UR"), (LED_UL, "UL"), (LED_LR, "LR"), (LED_LL, "LL")]:
                self.leds[pos_name] = LEDState(position=pos)
    
    def get_led(self, position_name: str) -> LEDState:
        """Get LED state by position name"""
        return self.leds.get(position_name)
    
    def set_led_color(self, position_name: str, color_name: str):
        """Set LED color"""
        if color_name not in COLOR_PRESETS:
            raise ValueError(f"Unknown color: {color_name}")
        
        led = self.get_led(position_name)
        if led:
            led.color = color_name
            color_values = COLOR_PRESETS[color_name]

            if color_name == "WHITE":
                led.g_dc = 44
                led.b_dc = 44
                led.r_dc = 44
            else:    
                # Update DC values based on color
                led.g_dc = int(color_values['G'] * DC_MAX / 100)
                led.b_dc = int(color_values['B'] * DC_MAX / 100)
                led.r_dc = int(color_values['R'] * DC_MAX / 100)
            
            # Update luminance values
            if color_name == "OFF":
                led.g_lumin = 0
                led.b_lumin = 0
                led.r_lumin = 0
            else:
                led.g_lumin = color_values['G']
                led.b_lumin = color_values['B']
                led.r_lumin = color_values['R']