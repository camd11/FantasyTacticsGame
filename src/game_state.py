import json
from datetime import datetime
from src.core.data_structures import Position, Phase, UnitType
from src.core.units import Unit
from src.core.map import Map
# from src.systems.events import EventSystem # Import later when implemented
# from src.systems.fatigue import FatigueSystem # Import later when implemented

# Placeholder for Action/ActionRecord classes (define later)
class Action:
    def execute(self): pass
    def undo(self): pass
class ActionRecord:
    def __init__(self, action: Action, state_before, state_after, timestamp, description):
        self.action = action
        self.state_before = state_before # Snapshot or diff
        self.state_after = state_after   # Snapshot or diff
        self.timestamp = timestamp
        self.description = description

class GameState:
    def __init__(self):
        self.current_turn: int = 1
        self.current_phase: Phase = Phase.PLAYER
        self.map: Map | None = None
        self.player_units: list[Unit] = []
        self.enemy_units: list[Unit] = []
        self.npc_units: list[Unit] = []
        self.flags: dict[str, bool] = {}
        self.variables: dict[str, int] = {}
        self.action_history: list[ActionRecord] = []
        # self.event_system = EventSystem(self) # Initialize later
        # self.fatigue_system = FatigueSystem(self) # Initialize later

        # TODO: Add handlers for events (turn start, phase change, etc.)
        self.turn_start_handlers = []
        self.phase_change_handlers = []

    def load_map(self, map_instance: Map):
        """Loads a map instance into the game state."""
        self.map = map_instance
        # Clear existing units when loading a new map? Or handle placement separately?
        self.player_units = []
        self.enemy_units = []
        self.npc_units = []
        self.units_by_id = {} # Reset unit lookup
        # TODO: Place units based on map spawn points or scenario data

    def add_unit(self, unit: Unit, position: Position):
        """Adds a unit to the game state and places it on the map."""
        if not self.map:
            print("Error: Cannot add unit, no map loaded.")
            return False
        if unit.unit_id in self.units_by_id:
             print(f"Error: Unit with ID {unit.unit_id} already exists.")
             return False

        if self.map.place_unit(unit, position):
            if unit.unit_type == UnitType.PLAYER:
                self.player_units.append(unit)
            elif unit.unit_type == UnitType.ENEMY:
                self.enemy_units.append(unit)
            elif unit.unit_type == UnitType.NPC:
                self.npc_units.append(unit)
            self.units_by_id[unit.unit_id] = unit
            return True
        return False

    def remove_unit(self, unit: Unit):
        """Removes a unit from the game state and map."""
        if self.map:
            self.map.remove_unit(unit)

        if unit.unit_type == UnitType.PLAYER and unit in self.player_units:
            self.player_units.remove(unit)
        elif unit.unit_type == UnitType.ENEMY and unit in self.enemy_units:
            self.enemy_units.remove(unit)
        elif unit.unit_type == UnitType.NPC and unit in self.npc_units:
            self.npc_units.remove(unit)

        if unit.unit_id in self.units_by_id:
            del self.units_by_id[unit.unit_id]

    def get_unit_at(self, position: Position) -> Unit | None:
        """Gets the unit at a specific map position."""
        if not self.map:
            return None
        return self.map.get_unit_at(position)

    def get_unit_by_id(self, unit_id: str) -> Unit | None:
        """Gets a unit by its unique ID."""
        return self.units_by_id.get(unit_id)

    def get_all_units(self) -> list[Unit]:
        """Gets a list of all units currently in the game state."""
        return self.player_units + self.enemy_units + self.npc_units

    def get_active_units(self) -> list[Unit]:
        """Gets the units belonging to the current active phase."""
        if self.current_phase == Phase.PLAYER:
            return self.player_units
        elif self.current_phase == Phase.ENEMY:
            return self.enemy_units
        elif self.current_phase == Phase.NPC:
            return self.npc_units
        else:
            return []

    def advance_turn(self):
        """Advances the game to the next turn, resetting phase to Player."""
        self.current_turn += 1
        self.current_phase = Phase.PLAYER
        print(f"--- Turn {self.current_turn} ---")
        self._trigger_turn_start_events()
        self._refresh_units_for_phase(self.current_phase)
        self._trigger_phase_start_events() # Trigger player phase start

    def change_phase(self, new_phase: Phase):
        """Changes the current game phase."""
        # Basic validation (can add more complex rules later)
        if new_phase == self.current_phase:
            return

        print(f"--- {new_phase.name} Phase ---")
        self.current_phase = new_phase
        self._refresh_units_for_phase(new_phase)
        self._trigger_phase_start_events()

    def end_current_phase(self):
        """Ends the current phase and transitions to the next."""
        if self.current_phase == Phase.PLAYER:
            self.change_phase(Phase.ENEMY)
        elif self.current_phase == Phase.ENEMY:
            # Check if NPCs exist before going to NPC phase
            if self.npc_units:
                self.change_phase(Phase.NPC)
            else:
                self.advance_turn() # Skip NPC phase if no NPCs
        elif self.current_phase == Phase.NPC:
            self.advance_turn()

    def _refresh_units_for_phase(self, phase: Phase):
        """Refreshes units at the start of their phase (e.g., resets move/action flags)."""
        units_to_refresh = []
        if phase == Phase.PLAYER:
            units_to_refresh = self.player_units
        elif phase == Phase.ENEMY:
            units_to_refresh = self.enemy_units
        elif phase == Phase.NPC:
            units_to_refresh = self.npc_units

        for unit in units_to_refresh:
            unit.start_turn()
            # TODO: Handle terrain healing
            # TODO: Handle status effects (poison damage, sleep check, etc.)

    def _trigger_turn_start_events(self):
        """Placeholder for triggering turn-based events."""
        print(f"Turn {self.current_turn} starting.")
        # Call registered handlers
        for handler in self.turn_start_handlers:
            handler(self)
        # self.event_system.check_turn_events(self.current_turn)

    def _trigger_phase_start_events(self):
        """Placeholder for triggering phase-based events."""
        print(f"{self.current_phase.name} phase starting.")
         # Call registered handlers
        for handler in self.phase_change_handlers:
            handler(self, self.current_phase)
        # self.event_system.check_phase_events(self.current_phase)

    def set_flag(self, flag_name: str, value: bool):
        """Sets a game flag."""
        self.flags[flag_name] = value
        print(f"Flag '{flag_name}' set to {value}")

    def get_flag(self, flag_name: str, default: bool = False) -> bool:
        """Gets the value of a game flag."""
        return self.flags.get(flag_name, default)

    def set_variable(self, var_name: str, value: int):
        """Sets a game variable."""
        self.variables[var_name] = value
        print(f"Variable '{var_name}' set to {value}")

    def get_variable(self, var_name: str, default: int = 0) -> int:
        """Gets the value of a game variable."""
        return self.variables.get(var_name, default)

    def record_action(self, action: Action):
        """Records an action in the history (basic placeholder)."""
        # TODO: Implement state snapshotting/diffing for undo
        state_before = None # self._create_state_snapshot()
        # action.execute() # Assume action is executed externally for now
        state_after = None # self._create_state_snapshot()

        record = ActionRecord(
            action=action,
            state_before=state_before,
            state_after=state_after,
            timestamp=datetime.now(),
            description=str(action) # Action should have a __str__ method
        )
        self.action_history.append(record)
        print(f"Action recorded: {record.description}")

    def undo_last_action(self):
        """Undoes the last recorded action (basic placeholder)."""
        if not self.action_history:
            print("No actions to undo.")
            return False

        last_record = self.action_history.pop()
        print(f"Undoing action: {last_record.description}")
        # TODO: Restore state from snapshot/diff
        # last_record.action.undo() # Or call an undo method on the action
        # self._restore_state_snapshot(last_record.state_before)
        return True

    def save_state(self, filename: str):
        """Saves the current game state to a file (basic placeholder)."""
        # TODO: Implement proper serialization for Map, Units, etc.
        state_data = {
            'current_turn': self.current_turn,
            'current_phase': self.current_phase.name,
            'map_id': self.map.map_id if self.map else None,
            # 'map_state': self.map.serialize() if self.map else None,
            # 'player_units': [unit.serialize() for unit in self.player_units],
            # 'enemy_units': [unit.serialize() for unit in self.enemy_units],
            # 'npc_units': [unit.serialize() for unit in self.npc_units],
            'flags': self.flags,
            'variables': self.variables,
            # 'action_history': [record.serialize() for record in self.action_history] # History might not be saved
        }
        try:
            with open(filename, 'w') as f:
                json.dump(state_data, f, indent=2)
            print(f"Game state saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False

    def load_state(self, filename: str):
        """Loads a game state from a file (basic placeholder)."""
        # TODO: Implement proper deserialization and state restoration
        try:
            with open(filename, 'r') as f:
                state_data = json.load(f)

            self.current_turn = state_data.get('current_turn', 1)
            self.current_phase = Phase[state_data.get('current_phase', 'PLAYER')]
            self.flags = state_data.get('flags', {})
            self.variables = state_data.get('variables', {})
            self.action_history = [] # Clear history on load

            map_id = state_data.get('map_id')
            if map_id:
                # TODO: Need a way to load map instance based on ID
                # self.load_map(load_map_by_id(map_id))
                # TODO: Deserialize and place units
                pass
            else:
                self.map = None
                self.player_units = []
                self.enemy_units = []
                self.npc_units = []
                self.units_by_id = {}


            print(f"Game state loaded from {filename}")
            # Refresh units for the loaded phase
            self._refresh_units_for_phase(self.current_phase)
            return True
        except FileNotFoundError:
            print(f"Error: Save file not found: {filename}")
            return False
        except Exception as e:
            print(f"Error loading game state: {e}")
            return False

    def check_victory_conditions(self):
        """Placeholder for checking if victory conditions are met."""
        # TODO: Implement based on chapter objectives (seize, escape, rout, etc.)
        pass

    def check_defeat_conditions(self):
        """Placeholder for checking if defeat conditions are met."""
        # TODO: Implement (e.g., Leif defeated, required NPC defeated)
        pass