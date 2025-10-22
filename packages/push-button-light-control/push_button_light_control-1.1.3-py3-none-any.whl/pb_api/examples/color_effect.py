#!/usr/bin/env python3
"""
Quick Color Effects Demo - Simple version for testing
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pb_api import PushButtonLightControl, CTRL_UART

def main():
    print("Quick Color Effects Demo")
    
    pb = PushButtonLightControl('COM6', timeout=3.0)  # Change port
    
    try:
        if not pb.connect():
            print("Connection warning, continuing...")
        
        time.sleep(1.0)
        pb.control_mode.set_control_mode(1, CTRL_UART)
        pb.luminosity.set_all_luminosity(1, 100)
        time.sleep(1.0)
        
        print("1. Quick Rainbow")
        pb.color.rainbow_cycle(1, cycles=1, duration_per_cycle=5.0)
        time.sleep(1.0)
        
        print("2. Breathing Blue")
        pb.color.breathing_effect(1, (0, 0, 44), breaths=1, breath_duration=2.0)
        time.sleep(1.0)

        print("2. Breathing Green")
        pb.color.breathing_effect(1, (44, 0, 0), breaths=1, breath_duration=2.0)
        time.sleep(1.0)

        print("2. Breathing Red")
        pb.color.breathing_effect(1, (0, 44, 0), breaths=1, breath_duration=2.0)
        time.sleep(1.0)        

        print("3. Color Wave")
        colors = [(44, 0, 0), (0, 44, 0), (0, 0, 44)]
        pb.color.color_wave(1, colors, wave_duration=10.0)
        time.sleep(1.0)
        
        print("Demo completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pb.disconnect()

if __name__ == "__main__":
    main()