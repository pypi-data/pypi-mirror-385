import serial
import time
import threading
from typing import Callable, Optional, List, Dict, Any
from .exceptions import PushButtonError, CommunicationError, TimeoutError, DeviceError, ProtocolError
from .protocol import PushButtonProtocol
from .constants import *

class PushButtonDeviceManager:
    """
    Device manager for Push Button Light controller communication
    Handles serial connection and protocol communication for push button light systems
    """
    
    def __init__(self, port: str = None, baudrate: int = 115200, timeout: float = 2.0, retry_count: int = 2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.retry_count = retry_count
        self.serial_conn = None
        self._lock = threading.RLock()
        self._callbacks = {
            'response_received': [],
            'error': [],
            'connected': [],
            'disconnected': []
        }
        self._response_buffer = bytearray()
        self._waiting_for_response = False
        self._response_event = threading.Event()
        self._last_response = None
        self._listening = False
        self._listen_thread = None
        self._command_queue = []
        self._is_processing = False
        
    def connect(self, port: str = None, baudrate: int = None) -> bool:
        """Establish connection to the device with better initialization"""
        if port:
            self.port = port
        if baudrate:
            self.baudrate = baudrate
            
        if not self.port:
            raise CommunicationError("No port specified")
            
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO,
                # Additional settings for stability
                write_timeout=self.timeout,
                inter_byte_timeout=0.1
            )
            
            # Clear any existing data in buffers
            self._clear_buffers()
            
            # Start listening thread
            self._listening = True
            self._listen_thread = threading.Thread(target=self._listen_serial, daemon=True)
            self._listen_thread.start()
            
            # Wait a bit for the connection to stabilize
            time.sleep(0.5)
            
            # Test connection with a simple command
            if self._test_connection():
                self._trigger_callback('connected')
                return True
            else:
                self.disconnect()
                return False
                
        except serial.SerialException as e:
            raise CommunicationError(f"Failed to connect: {e}")
    
    def _clear_buffers(self):
        """Clear serial buffers to prevent stale data"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.reset_input_buffer()
                self.serial_conn.reset_output_buffer()
                self._response_buffer.clear()
            except:
                pass
    
    def send_command(self, packet: bytes, wait_for_response: bool = True, timeout: float = None, retry_count: int = None) -> Dict[str, Any]:
        """
        Send command to device with retry logic and better error handling
        """
        if not self.is_connected():
            raise CommunicationError("Device not connected")
            
        retry_count = retry_count or self.retry_count
        timeout = timeout or self.timeout
        
        last_exception = None
        
        for attempt in range(retry_count):
            with self._lock:
                self._response_event.clear()
                self._last_response = None
                
                try:
                    # Clear buffers before each attempt
                    self._clear_buffers()
                    
                    # Add small delay between retries (except first attempt)
                    if attempt > 0:
                        time.sleep(0.2 * attempt)  # Increasing delay
                    
                    print(f"Attempt {attempt + 1}/{retry_count}: Sending {len(packet)} bytes")
                    self.serial_conn.write(packet)
                    
                    if wait_for_response:
                        response = self._wait_for_response(timeout)
                        print(f"Attempt {attempt + 1} successful: {response.get('type')}")
                        return response
                    else:
                        return {'type': 'sent', 'success': True}
                        
                except (TimeoutError, CommunicationError) as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < retry_count - 1:
                        print(f"Retrying... ({attempt + 1}/{retry_count})")
                        continue
                    else:
                        raise last_exception
                except serial.SerialException as e:
                    last_exception = CommunicationError(f"Serial error: {e}")
                    print(f"Attempt {attempt + 1} failed with serial error: {e}")
                    if attempt < retry_count - 1:
                        continue
                    else:
                        raise last_exception
    
    def _wait_for_response(self, timeout: float = None) -> Dict[str, Any]:
        """Wait for response with timeout and better state management"""
        timeout = timeout or self.timeout
        
        # Wait for response event with timeout
        if self._response_event.wait(timeout):
            if self._last_response:
                return self._last_response
            else:
                raise CommunicationError("Response received but no data")
        else:
            # Check if we received any partial data
            if len(self._response_buffer) > 0:
                print(f"Timeout with partial data in buffer: {len(self._response_buffer)} bytes")
                # Try to process what we have
                try:
                    response = self._extract_complete_response()
                    if response:
                        return PushButtonProtocol.decode_response(response)
                except:
                    pass
            raise TimeoutError(f"No response received within {timeout} seconds")
    
    def _listen_serial(self):
        """Improved serial listening with better buffer management"""
        buffer = bytearray()
        last_data_time = time.time()
        
        while self._listening and self.is_connected():
            try:
                # Check for new data
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    buffer.extend(data)
                    last_data_time = time.time()
                    
                    # Process complete messages from buffer
                    processed_any = False
                    while len(buffer) > 0:
                        response = self._extract_complete_response_from_buffer(buffer)
                        if response:
                            self._handle_response(response)
                            processed_any = True
                        else:
                            # No complete message yet, break and wait for more data
                            break
                    
                    # If we didn't process anything but have data, check if we're waiting
                    if not processed_any and len(buffer) > 0:
                        # If we have data but can't parse it, wait a bit for more
                        time.sleep(0.01)
                        
                else:
                    # No data available, small sleep to prevent CPU spinning
                    time.sleep(0.01)
                    
                    # If we have data in buffer but no new data for a while, try to process it
                    if len(buffer) > 0 and (time.time() - last_data_time) > 0.1:
                        response = self._extract_complete_response_from_buffer(buffer)
                        if response:
                            self._handle_response(response)
                    
            except Exception as e:
                if self._listening:
                    self._trigger_callback('error', {'error': f"Serial listening error: {e}"})
                time.sleep(0.1)
    
    def _extract_complete_response_from_buffer(self, buffer: bytearray) -> Optional[bytes]:
        """Extract complete response from buffer with better parsing"""
        if not buffer:
            return None
            
        # Single byte responses (ACKs, NACKs, firmware ACKs)
        if len(buffer) >= 1:
            byte_val = buffer[0]
            
            # Check for single byte responses
            if ((byte_val & 0xF0) == ACK_FIRMWARE_BASE or 
                byte_val in [ACK_SUCCESS, NACK_INVALID_HEADER, NACK_INVALID_DC, 
                           NACK_INVALID_GS, NACK_INVALID_MODE, NACK_CHECKSUM_ERROR]):
                response = bytes([byte_val])
                del buffer[0]
                return response
        
        # Control mode response (3 bytes)
        if len(buffer) >= 3:
            if (buffer[0] & CMD_MASK) == CMD_CONTROL_MODE:
                # Check if we have a complete control mode response
                if buffer[2] == (buffer[0] ^ buffer[1]):  # Valid checksum
                    response = bytes(buffer[:3])
                    del buffer[:3]
                    return response
        
        # Setting/Operating response (15 bytes)
        if len(buffer) >= 15:
            cmd_type = buffer[0] & CMD_MASK
            if cmd_type in [CMD_SETTING, CMD_OPERATING]:
                # Verify checksum
                checksum = 0
                for i in range(14):
                    checksum ^= buffer[i]
                if checksum == buffer[14]:
                    response = bytes(buffer[:15])
                    del buffer[:15]
                    return response
        
        # If we can't extract a complete message, return None
        return None
    
    def _handle_response(self, data: bytes):
        """Handle response data with better error handling"""
        try:
            parsed_response = PushButtonProtocol.decode_response(data)
            self._last_response = parsed_response
            self._response_event.set()
            self._trigger_callback('response_received', parsed_response)
            
            # Handle NACK errors
            if (parsed_response.get('type') == 'command_response' and 
                parsed_response['response_code'] != ACK_SUCCESS):
                error_code = parsed_response['response_code']
                error_msg = PushButtonProtocol.get_error_message(error_code)
                self._trigger_callback('error', {'error': f"Device NACK: {error_msg}"})
                
        except (ProtocolError, DeviceError) as e:
            self._trigger_callback('error', {'error': str(e)})
        except Exception as e:
            self._trigger_callback('error', {'error': f"Unexpected error handling response: {e}"})
    
    def _test_connection(self) -> bool:
        """Simplified connection test - just check if port is open"""
        try:
            # Just verify the port is open and we can write to it
            if self.serial_conn and self.serial_conn.is_open:
                print("Connection test: Port is open and ready")
                return True
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def disconnect(self):
        """Clean disconnect"""
        self._listening = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except:
                pass
            self._trigger_callback('disconnected')
        self.serial_conn = None
    
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.serial_conn is not None and self.serial_conn.is_open
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for events"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, data: dict = None):
        """Trigger registered callbacks with error handling"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data) if data else callback()
            except Exception as e:
                print(f"Callback error: {e}")