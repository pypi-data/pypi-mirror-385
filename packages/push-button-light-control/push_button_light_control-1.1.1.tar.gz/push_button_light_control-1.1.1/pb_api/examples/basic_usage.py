#!/usr/bin/env python3
"""
Basic usage example for Push Button Light Control API
Improved version with better response handling
"""

import time
from pb_api import PushButtonLightControl, CTRL_UART, CTRL_SW_LUMIN, LED_UR, LED_UL, LED_LR, LED_LL
from pb_api import PushButtonProtocol
from pb_api.core.constants import ACK_SUCCESS, BROADCAST_ID


class DemoController:
    def __init__(self, port):
        self.pb = PushButtonLightControl(port)
        #self.setup_callbacks()
        self.command_count = 0
        self.success_count = 0

    '''    
    def setup_callbacks(self):
        """Setup event callbacks with better filtering"""
        self.pb.register_callback('response_received', self.on_response)
        self.pb.register_callback('error', self.on_error)
        
    def on_response(self, data):
        """Handle device responses with better filtering"""
        response_type = data.get('type')
        
        if response_type == 'firmware_ack':
            # These are normal - device acknowledges each byte received
            firmware_version = data.get('firmware_version', 'Unknown')
            print(f"Device firmware: {firmware_version}.0")
            
        elif response_type == 'command_response':
            # Final command response
            response_code = data.get('response_code')
            if response_code == ACK_SUCCESS:
                print("✓ Command executed successfully")
                self.success_count += 1
            else:
                error_msg = PushButtonProtocol.get_error_message(response_code)
                print(f"✗ Command failed: {error_msg}")
                
        elif response_type in ['control_mode_response', 'setting_response', 'operating_response']:
            # These are the main responses we care about
            print(f"✓ {response_type.replace('_', ' ').title()}: {data}")
            self.success_count += 1
            
        elif response_type == 'unknown_single_byte':
            # Ignore these - they're normal per-byte ACKs
            pass
            
        else:
            print(f"Other response: {data}")
            
        self.command_count += 1
        
    def on_error(self, data):
        """Handle errors"""
        error_msg = data.get('error', 'Unknown error')
        print(f"Error: {error_msg}")
    '''
    def run_demo(self):
        """Run the demo sequence"""
        try:
            # Connect to device
            print("Connecting to Push Button Light device...")
            if not self.pb.connect():
                print("Failed to connect to device")
                return False
            
            print("Connected successfully!")
            
            # Set to UART control mode
            print("Setting UART control mode...")
            #if self.pb.control_mode.set_control_mode(device_id=1, control_mode=CTRL_UART):
            #    print("Control mode set successfully")
            #else:
            #    print("Failed to set control mode")
            #    return False
            
            # Set LED colors - INTUITIVE COLOR METHODS
            print("\nSetting LED colors...")
            
            #print("Setting UR LED to RED")
            self.pb.color.set_led_color(1, LED_UR, 'RED')
            #time.sleep(1.0)
            self.pb.luminosity.set_luminosity_preset(1, "MAX")
            time.sleep(1.0)
            
            #print("Setting UL LED to GREEN")  
            self.pb.color.set_led_color(1, LED_UL, 'GREEN')
            #time.sleep(1.0)
            self.pb.luminosity.set_luminosity_preset(1, "MAX")
            time.sleep(1.0)
            
            #print("Setting LR LED to BLUE")
            self.pb.color.set_led_color(1, LED_LR, 'BLUE')
            #time.sleep(1.0)
            self.pb.luminosity.set_luminosity_preset(1, "MAX")
            time.sleep(1.0)
            
            #print("Setting LL LED to WHITE")
            self.pb.color.set_led_color(1, LED_LL, 'WHITE')
            #time.sleep(1.0)
            self.pb.luminosity.set_luminosity_preset(1, "MAX")
            time.sleep(1.0)
            
            # Set LED luminosity - INTUITIVE LUMINOSITY METHODS
            print("\nSetting LED luminosity...")

            # Set all LEDs to same color and brightness
            #print("\nSetting all LEDs to blue at 100%...")
            self.pb.color.set_all_leds_color(1, 'BLUE')
            #time.sleep(1.0)
            self.pb.luminosity.set_all_luminosity(1, 100)
            time.sleep(1.0)

            #print("\nSetting all LEDs to red at 100%...")
            self.pb.color.set_all_leds_color(1, 'RED')
            #time.sleep(1.0)
            self.pb.luminosity.set_all_luminosity(1, 100)
            time.sleep(1.0)
            
            #print("\nSetting all LEDs to green at 100%...")
            self.pb.color.set_all_leds_color(1, 'GREEN')
            #time.sleep(1.0)
            self.pb.luminosity.set_all_luminosity(1, 100)
            time.sleep(1.0)

            #print("\nSetting all LEDs to white at 100%...")
            self.pb.color.set_all_leds_color(1, 'WHITE')
            #time.sleep(1.0)
            self.pb.luminosity.set_all_luminosity(1, 100)
            time.sleep(1.0)
            '''
            print("Setting UR LED to 100%")
            self.pb.luminosity.set_led_luminosity(1, LED_UR, 100)
            time.sleep(1.0)
            
            print("Setting UL LED to 75%")
            self.pb.luminosity.set_led_luminosity(1, LED_UL, 75)
            time.sleep(1.0)
            
            print("Setting LR LED to 50%")
            self.pb.luminosity.set_led_luminosity(1, LED_LR, 50)
            time.sleep(1.0)
            
            print("Setting LL LED to 25%")
            self.pb.luminosity.set_led_luminosity(1, LED_LL, 25)
            time.sleep(1)
            '''
            # Use luminosity presets
            print("\nUsing luminosity presets...")
            
            #print("Setting NIGHT preset (20%)")
            self.pb.luminosity.set_luminosity_preset(1, "NIGHT")
            time.sleep(1.0)
            
            #print("Setting DAY preset (50%)")
            self.pb.luminosity.set_luminosity_preset(1, "DAY")
            time.sleep(1.0)
            
            #print("Setting MAX preset (100%)")
            self.pb.luminosity.set_luminosity_preset(1, "MAX")
            time.sleep(1.0)

            # Turn off all LEDs
            print("\nTurning off all LEDs...")
            self.pb.luminosity.set_luminosity_preset(1, "OFF")
            
            # Print summary
            print(f"\n=== DEMO COMPLETED ===")
            #print(f"Commands sent: {self.command_count}")
            #print(f"Successful responses: {self.success_count}")
            print(f"Push Button Light Control demo completed successfully!")
            
            return True
            
        except Exception as e:
            print(f"Demo error: {e}")
            return False
        finally:
            self.pb.disconnect()
            print("Disconnected from Push Button device")

def main():
    # Run the demo on COM6 (change to your actual port)
    controller = DemoController('COM6')
    controller.run_demo()

if __name__ == "__main__":
    main()