# Fantasy Tactics Game CLI Design

This document outlines the design of the Command Line Interface (CLI) for the Fantasy Tactics Game. The CLI serves as the primary interface for the text-based implementation of the game, allowing players to interact with the game through text commands.

## Overview

The CLI is designed to be:

1. **Intuitive**: Commands follow a logical structure and are easy to remember
2. **Informative**: Provides clear feedback and information about the game state
3. **Efficient**: Allows quick execution of common actions
4. **Testable**: Supports automated testing and debugging
5. **Extensible**: Can be easily extended with new commands

## Command Structure

Commands follow a consistent structure:

```
<command> [subcommand] [arguments]
```

For example:
```
move 5,5 6,6
attack 6,6 7,6
use vulnerary
```

## Display Elements

The CLI displays the following elements:

### Map Display

The map is displayed as a grid of ASCII characters, with different characters representing different terrain types, units, and objects.

```
+-------------------+
|..^^...|          G|
|..^^...|           |
|P......|           |
|.E.....|           |
|.......|           |
|.......|           |
|.......|           |
+-------------------+

Legend:
. = Plain
^ = Mountain
| = Wall
P = Player Unit
E = Enemy Unit
G = Gate (Objective)
```

### Unit Information

Unit information is displayed in a compact format:

```
Leif (Lord) [5,5] HP: 22/22 Fatigue: 0
Equipped: Light Brand (60/60)
Inventory: Light Brand, Iron Sword, Vulnerary
```

### Combat Forecast

When initiating combat, a forecast is displayed:

```
Combat Forecast:
Leif (Light Brand) vs Enemy Soldier (Iron Lance)
Leif: HP 22/22, Hit 85%, Dmg 8, Crit 12%, x2
Enemy: HP 20/20, Hit 65%, Dmg 4, Crit 0%
```

### Turn Information

The current turn and phase are displayed at the top of the screen:

```
Turn 1 - Player Phase
```

## Command Categories

Commands are organized into the following categories:

### Navigation Commands

- `help`: Display help information
- `map`: Display the map
- `info <x,y>`: Display information about a unit or terrain at the specified coordinates
- `status [unit_id]`: Display detailed status of a unit
- `list units`: List all player units
- `list enemies`: List all enemy units
- `list items`: List all items in the player's inventory

### Unit Action Commands

- `move <from_x,from_y> <to_x,to_y>`: Move a unit from one position to another
- `attack <from_x,from_y> <to_x,to_y>`: Attack an enemy at the specified coordinates
- `capture <from_x,from_y> <to_x,to_y>`: Attempt to capture an enemy
- `release <x,y>`: Release a captured enemy
- `trade <unit1_x,unit1_y> <unit2_x,unit2_y>`: Trade items between two adjacent units
- `use <item_name> [target_x,target_y]`: Use an item, optionally specifying a target
- `equip <x,y> <item_name>`: Equip an item to a unit
- `wait <x,y>`: End a unit's turn
- `rescue <rescuer_x,rescuer_y> <target_x,target_y>`: Rescue another unit
- `drop <x,y> <direction>`: Drop a rescued unit in the specified direction
- `take <taker_x,taker_y> <holder_x,holder_y>`: Take a rescued/captured unit from another unit
- `visit <x,y>`: Visit a village or house
- `open <x,y>`: Open a door or chest
- `seize <x,y>`: Seize an objective (Lord only)
- `talk <talker_x,talker_y> <target_x,target_y>`: Initiate a conversation with another unit
- `dismount <x,y>`: Dismount a mounted unit
- `mount <x,y>`: Mount a dismounted unit

### Turn Management Commands

- `end turn`: End the current player phase
- `auto end`: Automatically end turn when all units have acted

### Game Management Commands

- `save <filename>`: Save the game
- `load <filename>`: Load a saved game
- `restart`: Restart the current chapter
- `quit`: Quit the game

### Debug Commands

- `debug state`: Display the current game state
- `debug unit <x,y>`: Display detailed debug information about a unit
- `debug map`: Display detailed map information
- `debug combat <attacker_x,attacker_y> <defender_x,defender_y>`: Show detailed combat calculations
- `debug path <from_x,from_y> <to_x,to_y>`: Show the pathfinding result between two points
- `debug event <event_id>`: Trigger a specific event
- `debug give <unit_x,unit_y> <item_id>`: Give an item to a unit
- `debug kill <x,y>`: Remove a unit from the map
- `debug spawn <unit_id> <x,y>`: Spawn a unit at the specified coordinates
- `debug fog <on|off>`: Toggle fog of war
- `debug stats <unit_x,unit_y> <stat> <value>`: Modify a unit's stats

## Command Flow

The typical flow of commands during a player's turn:

1. View the map with `map`
2. Check unit status with `status` or `info`
3. Move a unit with `move`
4. Perform an action (attack, use item, etc.)
5. Repeat for all units
6. End the turn with `end turn`

## Example Session

