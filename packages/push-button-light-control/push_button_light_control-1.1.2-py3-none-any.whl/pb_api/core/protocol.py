'''
import struct
from typing import List, Tuple, Dict, Any, Optional
from .exceptions import ProtocolError, DeviceError
from .constants import *

class PushButtonProtocol:
    """
    Protocol handler for Push Button Light controller communication
    """
    
    @staticmethod
    def build_packet_start_byte(command_type: int, device_id: int) -> int:
        """Build start byte with command type and device ID for Push Button device"""
        device_id = device_id & DEVICE_ID_MASK
        return command_type | device_id
    
    @staticmethod
    def encode_control_mode(device_id: int, control_mode: int) -> bytes:
        """Encode control mode command for Push Button device (3 bytes)"""
        if not (0 <= device_id <= DEVICE_ID_MASK):
            raise ProtocolError(f"Invalid device ID for Push Button: {device_id}")
        if control_mode not in CTRL_MODES:
            raise ProtocolError(f"Invalid control mode for Push Button: {control_mode}")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_CONTROL_MODE, device_id)
        checksum = start_byte ^ control_mode
        
        return bytes([start_byte, control_mode, checksum])
    
    @staticmethod
    def encode_setting_command(device_id: int, dc_values: List[int]) -> bytes:
        """Encode setting command for DC values (15 bytes)"""
        if len(dc_values) != 12:
            raise ProtocolError("DC values must contain exactly 12 values")
        if any(not (0 <= dc <= 63) for dc in dc_values):
            raise ProtocolError("DC values must be between 0-63")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_SETTING, device_id)
        packet = [start_byte] + [0x0F] + dc_values # Reserved byte
        
        # Calculate checksum (XOR of bytes 0-13)
        checksum = 0
        for byte in packet:
            checksum ^= byte
            
        packet.append(checksum)
        return bytes(packet)
    
    @staticmethod
    def encode_operating_command(device_id: int, led_states: int, gs_values: List[int]) -> bytes:
        """Encode operating command for GS values (15 bytes)"""
        if len(gs_values) != 12:
            raise ProtocolError("GS values must contain exactly 12 values")
        if any(not (0 <= gs <= 100) for gs in gs_values):
            raise ProtocolError("GS values must be between 0-100")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_OPERATING, device_id)
        packet = [start_byte, led_states & 0x0F] + gs_values
        
        # Calculate checksum (XOR of bytes 0-13)
        checksum = 0
        for byte in packet:
            checksum ^= byte
            
        packet.append(checksum)
        return bytes(packet)
    
    @staticmethod
    def encode_lumin_command(device_id: int, gs_max: int, gs_day: int, gs_night: int) -> bytes:
        """Encode set lumin command (8 bytes)"""
        if not (0 <= gs_max <= GS_MAX) or not (0 <= gs_day <= GS_MAX) or not (0 <= gs_night <= GS_MAX):
            raise ProtocolError("GS values must be between 0-4095")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_LUMIN, device_id)
        packet = [start_byte]
        
        # Add 16-bit values (big-endian)
        packet.extend([(gs_max >> 8) & 0xFF, gs_max & 0xFF])
        packet.extend([(gs_day >> 8) & 0xFF, gs_day & 0xFF])
        packet.extend([(gs_night >> 8) & 0xFF, gs_night & 0xFF])
        
        # Calculate checksum (XOR of bytes 0-6)
        checksum = 0
        for byte in packet:
            checksum ^= byte
            
        packet.append(checksum)
        return bytes(packet)
    
    @staticmethod
    def create_led_states(ur: bool, ul: bool, lr: bool, ll: bool) -> int:
        """Create LED states byte from individual LED states"""
        states = 0
        if ur: states |= (1 << 3)  # UR = bit 3
        if ul: states |= (1 << 2)  # UL = bit 2  
        if lr: states |= (1 << 1)  # LR = bit 1
        if ll: states |= (1 << 0)  # LL = bit 0
        return states
    
    @staticmethod
    def parse_led_states(led_states: int) -> Dict[str, bool]:
        """Parse LED states byte to individual LED states"""
        return {
            'UR': bool(led_states & (1 << 3)),
            'UL': bool(led_states & (1 << 2)),
            'LR': bool(led_states & (1 << 1)),
            'LL': bool(led_states & (1 << 0))
        }
    
    @staticmethod
    def decode_response(data: bytes) -> Dict[str, Any]:
        """Decode response from device - FIXED RESPONSE TYPES"""
        if not data:
            raise ProtocolError("Empty response")
            
        # Single byte responses
        if len(data) == 1:
            byte_val = data[0]
            
            # Check if this is a per-byte ACK (firmware release)
            if (byte_val & 0xF0) == ACK_FIRMWARE_BASE:
                firmware_release = byte_val & 0x0F
                return {
                    'type': 'firmware_ack', 
                    'firmware_version': firmware_release,
                    'raw_byte': byte_val
                }
                
            # Check if this is a final response ACK/NACK
            elif byte_val in [ACK_SUCCESS, NACK_INVALID_HEADER, NACK_INVALID_DC, 
                            NACK_INVALID_GS, NACK_INVALID_MODE, NACK_CHECKSUM_ERROR]:
                return {
                    'type': 'command_response', 
                    'response_code': byte_val,
                    'raw_byte': byte_val
                }
            
            else:
                return {
                    'type': 'unknown_single_byte',
                    'raw_byte': byte_val,
                    'message': f'Unknown single byte: 0x{byte_val:02x}'
                }
        
        # Control mode response packets (3 bytes)
        elif len(data) == 3:
            if (data[0] & CMD_MASK) != CMD_CONTROL_MODE:
                raise ProtocolError("Invalid control mode response")
                
            # Verify checksum
            if data[2] != (data[0] ^ data[1]):
                raise ProtocolError("Control mode checksum error")
                
            return {
                'type': 'control_mode_response',
                'device_id': data[0] & DEVICE_ID_MASK,
                'control_mode': data[1],
                'control_mode_name': CTRL_MODES.get(data[1], "UNKNOWN"),
                'raw_data': list(data)
            }
        
        # Status response packets (15 bytes) - FIXED RESPONSE TYPE MAPPING
        elif len(data) == 15:
            cmd_type = data[0] & CMD_MASK
            
            # Verify checksum
            checksum = 0
            for i in range(14):
                checksum ^= data[i]
            if checksum != data[14]:
                raise ProtocolError("Response checksum error")
            
            # FIXED: Correct response type mapping
            if cmd_type == CMD_SETTING:
                response_type = 'setting_response'
            elif cmd_type == CMD_OPERATING:
                response_type = 'operating_response'
            else:
                raise ProtocolError(f"Invalid command type in response: 0x{cmd_type:02x}")
            
            led_states = PushButtonProtocol.parse_led_states(data[1])
            
            return {
                'type': response_type,
                'device_id': data[0] & DEVICE_ID_MASK,
                'led_states': led_states,
                'values': list(data[2:14]),
                'raw_data': list(data)
            }
        
        # Unknown format
        return {
            'type': 'unknown_format',
            'raw_data': list(data),
            'message': f'Unknown response format: {len(data)} bytes'
        }
    
    @staticmethod
    def convert_percentage_to_12bit(percent: int) -> int:
        """Convert percentage (0-100) to 12-bit value (0-4095)"""
        if not 0 <= percent <= 100:
            raise ValueError("Percentage must be between 0-100")
        return int((percent * GS_MAX) / 100)
    
    @staticmethod
    def convert_12bit_to_percentage(value: int) -> int:
        """Convert 12-bit value (0-4095) to percentage (0-100)"""
        if not 0 <= value <= GS_MAX:
            raise ValueError("12-bit value must be between 0-4095")
        return int((value * 100) / GS_MAX)
    
    @staticmethod
    def get_error_message(error_code: int) -> str:
        """Get human-readable error message from error code"""
        error_messages = {
            NACK_INVALID_HEADER: "Invalid header",
            NACK_INVALID_DC: "Invalid DC value",
            NACK_INVALID_GS: "Invalid GS value",
            NACK_INVALID_MODE: "Invalid control mode",
            NACK_CHECKSUM_ERROR: "Checksum error"
        }
        return error_messages.get(error_code, f"Unknown error (0x{error_code:02x})")
'''

