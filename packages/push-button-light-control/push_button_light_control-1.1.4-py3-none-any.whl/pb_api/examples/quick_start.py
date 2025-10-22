#!/usr/bin/env python3
"""
Basic usage example for Push Button Light Control API
Fixed connection and error handling
"""

import time
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pb_api import PushButtonLightControl, CTRL_UART, CTRL_SW_LUMIN, LED_UR, LED_UL, LED_LR, LED_LL

def main():
    print("Starting Push Button Light Control Demo")
    print("=" * 40)
    
    # Initialize API with longer timeout
    pb = PushButtonLightControl('COM6', timeout=3.0)  # Change port as needed
    
    try:
        # Connect to device
        print("1. Connecting to device...")
        if pb.connect():
            print("✓ Connected successfully!")
        else:
            print("✗ Connection failed, but continuing anyway...")
            # Don't return - try to continue
        
        # Small delay after connection
        time.sleep(1.0)
        
        # Set to UART control mode
        print("\n2. Setting UART control mode...")
        try:
            success = pb.control_mode.set_control_mode(1, CTRL_UART)
            time.sleep(0.3)
            if success:
                print("✓ Control mode set successfully")
            else:
                print("⚠ Control mode setting may have failed, continuing...")
        except Exception as e:
            print(f"⚠ Control mode error: {e}, continuing...")

        pb.color.set_all_leds_color(1, 'OFF')
        time.sleep(0.3)
        pb.luminosity.set_all_luminosity(1, 0)
        time.sleep(1.0)
        
        # Set LED colors
        print("\n3. Setting LED colors...")

        try:
            pb.luminosity.set_all_luminosity(1, 100)
            time.sleep(0.3)

            print("\n3. Testing multiple LED colors simultaneously...")

            # Method 1: Using set_multiple_leds_color
            print("\n--- Method 1: Set multiple LEDs at once ---")
            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'OFF', 
                LED_LR: 'OFF',
                LED_LL: 'OFF'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ One LED")
            time.sleep(0.5)

            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'GREEN', 
                LED_LR: 'OFF',
                LED_LL: 'OFF'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ Two LEDS")
            time.sleep(0.5)            

            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'GREEN', 
                LED_LR: 'BLUE',
                LED_LL: 'OFF'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ Three LEDs")
            time.sleep(0.5)

            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'GREEN', 
                LED_LR: 'BLUE',
                LED_LL: 'WHITE'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ All 4 LEDs set to different colors simultaneously")
            time.sleep(0.5)

            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'GREEN', 
                LED_LR: 'BLUE',
                LED_LL: 'OFF'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ Three LEDs")
            time.sleep(0.5)

            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'GREEN', 
                LED_LR: 'OFF',
                LED_LL: 'OFF'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ Two LEDS")
            time.sleep(0.5) 

            led_colors = {
                LED_UR: 'RED',
                LED_UL: 'OFF', 
                LED_LR: 'OFF',
                LED_LL: 'OFF'
            }
            success = pb.color.set_multiple_leds_color(1, led_colors)
            if success:
                print("✓ One LED")
            time.sleep(0.5)

            # Reset state
            pb.color.reset_state()

            pb.color.set_led_color_preserve(1, LED_UR, 'GREEN')
            print("✓ UR LED set to GREEN")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_UL, 'ORANGE')
            print("✓ UL LED set to ORANGE")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_LL, 'RED')
            print("✓ LL LED set to RED")
            time.sleep(0.2)
            
            pb.color.set_led_color_preserve(1, LED_LR, 'MAGENTA')
            print("✓ LR LED set to MAGENTA")  
            time.sleep(0.2)
            
            pb.color.set_led_color_preserve(1, LED_UR, 'BLUE')
            print("✓ UR LED set to BLUE")
            time.sleep(0.2)
            
            pb.color.set_led_color_preserve(1, LED_UL, 'CYAN')
            print("✓ UL LED set to CYAN")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_LL, 'WHITE')
            print("✓ LL LED set to WHITE")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_LR, 'CYAN')
            print("✓ LR LED set to CYAN")  
            time.sleep(0.2)

            #######
            pb.color.set_led_color_preserve(1, LED_UR, 'GREEN')
            print("✓ UR LED set to GREEN")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_UL, 'ORANGE')
            print("✓ UL LED set to ORANGE")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_LL, 'RED')
            print("✓ LL LED set to RED")
            time.sleep(0.2)
            
            pb.color.set_led_color_preserve(1, LED_LR, 'MAGENTA')
            print("✓ LR LED set to MAGENTA")  
            time.sleep(0.2)
            
            pb.color.set_led_color_preserve(1, LED_UR, 'BLUE')
            print("✓ UR LED set to BLUE")
            time.sleep(0.2)
            
            pb.color.set_led_color_preserve(1, LED_UL, 'CYAN')
            print("✓ UL LED set to CYAN")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_LL, 'WHITE')
            print("✓ LL LED set to WHITE")
            time.sleep(0.2)

            pb.color.set_led_color_preserve(1, LED_LR, 'CYAN')
            print("✓ LR LED set to CYAN")  
            time.sleep(0.2)

            # Then set each LED one by one (they should accumulate)
            pb.color.set_led_color(1, LED_UR, 'RED')
            print("✓ UR LED set to RED")
            time.sleep(0.5)
            
            pb.color.set_led_color(1, LED_UL, 'GREEN')
            print("✓ UL LED set to GREEN") 
            time.sleep(0.5)
            
            pb.color.set_led_color(1, LED_LL, 'BLUE')
            print("✓ LR LED set to BLUE")
            time.sleep(0.5)
            
            pb.color.set_led_color(1, LED_LR, 'WHITE')
            print("✓ LL LED set to WHITE")
            time.sleep(0.5)

            print("\nSetting LED luminosity...")

            # Set all LEDs to same color and brightness
            #print("\nSetting all LEDs to blue at 100%...")
            pb.color.set_all_leds_color(1, 'BLUE')
            time.sleep(0.2)

            #print("\nSetting all LEDs to red at 100%...")
            pb.color.set_all_leds_color(1, 'RED')
            time.sleep(0.2)
            
            #print("\nSetting all LEDs to green at 100%...")
            pb.color.set_all_leds_color(1, 'GREEN')
            time.sleep(0.2)

            pb.color.set_all_leds_color(1, 'BLUE')
            time.sleep(0.2)

            #print("\nSetting all LEDs to red at 100%...")
            pb.color.set_all_leds_color(1, 'RED')
            time.sleep(0.2)
            
            #print("\nSetting all LEDs to green at 100%...")
            pb.color.set_all_leds_color(1, 'GREEN')
            time.sleep(0.2)

        except Exception as e:
            print(f"⚠ Color setting error: {e}")
        
        # Set luminosity
        print("\n4. Setting luminosity to MAX...")
        try:
            pb.color.set_all_leds_color(1, 'WHITE')
            time.sleep(0.2)
            pb.luminosity.set_all_luminosity(1, 100)
            print("✓ Luminosity set to 100%")
            time.sleep(0.2)
        except Exception as e:
            print(f"⚠ Luminosity error: {e}")
        
        # Test presets
        print("\n5. Testing presets...")
        presets = ["DAY", "NIGHT", "OFF"]
        
        for preset in presets:
            try:
                pb.luminosity.set_luminosity_preset(1, preset)
                print(f"✓ Preset {preset} set")
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠ Preset {preset} error: {e}")
        
        print("\n" + "=" * 40)
        print("Demo completed!")
        
    except Exception as e:
        print(f"\n💥 Demo failed with exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pb.disconnect()
        print("Disconnected from device")

if __name__ == "__main__":
    main()