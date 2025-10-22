"""
Push Button Light Control API (PB_API)
Version: 1.0.0

High-level API for controlling Push Button Light devices with PIC24 microcontrollers
using custom UART protocol for LED control systems.
"""

import time
from .core.device_manager import PushButtonDeviceManager
from .core.protocol import PushButtonProtocol
from .core.exceptions import (
    PushButtonError, CommunicationError, 
    TimeoutError, DeviceError, ProtocolError
)
from .commands.control_mode import ControlModeCommand
from .commands.color import ColorCommand
from .commands.luminosity import LuminosityCommand
from .commands.system_config import SystemConfigCommand
from .core.constants import *

__version__ = "1.0.0"
__all__ = [
    'PushButtonLightControl', 
    'PushButtonDeviceManager',
    'PushButtonProtocol',
    'PushButtonError', 
    'CommunicationError', 
    'TimeoutError', 
    'DeviceError', 
    'ProtocolError',
    'ControlModeCommand', 
    'ColorCommand', 
    'LuminosityCommand', 
    'SystemConfigCommand',
    # Constants
    'CMD_CONTROL_MODE', 
    'CMD_SETTING', 
    'CMD_OPERATING', 
    'CMD_LUMIN',
    'CTRL_SW_STATE', 
    'CTRL_SW_LUMIN', 
    'CTRL_SW_AN0', 
    'CTRL_SW_PWM', 
    'CTRL_UART',
    'LED_UR', 
    'LED_UL', 
    'LED_LR', 
    'LED_LL',
    'ACK_FIRMWARE_BASE', 
    'ACK_SUCCESS', 
    'COLOR_PRESETS',
    'LUMINOSITY_PRESETS',
    'BROADCAST_ID', 
    'DEFAULT_DEVICE_ID'
]

class PushButtonLightControl:
    """
    Main API class for Push Button Light Control devices
    """
    
    def __init__(self, port: str = None, baudrate: int = 115200, timeout: float = 2.0, retry_count: int = 2):
        self.device_manager = PushButtonDeviceManager(port, baudrate, timeout, retry_count)
        self.control_mode = ControlModeCommand(self.device_manager)
        self.color = ColorCommand(self.device_manager)
        self.luminosity = LuminosityCommand(self.device_manager)
        self.system_config = SystemConfigCommand(self.device_manager)
        self.protocol = PushButtonProtocol()
        
        # Track command state
        self._last_command_time = 0
        self._min_command_interval = 0.1  # Minimum time between commands
    
    def connect(self, port: str = None, baudrate: int = None) -> bool:
        """Connect with better initialization"""
        return self.device_manager.connect(port, baudrate)
    
    def disconnect(self):
        """Disconnect"""
        self.device_manager.disconnect()
    
    def is_connected(self) -> bool:
        """Check connection"""
        return self.device_manager.is_connected()
    
    def register_callback(self, event: str, callback: callable):
        """Register callback"""
        self.device_manager.register_callback(event, callback)
    
    def _ensure_command_interval(self):
        """Ensure minimum time between commands to prevent overwhelming the device"""
        current_time = time.time()
        time_since_last = current_time - self._last_command_time
        
        if time_since_last < self._min_command_interval:
            sleep_time = self._min_command_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_command_time = time.time()

# Create convenient alias
PBControl = PushButtonLightControl