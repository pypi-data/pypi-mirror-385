from .base import BaseCommand
from ..core.protocol import PushButtonProtocol
from ..core.constants import *
from ..core.exceptions import DeviceError

class ControlModeCommand(BaseCommand):
    """Control mode configuration commands"""
    
    def execute(self, device_id: int, control_mode: int) -> bool:
        """
        Execute control mode setting (implements abstract method)
        
        Args:
            device_id: Target device ID
            control_mode: Control mode constant
            
        Returns:
            Success status
        """
        return self.set_control_mode(device_id, control_mode)
    
    def set_control_mode(self, device_id: int, control_mode: int) -> bool:
        """
        Set control mode for device
        
        Args:
            device_id: Target device ID (0 for broadcast, 1-62 for specific devices)
            control_mode: One of CTRL_SW_STATE, CTRL_SW_LUMIN, CTRL_SW_AN0, CTRL_SW_PWM, CTRL_UART
            
        Returns:
            Success status
        """
        packet = PushButtonProtocol.encode_control_mode(device_id, control_mode)
        response = self.device.send_command(packet)
        
        if response.get('type') == 'control_mode_response':
            return response['control_mode'] == control_mode
        elif response.get('type') == 'command_response':
            return response['response_code'] == ACK_SUCCESS
            
        return False
    
    def set_control_mode_by_name(self, device_id: int, control_mode_name: str) -> bool:
        """
        Set control mode by name
        
        Args:
            device_id: Target device ID
            control_mode_name: One of "SWITCH_MODE", "SWITCH_LUMIN_MODE", "ANALOG_MODE", "PWM_MODE", "UART_MODE"
            
        Returns:
            Success status
        """
        if control_mode_name not in CTRL_MODE_BYTES:
            raise ValueError(f"Invalid control mode name: {control_mode_name}")
        
        control_mode = CTRL_MODE_BYTES[control_mode_name]
        return self.set_control_mode(device_id, control_mode)