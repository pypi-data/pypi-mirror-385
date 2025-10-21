#!/usr/bin/env python3
"""
Test script to verify the protocol fix
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pb_api import PushButtonLightControl
from pb_api.core.protocol import PushButtonProtocol

def test_protocol_fix():
    """Test the protocol decoding fix"""
    print("Testing protocol decoding...")
    
    # Test single-byte responses that were causing errors
    test_bytes = [
        b'\xC0',  # Firmware ACK
        b'\xDD',  # Success ACK  
        b'\x33',  # NACK
        b'\x44',  # Checksum error
        b'\x00',  # Unknown byte (should not error now)
        b'\xFF',  # Unknown byte (should not error now)
    ]
    
    for test_byte in test_bytes:
        try:
            result = PushButtonProtocol.decode_response(test_byte)
            print(f"✓ 0x{test_byte[0]:02x} -> {result.get('type')}")
        except Exception as e:
            print(f"✗ 0x{test_byte[0]:02x} -> ERROR: {e}")
    
    print("\nProtocol test completed!")

def quick_connection_test():
    """Quick test to verify basic functionality"""
    print("\nTesting connection...")
    
    try:
        pb = PushButtonLightControl('COM6')
        
        if pb.connect():
            print("✓ Connected successfully")
            
            # Simple test command
            print("Sending test command...")
            pb.color.set_all_leds_color(1, 'WHITE')
            pb.luminosity.set_all_luminosity(1, 50)
            
            pb.disconnect()
            print("✓ Disconnected successfully")
        else:
            print("✗ Connection failed")
            
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    test_protocol_fix()
    quick_connection_test()