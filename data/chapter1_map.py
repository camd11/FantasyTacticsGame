# Placeholder data for Chapter 1 Map

# Define terrain characters (example)
PLAIN = '.'
FOREST = 'F'
MOUNTAIN = '^'
FORT = '#'
THRONE = 'T' # Seize point

# Map dimensions (adjust to actual Chapter 1 size later)
WIDTH = 20
HEIGHT = 15

# Simple map grid data (replace with actual Chapter 1 layout)
# This is just a small example
GRID_DATA = [
    [PLAIN, PLAIN, PLAIN, FOREST, FOREST, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, FOREST, FOREST, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, MOUNTAIN, MOUNTAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, MOUNTAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, FORT, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, THRONE, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
    [PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN, PLAIN],
]

# Initial unit placements (example)
# Format: (unit_id, name, affiliation, stats_dict, position_tuple)
# Stats dict keys: hp, str, mag, skl, spd, lck, def, bld, mov, con
INITIAL_UNITS = [
    ('leif', 'Leif', 'player', {'hp': 18, 'str': 3, 'mag': 0, 'skl': 1, 'spd': 5, 'lck': 2, 'def': 2, 'bld': 5, 'mov': 6, 'con': 5}, (6, 6)),
    ('finn', 'Finn', 'player', {'hp': 22, 'str': 6, 'mag': 1, 'skl': 5, 'spd': 7, 'lck': 4, 'def': 5, 'bld': 8, 'mov': 8, 'con': 8}, (7, 6)),
    ('brigand1', 'Brigand', 'enemy', {'hp': 20, 'str': 4, 'mag': 0, 'skl': 2, 'spd': 3, 'lck': 0, 'def': 3, 'bld': 10, 'mov': 5, 'con': 10}, (10, 10)),
    ('brigand2', 'Brigand', 'enemy', {'hp': 20, 'str': 4, 'mag': 0, 'skl': 2, 'spd': 3, 'lck': 0, 'def': 3, 'bld': 10, 'mov': 5, 'con': 10}, (11, 11)),
]

# Define items later
INITIAL_ITEMS = {} # Map unit_id to list of Item objects/definitions