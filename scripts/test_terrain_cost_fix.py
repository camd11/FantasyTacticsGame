import logging
from src.fantasy_tactics_core.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create a DataProvider instance
data_provider = DataProvider()

# Load the data
data_provider.load_all_data("data")

# Test the movement cost for plains with different input types
movement_type = MovementTypeEnum.INFANTRY

print("\n=== Testing get_terrain_cost with different input types ===")

# Test with TerrainTypeEnum.PLAIN (Case 1)
print("\nCase 1: Using TerrainTypeEnum.PLAIN")
cost = data_provider.get_terrain_cost(TerrainTypeEnum.PLAIN, movement_type)
print(f"  Movement cost for {movement_type.name}: {cost}")

# Test with string "PLAINS" (Case 2)
print("\nCase 2: Using string 'PLAINS'")
cost = data_provider.get_terrain_cost("PLAINS", movement_type)
print(f"  Movement cost for {movement_type.name}: {cost}")

# Test with another TerrainTypeEnum (Case 3)
print("\nCase 3: Using TerrainTypeEnum.FOREST")
cost = data_provider.get_terrain_cost(TerrainTypeEnum.FOREST, movement_type)
print(f"  Movement cost for {movement_type.name}: {cost}")

# Test with another string (similar to Case 2)
print("\nCase 4: Using string 'FOREST'")
cost = data_provider.get_terrain_cost("FOREST", movement_type)
print(f"  Movement cost for {movement_type.name}: {cost}")

# Test with invalid type (Case 5)
print("\nCase 5: Using invalid type (int)")
try:
    cost = data_provider.get_terrain_cost(1, movement_type)
    print(f"  Movement cost for {movement_type.name}: {cost}")
except Exception as e:
    print(f"  Error: {e}")

print("\n=== Testing other terrain methods with different input types ===")

# Test get_terrain_data
print("\nTesting get_terrain_data:")
terrain_data1 = data_provider.get_terrain_data(TerrainTypeEnum.PLAIN)
terrain_data2 = data_provider.get_terrain_data("PLAINS")
print(f"  Using enum: {terrain_data1.name if terrain_data1 else None}")
print(f"  Using string: {terrain_data2.name if terrain_data2 else None}")

# Test get_terrain_bonuses
print("\nTesting get_terrain_bonuses:")
bonuses1 = data_provider.get_terrain_bonuses(TerrainTypeEnum.PLAIN)
bonuses2 = data_provider.get_terrain_bonuses("PLAINS")
print(f"  Using enum: {bonuses1}")
print(f"  Using string: {bonuses2}")

# Test is_terrain_healing
print("\nTesting is_terrain_healing:")
healing1 = data_provider.is_terrain_healing(TerrainTypeEnum.PLAIN)
healing2 = data_provider.is_terrain_healing("PLAINS")
print(f"  Using enum: {healing1}")
print(f"  Using string: {healing2}")

# Test is_terrain_indoor
print("\nTesting is_terrain_indoor:")
indoor1 = data_provider.is_terrain_indoor(TerrainTypeEnum.PLAIN)
indoor2 = data_provider.is_terrain_indoor("PLAINS")
print(f"  Using enum: {indoor1}")
print(f"  Using string: {indoor2}")