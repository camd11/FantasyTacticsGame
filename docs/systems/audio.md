# Audio System

This document provides information about the audio system in the Fantasy Tactics Game.

## Overview

The game's audio system handles sound effects for various game actions and animations. Sound effects add feedback and immersion to the gameplay experience. The current implementation focuses on gameplay sound effects, with potential for music implementation in the future.

The audio system is integrated with the game's three-component testing vision, providing auditory feedback that complements the visual and logging components.

## Sound Effects

Sound effects are played during specific game actions:

| Sound Name | Description | Trigger |
|------------|-------------|---------|
| `move`     | Unit movement sound | When a unit moves on the map |
| `attack`   | Attack initiation | When a unit attacks an enemy |
| `damage`   | Impact/damage sound | When a unit takes damage |
| `heal`     | Healing sound | When a unit is healed |
| `status`   | Status effect sound | When a status effect is applied or removed |
| `menu`     | Menu navigation | When a menu is opened |
| `select`   | Selection sound | When an option is selected |
| `cancel`   | Cancel sound | When an action is canceled |

## Implementation

### Sound Files

Sound effect files are stored in the `assets/sounds/` directory as WAV files. Each sound has a specific name that matches its function (e.g., `attack.wav`).

### Sound Integration with Animations

Sound effects are integrated with the animation system:

1. The base `Animation` class accepts a `sound_effect` parameter and handles playing it during animation updates
2. Each animation subclass (e.g., `MoveAnimation`, `AttackAnimation`) receives the appropriate sound effect
3. The `GameRenderer.play_animation()` method determines which sound effect to use based on the animation type
4. Sounds are played exactly once during each animation by tracking the `sound_played` flag

### Configuration

Sound settings are controlled by two constants in `src/ui/pygame_renderer.py`:

```python
# Sound configuration
SOUND_ENABLED = True  # Master toggle for all sounds
SOUND_VOLUME = 0.7    # Global volume level (0.0 to 1.0)
```

To disable sounds entirely, set `SOUND_ENABLED = False`.

## Testing Sound Effects

You can test all sound effects by running:

```bash
python test_sound_effects.py
```

This script will load and play each sound effect in sequence, confirming that all files are present and properly formatted.

## Integration with the Three-Component Testing Vision

The audio system plays a key role in the project's three-component testing approach:

1. **Standard Logging**: Sound effect playback events are logged to provide a record of when audio should trigger.
2. **Visual Logs**: Audio events are noted in the visual logs to correlate with game state changes.
3. **Pygame Visuals**: Audio provides immediate feedback synchronized with visual events.

When developing or modifying features, ensure that sound effects are properly integrated into all three components.

## Future Enhancements

Planned future enhancements for the audio system include:

1. **Background Music** - Adding music tracks for different game states (battles, menus, etc.)
2. **Volume Controls** - Separate volume sliders for music and sound effects 
3. **Sound Variations** - Multiple variations of each sound effect for more variety
4. **Spatial Audio** - Positioning sounds based on their location on the map
5. **Audio Settings Menu** - In-game menu for adjusting audio preferences
6. **Enhanced Sound Integration** - Adding more sound effects for specific skill activations and special events 