#!/usr/bin/env python3
"""
Script to generate simple sound effects for the game
"""

import os
import numpy as np
from scipy.io import wavfile

# Ensure directory exists
os.makedirs("assets/sounds", exist_ok=True)

# Sample rate (samples per second)
sample_rate = 44100

# Function to create a simple tone
def create_tone(freq, duration, volume=0.5, fade=0.1):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * 2 * np.pi * t) * volume
    
    # Apply fade in and fade out
    fade_samples = int(fade * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    # Apply fades
    if len(tone) > 2 * fade_samples:
        tone[:fade_samples] *= fade_in
        tone[-fade_samples:] *= fade_out
    
    return tone

# Create move sound (rising tone)
def create_move_sound():
    start_freq = 220
    end_freq = 440
    duration = 0.4
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create frequency array that increases over time
    freq = np.linspace(start_freq, end_freq, len(t))
    
    # Create the tone with varying frequency
    tone = np.sin(2 * np.pi * freq * t / sample_rate) * 0.4
    
    # Apply fade in and fade out
    fade_samples = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    tone[:fade_samples] *= fade_in
    tone[-fade_samples:] *= fade_out
    
    return tone

# Create attack sound (sharp noise)
def create_attack_sound():
    duration = 0.3
    noise = np.random.uniform(-0.7, 0.7, int(sample_rate * duration))
    
    # Apply envelope
    envelope = np.exp(-np.linspace(0, 10, len(noise)))
    noise *= envelope
    
    # Add a tone
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(300 * 2 * np.pi * t) * 0.3 * envelope
    
    return noise + tone

# Create damage sound (descending tone with noise)
def create_damage_sound():
    start_freq = 500
    end_freq = 200
    duration = 0.5
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create frequency array that decreases over time
    freq = np.linspace(start_freq, end_freq, len(t))
    
    # Create the tone with varying frequency
    tone = np.sin(2 * np.pi * freq * t / sample_rate) * 0.5
    
    # Add noise
    noise = np.random.uniform(-0.3, 0.3, len(tone))
    noise *= np.exp(-np.linspace(0, 8, len(noise)))
    
    return tone + noise

# Create heal sound (pleasant ascending chords)
def create_heal_sound():
    duration = 0.6
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create base tone
    tone1 = np.sin(440 * 2 * np.pi * t) * 0.3
    tone2 = np.sin(550 * 2 * np.pi * t) * 0.2
    tone3 = np.sin(660 * 2 * np.pi * t) * 0.15
    
    # Create envelope that rises and falls
    envelope = np.sin(np.pi * t / duration)
    
    combined = (tone1 + tone2 + tone3) * envelope
    return combined

# Create status effect sound (wobbling tone)
def create_status_sound():
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create wobbling frequency
    wobble = 5 + 10 * np.sin(2 * np.pi * 8 * t)
    freq = 350 + wobble
    
    # Create tone with wobbling frequency
    tone = np.sin(2 * np.pi * freq * t) * 0.4
    
    # Apply envelope
    envelope = np.exp(-np.linspace(0, 4, len(tone)))
    tone *= envelope
    
    return tone

# Create menu sound (simple click)
def create_menu_sound():
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    tone = np.sin(1200 * 2 * np.pi * t) * 0.3
    
    # Sharp attack, quick decay
    envelope = np.exp(-np.linspace(0, 20, len(tone)))
    tone *= envelope
    
    return tone

# Create select sound (pleasant ping)
def create_select_sound():
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    tone1 = np.sin(880 * 2 * np.pi * t) * 0.3
    tone2 = np.sin(1100 * 2 * np.pi * t) * 0.15
    
    # Bell-like envelope
    envelope = np.exp(-np.linspace(0, 10, len(tone1)))
    combined = (tone1 + tone2) * envelope
    
    return combined

# Create cancel sound (descending ping)
def create_cancel_sound():
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Descending frequency
    freq = np.linspace(800, 400, len(t))
    tone = np.sin(2 * np.pi * freq * t / sample_rate) * 0.35
    
    # Apply envelope
    envelope = np.exp(-np.linspace(0, 8, len(tone)))
    tone *= envelope
    
    return tone

# Generate and save all sounds
sounds = {
    'move': create_move_sound(),
    'attack': create_attack_sound(),
    'damage': create_damage_sound(),
    'heal': create_heal_sound(),
    'status': create_status_sound(),
    'menu': create_menu_sound(),
    'select': create_select_sound(),
    'cancel': create_cancel_sound()
}

for name, sound_data in sounds.items():
    # Convert to 16-bit data
    sound_data_16bit = (sound_data * 32767).astype(np.int16)
    
    # Save the audio file
    wavfile.write(f"assets/sounds/{name}.wav", sample_rate, sound_data_16bit)
    print(f"Created sound effect: assets/sounds/{name}.wav")

print("All sound effects created successfully!") 