"""
Command Line Display Module

This module provides functions for displaying the game state in the command line interface.
It handles rendering the map, units, menus, and other game elements, including ASCII map display.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Set
import os
import platform

# Import necessary modules
from src.gameplay_systems.combat_system import CombatSystem

# ANSI color codes for colored output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

# Terrain symbols and colors
TERRAIN_DISPLAY = {
    'P': (Colors.GREEN, '🟩'),  # Plain
    'F': (Colors.GREEN + Colors.BOLD, '🌲'),  # Forest
    'W': (Colors.BLUE, '🌊'),  # Water
    'D': (Colors.BLUE + Colors.BOLD, '🌉'),  # Bridge
    'V': (Colors.YELLOW, '🏠'),  # Village
    'S': (Colors.MAGENTA, '👑'),  # Seize point
    'M': (Colors.BLACK + Colors.BG_WHITE, '⛰️'),  # Mountain
    'H': (Colors.YELLOW + Colors.BOLD, '🏰'),  # Castle/Fortress
    'T': (Colors.CYAN, '🏛️'),  # Throne
}

# ASCII terrain symbols for simple display
ASCII_TERRAIN = {
    'P': '.',  # Plain
    'F': 'T',  # Forest
    'W': '~',  # Water
    'D': '=',  # Bridge
    'V': 'v',  # Village
    'S': 'S',  # Seize point
    'M': '^',  # Mountain
    'H': 'H',  # Castle/Fortress
    'T': 'O',  # Throne
    'INVALID': '?'  # Invalid terrain
}

# ASCII unit symbols
ASCII_UNITS = {
    'PLAYER': 'P',
    'ENEMY': 'E',
    'NPC': 'N'
}

# Faction colors
FACTION_COLORS = {
    'PLAYER': Colors.CYAN,
    'ENEMY': Colors.RED,
    'NPC': Colors.YELLOW,
}

# Unit type symbols
UNIT_SYMBOLS = {
    'INFANTRY': '👤',
    'CAVALRY': '🐎',
    'FLIER': '🦅',
    'ARMOR': '🛡️',
    'ARCHER': '🏹',
    'MAGE': '🧙',
    'THIEF': '🗡️',
    'LORD': '👑',
}

class CLIDisplay:
    """
    Handles the display of game elements in the command line interface.
    """
    
    def __init__(self):
        """Initialize the CLIDisplay."""
        self.combat_system = None
        self.game_state_manager = None
        self.unit_system = None
        self.movement_system = None
        self.map_system = None
        self.data_provider = None
        self.combat_system = None
        
        # Enable ANSI colors on Windows
        if platform.system() == 'Windows':
            os.system('color')
    
    def initialize(self, game_state_manager, unit_system, movement_system, map_system, data_provider, combat_system=None):
        """
        Initialize the CLIDisplay with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            unit_system: Instance of the UnitSystem
            movement_system: Instance of the MovementSystem
            map_system: Instance of the MapSystem
            data_provider: Instance of the DataProvider
            combat_system: Instance of the CombatSystem (optional)
        """
        self.game_state_manager = game_state_manager
        self.unit_system = unit_system
        self.movement_system = movement_system
        self.map_system = map_system
        self.data_provider = data_provider
        self.combat_system = combat_system
        logging.info("CLIDisplay initialized.")
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def display_map(self, highlight_positions: Set[Tuple[int, int]] = None,
                   selected_unit_id: str = None, cursor_position: Tuple[int, int] = None,
                   highlight_color: str = Colors.BG_CYAN):
        """
        Display the game map with terrain and units.
        
        Args:
            highlight_positions: Set of positions to highlight (e.g., movement range)
            selected_unit_id: ID of the currently selected unit
            cursor_position: Current cursor position (x, y)
            highlight_color: Color to use for highlighting positions (default: cyan)
        """
        self.clear_screen()
        
        # Get map dimensions
        map_width, map_height = self.game_state_manager.get_map_dimensions()
        
        # Print column headers (x-coordinates)
        print("   ", end="")
        for x in range(map_width):
            print(f" {x:2d}", end="")
        print("\n   ", end="")
        for x in range(map_width):
            print("---", end="")
        print()
        
        # Print each row
        for y in range(map_height):
            # Print row header (y-coordinate)
            print(f"{y:2d} |", end="")
            
            for x in range(map_width):
                position = (x, y)
                terrain_type = self.game_state_manager.get_terrain_type(position)
                unit_id = self._get_unit_at_position(position)
                
                # Determine cell display
                if unit_id:
                    # Display unit
                    unit = self.game_state_manager.get_unit(unit_id)
                    faction_color = FACTION_COLORS.get(unit.faction, Colors.WHITE)
                    
                    # Get unit symbol based on class
                    class_data = self.data_provider.get_class_data(unit.class_id)
                    unit_type = getattr(class_data, 'movement_type', 'INFANTRY')
                    unit_symbol = UNIT_SYMBOLS.get(unit_type, '👤')
                    
                    # Highlight selected unit
                    if unit_id == selected_unit_id:
                        cell = f"{faction_color}{Colors.BG_YELLOW}{unit_symbol}{Colors.RESET}"
                    else:
                        cell = f"{faction_color}{unit_symbol}{Colors.RESET}"
                else:
                    # Display terrain
                    terrain_color, terrain_symbol = TERRAIN_DISPLAY.get(terrain_type, (Colors.WHITE, '·'))
                    
                    # Highlight position if in highlighted positions
                    if highlight_positions and position in highlight_positions:
                        cell = f"{highlight_color}{terrain_color}{terrain_symbol}{Colors.RESET}"
                    else:
                        cell = f"{terrain_color}{terrain_symbol}{Colors.RESET}"
                
                # Highlight cursor position
                if cursor_position and position == cursor_position:
                    cell = f"{Colors.BG_WHITE}{Colors.BLACK}{cell.strip(Colors.RESET)}{Colors.RESET}"
                
                print(f" {cell}", end="")
            
            print()
        
        print()
    
    def display_unit_details(self, unit_id: str):
        """
        Display detailed information about a unit.
        
        Args:
            unit_id: ID of the unit
        """
        unit_details = self.unit_system.get_unit_details(unit_id)
        if not unit_details:
            print(f"Unit {unit_id} not found.")
            return
        
        unit = unit_details['state']
        calculated_stats = unit_details['calculated_stats']
        class_info = unit_details['class_info']
        
        # Display unit header
        faction_color = FACTION_COLORS.get(unit.faction, Colors.WHITE)
        print(f"\n{faction_color}{Colors.BOLD}=== {unit.name} ({class_info.name}) ==={Colors.RESET}")
        
        # Display position and HP
        print(f"Position: {unit.position}")
        print(f"HP: {unit.current_hp}/{unit.max_hp}")
        
        # Display stats in a formatted table
        print("\n--- Stats ---")
        print(f"STR: {unit.base_stats.get('STR', 0):2d}   MAG: {unit.base_stats.get('MAG', 0):2d}   SKL: {unit.base_stats.get('SKL', 0):2d}")
        print(f"SPD: {unit.base_stats.get('SPD', 0):2d}   LUK: {unit.base_stats.get('LUK', 0):2d}   DEF: {unit.base_stats.get('DEF', 0):2d}")
        print(f"CON: {unit.base_stats.get('CON', 0):2d}   MOV: {unit.base_stats.get('MOV', 0):2d}")
        
        # Display combat stats
        print("\n--- Combat Stats ---")
        print(f"ATK: {calculated_stats.get('atk', 0):2d}   HIT: {calculated_stats.get('hit', 0):3d}   CRT: {calculated_stats.get('crit', 0):3d}")
        print(f"AS : {calculated_stats.get('AS', 0):2d}   AVO: {calculated_stats.get('avo', 0):3d}   DDG: {calculated_stats.get('ddg', 0):3d}")
        print(f"RNG: {calculated_stats.get('rng', '-')}")
        
        # Display inventory
        print("\n--- Inventory ---")
        for i, item_detail in enumerate(unit_details['inventory_details'], 1):
            equipped_marker = " *" if i - 1 == unit.equipped_weapon_index else ""
            print(f"{i}. {item_detail['name']} ({item_detail['durability']}/{item_detail['max_durability']}){equipped_marker}")
        
        # Display status effects if any
        if hasattr(unit, 'status_effects') and unit.status_effects:
            print("\n--- Status Effects ---")
            for status in unit.status_effects:
                print(f"- {status.type}: {status.duration} turns remaining")
        
        print()
    
    def display_movement_range(self, movement_range: Set[Tuple[int, int]], unit_id: str):
        """
        Display the map with the movement range highlighted.
        
        Args:
            movement_range: Set of positions the unit can move to
            unit_id: ID of the unit
        """
        self.display_map(highlight_positions=movement_range, selected_unit_id=unit_id)
        print(f"Movement range: {len(movement_range)} tiles")
    def display_attack_range(self, attack_range: Set[Tuple[int, int]], unit_id: str):
        """
        Display the map with the attack range highlighted.
        
        Args:
            attack_range: Set of positions the unit can attack
            unit_id: ID of the unit
        """
        # Use red background for attack range
        self.display_map(highlight_positions=attack_range, selected_unit_id=unit_id, highlight_color=Colors.BG_RED)
        print(f"Attack range: {len(attack_range)} tiles")
        print(f"Attack range: {len(attack_range)} tiles")
    
    def display_action_menu(self, unit_id: str, actions: List[str]):
        """
        Display the action menu for a unit.
        
        Args:
            unit_id: ID of the unit
            actions: List of available actions
        """
        unit = self.game_state_manager.get_unit(unit_id)
        print(f"\n{Colors.BOLD}Available actions for {unit.name}:{Colors.RESET}")
        
        for i, action in enumerate(actions, 1):
            print(f"{i}. {action}")
    
    def display_turn_info(self):
        """Display the current turn and phase."""
        # Access turn information directly from the game state
        current_turn = self.game_state_manager.current_game_state.current_turn
        current_phase = self.game_state_manager.current_game_state.current_phase
        
        phase_color = FACTION_COLORS.get(current_phase.name, Colors.WHITE)
        print(f"\n{Colors.BOLD}{phase_color}=== Turn {current_turn}, {current_phase.name} Phase ==={Colors.RESET}")
    
    def display_active_units(self, units: List):
        """
        Display a list of active units.
        
        Args:
            units: List of active units
        """
        print(f"\n{Colors.BOLD}Active units:{Colors.RESET}")
        
        for i, unit in enumerate(units, 1):
            faction_color = FACTION_COLORS.get(unit.faction, Colors.WHITE)
            hp_color = Colors.GREEN if unit.current_hp > unit.max_hp * 0.5 else Colors.YELLOW
            if unit.current_hp < unit.max_hp * 0.25:
                hp_color = Colors.RED
                
            print(f"{i}. {faction_color}{unit.name}{Colors.RESET} at {unit.position} "
                  f"(HP: {hp_color}{unit.current_hp}/{unit.max_hp}{Colors.RESET})")
    
    def display_targets(self, targets: List[str], action_type: str):
        """
        Display a list of target units for an action.
        
        Args:
            targets: List of target unit IDs
            action_type: Type of action (e.g., 'ATTACK', 'TRADE')
        """
        print(f"\n{Colors.BOLD}Available targets for {action_type}:{Colors.RESET}")
        
        for i, target_id in enumerate(targets, 1):
            target = self.game_state_manager.get_unit(target_id)
            faction_color = FACTION_COLORS.get(target.faction, Colors.WHITE)
            hp_color = Colors.GREEN if target.current_hp > target.max_hp * 0.5 else Colors.YELLOW
            if target.current_hp < target.max_hp * 0.25:
                hp_color = Colors.RED
                
            print(f"{i}. {faction_color}{target.name}{Colors.RESET} at {target.position} "
                  f"(HP: {hp_color}{target.current_hp}/{target.max_hp}{Colors.RESET})")
        
        print(f"{len(targets) + 1}. Cancel")
    
    def display_inventory(self, unit_id: str):
        """
        Display the inventory of a unit.
        
        Args:
            unit_id: ID of the unit
        """
        unit = self.game_state_manager.get_unit(unit_id)
        
        print(f"\n{Colors.BOLD}Inventory for {unit.name}:{Colors.RESET}")
        
        if not unit.inventory:
            print("No items.")
            return
        
        for i, item in enumerate(unit.inventory, 1):
            item_data = self.data_provider.get_item_data(item.item_id)
            equipped_marker = " *" if i - 1 == unit.equipped_weapon_index else ""
            
            # Color based on durability
            durability_ratio = item.current_durability / item_data.max_durability
            durability_color = Colors.GREEN
            if durability_ratio < 0.5:
                durability_color = Colors.YELLOW
            if durability_ratio < 0.25:
                durability_color = Colors.RED
                
            print(f"{i}. {item_data.name} "
                  f"({durability_color}{item.current_durability}/{item_data.max_durability}{Colors.RESET})"
                  f"{equipped_marker}")
    
    def display_trade_inventories(self, unit1_id: str, unit2_id: str, trade_data: Dict):
        """
        Display inventories for trade.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            trade_data: Trade data from initiate_trade
        """
        unit1 = self.game_state_manager.get_unit(unit1_id)
        unit2 = self.game_state_manager.get_unit(unit2_id)
        
        print(f"\n{Colors.BOLD}=== Trade between {unit1.name} and {unit2.name} ==={Colors.RESET}")
        
        # Display first unit's inventory
        print(f"\n{Colors.CYAN}{unit1.name}'s inventory:{Colors.RESET}")
        for i, item in enumerate(trade_data['unit1_inventory']):
            item_data = self.data_provider.get_item_data(item.item_id)
            durability_ratio = item.current_durability / item_data.max_durability
            durability_color = Colors.GREEN
            if durability_ratio < 0.5:
                durability_color = Colors.YELLOW
            if durability_ratio < 0.25:
                durability_color = Colors.RED
                
            print(f"{i}. {item_data.name} "
                  f"({durability_color}{item.current_durability}/{item_data.max_durability}{Colors.RESET})")
        
        # Display second unit's inventory
        print(f"\n{Colors.CYAN}{unit2.name}'s inventory:{Colors.RESET}")
        for i, item in enumerate(trade_data['unit2_inventory']):
            item_data = self.data_provider.get_item_data(item.item_id)
            durability_ratio = item.current_durability / item_data.max_durability
            durability_color = Colors.GREEN
            if durability_ratio < 0.5:
                durability_color = Colors.YELLOW
            if durability_ratio < 0.25:
                durability_color = Colors.RED
                
            print(f"{i}. {item_data.name} "
                  f"({durability_color}{item.current_durability}/{item_data.max_durability}{Colors.RESET})")
    
    def display_combat_forecast(self, attacker_id: str, defender_id: str):
        """
        Display a combat forecast between two units.
        
        Args:
            attacker_id: ID of the attacking unit
            defender_id: ID of the defending unit
        """
        # Check if combat system is available
        if not self.combat_system:
            print("Combat forecast not available - combat system not initialized.")
            return
            
        # Get combat forecast from combat system
        forecast = self.combat_system.get_combat_forecast(attacker_id, defender_id)
        
        if not forecast:
            print("Cannot generate combat forecast.")
            return
        
        attacker = self.game_state_manager.get_unit(attacker_id)
        defender = self.game_state_manager.get_unit(defender_id)
        
        print(f"\n{Colors.BOLD}=== Combat Forecast ==={Colors.RESET}")
        
        # Attacker info
        print(f"\n{Colors.CYAN}{attacker.name}{Colors.RESET} (HP: {attacker.current_hp}/{attacker.max_hp})")
        print(f"ATK: {forecast['attacker']['atk']}  HIT: {forecast['attacker']['hit']}%  CRT: {forecast['attacker']['crit']}%")
        
        # Defender info
        print(f"\n{Colors.RED}{defender.name}{Colors.RESET} (HP: {defender.current_hp}/{defender.max_hp})")
        print(f"ATK: {forecast['defender']['atk']}  HIT: {forecast['defender']['hit']}%  CRT: {forecast['defender']['crit']}%")
        
        # Outcome prediction
        print(f"\n{Colors.BOLD}Predicted outcome:{Colors.RESET}")
        
        # Attacker attacks
        dmg_color = Colors.RED if forecast['attacker']['damage'] > 0 else Colors.GRAY
        print(f"{Colors.CYAN}{attacker.name}{Colors.RESET} attacks: "
              f"{dmg_color}{forecast['attacker']['damage']} damage{Colors.RESET} "
              f"({forecast['attacker']['hit']}% hit, {forecast['attacker']['crit']}% crit)")
        
        # Defender counterattacks if possible
        if forecast['defender']['can_counter']:
            dmg_color = Colors.RED if forecast['defender']['damage'] > 0 else Colors.GRAY
            print(f"{Colors.RED}{defender.name}{Colors.RESET} counterattacks: "
                  f"{dmg_color}{forecast['defender']['damage']} damage{Colors.RESET} "
                  f"({forecast['defender']['hit']}% hit, {forecast['defender']['crit']}% crit)")
        else:
            print(f"{Colors.RED}{defender.name}{Colors.RESET} cannot counterattack.")
        
        # Follow-up attacks
        if forecast['attacker']['follow_up']:
            dmg_color = Colors.RED if forecast['attacker']['damage'] > 0 else Colors.GRAY
            print(f"{Colors.CYAN}{attacker.name}{Colors.RESET} follows up: "
                  f"{dmg_color}{forecast['attacker']['damage']} damage{Colors.RESET}")
        
        if forecast['defender']['follow_up']:
            dmg_color = Colors.RED if forecast['defender']['damage'] > 0 else Colors.GRAY
            print(f"{Colors.RED}{defender.name}{Colors.RESET} follows up: "
                  f"{dmg_color}{forecast['defender']['damage']} damage{Colors.RESET}")
    
    # --- Helper Methods ---
    
    def _get_unit_at_position(self, position: Tuple[int, int]) -> Optional[str]:
        """
        Get the ID of the unit at a position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            Unit ID or None if no unit is present
        """
        for unit_id, unit in self.game_state_manager.current_game_state.unit_states.items():
            if unit.position == position:
                return unit_id
    def render_ascii_map(self, game_state_manager):
        """
        Render the game map in ASCII format to the console.
        
        Args:
            game_state_manager: Instance of the GameStateManager containing the current game state
        """
        # Get map dimensions
        map_width, map_height = game_state_manager.get_map_dimensions()
        
        # Print a header
        # Access turn information from the game state
        current_turn = game_state_manager.current_game_state.current_turn
        current_phase = game_state_manager.current_game_state.current_phase
        print(f"\n=== ASCII MAP (Turn {current_turn}, {current_phase.name} Phase) ===")
        
        # Print column headers (x-coordinates)
        print("   ", end="")
        for x in range(map_width):
            print(f"{x % 10}", end="")
        print()
        
        # Print each row
        for y in range(map_height):
            # Print row header (y-coordinate)
            print(f"{y:2d}|", end="")
            
            for x in range(map_width):
                position = (x, y)
                terrain_type = game_state_manager.get_terrain_type(position)
                
                # Check if there's a unit at this position - directly access unit_states
                unit_found = False
                unit_symbol = None
                faction_color = None
                
                # Explicitly iterate through all units to find one at this position
                for unit_id, unit_state in game_state_manager.current_game_state.unit_states.items():
                    # Ensure position comparison is done correctly
                    if hasattr(unit_state, 'position') and unit_state.position == position:
                        # Get faction and determine symbol
                        faction = getattr(unit_state, 'faction', 'PLAYER')  # Default to PLAYER if no faction
                        
                        # Convert FactionEnum to string for lookup
                        if hasattr(faction, 'name'):
                            faction_str = faction.name  # Get the name of the enum value
                        else:
                            faction_str = str(faction)  # Fallback to string conversion
                            
                        unit_symbol = ASCII_UNITS.get(faction_str, 'U')  # Default to 'U' if faction not found
                        faction_color = FACTION_COLORS.get(faction_str, Colors.WHITE)
                        unit_found = True
                        break
                
                # Determine what to display - prioritize units over terrain
                if unit_found and unit_symbol and faction_color:
                    # Display unit with faction color
                    cell = f"{faction_color}{unit_symbol}{Colors.RESET}"
                else:
                    # Display terrain when no unit is found
                    terrain_symbol = ASCII_TERRAIN.get(terrain_type, '?')
                    terrain_color, _ = TERRAIN_DISPLAY.get(terrain_type, (Colors.WHITE, '·'))
                    cell = f"{terrain_color}{terrain_symbol}{Colors.RESET}"
                
                print(cell, end="")
            
            print()
        
        print()
        
        # Print a legend
        print("Legend:")
        print(f"Terrain: {Colors.GREEN}.{Colors.RESET}=Plain, {Colors.GREEN}T{Colors.RESET}=Forest, {Colors.BLUE}~{Colors.RESET}=Water, {Colors.BLUE}={Colors.RESET}=Bridge")
        print(f"        {Colors.YELLOW}v{Colors.RESET}=Village, {Colors.MAGENTA}S{Colors.RESET}=Seize, {Colors.BLACK + Colors.BG_WHITE}^{Colors.RESET}=Mountain, {Colors.YELLOW}H{Colors.RESET}=Castle, {Colors.CYAN}O{Colors.RESET}=Throne")
        print(f"Units:  {Colors.CYAN}P{Colors.RESET}=Player, {Colors.RED}E{Colors.RESET}=Enemy, {Colors.YELLOW}N{Colors.RESET}=NPC")
        print()
        return None