#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sound Effects Test

This script loads and plays all sound effects to ensure they're working properly.
"""

import os
import sys
import time
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Sound settings
SOUND_VOLUME = 0.7  # 0.0 to 1.0
SOUND_NAMES = ['move', 'attack', 'damage', 'heal', 'status', 'menu', 'select', 'cancel']

def main():
    """Load and play all sound effects."""
    try:
        # Initialize pygame and mixer
        print("Initializing pygame...")
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_mode((400, 300))  # Small display window
        
        # Load sound effects
        print("\nLoading sound effects:")
        sounds = {}
        sounds_dir = os.path.join(PROJECT_ROOT, "assets", "sounds")
        
        for sound_name in SOUND_NAMES:
            file_path = os.path.join(sounds_dir, f"{sound_name}.wav")
            
            if os.path.exists(file_path):
                print(f"✓ Loading '{sound_name}'")
                sounds[sound_name] = pygame.mixer.Sound(file_path)
                sounds[sound_name].set_volume(SOUND_VOLUME)
            else:
                print(f"✗ Missing '{sound_name}' sound file: {file_path}")
        
        # Play each sound effect
        print("\nPlaying sound effects:")
        for name, sound in sounds.items():
            print(f"► Playing '{name}'...")
            sound.play()
            time.sleep(1.5)  # Wait a bit for sound to play
        
        print("\nAll sound effects tested!")
        
    except Exception as e:
        print(f"Error testing sound effects: {e}")
    finally:
        pygame.quit()
        print("Test completed.")

if __name__ == "__main__":
    main() 