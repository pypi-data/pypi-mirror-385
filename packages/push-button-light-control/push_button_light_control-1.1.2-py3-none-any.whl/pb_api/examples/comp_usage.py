#!/usr/bin/env python3
"""
Comprehensive usage example for PB_API with all functions
"""
'''

import time
import sys
import os

# Add the parent directory to the path so we can import pb_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pb_api import PB_API, CTRL_UART, LED_UR, LED_UL, LED_LR, LED_LL
import time
from pb_api import PushButtonLightControl, CTRL_UART, CTRL_SW_LUMIN, LED_UR, LED_UL, LED_LR, LED_LL
from pb_api import PushButtonProtocol
from pb_api.core.constants import ACK_SUCCESS, BROADCAST_ID

def response_callback(data):
    """Handle response callbacks"""
    print(f"Response: {data}")

def error_callback(data):
    """Handle error callbacks"""
    print(f"Error: {data}")

def main():
    # Initialize API
    api = PB_API(port='COM3', baudrate=115200)  # Change port as needed
    
    # Register callbacks
    api.register_callback('response_received', response_callback)
    api.register_callback('error', error_callback)
    
    try:
        # Connect to device
        print("Connecting to device...")
        if not api.connect():
            print("Failed to connect to device")
            return
        
        print("Connected successfully!")
        
        # 1. Set to UART control mode
        print("\n1. Setting UART control mode...")
        if api.control_mode.set_control_mode(device_id=1, control_mode=CTRL_UART):
            print("Control mode set successfully")
        else:
            print("Failed to set control mode")
            return
        
        time.sleep(0.5)
        
        # 2. Set LED colors using DC values directly (0-63)
        print("\n2. Setting LED colors using DC values...")
        api.color.set_led_color(1, LED_UR, 'RED')
        time.sleep(0.5)
        api.color.set_led_color(1, LED_UL, 'GREEN')
        time.sleep(0.5)
        api.color.set_led_color(1, LED_LR, 'BLUE')
        time.sleep(0.5)
        api.color.set_led_color(1, LED_LL, 'WHITE')
        time.sleep(1.0)
        
        # 3. Set custom RGB using DC values (0-63)
        print("\n3. Setting custom RGB using DC values...")
        api.color.set_custom_rgb_dc(1, LED_UR, 63, 31, 0)  # Orange
        time.sleep(1.0)
        
        # 4. Set individual LED luminosity - CORRECTED FUNCTION CALL
        print("\n4. Setting individual LED luminosity...")
        print("Setting UR LED to 100%")
        success = api.luminosity.set_led_luminosity(1, LED_UR, 100)
        print(f"UR LED set: {success}")
        time.sleep(1.0)
        
        print("Setting UL LED to 75%")
        success = api.luminosity.set_led_luminosity(1, LED_UL, 75)
        print(f"UL LED set: {success}")
        time.sleep(1.0)
        
        print("Setting LR LED to 50%")
        success = api.luminosity.set_led_luminosity(1, LED_LR, 50)
        print(f"LR LED set: {success}")
        time.sleep(1.0)
        
        print("Setting LL LED to 25%")
        success = api.luminosity.set_led_luminosity(1, LED_LL, 25)
        print(f"LL LED set: {success}")
        time.sleep(1.0)
        
        # 5. Set all LEDs to same luminosity
        print("\n5. Setting all LEDs to 80% luminosity...")
        api.luminosity.set_all_luminosity(1, 80)
        time.sleep(2.0)
        
        # 6. Use luminosity presets
        print("\n6. Testing luminosity presets...")
        api.luminosity.set_luminosity_preset(1, "NIGHT")
        time.sleep(1.0)
        api.luminosity.set_luminosity_preset(1, "DAY")
        time.sleep(1.0)
        api.luminosity.set_luminosity_preset(1, "MAX")
        time.sleep(1.0)
        
        # 7. Set all LEDs to same color
        print("\n7. Setting all LEDs to CYAN...")
        api.color.set_all_leds_color(1, "CYAN")
        time.sleep(2.0)
        
        # 8. Fade luminosity
        print("\n8. Fading luminosity from 0% to 100%...")
        api.luminosity.fade_luminosity(1, 0, 100, steps=20, delay=0.1)
        
        # 9. Set luminosity presets for switch mode
        print("\n9. Setting luminosity presets for switch mode...")
        api.system_config.set_luminosity_percentages(1, 100, 50, 20)
        time.sleep(1.0)
        
        # 10. Turn off all LEDs
        print("\n10. Turning off all LEDs...")
        api.luminosity.set_luminosity_preset(1, "OFF")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        api.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()

'''

