#!/usr/bin/env python3
"""
Advanced Color Transition Demo for Push Button Light Control
Features smooth transitions, rainbow effects, and dynamic color patterns
"""

import time
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pb_api import PushButtonLightControl, CTRL_UART

class ColorTransitionDemo:
    def __init__(self, port):
        self.pb = PushButtonLightControl(port, timeout=3.0)
        
    def run_demo(self):
        """Run the comprehensive color transition demo"""
        print("🎨 Starting Advanced Color Transition Demo")
        print("=" * 50)
        
        try:
            # Connect to device
            print("\n1. Connecting to device...")
            if not self.pb.connect():
                print("Connection test failed, but continuing anyway...")
            
            time.sleep(1.0)
            
            # Set to UART control mode
            print("\n2. Setting UART control mode...")
            try:
                self.pb.control_mode.set_control_mode(1, CTRL_UART)
                print("✓ Control mode set")
            except:
                print("⚠ Control mode setting may have failed, continuing...")
            
            # Ensure maximum luminosity
            self.pb.color.set_all_leds_color(1, 'OFF')
            self.pb.luminosity.set_all_luminosity(1, 100)
            
            time.sleep(1)
            
            # Demo 1: Basic Color Transitions
            print("\n3. 🎨 Basic Color Transitions")
            print("   Transitioning between primary colors...")
            
            # Define some beautiful color transitions (RGB DC values 0-63)
            color_transitions = [
                ((44, 0, 0), (0, 44, 0)),    # Red to Green
                ((0, 44, 0), (0, 0, 44)),    # Green to Blue
                ((0, 0, 44), (44, 44, 0)),   # Blue to Yellow
                ((44, 44, 0), (44, 0, 44)),  # Yellow to Magenta
                ((44, 0, 44), (0, 44, 44)),  # Magenta to Cyan
                ((0, 44, 44), (44, 0, 0)),   # Cyan to Red
            ]
            
            for i, (start_color, end_color) in enumerate(color_transitions):
                print(f"   Transition {i+1}/6: {start_color} → {end_color}")
                self.pb.color.smooth_color_transition(1, start_color, end_color, duration=3.0)
                time.sleep(0.1)
            
            # Demo 2: Rainbow Cycle
            print("\n4. 🌈 Rainbow Cycle Effect")
            print("   Creating beautiful rainbow colors...")
            self.pb.color.rainbow_cycle(1, cycles=2, duration_per_cycle=8.0)
            time.sleep(0.1)
            
            # Demo 4: Color Wave
            print("\n6. 🌊 Color Wave")
            print("   Flowing through a spectrum of colors...")
            wave_colors = [
                (44, 0, 0),     # Red
                (44, 15, 0),    # Orange
                (44, 44, 0),    # Yellow
                (22, 44, 0),    # Lime
                (0, 44, 0),     # Green
                (0, 44, 22),    # Teal
                (0, 44, 44),    # Cyan
                (0, 22, 44),    # Light Blue
                (0, 0, 44),     # Blue
                (22, 0, 44),    # Purple
                (44, 0, 44),    # Magenta
                (44, 0, 22),    # Pink
            ]
            
            self.pb.color.color_wave(1, wave_colors, wave_duration=12.0)
            
            # Demo 5: Random Color Transitions
            print("\n7. 🎲 Random Color Transitions")
            print("   Exploring random color combinations...")
            self.pb.color.random_color_transition(1, transitions=8, transition_duration=1.0)
            
            # Demo 6: Temperature Colors
            print("\n8. 🌡️ Temperature-Based Colors")
            temperatures = ["warm", "cool", "daylight", "candle"]
            
            for temp in temperatures:
                print(f"   Setting {temp} white...")
                self.pb.color.temperature_colors(1, temp)
                time.sleep(0.1)
            
            # Demo 7: Custom Color Scenes
            print("\n9. 🎭 Custom Color Scenes")
            scenes = [
                ("Sunset", [(44, 20, 5), (44, 30, 7), (44, 15, 22)]),
                ("Ocean", [(5, 15, 30), (7, 22, 40), (10, 20, 38)]),
                ("Forest", [(7, 30, 11), (10, 38, 15), (15, 40, 19)]),
                ("Aurora", [(15, 30, 40), (22, 15, 42), (30, 38, 22)]),
            ]
            
            for scene_name, scene_colors in scenes:
                print(f"   {scene_name} scene...")
                for color in scene_colors:
                    self.pb.color.set_all_leds_rgb_dc(1, color[0], color[1], color[2])
                    time.sleep(0.1)
            
            # Finale: Grand Finale with multiple effects
            print("\n10. 🎉 Grand Finale")
            print("    Combining multiple effects...")
            
            # Quick rainbow
            self.pb.color.rainbow_cycle(1, cycles=1, duration_per_cycle=5.0)
            
            # Final smooth transition to warm white
            self.pb.color.smooth_color_transition(
                1, 
                start_color=(44, 44, 0),  # Yellow
                end_color=(44, 21, 7),   # Warm white
                duration=4.0
            )
            
            # Gentle breathing to end
            #self.pb.color.breathing_effect(1, (63, 30, 10), breaths=2, breath_duration=4.0)
            
            # Turn off gently
            self.pb.color.smooth_color_transition(
                1,
                start_color=(44, 15, 7),
                end_color=(0, 0, 0),
                duration=3.0
            )
            
            print("\n" + "=" * 50)
            print("🎊 Color Transition Demo Completed Successfully!")
            return True
            
        except Exception as e:
            print(f"\n💥 Demo failed with exception: {e}")
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
    
    # Run the color transition demo
    demo = ColorTransitionDemo(port)
    success = demo.run_demo()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()