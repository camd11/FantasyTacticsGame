import sys
from src.game_state import GameState, Phase
from src.core.map import Map # For creating a dummy map
from src.core.units import Unit, Class, Stats, ClassType, MovementType, WeaponRank # For dummy units/classes
from src.core.items import Weapon, WeaponType, ItemType # For dummy items
from src.core.data_structures import Position, UnitType as CoreUnitType, TerrainType # Distinguish from units.UnitType

# --- Dummy Data (Replace with actual data loading later) ---
DUMMY_STATS = Stats(hp=20, strength=5, magic=1, skill=5, speed=5, luck=5, defense=5, constitution=5, movement=5)
DUMMY_GROWTHS = Stats(hp=50, strength=30, magic=10, skill=30, speed=30, luck=30, defense=20, constitution=10, movement=5)
DUMMY_CLASS = Class(
    name="Lord", class_type=ClassType.LORD, base_stats=DUMMY_STATS, max_stats=Stats(20,20,20,20,20,20,20,20,20),
    usable_weapons=[WeaponType.SWORD], weapon_ranks={WeaponType.SWORD: WeaponRank.A},
    class_skills=[], movement_type=MovementType.INFANTRY
)
DUMMY_WEAPON = Weapon("Iron Sword", WeaponType.SWORD, 5, 90, 0, 3, 1, 1, WeaponRank.E, 45)
# --- End Dummy Data ---

class GameApplication:
    def __init__(self):
        self.game_state = GameState()
        self.is_running = False
        # TODO: Initialize command parser
        # TODO: Initialize renderer

    def initialize_game(self):
        """Initializes a new game with dummy data."""
        print("Initializing new game...")
        # Create and load a dummy map
        dummy_map = Map(map_id="dummy_map", name="Test Map", width=10, height=10)
        # Simple terrain for testing
        terrain = [[TerrainType.PLAIN for _ in range(10)] for _ in range(10)]
        terrain[3][3] = TerrainType.FOREST
        terrain[4][5] = TerrainType.MOUNTAIN
        dummy_map.load_map_data(terrain)
        self.game_state.load_map(dummy_map)

        # Add dummy units
        leif = Unit("leif", "Leif", CoreUnitType.PLAYER, DUMMY_CLASS, DUMMY_STATS, DUMMY_GROWTHS, inventory=[DUMMY_WEAPON])
        enemy = Unit("enemy1", "Soldier", CoreUnitType.ENEMY, DUMMY_CLASS, DUMMY_STATS, DUMMY_GROWTHS, inventory=[DUMMY_WEAPON])

        self.game_state.add_unit(leif, Position(1, 1))
        self.game_state.add_unit(enemy, Position(5, 5))

        self.is_running = True
        print("Game initialized.")

    def render_game_state(self):
        """Renders the current game state to the console (basic)."""
        print("-" * 20)
        print(f"Turn: {self.game_state.current_turn} - Phase: {self.game_state.current_phase.name}")
        if self.game_state.map:
            # Basic map string representation
            print(str(self.game_state.map))
        else:
            print("No map loaded.")
        # Print active units' basic info
        print("Active Units:")
        for unit in self.game_state.get_active_units():
             print(f"  - {unit} | Moved: {unit.has_moved}, Acted: {unit.has_acted}")
        print("-" * 20)


    def process_input(self, command_str: str):
        """Processes a single command string."""
        command_str = command_str.strip().lower()
        parts = command_str.split()
        if not parts:
            return

        command = parts[0]
        args = parts[1:]

        print(f"Processing command: {command} with args: {args}") # Debug print

        # --- Basic Command Parsing (Expand significantly later) ---
        if command == "quit":
            self.is_running = False
            print("Exiting game.")
        elif command == "end":
            if self.game_state.current_phase == Phase.PLAYER:
                self.game_state.end_current_phase()
                # TODO: Trigger AI phase if applicable
            else:
                print("Can only end player phase.")
        elif command == "map":
            self.render_game_state() # Re-render to show map
        elif command == "move":
            # Very basic move: move <unit_id> <x> <y>
            if len(args) == 3:
                unit_id, x_str, y_str = args
                try:
                    x, y = int(x_str), int(y_str)
                    unit = self.game_state.get_unit_by_id(unit_id)
                    target_pos = Position(x,y)
                    if unit and unit.unit_type == CoreUnitType.PLAYER and self.game_state.current_phase == Phase.PLAYER:
                        if not unit.can_move():
                             print(f"Error: {unit.name} cannot move anymore this turn.")
                             return
                        # TODO: Proper pathfinding and range check needed here!
                        # This is just a teleport for now.
                        if self.game_state.map.move_unit(unit, target_pos):
                            unit.has_moved = True # Mark as moved
                            print(f"{unit.name} moved to {target_pos}.")
                        else:
                            print(f"Failed to move {unit.name} to {target_pos}.")
                    else:
                        print(f"Error: Cannot move unit '{unit_id}'. Invalid unit or not player phase.")
                except (ValueError, IndexError):
                    print("Error: Invalid move command. Use: move <unit_id> <x> <y>")
            else:
                 print("Error: Invalid move command. Use: move <unit_id> <x> <y>")
        elif command == "wait":
             # Basic wait: wait <unit_id>
             if len(args) == 1:
                 unit_id = args[0]
                 unit = self.game_state.get_unit_by_id(unit_id)
                 if unit and unit.unit_type == CoreUnitType.PLAYER and self.game_state.current_phase == Phase.PLAYER:
                     if unit.has_acted:
                         print(f"Error: {unit.name} has already acted.")
                     else:
                         unit.end_turn() # Mark as moved and acted
                         print(f"{unit.name} waits.")
                 else:
                     print(f"Error: Cannot wait unit '{unit_id}'. Invalid unit or not player phase.")
             else:
                 print("Error: Invalid wait command. Use: wait <unit_id>")

        # TODO: Add commands for attack, use, info, status, etc.
        else:
            print(f"Unknown command: {command}")

    def run_game_loop(self):
        """Main game loop."""
        self.initialize_game()

        while self.is_running:
            self.render_game_state()

            # TODO: Handle AI turns automatically
            if self.game_state.current_phase != Phase.PLAYER:
                print(f"Skipping {self.game_state.current_phase.name} phase (AI not implemented).")
                self.game_state.end_current_phase()
                continue

            # Get player input
            try:
                command_input = input("> ")
                self.process_input(command_input)
            except EOFError: # Handle Ctrl+D
                print("\nExiting.")
                self.is_running = False
            except KeyboardInterrupt: # Handle Ctrl+C
                 print("\nExiting.")
                 self.is_running = False

            # TODO: Check victory/defeat conditions

        print("Game Over.")

if __name__ == "__main__":
    app = GameApplication()
    app.run_game_loop()