"""
Robust demo for Push Button Light Control API
With comprehensive error handling and retry logic
"""

import time
import sys
from pb_api import PushButtonLightControl, CTRL_UART, LED_UR, LED_UL, LED_LR, LED_LL

class RobustDemoController:
    def __init__(self, port):
        # Initialize with longer timeout and retry mechanism
        self.pb = PushButtonLightControl(port, timeout=3.0, retry_count=3)
        self.setup_callbacks()
        self.demo_success = True
        
    def setup_callbacks(self):
        """Setup comprehensive event callbacks"""
        self.pb.register_callback('response_received', self.on_response)
        self.pb.register_callback('error', self.on_error)
        
    def on_response(self, data):
        """Handle device responses"""
        response_type = data.get('type', 'unknown')
        
        if response_type == 'firmware_ack':
            firmware_version = data.get('firmware_version', 'Unknown')
            print(f"  → Firmware: {firmware_version}.0")
            
        elif response_type == 'command_response':
            response_code = data.get('response_code')
            if response_code == 0xDD:  # ACK_SUCCESS
                print("  → ✓ Command acknowledged")
            else:
                print(f"  → ✗ Command rejected: 0x{response_code:02x}")
                self.demo_success = False
                
        elif response_type in ['control_mode_response', 'setting_response', 'operating_response']:
            print(f"  → ✓ {response_type} received")
            
        elif response_type == 'unknown_single_byte':
            # Ignore normal per-byte ACKs
            pass
            
        else:
            print(f"  → ? Unknown response: {data}")
        
    def on_error(self, data):
        """Handle errors"""
        error_msg = data.get('error', 'Unknown error')
        print(f"  → ✗ Error: {error_msg}")
        self.demo_success = False
    
    def execute_command_with_retry(self, command_func, command_name, *args, max_retries=2, delay=0.5):
        """Execute a command with retry logic"""
        for attempt in range(max_retries + 1):
            try:
                print(f"  Executing: {command_name} (attempt {attempt + 1})")
                success = command_func(*args)
                
                if success:
                    print(f"  → ✓ {command_name} completed")
                    return True
                else:
                    if attempt < max_retries:
                        print(f"  → ⚠ {command_name} failed, retrying...")
                        time.sleep(delay)
                    else:
                        print(f"  → ✗ {command_name} failed after {max_retries + 1} attempts")
                        self.demo_success = False
                        return False
                        
            except Exception as e:
                if attempt < max_retries:
                    print(f"  → ⚠ {command_name} exception: {e}, retrying...")
                    time.sleep(delay)
                else:
                    print(f"  → ✗ {command_name} failed with exception: {e}")
                    self.demo_success = False
                    return False
        return False
    
    def run_demo(self):
        """Run the demo sequence with comprehensive error handling"""
        print("🚀 Starting Robust Push Button Light Control Demo")
        print("=" * 50)
        
        try:
            # Step 1: Connect to device
            print("\n1. Connecting to device...")
            if not self.pb.connect():
                print("✗ Failed to connect to device")
                return False
            print("✓ Connected successfully!")
            
            # Small delay after connection
            time.sleep(1.0)
            
            # Step 2: Set control mode
            print("\n2. Setting UART control mode...")
            if not self.execute_command_with_retry(
                self.pb.control_mode.set_control_mode, 
                "Set Control Mode", 1, CTRL_UART
            ):
                return False
            time.sleep(1.0)  # Important: Give device time to switch modes
            
            # Step 3: Set individual LED colors
            print("\n3. Setting individual LED colors...")
            color_commands = [
                ("UR LED to RED", lambda: self.pb.color.set_led_color(1, LED_UR, 'RED')),
                ("UL LED to GREEN", lambda: self.pb.color.set_led_color(1, LED_UL, 'GREEN')),
                ("LR LED to BLUE", lambda: self.pb.color.set_led_color(1, LED_LR, 'BLUE')),
                ("LL LED to WHITE", lambda: self.pb.color.set_led_color(1, LED_LL, 'WHITE')),
            ]
            
            for desc, command in color_commands:
                if not self.execute_command_with_retry(command, desc):
                    print(f"⚠ Continuing despite {desc} failure")
                time.sleep(0.5)  # Crucial: Delay between color commands
            
            # Step 4: Set luminosity for all LEDs
            print("\n4. Setting maximum luminosity...")
            if not self.execute_command_with_retry(
                self.pb.luminosity.set_all_luminosity,
                "Set All Luminosity", 1, 100
            ):
                print("⚠ Continuing despite luminosity setting failure")
            time.sleep(2.0)
            
            # Step 5: Test color cycling
            print("\n5. Testing color cycling...")
            colors = ['RED', 'GREEN', 'BLUE', 'WHITE', 'CYAN', 'MAGENTA']
            
            for color in colors:
                print(f"  Setting all LEDs to {color}")
                if self.execute_command_with_retry(
                    self.pb.color.set_all_leds_color,
                    f"Set {color}", 1, color
                ):
                    time.sleep(1.5)
                else:
                    print(f"⚠ Skipping {color} due to failure")
            
            # Step 6: Test luminosity presets
            print("\n6. Testing luminosity presets...")
            presets = [
                ("OFF", 0),
                ("NIGHT", 20), 
                ("DAY", 50),
                ("MAX", 100)
            ]
            
            for preset_name, expected_level in presets:
                print(f"  Setting {preset_name} preset")
                if self.execute_command_with_retry(
                    self.pb.luminosity.set_luminosity_preset,
                    f"Set {preset_name}", 1, preset_name
                ):
                    time.sleep(1.5)
                else:
                    print(f"⚠ Skipping {preset_name} preset due to failure")
            
            # Step 7: Test individual luminosity control
            print("\n7. Testing individual LED luminosity...")
            luminosity_commands = [
                ("UR LED to 100%", lambda: self.pb.luminosity.set_led_luminosity(1, LED_UR, 100)),
                ("UL LED to 75%", lambda: self.pb.luminosity.set_led_luminosity(1, LED_UL, 75)),
                ("LR LED to 50%", lambda: self.pb.luminosity.set_led_luminosity(1, LED_LR, 50)),
                ("LL LED to 25%", lambda: self.pb.luminosity.set_led_luminosity(1, LED_LL, 25)),
            ]
            
            for desc, command in luminosity_commands:
                if self.execute_command_with_retry(command, desc):
                    time.sleep(1.0)
                else:
                    print(f"⚠ Skipping {desc} due to failure")
            
            # Final step: Turn off all LEDs
            print("\n8. Turning off all LEDs...")
            self.execute_command_with_retry(
                self.pb.luminosity.set_luminosity_preset,
                "Turn Off LEDs", 1, "OFF"
            )
            time.sleep(1.0)
            
            # Demo summary
            print("\n" + "=" * 50)
            if self.demo_success:
                print("🎉 DEMO COMPLETED SUCCESSFULLY!")
            else:
                print("⚠ Demo completed with some errors, but majority worked")
            
            return self.demo_success
            
        except Exception as e:
            print(f"\n💥 DEMO FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.pb.disconnect()
            print("🔌 Disconnected from device")

def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = 'COM6'  # Change to your actual port
    
    print(f"Targeting port: {port}")
    
    # Run the robust demo
    controller = RobustDemoController(port)
    success = controller.run_demo()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
