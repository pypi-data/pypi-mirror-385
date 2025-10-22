#!/usr/bin/env python3
"""
Quick Start optimized for PIC24FV16KM202 firmware
Perfectly synchronized with firmware protocol
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pb_api import PushButtonLightControl, CTRL_UART, LED_UR, LED_UL, LED_LR, LED_LL

def firmware_sync_demo():
    """Demo that matches firmware timing and protocol exactly"""
    print("🎯 PIC24FV16KM202 Firmware-Synchronized Demo")
    print("=" * 50)
    print("Protocol Features:")
    print("• Per-byte ACK handling")
    print("• 5ms firmware loop synchronization") 
    print("• Exact packet format matching")
    print("=" * 50)
    
    # Configuration
    PORT = 'COM6'  # Change to your port
    DEVICE_ID = 1
    
    # Initialize with firmware-compatible settings
    pb = PushButtonLightControl(timeout=3.0, retry_count=2)
    
    try:
        # Connect with firmware timing
        print("\n1. Connecting to firmware...")
        if pb.connect(PORT):
            print("✅ Firmware connected and synchronized")
        else:
            print("❌ Connection failed")
            return
        
        # Allow firmware to stabilize
        time.sleep(0.5)
        
        # Set to UART control mode
        print("\n2. Setting UART control mode...")
        success = pb.control_mode.set_control_mode(DEVICE_ID, CTRL_UART)
        if success:
            print("✅ UART mode set successfully")
        else:
            print("⚠ UART mode may have failed")
        
        time.sleep(0.3)
        
        # Reset to known state
        print("\n3. Resetting to known state...")
        pb.color.set_all_leds_color(DEVICE_ID, 'OFF')
        time.sleep(0.3)
        pb.luminosity.set_all_luminosity(DEVICE_ID, 0)
        time.sleep(0.3)
        
        # Test individual LED control with firmware timing
        print("\n4. Testing individual LED control...")
        
        led_sequence = [
            (LED_UR, 'RED', 'Upper Right RED'),
            (LED_UL, 'GREEN', 'Upper Left GREEN'),
            (LED_LR, 'BLUE', 'Lower Right BLUE'), 
            (LED_LL, 'WHITE', 'Lower Left WHITE')
        ]
        pb.luminosity.set_all_luminosity(DEVICE_ID, 100)
        time.sleep(0.3)

        for led_pos, color, description in led_sequence:
            print(f"   Setting {description}")
            success = pb.color.set_led_color(DEVICE_ID, led_pos, color)
            if success:
                print(f"   ✅ {description} - Success")
            else:
                print(f"   ⚠ {description} - May have failed")
            time.sleep(0.3)  # Match firmware processing time
        
        # Test color sequences
        print("\n5. Testing color sequences...")
        colors = ['RED', 'GREEN', 'BLUE', 'ORANGE', 'CYAN', 'MAGENTA']
        
        for color in colors:
            print(f"   Setting all LEDs to {color}")
            success = pb.color.set_all_leds_color(DEVICE_ID, color)
            if success:
                print(f"   ✅ {color} - Success")
            else:
                print(f"   ⚠ {color} - May have failed")
            time.sleep(0.3)  # Allow firmware to process
        
        # Test luminosity control
        print("\n6. Testing luminosity control...")
        pb.color.set_all_leds_color(DEVICE_ID, 'WHITE')
        time.sleep(0.3)

        luminosity_levels = [100, 75, 50, 25, 10, 25, 50, 75, 100]
        for level in luminosity_levels:
            print(f"   Setting luminosity to {level}%")
            success = pb.luminosity.set_all_luminosity(DEVICE_ID, level)
            if success:
                print(f"   ✅ {level}% - Success")
            else:
                print(f"   ⚠ {level}% - May have failed")
            time.sleep(0.3)
        
        # Final state
        print("\n7. Setting final state...")
        pb.color.set_all_leds_color(DEVICE_ID, 'RED')
        time.sleep(0.3)
        #pb.luminosity.set_all_luminosity(DEVICE_ID, 70)
        #time.sleep(0.3)

        pb.color.set_all_leds_color(DEVICE_ID, 'WHITE')
        time.sleep(0.3)
        #pb.luminosity.set_all_luminosity(DEVICE_ID, 70)
        #time.sleep(0.3)

        pb.color.set_all_leds_color(DEVICE_ID, 'GREEN')
        time.sleep(0.3)
        #pb.luminosity.set_all_luminosity(DEVICE_ID, 70)
        #time.sleep(0.3)

        print("\n" + "=" * 50)
        print("🎉 Firmware-synchronized demo completed successfully!")
        print("All commands executed with proper timing and protocol")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean shutdown
        print("\n🧹 Cleaning up...")
        try:
            if pb.is_connected():
                pb.color.set_all_leds_color(DEVICE_ID, 'OFF')
                time.sleep(0.2)
        except:
            pass
        
        pb.disconnect()
        print("✅ Disconnected from firmware")

if __name__ == "__main__":
    firmware_sync_demo()