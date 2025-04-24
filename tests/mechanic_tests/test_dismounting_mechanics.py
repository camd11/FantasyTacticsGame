"""
Test script to demonstrate the dismounting mechanics.

This script showcases how mounted units can dismount, affecting their:
- Stats (particularly movement and other stats)
- Movement type (and associated terrain penalties)
- Weapon usability (typically restricted to swords when dismounted)
- Susceptibility to effective weapons
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

@dataclass
class Weapon:
    """Simple weapon class for demonstration."""
    name: str
    type: str
    effective_against: List[str] = None
    
    def __post_init__(self):
        if self.effective_against is None:
            self.effective_against = []


@dataclass
class Unit:
    """Simple Unit class for demonstration purposes."""
    name: str
    class_type: str
    is_mounted: bool = True
    is_dismounted: bool = False
    
    # Base stats
    stats: Dict[str, int] = None
    mounted_stats: Dict[str, int] = None
    dismounted_stats: Dict[str, int] = None
    
    # Movement
    movement_type: str = "INFANTRY"
    mounted_movement: str = "CAVALRY"
    dismounted_movement: str = "INFANTRY"
    
    # Weapons
    usable_weapon_types_mounted: List[str] = None
    usable_weapon_types_dismounted: List[str] = None
    current_weapon: Optional[Weapon] = None
    inventory: List[Weapon] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.stats is None:
            self.stats = {}
        if self.mounted_stats is None:
            self.mounted_stats = {}
        if self.dismounted_stats is None:
            self.dismounted_stats = {}
        if self.usable_weapon_types_mounted is None:
            self.usable_weapon_types_mounted = []
        if self.usable_weapon_types_dismounted is None:
            self.usable_weapon_types_dismounted = []
        if self.inventory is None:
            self.inventory = []
    
    def can_dismount(self) -> bool:
        """Check if the unit can dismount."""
        return self.is_mounted and not self.is_dismounted
    
    def can_mount(self) -> bool:
        """Check if the unit can mount."""
        return not self.is_mounted and self.is_dismounted
    
    def dismount(self) -> bool:
        """Dismount the unit, applying all state changes."""
        if not self.can_dismount():
            print(f"{self.name} cannot dismount.")
            return False
        
        # Update state
        self.is_mounted = False
        self.is_dismounted = True
        
        # Update movement type
        self.movement_type = self.dismounted_movement
        
        # Apply stat changes (copy dismounted stats to current stats)
        for stat, value in self.dismounted_stats.items():
            self.stats[stat] = value
        
        # Handle weapon restrictions
        self._handle_weapon_restrictions()
        
        print(f"{self.name} has dismounted. Now using {self.movement_type} movement.")
        return True
    
    def mount(self) -> bool:
        """Mount the unit, reverting all state changes."""
        if not self.can_mount():
            print(f"{self.name} cannot mount.")
            return False
        
        # Update state
        self.is_mounted = True
        self.is_dismounted = False
        
        # Update movement type
        self.movement_type = self.mounted_movement
        
        # Apply stat changes (copy mounted stats to current stats)
        for stat, value in self.mounted_stats.items():
            self.stats[stat] = value
        
        # Handle weapon access restoration
        self._handle_weapon_access_restoration()
        
        print(f"{self.name} has mounted. Now using {self.movement_type} movement.")
        return True
    
    def _handle_weapon_restrictions(self):
        """Apply weapon restrictions when dismounting."""
        # Check if current weapon is still usable
        if self.current_weapon and self.current_weapon.type not in self.usable_weapon_types_dismounted:
            print(f"{self.name} can no longer use {self.current_weapon.name} when dismounted.")
            
            # Try to equip a valid weapon
            valid_weapons = [w for w in self.inventory if w.type in self.usable_weapon_types_dismounted]
            if valid_weapons:
                self.current_weapon = valid_weapons[0]
                print(f"{self.name} automatically equipped {self.current_weapon.name}.")
            else:
                self.current_weapon = None
                print(f"{self.name} has no usable weapons while dismounted.")
    
    def _handle_weapon_access_restoration(self):
        """Restore weapon access when mounting."""
        # If no weapon equipped, try to equip one
        if not self.current_weapon:
            valid_weapons = [w for w in self.inventory if w.type in self.usable_weapon_types_mounted]
            if valid_weapons:
                self.current_weapon = valid_weapons[0]
                print(f"{self.name} automatically equipped {self.current_weapon.name}.")
    
    def check_weapon_effectiveness(self, enemy_weapon: Weapon) -> bool:
        """Check if an enemy weapon is effective against this unit."""
        if self.is_mounted and self.movement_type == "CAVALRY" and "CAVALRY" in enemy_weapon.effective_against:
            return True
        if self.is_mounted and self.movement_type == "FLYING" and "FLYING" in enemy_weapon.effective_against:
            return True
        return False


@dataclass
class Terrain:
    """Simple terrain class for demonstration."""
    name: str
    movement_cost: Dict[str, int]
    is_indoor: bool = False
    
    def get_movement_cost(self, movement_type: str) -> int:
        """Get the movement cost for a specific movement type."""
        return self.movement_cost.get(movement_type, 99)  # 99 = impassable


def print_unit_stats(unit: Unit):
    """Print a unit's current stats."""
    print(f"\n{unit.name} Stats:")
    print(f"Class: {unit.class_type} ({'Mounted' if unit.is_mounted else 'Dismounted'})")
    print(f"Movement Type: {unit.movement_type}")
    
    # Print stats
    print("Stats:")
    for stat, value in unit.stats.items():
        print(f"  {stat}: {value}")
    
    # Print weapon info
    print("Current Weapon:", end=" ")
    if unit.current_weapon:
        print(f"{unit.current_weapon.name} ({unit.current_weapon.type})")
    else:
        print("None")
    
    # Print usable weapon types
    if unit.is_mounted:
        print(f"Usable Weapon Types: {', '.join(unit.usable_weapon_types_mounted)}")
    else:
        print(f"Usable Weapon Types: {', '.join(unit.usable_weapon_types_dismounted)}")
    
    print("-" * 50)