import struct
from typing import List, Tuple, Dict, Any, Optional
from .exceptions import ProtocolError, DeviceError
from .constants import *

class PushButtonProtocol:
    """
    Protocol handler perfectly synchronized with PIC24FV16KM202 firmware
    Matches exact packet formats and response handling
    """
    
    @staticmethod
    def build_packet_start_byte(command_type: int, device_id: int) -> int:
        """Build start byte matching firmware format: | CMD[7:6] | ID[5:0] |"""
        device_id = device_id & DEVICE_ID_MASK
        return command_type | device_id
    
    @staticmethod
    def encode_control_mode(device_id: int, control_mode: int) -> bytes:
        """Encode control mode command (3 bytes) matching firmware"""
        if not (0 <= device_id <= DEVICE_ID_MASK):
            raise ProtocolError(f"Invalid device ID: {device_id}")
        if control_mode not in [CTRL_SW_STATE, CTRL_SW_LUMIN, CTRL_SW_AN0, CTRL_SW_PWM, CTRL_UART]:
            raise ProtocolError(f"Invalid control mode: {control_mode}")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_CONTROL_MODE, device_id)
        checksum = start_byte ^ control_mode
        
        return bytes([start_byte, control_mode, checksum])
    
    @staticmethod
    def encode_setting_command(device_id: int, dc_values: List[int]) -> bytes:
        """Encode setting command (15 bytes) matching firmware DC format"""
        if len(dc_values) != 12:
            raise ProtocolError("DC values must contain exactly 12 values")
        if any(not (0 <= dc <= 63) for dc in dc_values):
            raise ProtocolError("DC values must be between 0-63")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_SETTING, device_id)
        packet = [start_byte, 0x00]  # LED states (will be set by firmware)
        
        # Add DC values in exact firmware order
        packet.extend(dc_values)
        
        # Calculate checksum (XOR of bytes 0-13)
        checksum = 0
        for byte in packet:
            checksum ^= byte
            
        packet.append(checksum)
        
        if len(packet) != SETTING_PACKET_SIZE:
            raise ProtocolError(f"Setting packet size incorrect: {len(packet)}")
            
        return bytes(packet)
    
    @staticmethod
    def encode_operating_command(device_id: int, led_states: int, gs_values: List[int]) -> bytes:
        """Encode operating command (15 bytes) matching firmware GS format"""
        if len(gs_values) != 12:
            raise ProtocolError("GS values must contain exactly 12 values")
        if any(not (0 <= gs <= 100) for gs in gs_values):
            raise ProtocolError("GS values must be between 0-100")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_OPERATING, device_id)
        packet = [start_byte, led_states & 0x0F]
        
        # Add GS values in exact firmware order
        packet.extend(gs_values)
        
        # Calculate checksum (XOR of bytes 0-13)
        checksum = 0
        for byte in packet:
            checksum ^= byte
            
        packet.append(checksum)
        
        if len(packet) != OPERATING_PACKET_SIZE:
            raise ProtocolError(f"Operating packet size incorrect: {len(packet)}")
            
        return bytes(packet)
    
    @staticmethod
    def encode_lumin_command(device_id: int, gs_max: int, gs_day: int, gs_night: int) -> bytes:
        """Encode set lumin command (8 bytes) matching firmware"""
        if not (0 <= gs_max <= GS_MAX) or not (0 <= gs_day <= GS_MAX) or not (0 <= gs_night <= GS_MAX):
            raise ProtocolError("GS values must be between 0-4095")
        
        start_byte = PushButtonProtocol.build_packet_start_byte(CMD_LUMIN, device_id)
        packet = [start_byte]
        
        # Add 16-bit values (big-endian) matching firmware
        packet.extend([(gs_max >> 8) & 0xFF, gs_max & 0xFF])
        packet.extend([(gs_day >> 8) & 0xFF, gs_day & 0xFF])
        packet.extend([(gs_night >> 8) & 0xFF, gs_night & 0xFF])
        
        # Calculate checksum (XOR of bytes 0-6)
        checksum = 0
        for byte in packet:
            checksum ^= byte
            
        packet.append(checksum)
        
        if len(packet) != LUMIN_PACKET_SIZE:
            raise ProtocolError(f"Lumin packet size incorrect: {len(packet)}")
            
        return bytes(packet)
    
    @staticmethod
    def create_led_states(ur: bool, ul: bool, lr: bool, ll: bool) -> int:
        """Create LED states byte matching firmware format: | 0000 | UR | UL | LR | LL |"""
        states = 0
        if ur: states |= (1 << 3)  # UR = bit 3
        if ul: states |= (1 << 2)  # UL = bit 2  
        if lr: states |= (1 << 1)  # LR = bit 1
        if ll: states |= (1 << 0)  # LL = bit 0
        return states
    
    @staticmethod
    def parse_led_states(led_states: int) -> Dict[str, bool]:
        """Parse LED states byte matching firmware format"""
        return {
            'UR': bool(led_states & (1 << 3)),
            'UL': bool(led_states & (1 << 2)),
            'LR': bool(led_states & (1 << 1)),
            'LL': bool(led_states & (1 << 0))
        }
    
    # In protocol.py - CORRECTED for fixed firmware
    @staticmethod
    def decode_response(data: bytes) -> Dict[str, Any]:
        """Decode response with CORRECT firmware response types"""
        if not data:
            raise ProtocolError("Empty response")
            
        # Single byte responses (final ACK/NACK)
        if len(data) == 1:
            byte_val = data[0]
            
            # Per-byte ACK (firmware release)
            if (byte_val & 0xF0) == ACK_FIRMWARE_BASE:
                firmware_release = byte_val & 0x0F
                return {
                    'type': 'firmware_ack', 
                    'firmware_version': firmware_release,
                    'raw_byte': byte_val
                }
                
            # Final response ACK/NACK
            elif byte_val in [ACK_SUCCESS, NACK_INVALID_HEADER, NACK_INVALID_DC, 
                            NACK_INVALID_GS, NACK_INVALID_MODE, NACK_CHECKSUM_ERROR]:
                response_type = 'success' if byte_val == ACK_SUCCESS else 'error'
                return {
                    'type': 'command_response',
                    'response_type': response_type,
                    'response_code': byte_val,
                    'message': PushButtonProtocol.get_error_message(byte_val),
                    'raw_byte': byte_val
                }
            
            else:
                return {
                    'type': 'unknown_single_byte',
                    'raw_byte': byte_val,
                    'message': f'Unknown single byte: 0x{byte_val:02x}'
                }
        
        # Status response packets (15 bytes) - CORRECTED FOR FIXED FIRMWARE
        elif len(data) == 15:
            cmd_type = data[0] & CMD_MASK

            # Verify checksum
            checksum = 0
            for i in range(14):
                checksum ^= data[i]
            if checksum != data[14]:
                raise ProtocolError("Response checksum error")
            
            # CORRECT: Firmware now responds with matching types
            if cmd_type == CMD_SETTING:
                response_type = 'setting_response'
            elif cmd_type == CMD_OPERATING:
                response_type = 'operating_response'
            else:
                raise ProtocolError(f"Invalid command type in response: 0x{cmd_type:02x}")
            
            led_states = PushButtonProtocol.parse_led_states(data[1])
            device_id = data[0] & DEVICE_ID_MASK
            
            return {
                'type': response_type,
                'device_id': device_id,
                'led_states': led_states,
                'values': list(data[2:14]),
                'raw_data': list(data)
            }
        
        # Control mode response (3 bytes)
        elif len(data) == 3:
            if (data[0] & CMD_MASK) != CMD_CONTROL_MODE:
                raise ProtocolError("Invalid control mode response")
                
            # Verify checksum
            if data[2] != (data[0] ^ data[1]):
                raise ProtocolError("Control mode checksum error")
                
            device_id = data[0] & DEVICE_ID_MASK
            control_mode = data[1]
                
            return {
                'type': 'control_mode_response',
                'device_id': device_id,
                'control_mode': control_mode,
                'control_mode_name': CTRL_MODES.get(control_mode, "UNKNOWN"),
                'raw_data': list(data)
            }
        
        # Unknown format
        return {
            'type': 'unknown_format',
            'raw_data': list(data),
            'message': f'Unknown response format: {len(data)} bytes'
        }
    
    @staticmethod
    def get_error_message(error_code: int) -> str:
        """Get human-readable error message matching firmware error codes"""
        error_messages = {
            ACK_SUCCESS: "Success",
            NACK_INVALID_HEADER: "Invalid header",
            NACK_INVALID_DC: "Invalid DC value",
            NACK_INVALID_GS: "Invalid GS value", 
            NACK_INVALID_MODE: "Invalid control mode",
            NACK_CHECKSUM_ERROR: "Checksum error"
        }
        return error_messages.get(error_code, f"Unknown error (0x{error_code:02x})")