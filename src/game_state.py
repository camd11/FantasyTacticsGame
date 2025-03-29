class GameState:
    """
    Holds the overall state of the game, including the map, units,
    turn information, and objective status.
    """
    def __init__(self, map_obj, units):
        self.map = map_obj
        self.units = units # Expected to be a list or dict of Unit objects
        self.current_turn = 'player' # 'player' or 'enemy'
        self.turn_count = 1
        self.objective_complete = False
        self.selected_unit_id = None # ID of the currently selected unit
        # Add more state variables as needed (e.g., player gold, specific flags)

    def get_unit_at(self, x, y):
        """Returns the unit object at the given coordinates, or None."""
        for unit in self.units:
            if unit.x == x and unit.y == y:
                return unit
        return None

    def end_turn(self):
        """Switches the turn between player and enemy."""
        if self.current_turn == 'player':
            self.current_turn = 'enemy'
            # Potentially reset unit actions, etc.
        else:
            self.current_turn = 'player'
            self.turn_count += 1
            # Potentially apply status effects, etc.

    # Add methods to get units, check objectives, etc.