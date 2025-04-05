from typing import Dict, List, Optional, Any, Tuple
from .models import Unit, UnitStats, UnitGrowths, WeaponRanks, WeaponExp, Affiliation, StatusEffect, Skill, MovementType
from .static_data_loader import StaticDataLoader
import random

class UnitManager:
    """
    Manages Unit instances in the game, including creation, tracking, and updates.
    Handles unit stats, status effects, fatigue, and other unit-related operations.
    """
    def __init__(self, static_loader: StaticDataLoader):
        """
        Initializes the UnitManager.
        Args:
            static_loader: An instance of StaticDataLoader to fetch unit and class data.
        """
        self.static_loader = static_loader
        self._units: Dict[str, Unit] = {}  # Maps unit_id to Unit objects
        self._player_units: List[str] = []  # List of player unit IDs
        self._enemy_units: List[str] = []   # List of enemy unit IDs
        self._npc_units: List[str] = []     # List of NPC unit IDs

    def create_unit(self, unit_id: str, name: str, cls_name: str, affiliation: Affiliation, 
                   level: int = 1, base_stats: Optional[Dict[str, int]] = None) -> Optional[Unit]:
        """
        Creates a new Unit instance based on static data and provided parameters.
        Args:
            unit_id: Unique identifier for the unit.
            name: The unit's name.
            cls_name: The class name (e.g., "Lord", "Fighter").
            affiliation: The unit's affiliation (Player, Enemy, NPC).
            level: The unit's starting level.
            base_stats: Optional dictionary of base stats to override class defaults.
        Returns:
            The created Unit instance, or None if creation failed.
        """
        # Get class data from static loader
        class_data = self.static_loader.get_class_data(cls_name)
        if not class_data:
            print(f"Error: Class data for '{cls_name}' not found.")
            return None

        try:
            # Extract movement type from class data
            movement_type_str = class_data.get("movement_type", "INFANTRY")
            try:
                movement_type = MovementType[movement_type_str.upper()]
            except KeyError:
                print(f"Warning: Unknown movement type '{movement_type_str}'. Using INFANTRY.")
                movement_type = MovementType.INFANTRY

            # Determine if the class is mounted
            is_mounted = class_data.get("is_mounted", False)

            # Create base stats from class data, overridden by provided base_stats
            class_base_stats = class_data.get("base_stats", {})
            stats_dict = {**class_base_stats}  # Start with class base stats
            if base_stats:
                stats_dict.update(base_stats)  # Override with provided base stats

            # Ensure all required stats have values
            default_stats = {
                "hp": 20, "max_hp": 20, "strength": 5, "magic": 0,
                "skill": 5, "speed": 5, "luck": 0, "defense": 5,
                "constitution": 5, "movement": 5, "build": 5
            }
            for stat, default in default_stats.items():
                if stat not in stats_dict:
                    stats_dict[stat] = default

            # Create UnitStats object
            stats = UnitStats(
                hp=stats_dict.get("hp", 20),
                max_hp=stats_dict.get("max_hp", 20),
                strength=stats_dict.get("strength", 5),
                magic=stats_dict.get("magic", 0),
                skill=stats_dict.get("skill", 5),
                speed=stats_dict.get("speed", 5),
                luck=stats_dict.get("luck", 0),
                defense=stats_dict.get("defense", 5),
                constitution=stats_dict.get("constitution", 5),
                movement=stats_dict.get("movement", 5),
                build=stats_dict.get("build", 5)
            )

            # Get growth rates from class data or use defaults
            growth_data = class_data.get("growths", {})
            growths = UnitGrowths(
                hp=growth_data.get("hp", 50),
                strength=growth_data.get("strength", 30),
                magic=growth_data.get("magic", 10),
                skill=growth_data.get("skill", 30),
                speed=growth_data.get("speed", 30),
                luck=growth_data.get("luck", 20),
                defense=growth_data.get("defense", 20),
                constitution=growth_data.get("constitution", 5),
                movement=growth_data.get("movement", 2)
            )

            # Get weapon ranks from class data
            weapon_ranks_data = class_data.get("weapon_ranks", {})
            weapon_ranks = WeaponRanks()
            for weapon_type, rank_str in weapon_ranks_data.items():
                if hasattr(weapon_ranks, weapon_type.lower()):
                    try:
                        from thracia776.data.models import WeaponRank
                        rank = WeaponRank[rank_str.upper()]
                        setattr(weapon_ranks, weapon_type.lower(), rank)
                    except (KeyError, AttributeError) as e:
                        print(f"Warning: Error setting weapon rank for {weapon_type}: {e}")

            # Create the Unit
            unit = Unit(
                id=unit_id,
                name=name,
                cls_name=cls_name,
                affiliation=affiliation,
                level=level,
                exp=0,
                stats=stats,
                growths=growths,
                status=StatusEffect.NORMAL,
                fatigue=0,
                weapon_ranks=weapon_ranks,
                movement_type=movement_type,
                is_mounted=is_mounted
            )

            # Store the unit
            self._units[unit_id] = unit
            
            # Add to appropriate affiliation list
            if affiliation == Affiliation.PLAYER:
                self._player_units.append(unit_id)
            elif affiliation == Affiliation.ENEMY:
                self._enemy_units.append(unit_id)
            elif affiliation == Affiliation.NPC:
                self._npc_units.append(unit_id)

            return unit

        except Exception as e:
            print(f"Error creating unit '{unit_id}': {e}")
            return None

    def get_unit(self, unit_id: str) -> Optional[Unit]:
        """
        Retrieves a Unit instance by its ID.
        Args:
            unit_id: The unique ID of the unit.
        Returns:
            The Unit instance, or None if not found.
        """
        return self._units.get(unit_id)

    def remove_unit(self, unit_id: str) -> bool:
        """
        Removes a unit from the system entirely.
        Args:
            unit_id: The unique ID of the unit.
        Returns:
            True if the unit was removed successfully, False otherwise.
        """
        if unit_id not in self._units:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False
            
        # Get the unit to check affiliation
        unit = self._units[unit_id]
        
        # Remove from appropriate affiliation list
        if unit.affiliation == Affiliation.PLAYER:
            if unit_id in self._player_units:
                self._player_units.remove(unit_id)
        elif unit.affiliation == Affiliation.ENEMY:
            if unit_id in self._enemy_units:
                self._enemy_units.remove(unit_id)
        elif unit.affiliation == Affiliation.NPC:
            if unit_id in self._npc_units:
                self._npc_units.remove(unit_id)
                
        # Remove from units dictionary
        del self._units[unit_id]
        return True

    def update_unit_stats(self, unit_id: str, **stat_changes) -> bool:
        """
        Updates specific stats of a unit.
        Args:
            unit_id: The unique ID of the unit.
            **stat_changes: Key-value pairs of stats to update.
        Returns:
            True if the stats were updated successfully, False otherwise.
        """
        unit = self.get_unit(unit_id)
        if not unit:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False
            
        # Update stats
        for stat_name, value in stat_changes.items():
            if hasattr(unit.stats, stat_name):
                setattr(unit.stats, stat_name, value)
            else:
                print(f"Warning: Unit stats has no attribute '{stat_name}'.")
                
        return True

    def update_unit_status(self, unit_id: str, status: StatusEffect) -> bool:
        """
        Updates the status effect of a unit.
        Args:
            unit_id: The unique ID of the unit.
            status: The new status effect.
        Returns:
            True if the status was updated successfully, False otherwise.
        """
        unit = self.get_unit(unit_id)
        if not unit:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False
            
        unit.status = status
        return True

    def update_fatigue(self, unit_id: str, fatigue_change: int) -> bool:
        """
        Updates the fatigue level of a unit.
        Args:
            unit_id: The unique ID of the unit.
            fatigue_change: The change in fatigue points.
        Returns:
            True if the fatigue was updated successfully, False otherwise.
        """
        unit = self.get_unit(unit_id)
        if not unit:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False
            
        unit.fatigue += fatigue_change
        
        # Ensure fatigue doesn't go below 0
        if unit.fatigue < 0:
            unit.fatigue = 0
            
        return True

    def level_up(self, unit_id: str) -> Tuple[bool, Dict[str, int]]:
        """
        Performs a level-up for a unit, applying random stat increases based on growth rates.
        Args:
            unit_id: The unique ID of the unit.
        Returns:
            A tuple of (success, stat_increases) where stat_increases is a dictionary
            mapping stat names to their increases.
        """
        unit = self.get_unit(unit_id)
        if not unit:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False, {}
            
        # Reset EXP and increment level
        unit.exp = 0
        unit.level += 1
        
        # Calculate stat increases based on growth rates
        stat_increases = {}
        
        # Check each stat for growth
        for stat_name in ["hp", "strength", "magic", "skill", "speed", "luck", "defense"]:
            growth_rate = getattr(unit.growths, stat_name)
            # Roll for stat increase (0-99)
            if random.randint(0, 99) < growth_rate:
                # Get current stat value
                current_value = getattr(unit.stats, stat_name)
                # Increase stat by 1
                setattr(unit.stats, stat_name, current_value + 1)
                # Record increase
                stat_increases[stat_name] = 1
            else:
                stat_increases[stat_name] = 0
                
        # Special cases for Con and Mov (rare growths)
        for stat_name in ["constitution", "movement"]:
            growth_rate = getattr(unit.growths, stat_name)
            if random.randint(0, 99) < growth_rate:
                current_value = getattr(unit.stats, stat_name)
                setattr(unit.stats, stat_name, current_value + 1)
                stat_increases[stat_name] = 1
            else:
                stat_increases[stat_name] = 0
                
        # Ensure max_hp is updated if hp increased
        if "hp" in stat_increases and stat_increases["hp"] > 0:
            unit.stats.max_hp += stat_increases["hp"]
            
        return True, stat_increases

    def get_all_units_by_affiliation(self, affiliation: Affiliation) -> List[Unit]:
        """
        Gets all units of a specific affiliation.
        Args:
            affiliation: The affiliation to filter by.
        Returns:
            A list of Unit instances with the specified affiliation.
        """
        if affiliation == Affiliation.PLAYER:
            return [self._units[unit_id] for unit_id in self._player_units if unit_id in self._units]
        elif affiliation == Affiliation.ENEMY:
            return [self._units[unit_id] for unit_id in self._enemy_units if unit_id in self._units]
        elif affiliation == Affiliation.NPC:
            return [self._units[unit_id] for unit_id in self._npc_units if unit_id in self._units]
        return []

    def reset_action_flags(self, affiliation: Optional[Affiliation] = None) -> None:
        """
        Resets the 'has_acted' flag for units, optionally filtered by affiliation.
        Args:
            affiliation: Optional affiliation to filter by. If None, resets all units.
        """
        units_to_reset = []
        
        if affiliation is None:
            # Reset all units
            units_to_reset = list(self._units.values())
        else:
            # Reset units of specific affiliation
            units_to_reset = self.get_all_units_by_affiliation(affiliation)
            
        for unit in units_to_reset:
            unit.has_acted = False

    def add_skill(self, unit_id: str, skill: Skill) -> bool:
        """
        Adds a skill to a unit.
        Args:
            unit_id: The unique ID of the unit.
            skill: The skill to add.
        Returns:
            True if the skill was added successfully, False otherwise.
        """
        unit = self.get_unit(unit_id)
        if not unit:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False
            
        if skill in unit.skills:
            print(f"Warning: Unit already has skill '{skill}'.")
            return True
            
        unit.skills.append(skill)
        return True

    def remove_skill(self, unit_id: str, skill: Skill) -> bool:
        """
        Removes a skill from a unit.
        Args:
            unit_id: The unique ID of the unit.
            skill: The skill to remove.
        Returns:
            True if the skill was removed successfully, False otherwise.
        """
        unit = self.get_unit(unit_id)
        if not unit:
            print(f"Error: Unit with ID '{unit_id}' not found.")
            return False
            
        if skill not in unit.skills:
            print(f"Warning: Unit does not have skill '{skill}'.")
            return False
            
        unit.skills.remove(skill)
        return True

# Example Usage (requires StaticDataLoader)
if __name__ == "__main__":
    # This example won't run without StaticDataLoader instance
    print("UnitManager example usage (requires dependencies)")
    # loader = StaticDataLoader() # Needs proper setup
    # loader.load_all_data()
    # unit_manager = UnitManager(loader)
    # leif = unit_manager.create_unit("leif", "Leif", "Lord", Affiliation.PLAYER)
    # if leif:
    #     print(f"Created unit: {leif.name}, Class: {leif.cls_name}")
    #     print(f"Base stats: HP={leif.stats.hp}, Str={leif.stats.strength}")
    #     success, increases = unit_manager.level_up("leif")
    #     print(f"Level up results: {increases}")
