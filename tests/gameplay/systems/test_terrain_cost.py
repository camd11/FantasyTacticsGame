import logging
from src.fantasy_tactics_core.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create a DataProvider instance
data_provider = DataProvider()

# Load the data
data_provider.load_all_data("data")

# Test the movement cost for plains with different movement types
movement_types = [
    MovementTypeEnum.INFANTRY,
    MovementTypeEnum.CAVALRY,
    MovementTypeEnum.ARMORED,
    MovementTypeEnum.FLYING
]

print("Testing movement costs for PLAIN terrain:")
for movement_type in movement_types:
    cost = data_provider.get_terrain_cost(TerrainTypeEnum.PLAIN, movement_type)
    print(f"  Movement cost for {movement_type.name}: {cost}")

# Also test a few other terrain types for comparison
other_terrains = [
    TerrainTypeEnum.FOREST,
    TerrainTypeEnum.MOUNTAIN,
    TerrainTypeEnum.RIVER
]

for terrain in other_terrains:
    print(f"\nTesting movement costs for {terrain.name} terrain:")
    for movement_type in movement_types:
        cost = data_provider.get_terrain_cost(terrain, movement_type)
        print(f"  Movement cost for {movement_type.name}: {cost}")