def print_terrain_interaction(unit: Unit, terrains: List[Terrain]):
    """Print how a unit interacts with different terrain types."""
    print(f"\n{unit.name}'s Terrain Interaction:")
    print(f"Movement Type: {unit.movement_type}")
    
    for terrain in terrains:
        cost = terrain.get_movement_cost(unit.movement_type)
        passable = cost < 99
        status = "Passable" if passable else "Impassable"
        if passable:
            status += f" (Cost: {cost})"
        
        indoor_status = "Indoor" if terrain.is_indoor else "Outdoor"
        print(f"  {terrain.name} [{indoor_status}]: {status}")
    
    print("-" * 50)


def print_weapon_effectiveness(unit: Unit, weapons: List[Weapon]):
    """Print which weapons are effective against the unit."""
    print(f"\n{unit.name}'s Vulnerability to Effective Weapons:")
    print(f"Class: {unit.class_type} ({'Mounted' if unit.is_mounted else 'Dismounted'})")
    print(f"Movement Type: {unit.movement_type}")
    
    for weapon in weapons:
        effective = unit.check_weapon_effectiveness(weapon)
        status = "Effective" if effective else "Normal damage"
        print(f"  {weapon.name}: {status}")
    
    print("-" * 50)


def main():
    """Run dismounting mechanics demonstration."""
    print("\n=== DISMOUNTING MECHANICS DEMONSTRATION ===\n")
    
    # Create some weapons
    iron_sword = Weapon("Iron Sword", "SWORD")
    steel_lance = Weapon("Steel Lance", "LANCE")
    hand_axe = Weapon("Hand Axe", "AXE")
    horseslayer = Weapon("Horseslayer", "SWORD", ["CAVALRY"])
    ridersbane = Weapon("Ridersbane", "LANCE", ["CAVALRY"])
    bow = Weapon("Iron Bow", "BOW", ["FLYING"])
    
    # Create some terrain types
    plains = Terrain("Plains", {"INFANTRY": 1, "CAVALRY": 1, "FLYING": 1})
    forest = Terrain("Forest", {"INFANTRY": 2, "CAVALRY": 3, "FLYING": 1})
    mountain = Terrain("Mountain", {"INFANTRY": 4, "CAVALRY": 99, "FLYING": 1})
    indoor_hall = Terrain("Castle Hall", {"INFANTRY": 1, "CAVALRY": 99, "FLYING": 99}, is_indoor=True)
    
    # Create a cavalry unit
    paladin = Unit(
        name="Frederick",
        class_type="Paladin",
        is_mounted=True,
        movement_type="CAVALRY",
        mounted_movement="CAVALRY",
        dismounted_movement="INFANTRY",
        stats={
            "HP": 40,
            "STR": 18,
            "DEF": 15,
            "SPD": 12,
            "SKL": 16,
            "MOV": 8
        },
        mounted_stats={
            "HP": 40,
            "STR": 18,
            "DEF": 15,
            "SPD": 12,
            "SKL": 16,
            "MOV": 8
        },
        dismounted_stats={
            "HP": 40,
            "STR": 16,  # -2
            "DEF": 13,  # -2
            "SPD": 10,  # -2
            "SKL": 14,  # -2
            "MOV": 5    # -3
        },
        usable_weapon_types_mounted=["SWORD", "LANCE"],
        usable_weapon_types_dismounted=["SWORD"],
        current_weapon=steel_lance,
        inventory=[iron_sword, steel_lance]
    )
    
    # Create a flying unit
    pegasus_knight = Unit(
        name="Cordelia",
        class_type="Pegasus Knight",
        is_mounted=True,
        movement_type="FLYING",
        mounted_movement="FLYING",
        dismounted_movement="INFANTRY",
        stats={
            "HP": 35,
            "STR": 14,
            "DEF": 10,
            "SPD": 18,
            "SKL": 16,
            "MOV": 7
        },
        mounted_stats={
            "HP": 35,
            "STR": 14,
            "DEF": 10,
            "SPD": 18,
            "SKL": 16,
            "MOV": 7
        },
        dismounted_stats={
            "HP": 35,
            "STR": 12,  # -2
            "DEF": 8,   # -2
            "SPD": 16,  # -2
            "SKL": 14,  # -2
            "MOV": 5    # -2
        },
        usable_weapon_types_mounted=["LANCE"],
        usable_weapon_types_dismounted=["SWORD", "LANCE"],
        current_weapon=steel_lance,
        inventory=[iron_sword, steel_lance]
    )
    
    # Demonstrate Paladin dismounting
    print("\n" + "="*20 + " PALADIN DEMONSTRATION " + "="*20)
    
    # Show initial state
    print_unit_stats(paladin)
    print_terrain_interaction(paladin, [plains, forest, mountain, indoor_hall])
    print_weapon_effectiveness(paladin, [horseslayer, ridersbane, bow])
    
    # Dismount the paladin
    print("\nDismounting Paladin...")
    paladin.dismount()
    
    # Show state after dismounting
    print_unit_stats(paladin)
    print_terrain_interaction(paladin, [plains, forest, mountain, indoor_hall])
    print_weapon_effectiveness(paladin, [horseslayer, ridersbane, bow])
    
    # Remount the paladin
    print("\nRemounting Paladin...")
    paladin.mount()
    
    # Show state after remounting
    print_unit_stats(paladin)
    
    # Demonstrate Pegasus Knight dismounting
    print("\n" + "="*20 + " PEGASUS KNIGHT DEMONSTRATION " + "="*20)
    
    # Show initial state
    print_unit_stats(pegasus_knight)
    print_terrain_interaction(pegasus_knight, [plains, forest, mountain, indoor_hall])
    print_weapon_effectiveness(pegasus_knight, [horseslayer, ridersbane, bow])
    
    # Dismount the pegasus knight
    print("\nDismounting Pegasus Knight...")
    pegasus_knight.dismount()
    
    # Show state after dismounting
    print_unit_stats(pegasus_knight)
    print_terrain_interaction(pegasus_knight, [plains, forest, mountain, indoor_hall])
    print_weapon_effectiveness(pegasus_knight, [horseslayer, ridersbane, bow])
    
    # Show automatic weapon switching
    print("\nDemonstrating Automatic Weapon Switching:")
    
    # Create a cavalier with lance only
    cavalier = Unit(
        name="Sully",
        class_type="Cavalier",
        is_mounted=True,
        movement_type="CAVALRY",
        mounted_movement="CAVALRY",
        dismounted_movement="INFANTRY",
        stats={"MOV": 7},
        mounted_stats={"MOV": 7},
        dismounted_stats={"MOV": 5},
        usable_weapon_types_mounted=["LANCE", "AXE"],
        usable_weapon_types_dismounted=["SWORD"],
        current_weapon=steel_lance,
        inventory=[steel_lance, hand_axe, iron_sword]
    )
    
    print(f"\n{cavalier.name}'s current weapon: {cavalier.current_weapon.name}")
    cavalier.dismount()
    print(f"{cavalier.name}'s current weapon after dismounting: {cavalier.current_weapon.name if cavalier.current_weapon else 'None'}")
    
    # Demonstrate indoor map
    print("\n" + "="*20 + " INDOOR MAP DEMONSTRATION " + "="*20)
    
    print("When entering an indoor map, mounted units are automatically dismounted.")
    print("This occurs when the map begins and cannot be reversed until returning outdoors.")
    print("This has the following consequences:")
    print("1. Mounted units lose their mounted movement types and stats")
    print("2. Most cavalry units can only use swords")
    print("3. Flying units completely lose their ability to fly over any terrain")
    print("4. Units are vulnerable to different effective weapons")
    print("5. Units interact with terrain differently")


if __name__ == "__main__":
    main() 