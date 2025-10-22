#!/usr/bin/env python3
"""
Test script to verify the command type fix
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pb_api import PushButtonLightControl, CTRL_UART

def test_command_types_fix():
    """Test that command types are used correctly"""
    print("🎯 Testing Command Type Fix")
    print("=" * 50)
    print("Setting Command (0x40) = Color (DC values 0-63)")
    print("Operating Command (0x80) = Luminosity (GS values 0-100)")
    print("=" * 50)
    
    try:
        pb = PushButtonLightControl('COM6', timeout=3.0)
        
        if pb.connect():
            print("✅ Connected successfully")
            time.sleep(1.0)
            
            # Set control mode to UART
            print("\n🔄 Setting control mode to UART...")
            pb.control_mode.set_control_mode(1, CTRL_UART)
            time.sleep(1.0)
            
            # Test 1: Reset everything
            print("\n1. Resetting all LEDs...")
            pb.luminosity.set_all_luminosity(1, 0)  # Should use Operating command
            time.sleep(0.2)
            pb.color.set_all_leds_color(1, 'OFF')   # Should use Setting command
            print("✅ Reset complete")
            time.sleep(2.0)
            
            # Test 2: Test luminosity functions
            print("\n2. Testing luminosity functions (Operating Command)...")
            #pb.luminosity.test_luminosity_functions(1)
            
            # Test 3: Test color functions  
            print("\n3. Testing color functions (Setting Command)...")
            print("   Setting UR LED to RED...")
            pb.color.set_led_color(1, 0, 'RED')
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 0, 100)  # UR 100%
            time.sleep(1.0)
            
            print("   Setting UL LED to GREEN...")
            pb.color.set_led_color(1, 1, 'GREEN')
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 1, 100)  # UR 100%
            time.sleep(1.0)
            
            print("   Setting LR LED to BLUE...")
            pb.color.set_led_color(1, 2, 'BLUE')
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 2, 100)  # UR 100%
            time.sleep(1.0)
            
            print("   Setting LL LED to WHITE...")
            pb.color.set_led_color(1, 3, 'WHITE')
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 3, 100)  # UR 100%
            time.sleep(1.0)
            
            # Test 4: Combined test
            print("\n4. Combined test: Color + Luminosity...")
            print("   Setting all LEDs to CYAN color...")
            pb.color.set_all_leds_color(1, 'CYAN')
            time.sleep(1.0)
            
            print("   Setting all LEDs to 80% luminosity...")
            pb.luminosity.set_all_luminosity(1, 80)
            time.sleep(2.0)
            
            print("   Setting individual LED luminosities...")
            pb.luminosity.set_led_luminosity(1, 0, 100)  # UR 100%
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 1, 60)   # UL 60%
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 2, 30)   # LR 30%
            time.sleep(1.0)
            pb.luminosity.set_led_luminosity(1, 3, 10)   # LL 10%
            time.sleep(2.0)
            
            # Clean up
            print("\n🧹 Cleaning up...")
            pb.luminosity.set_all_luminosity(1, 0)
            pb.color.set_all_leds_color(1, 'OFF')
            
            pb.disconnect()
            print("✅ All tests completed!")
        else:
            print("❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_command_types_fix()