```
> map
[Map is displayed]

> info 5,5
Leif (Lord) HP: 22/22 Fatigue: 0
Equipped: Light Brand (60/60)
Inventory: Light Brand, Iron Sword, Vulnerary

> move 5,5 6,6
Leif moved from (5,5) to (6,6).

> info 7,6
Enemy Soldier HP: 20/20
Equipped: Iron Lance (45/45)

> attack 6,6 7,6
Combat Forecast:
Leif (Light Brand) vs Enemy Soldier (Iron Lance)
Leif: HP 22/22, Hit 85%, Dmg 8, Crit 12%, x2
Enemy: HP 20/20, Hit 65%, Dmg 4, Crit 0%
Confirm attack? (y/n) y

Leif attacks Enemy Soldier for 8 damage!
Enemy Soldier has 12 HP remaining.
Enemy Soldier counterattacks Leif for 4 damage!
Leif has 18 HP remaining.
Leif attacks again for 8 damage!
Enemy Soldier has 4 HP remaining.
Leif gained 10 experience.

> move 3,4 4,4
Finn moved from (3,4) to (4,4).

> end turn
Enemy Phase begins.

[Enemy units move and attack]

Player Phase begins.
Turn 2
```

## CLI Implementation Details

### Input Handling

The CLI will use a command parser that:

1. Tokenizes the input string
2. Identifies the command and subcommand
3. Validates the arguments
4. Executes the appropriate function

### Output Formatting

The CLI will use ANSI color codes to enhance readability:
- Blue for player units
- Red for enemy units
- Green for NPC units
- Yellow for objectives and important information
- White for normal text
- Cyan for terrain information

### Error Handling

When a command fails, the CLI will provide clear error messages:

```
> move 5,5 20,20
Error: Position (20,20) is outside the map boundaries.

> attack 5,5 6,6
Error: No enemy unit at position (6,6).

> use vulnerary 5,5
Error: Unit at (5,5) does not have a Vulnerary.
```

### Help System

The help system provides context-sensitive help:

```
> help
[List of all commands]

> help move
move <from_x,from_y> <to_x,to_y>
Move a unit from one position to another.
The destination must be within the unit's movement range.
Example: move 5,5 6,6
```

## Map Representation

The map is represented using ASCII characters:

- `.` - Plain
- `^` - Mountain
- `~` - Water
- `#` - Wall
- `+` - Forest
- `=` - Bridge
- `_` - Road
- `F` - Fort
- `T` - Throne
- `H` - House/Village
- `D` - Door
- `C` - Chest
- `G` - Gate

Units are represented by letters:
- Uppercase letters (A-Z) for player units
- Lowercase letters (a-z) for enemy units
- Numbers (0-9) for NPC units

When multiple units are in the same area (e.g., in fog of war), only the top unit is shown.

## Accessibility Features

The CLI includes several accessibility features:

1. **Verbose Mode**: Provides more detailed descriptions of actions and states
2. **Simplified Map**: Option to display a simplified map with fewer details
3. **Command Aliases**: Short aliases for common commands
4. **Command History**: Ability to recall and edit previous commands
5. **Tab Completion**: Completes commands and arguments when Tab is pressed

## Testing Support

The CLI is designed to support automated testing:

1. **Command Scripts**: Ability to run a sequence of commands from a file
2. **Predictable RNG**: Option to set the random seed for deterministic outcomes
3. **Batch Mode**: Run without interactive prompts for automated testing
4. **Logging**: Detailed logging of all actions and state changes
5. **Assertion Commands**: Special commands for test assertions

Example test script:

```
# Test basic combat
seed 12345
load test_map
move 5,5 6,6
attack 6,6 7,6
assert unit_hp 7,6 4
assert unit_hp 6,6 18
end turn
assert turn 2
```

## CLI Configuration

The CLI behavior can be customized through a configuration file:

```json
{
  "display": {
    "use_colors": true,
    "map_width": 80,
    "map_height": 24,
    "show_grid": true
  },
  "interface": {
    "verbose_mode": false,
    "auto_end_turn": false,
    "confirm_attacks": true,
    "show_movement_range": true,
    "show_attack_range": true
  },
  "debug": {
    "log_level": "info",
    "show_coordinates": true,
    "show_hidden_units": false
  }
}
```

## Command Line Arguments

The game can be started with various command line arguments:

```
fantasy-tactics [options] [chapter]

Options:
  --help            Show this help message and exit
  --load FILE       Load a saved game
  --config FILE     Use a custom configuration file
  --test SCRIPT     Run a test script
  --seed NUMBER     Set the random seed
  --debug           Enable debug mode
  --batch           Run in batch mode (no interactive prompts)
  --no-color        Disable colored output
```

## Conclusion

The CLI design provides a robust and flexible interface for the text-based implementation of the Fantasy Tactics Game. It supports all the core gameplay mechanics while remaining accessible and testable. This design serves as the foundation for the initial implementation, which can later be extended with a graphical interface.