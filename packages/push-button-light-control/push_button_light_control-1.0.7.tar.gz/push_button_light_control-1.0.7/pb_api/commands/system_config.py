from .base import BaseCommand
from ..core.protocol import PushButtonProtocol
from ..core.constants import *

class SystemConfigCommand(BaseCommand):
    """System configuration commands"""
    
    def execute(self, device_id: int, gs_max: int, gs_day: int, gs_night: int) -> bool:
        """
        Execute system configuration (implements abstract method)
        
        Args:
            device_id: Target device ID
            gs_max: Maximum grayscale value
            gs_day: Daytime grayscale value
            gs_night: Nighttime grayscale value
            
        Returns:
            Success status
        """
        return self.set_luminosity_presets(device_id, gs_max, gs_day, gs_night)
    
    def set_luminosity_presets(self, device_id: int, gs_max: int, gs_day: int, gs_night: int) -> bool:
        """
        Set luminosity presets for switch control mode
        """
        if not (0 <= gs_max <= GS_MAX) or not (0 <= gs_day <= GS_MAX) or not (0 <= gs_night <= GS_MAX):
            raise ValueError("GS values must be between 0-4095")
        
        packet = PushButtonProtocol.encode_lumin_command(device_id, gs_max, gs_day, gs_night)
        response = self.device.send_command(packet)
        
        return (response.get('type') == 'command_response' and 
                response.get('response_code') == ACK_SUCCESS)
    
    def set_luminosity_percentages(self, device_id: int, max_percent: int, 
                                 day_percent: int, night_percent: int) -> bool:
        """
        Set luminosity presets using percentages
        """
        gs_max = PushButtonProtocol.convert_percentage_to_12bit(max_percent)
        gs_day = PushButtonProtocol.convert_percentage_to_12bit(day_percent)
        gs_night = PushButtonProtocol.convert_percentage_to_12bit(night_percent)
        
        return self.set_luminosity_presets(device_id, gs_max, gs_day, gs_night)