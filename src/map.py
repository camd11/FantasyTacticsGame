class Map:
    """
    Represents the game board, including terrain and unit locations.
    """
    def __init__(self, width, height, grid_data):
        self.width = width
        self.height = height
        # grid_data is expected to be a 2D list/tuple representing terrain
        # e.g., [['plain', 'forest'], ['plain', 'mountain']]
        self.grid = grid_data
        # We might store unit locations here or query GameState/Units directly
        # For simplicity, let's assume GameState manages unit positions for now.

    def get_tile(self, x, y):
        """Returns the terrain type at the given coordinates."""
        if self.is_valid_coordinate(x, y):
            return self.grid[y][x]
        return None # Or raise an error

    def is_valid_coordinate(self, x, y):
        """Checks if the coordinates are within the map boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    # Methods for pathfinding, move range calculation, etc., will be added later.
    # def calculate_move_range(self, unit):
    #     pass

    # def get_unit_at(self, x, y, units): # Needs unit list from GameState
    #     pass