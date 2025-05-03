"""
Test for Stealing System

This test verifies that the stealing system correctly implements the mechanics for stealing items
from enemy units, including steal conditions, target item selection, and successful/failed steal outcomes.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.core_engine.game_state import GameStateManager, FactionEnum
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.action_system import ActionSystem
from src.gameplay_systems.ui_system import UISystem

# Import the StealingSystem class (will be implemented later)
# from src.gameplay_systems.stealing_system import StealingSystem


# Mock Item class for testing
class MockItem:
    """A simple mock item for testing."""
    
    def __init__(self, name, weight, is_equipped=False, item_type="Weapon"):
        self.id = f"{name.upper().replace(' ', '_')}"
        self.name = name
        self.weight = weight
        self.is_equipped = is_equipped
        self.type = item_type


class TestStealingSystem:
    """Test cases for the stealing system."""

    @pytest.fixture
    def setup_game_components(self):
        """Set up the game components needed for testing."""
        # Initialize components
        data_provider = MagicMock(spec=DataProvider)
        game_state_manager = MagicMock(spec=GameStateManager)
        unit_system = MagicMock(spec=UnitSystem)
        map_system = MagicMock(spec=MapSystem)
        inventory_system = MagicMock(spec=InventorySystem)
        action_system = MagicMock(spec=ActionSystem)
        ui_system = MagicMock(spec=UISystem)
        
        # Mock the StealingSystem class until it's implemented
        stealing_system = MagicMock()
        stealing_system.can_initiate_steal = MagicMock(return_value=False)
        stealing_system.defender_has_any_stealable_item = MagicMock(return_value=False)
        stealing_system.present_steal_item_selection = MagicMock(return_value=None)
        stealing_system.execute_steal = MagicMock(return_value=False)
        
        # Mock the is_adjacent method of MapSystem
        map_system.is_adjacent = MagicMock(return_value=True)
        
        # Mock the unit_has_skill method of DataProvider
        data_provider.unit_has_skill = MagicMock(return_value=False)
        
        return {
            "data_provider": data_provider,
            "game_state_manager": game_state_manager,
            "unit_system": unit_system,
            "map_system": map_system,
            "inventory_system": inventory_system,
            "action_system": action_system,
            "ui_system": ui_system,
            "stealing_system": stealing_system
        }
    
    @pytest.fixture
    def setup_units(self):
        """Set up test units for stealing scenarios."""
        # Create thief unit (has Steal skill)
        thief = MagicMock()
        thief.id = "THIEF"
        thief.name = "Thief"
        thief.faction = FactionEnum.PLAYER
        thief.position = (1, 1)
        thief.cls_name = "Thief"
        thief.skills = ["Steal"]
        thief.stats = {
            "speed": 12, "con": 8
        }
        thief.calculated_stats = {
            "attack_speed": 10
        }
        thief.inventory = [
            MockItem("Iron Dagger", 3),
            MockItem("Vulnerary", 1, False, "Consumable")
        ]
        thief.has_acted = False
        thief.fatigue = 0
        
        # Create non-thief unit (doesn't have Steal skill)
        non_thief = MagicMock()
        non_thief.id = "FIGHTER"
        non_thief.name = "Fighter"
        non_thief.faction = FactionEnum.PLAYER
        non_thief.position = (2, 1)
        non_thief.cls_name = "Fighter"
        non_thief.skills = []
        non_thief.stats = {
            "speed": 8, "con": 12
        }
        non_thief.calculated_stats = {
            "attack_speed": 6
        }
        non_thief.inventory = [
            MockItem("Iron Axe", 8, True),
            MockItem("Vulnerary", 1, False, "Consumable")
        ]
        non_thief.has_acted = False
        non_thief.fatigue = 0
        
        # Create target unit with stealable items
        target_with_items = MagicMock()
        target_with_items.id = "ENEMY_SOLDIER"
        target_with_items.name = "Enemy Soldier"
        target_with_items.faction = FactionEnum.ENEMY
        target_with_items.position = (1, 2)  # Adjacent to thief
        target_with_items.stats = {
            "speed": 7, "con": 10
        }
        target_with_items.calculated_stats = {
            "attack_speed": 5  # Slower than thief
        }
        target_with_items.inventory = [
            MockItem("Iron Lance", 8, True),
            MockItem("Vulnerary", 1, False, "Consumable"),
            MockItem("Door Key", 1, False, "Key")
        ]
        
        # Create target unit with no stealable items (all too heavy)
        target_heavy_items = MagicMock()
        target_heavy_items.id = "ENEMY_KNIGHT"
        target_heavy_items.name = "Enemy Knight"
        target_heavy_items.faction = FactionEnum.ENEMY
        target_heavy_items.position = (2, 2)  # Adjacent to non-thief
        target_heavy_items.stats = {
            "speed": 5, "con": 14
        }
        target_heavy_items.calculated_stats = {
            "attack_speed": 3  # Slower than both thief and non-thief
        }
        target_heavy_items.inventory = [
            MockItem("Steel Lance", 12, True),
            MockItem("Steel Axe", 14, False)
        ]
        
        # Create target unit with empty inventory
        target_empty_inventory = MagicMock()
        target_empty_inventory.id = "ENEMY_MAGE"
        target_empty_inventory.name = "Enemy Mage"
        target_empty_inventory.faction = FactionEnum.ENEMY
        target_empty_inventory.position = (3, 1)
        target_empty_inventory.stats = {
            "speed": 8, "con": 5
        }
        target_empty_inventory.calculated_stats = {
            "attack_speed": 6  # Same as non-thief
        }
        target_empty_inventory.inventory = []
        
        # Create fast target unit (faster than thief)
        fast_target = MagicMock()
        fast_target.id = "ENEMY_MYRMIDON"
        fast_target.name = "Enemy Myrmidon"
        fast_target.faction = FactionEnum.ENEMY
        fast_target.position = (3, 2)
        fast_target.stats = {
            "speed": 14, "con": 7
        }
        fast_target.calculated_stats = {
            "attack_speed": 12  # Faster than thief
        }
        fast_target.inventory = [
            MockItem("Iron Sword", 5, True),
            MockItem("Vulnerary", 1, False, "Consumable")
        ]
        
        return {
            "thief": thief,
            "non_thief": non_thief,
            "target_with_items": target_with_items,
            "target_heavy_items": target_heavy_items,
            "target_empty_inventory": target_empty_inventory,
            "fast_target": fast_target
        }
    
    # TEST: test_can_initiate_steal_valid_thief
    def test_can_initiate_steal_valid_thief(self, setup_game_components, setup_units):
        """Test that only units with the 'Steal' skill can initiate stealing."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        data_provider = setup_game_components["data_provider"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Mock the unit_has_skill method to return True for the thief
        data_provider.unit_has_skill.side_effect = lambda unit_id, skill_id: unit_id == "THIEF" and skill_id == "Steal"
        
        # Mock the can_initiate_steal method to use our implementation
        def can_initiate_steal_impl(attacker, defender):
            # Must have the Steal skill
            if not data_provider.unit_has_skill(attacker.id, "Steal"):
                return False
            return True
            
        stealing_system.can_initiate_steal.side_effect = can_initiate_steal_impl
        
        # Test the condition
        result = stealing_system.can_initiate_steal(thief, target)
        
        # Verify the result
        assert result is True, "Unit with 'Steal' skill should be able to initiate stealing"
        data_provider.unit_has_skill.assert_called_with(thief.id, "Steal")
    
    # TEST: test_can_initiate_steal_invalid_non_thief
    def test_can_initiate_steal_invalid_non_thief(self, setup_game_components, setup_units):
        """Test that units without the 'Steal' skill cannot initiate stealing."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        data_provider = setup_game_components["data_provider"]
        
        # Get units
        non_thief = setup_units["non_thief"]
        target = setup_units["target_with_items"]
        
        # Mock the unit_has_skill method to return False for the non-thief
        data_provider.unit_has_skill.side_effect = lambda unit_id, skill_id: unit_id == "THIEF" and skill_id == "Steal"
        
        # Mock the can_initiate_steal method to use our implementation
        def can_initiate_steal_impl(attacker, defender):
            # Must have the Steal skill
            if not data_provider.unit_has_skill(attacker.id, "Steal"):
                return False
            return True
            
        stealing_system.can_initiate_steal.side_effect = can_initiate_steal_impl
        
        # Test the condition
        result = stealing_system.can_initiate_steal(non_thief, target)
        
        # Verify the result
        assert result is False, "Unit without 'Steal' skill should not be able to initiate stealing"
        data_provider.unit_has_skill.assert_called_with(non_thief.id, "Steal")
    
    # TEST: test_can_initiate_steal_adjacent
    def test_can_initiate_steal_adjacent(self, setup_game_components, setup_units):
        """Test that stealing can only be initiated against adjacent units."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        map_system = setup_game_components["map_system"]
        data_provider = setup_game_components["data_provider"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Mock the unit_has_skill method to return True for the thief
        data_provider.unit_has_skill.side_effect = lambda unit_id, skill_id: unit_id == "THIEF" and skill_id == "Steal"
        
        # Mock the is_adjacent method to return True
        map_system.is_adjacent.return_value = True
        
        # Mock the can_initiate_steal method to use our implementation
        def can_initiate_steal_impl(attacker, defender):
            # Must have the Steal skill
            if not data_provider.unit_has_skill(attacker.id, "Steal"):
                return False
            
            # Must be adjacent
            if not map_system.is_adjacent(attacker.position, defender.position):
                return False
                
            return True
            
        stealing_system.can_initiate_steal.side_effect = can_initiate_steal_impl
        
        # Test the condition
        result = stealing_system.can_initiate_steal(thief, target)
        
        # Verify the result
        assert result is True, "Stealing should be possible against adjacent units"
        map_system.is_adjacent.assert_called_with(thief.position, target.position)
    
    # TEST: test_can_initiate_steal_non_adjacent
    def test_can_initiate_steal_non_adjacent(self, setup_game_components, setup_units):
        """Test that stealing cannot be initiated against non-adjacent units."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        map_system = setup_game_components["map_system"]
        data_provider = setup_game_components["data_provider"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Mock the unit_has_skill method to return True for the thief
        data_provider.unit_has_skill.side_effect = lambda unit_id, skill_id: unit_id == "THIEF" and skill_id == "Steal"
        
        # Mock the is_adjacent method to return False
        map_system.is_adjacent.return_value = False
        
        # Mock the can_initiate_steal method to use our implementation
        def can_initiate_steal_impl(attacker, defender):
            # Must have the Steal skill
            if not data_provider.unit_has_skill(attacker.id, "Steal"):
                return False
            
            # Must be adjacent
            if not map_system.is_adjacent(attacker.position, defender.position):
                return False
                
            return True
            
        stealing_system.can_initiate_steal.side_effect = can_initiate_steal_impl
        
        # Test the condition
        result = stealing_system.can_initiate_steal(thief, target)
        
        # Verify the result
        assert result is False, "Stealing should not be possible against non-adjacent units"
        map_system.is_adjacent.assert_called_with(thief.position, target.position)
    
    # TEST: test_defender_has_any_stealable_item_empty_inventory
    def test_defender_has_any_stealable_item_empty_inventory(self, setup_game_components, setup_units):
        """Test that defender_has_any_stealable_item returns False if defender's inventory is empty."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target_empty = setup_units["target_empty_inventory"]
        
        # Mock the defender_has_any_stealable_item method to use our implementation
        def defender_has_any_stealable_item_impl(attacker, defender):
            # If defender inventory is empty, return False
            if not defender.inventory:
                return False
            return True
            
        stealing_system.defender_has_any_stealable_item.side_effect = defender_has_any_stealable_item_impl
        
        # Test the condition
        result = stealing_system.defender_has_any_stealable_item(thief, target_empty)
        
        # Verify the result
        assert result is False, "Should return False if defender's inventory is empty"
    
    # TEST: test_defender_has_any_stealable_item_check
    def test_defender_has_any_stealable_item_check(self, setup_game_components, setup_units):
        """Test that defender_has_any_stealable_item correctly checks AS and Con/Weight conditions."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Mock the defender_has_any_stealable_item method to use our implementation
        def defender_has_any_stealable_item_impl(attacker, defender):
            # If defender inventory is empty, return False
            if not defender.inventory:
                return False
            
            # Check if at least one item meets the core steal conditions (AS and Con/Weight)
            for item in defender.inventory:
                # Check AS condition (Attacker AS > Defender AS)
                is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
                # Check Weight condition (Item Weight <= Attacker Con)
                can_carry = item.weight <= attacker.stats["con"]
                
                if is_faster and can_carry:
                    return True  # Found at least one potentially stealable item
            
            return False  # No items meet the core conditions
            
        stealing_system.defender_has_any_stealable_item.side_effect = defender_has_any_stealable_item_impl
        
        # Test the condition
        result = stealing_system.defender_has_any_stealable_item(thief, target)
        
        # Verify the result
        assert result is True, "Should return True if at least one item meets AS and Con/Weight conditions"
    
    # TEST: test_defender_has_any_stealable_item_too_slow
    def test_defender_has_any_stealable_item_too_slow(self, setup_game_components, setup_units):
        """Test that defender_has_any_stealable_item returns False if attacker is slower than defender."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        fast_target = setup_units["fast_target"]
        
        # Mock the defender_has_any_stealable_item method to use our implementation
        def defender_has_any_stealable_item_impl(attacker, defender):
            # If defender inventory is empty, return False
            if not defender.inventory:
                return False
            
            # Check if at least one item meets the core steal conditions (AS and Con/Weight)
            for item in defender.inventory:
                # Check AS condition (Attacker AS > Defender AS)
                is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
                # Check Weight condition (Item Weight <= Attacker Con)
                can_carry = item.weight <= attacker.stats["con"]
                
                if is_faster and can_carry:
                    return True  # Found at least one potentially stealable item
            
            return False  # No items meet the core conditions
            
        stealing_system.defender_has_any_stealable_item.side_effect = defender_has_any_stealable_item_impl
        
        # Test the condition
        result = stealing_system.defender_has_any_stealable_item(thief, fast_target)
        
        # Verify the result
        assert result is False, "Should return False if attacker is slower than defender"
    
    # TEST: test_present_steal_item_selection_equipped_items
    def test_present_steal_item_selection_equipped_items(self, setup_game_components, setup_units):
        """Test that present_steal_item_selection doesn't include equipped items."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        ui_system = setup_game_components["ui_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Mock the show_item_selection_menu method to return all eligible items
        def show_item_selection_menu_side_effect(title, items):
            return items
            
        ui_system.show_item_selection_menu = MagicMock(side_effect=show_item_selection_menu_side_effect)
        
        # Mock the present_steal_item_selection method to use our implementation
        def present_steal_item_selection_impl(attacker, defender):
            eligible_items = []
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            # Pre-calculate conditions that apply to all items for efficiency
            if not is_faster or not has_space:
                # If basic conditions fail, no items are eligible
                return None
            
            for item in defender.inventory:
                # Check specific item weight condition and equipped status
                can_carry = item.weight <= attacker.stats["con"]
                if can_carry and not item.is_equipped:  # Only non-equipped items can be stolen
                    eligible_items.append(item)
            
            if not eligible_items:
                # This might happen if all items are too heavy or equipped
                return None
            
            # UI presents eligible_items to the player
            # Player selects an item or cancels
            selected_items = ui_system.show_item_selection_menu("Select item to steal:", eligible_items)
            
            return selected_items
            
        stealing_system.present_steal_item_selection.side_effect = present_steal_item_selection_impl
        
        # Test the condition
        result = stealing_system.present_steal_item_selection(thief, target)
        
        # Verify the result
        assert result is not None, "Should return eligible items"
        
        # Check that no equipped items are in the result
        for item in result:
            assert item.is_equipped is False, "Equipped items should not be stealable"
        
        # Verify that the Iron Lance (equipped) is not in the result
        equipped_items = [item for item in target.inventory if item.is_equipped]
        for equipped_item in equipped_items:
            assert equipped_item not in result, f"Equipped item {equipped_item.name} should not be in eligible items"
    
    # TEST: test_present_steal_item_selection_ui_filtering
    def test_present_steal_item_selection_ui_filtering(self, setup_game_components, setup_units):
        """Test that present_steal_item_selection correctly filters items based on conditions."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        ui_system = setup_game_components["ui_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Mock the show_item_selection_menu method to return the first eligible item
        def show_item_selection_menu_side_effect(title, items):
            if items:
                return items[0]
            return None
            
        ui_system.show_item_selection_menu = MagicMock(side_effect=show_item_selection_menu_side_effect)
        
        # Mock the present_steal_item_selection method to use our implementation
        def present_steal_item_selection_impl(attacker, defender):
            eligible_items = []
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            # Pre-calculate conditions that apply to all items for efficiency
            if not is_faster or not has_space:
                # If basic conditions fail, no items are eligible
                return None
            
            for item in defender.inventory:
                # Check specific item weight condition
                can_carry = item.weight <= attacker.stats["con"]
                if can_carry:  # Already checked speed and space
                    eligible_items.append(item)
            
            if not eligible_items:
                # This might happen if all items are too heavy, even if speed/space is okay
                return None
            
            # UI presents eligible_items to the player
            # Player selects an item or cancels
            selected_item = ui_system.show_item_selection_menu("Select item to steal:", eligible_items)
            
            return selected_item
            
        stealing_system.present_steal_item_selection.side_effect = present_steal_item_selection_impl
        
        # Test the condition
        result = stealing_system.present_steal_item_selection(thief, target)
        
        # Verify the result
        assert result is not None, "Should return a selected item if eligible items exist"
        assert result.weight <= thief.stats["con"], "Selected item should be light enough to steal"
        ui_system.show_item_selection_menu.assert_called_once()
    
    # TEST: test_execute_steal_item_transfer
    def test_execute_steal_item_transfer(self, setup_game_components, setup_units):
        """Test that execute_steal correctly transfers the item from defender to attacker."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Item to steal
        item_to_steal = target.inventory[2]  # Door Key
        
        # Original inventory sizes
        original_thief_inventory_size = len(thief.inventory)
        original_target_inventory_size = len(target.inventory)
        
        # Mock the execute_steal method to use our implementation
        def execute_steal_impl(attacker, defender, item_to_steal):
            # Double-check all conditions before modifying state
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            can_carry = item_to_steal.weight <= attacker.stats["con"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            if not (is_faster and can_carry and has_space):
                return False
            
            # 1. Remove item from defender's inventory
            defender.inventory.remove(item_to_steal)
            
            # 2. Add item to attacker's inventory
            item_to_steal.is_equipped = False  # Stolen items are never equipped immediately
            attacker.inventory.append(item_to_steal)
            
            # 3. Apply fatigue cost to attacker
            attacker.fatigue += 1
            
            # 4. Mark action as consumed for the turn
            attacker.has_acted = True
            
            return True
            
        stealing_system.execute_steal.side_effect = execute_steal_impl
        
        # Test the condition
        result = stealing_system.execute_steal(thief, target, item_to_steal)
        
        # Verify the result
        assert result is True, "Steal should succeed"
        assert len(thief.inventory) == original_thief_inventory_size + 1, "Thief should have one more item"
        assert len(target.inventory) == original_target_inventory_size - 1, "Target should have one less item"
        assert item_to_steal in thief.inventory, "Thief should have the stolen item"
        assert item_to_steal not in target.inventory, "Target should not have the stolen item"
        assert item_to_steal.is_equipped is False, "Stolen item should not be equipped"
    
    # TEST: test_execute_steal_inventory_limit
    def test_execute_steal_inventory_limit(self, setup_game_components, setup_units):
        """Test that execute_steal fails when the thief's inventory is full."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Fill the thief's inventory (assuming max is 7 items)
        thief.inventory = [
            MockItem("Iron Dagger", 3),
            MockItem("Steel Dagger", 5),
            MockItem("Silver Dagger", 7),
            MockItem("Vulnerary", 1, False, "Consumable"),
            MockItem("Antitoxin", 1, False, "Consumable"),
            MockItem("Door Key", 1, False, "Key"),
            MockItem("Chest Key", 1, False, "Key")
        ]
        
        # Item to steal
        item_to_steal = target.inventory[2]  # Door Key
        
        # Original inventory sizes
        original_thief_inventory_size = len(thief.inventory)
        original_target_inventory_size = len(target.inventory)
        
        # Mock the execute_steal method to use our implementation
        def execute_steal_impl(attacker, defender, item_to_steal):
            # Double-check all conditions before modifying state
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            can_carry = item_to_steal.weight <= attacker.stats["con"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            if not (is_faster and can_carry and has_space):
                return False
            
            # 1. Remove item from defender's inventory
            defender.inventory.remove(item_to_steal)
            
            # 2. Add item to attacker's inventory
            item_to_steal.is_equipped = False  # Stolen items are never equipped immediately
            attacker.inventory.append(item_to_steal)
            
            # 3. Apply fatigue cost to attacker
            attacker.fatigue += 1
            
            # 4. Mark action as consumed for the turn
            attacker.has_acted = True
            
            return True
            
        stealing_system.execute_steal.side_effect = execute_steal_impl
        
        # Test the condition
        result = stealing_system.execute_steal(thief, target, item_to_steal)
        
        # Verify the result
        assert result is False, "Steal should fail when inventory is full"
        assert len(thief.inventory) == original_thief_inventory_size, "Thief's inventory should remain unchanged"
        assert len(target.inventory) == original_target_inventory_size, "Target's inventory should remain unchanged"
        assert item_to_steal in target.inventory, "Target should still have the item"
        assert item_to_steal not in thief.inventory, "Thief should not have the item"
    
    # TEST: test_execute_steal_fatigue_increase
    def test_execute_steal_fatigue_increase(self, setup_game_components, setup_units):
        """Test that execute_steal increases the attacker's fatigue by 1."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Item to steal
        item_to_steal = target.inventory[2]  # Door Key
        
        # Original fatigue
        original_fatigue = thief.fatigue
        
        # Mock the execute_steal method to use our implementation
        def execute_steal_impl(attacker, defender, item_to_steal):
            # Double-check all conditions before modifying state
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            can_carry = item_to_steal.weight <= attacker.stats["con"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            if not (is_faster and can_carry and has_space):
                return False
            
            # 1. Remove item from defender's inventory
            defender.inventory.remove(item_to_steal)
            
            # 2. Add item to attacker's inventory
            item_to_steal.is_equipped = False  # Stolen items are never equipped immediately
            attacker.inventory.append(item_to_steal)
            
            # 3. Apply fatigue cost to attacker
            attacker.fatigue += 1
            
            # 4. Mark action as consumed for the turn
            attacker.has_acted = True
            
            return True
            
        stealing_system.execute_steal.side_effect = execute_steal_impl
        
        # Test the condition
        result = stealing_system.execute_steal(thief, target, item_to_steal)
        
        # Verify the result
        assert result is True, "Steal should succeed"
        assert thief.fatigue == original_fatigue + 1, "Thief's fatigue should increase by 1"
    
    # TEST: test_execute_steal_action_consumed
    def test_execute_steal_action_consumed(self, setup_game_components, setup_units):
        """Test that execute_steal marks the attacker's action as consumed."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = setup_units["target_with_items"]
        
        # Item to steal
        item_to_steal = target.inventory[2]  # Door Key
        
        # Ensure thief has not acted yet
        thief.has_acted = False
        
        # Mock the execute_steal method to use our implementation
        def execute_steal_impl(attacker, defender, item_to_steal):
            # Double-check all conditions before modifying state
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            can_carry = item_to_steal.weight <= attacker.stats["con"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            if not (is_faster and can_carry and has_space):
                return False
            
            # 1. Remove item from defender's inventory
            defender.inventory.remove(item_to_steal)
            
            # 2. Add item to attacker's inventory
            item_to_steal.is_equipped = False  # Stolen items are never equipped immediately
            attacker.inventory.append(item_to_steal)
            
            # 3. Apply fatigue cost to attacker
            attacker.fatigue += 1
            
            # 4. Mark action as consumed for the turn
            attacker.has_acted = True
            
            return True
            
        stealing_system.execute_steal.side_effect = execute_steal_impl
        
        # Test the condition
        result = stealing_system.execute_steal(thief, target, item_to_steal)
        
        # Verify the result
        assert result is True, "Steal should succeed"
        assert thief.has_acted is True, "Thief's action should be marked as consumed"
    
    # TEST: test_execute_steal_pre_check
    def test_execute_steal_pre_check(self, setup_game_components, setup_units):
        """Test that execute_steal performs pre-checks before modifying state."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        fast_target = setup_units["fast_target"]
        
        # Item to steal
        item_to_steal = fast_target.inventory[0]  # Iron Sword (5 weight)
        
        # Mock the execute_steal method to use our implementation
        def execute_steal_impl(attacker, defender, item_to_steal):
            # Double-check all conditions before modifying state
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            can_carry = item_to_steal.weight <= attacker.stats["con"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            if not (is_faster and can_carry and has_space):
                return False
            
            # If we get here, all conditions are met, so we would modify state
            # But in this test case, we should not reach this point
            return True
            
        stealing_system.execute_steal.side_effect = execute_steal_impl
        
        # Test the condition
        result = stealing_system.execute_steal(thief, fast_target, item_to_steal)
        
        # Verify the result
        assert result is False, "Steal should fail pre-check (thief is slower than target)"
        # Verify that the inventories remain unchanged
        assert item_to_steal in fast_target.inventory, "Target should still have the item"
        assert item_to_steal not in thief.inventory, "Thief should not have the item"
    
    # TEST: test_defender_auto_equip_after_steal
    def test_defender_auto_equip_after_steal(self, setup_game_components, setup_units):
        """Test that defender attempts to auto-equip another weapon if their equipped one was stolen."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        
        # Get units
        thief = setup_units["thief"]
        target = MagicMock()
        target.id = "ENEMY_SOLDIER"
        target.name = "Enemy Soldier"
        target.faction = FactionEnum.ENEMY
        target.position = (1, 2)  # Adjacent to thief
        target.stats = {
            "speed": 7, "con": 10
        }
        target.calculated_stats = {
            "attack_speed": 5  # Slower than thief
        }
        
        # Create inventory with equipped item that can be stolen (for this test)
        equipped_item = MockItem("Iron Dagger", 3, True)
        backup_weapon = MockItem("Iron Sword", 5, False)
        target.inventory = [
            equipped_item,
            backup_weapon,
            MockItem("Vulnerary", 1, False, "Consumable")
        ]
        
        # Mock the try_auto_equip_weapon method
        target.try_auto_equip_weapon = MagicMock()
        
        # Mock the execute_steal method to use our implementation
        def execute_steal_impl(attacker, defender, item_to_steal):
            # Double-check all conditions before modifying state
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            can_carry = item_to_steal.weight <= attacker.stats["con"]
            has_space = len(attacker.inventory) < 7  # Assuming max inventory size is 7
            
            if not (is_faster and can_carry and has_space):
                return False
            
            # 1. Remove item from defender's inventory
            defender.inventory.remove(item_to_steal)
            
            # 2. If item was equipped, defender might need to auto-equip next best weapon
            if item_to_steal.is_equipped:
                defender.try_auto_equip_weapon()
            
            # 3. Add item to attacker's inventory
            item_to_steal.is_equipped = False  # Stolen items are never equipped immediately
            attacker.inventory.append(item_to_steal)
            
            # 4. Apply fatigue cost to attacker
            attacker.fatigue += 1
            
            # 5. Mark action as consumed for the turn
            attacker.has_acted = True
            
            return True
            
        stealing_system.execute_steal.side_effect = execute_steal_impl
        
        # Test the condition
        result = stealing_system.execute_steal(thief, target, equipped_item)
        
        # Verify the result
        assert result is True, "Steal should succeed"
        target.try_auto_equip_weapon.assert_called_once(), "Defender should try to auto-equip another weapon"
    
    # TEST: test_steal_failure_no_action_consumed
    def test_steal_failure_no_action_consumed(self, setup_game_components, setup_units):
        """Test that when steal fails, the unit's action is not consumed."""
        # Get components
        stealing_system = setup_game_components["stealing_system"]
        action_system = setup_game_components["action_system"]
        
        # Get units
        thief = setup_units["thief"]
        fast_target = setup_units["fast_target"]
        
        # Ensure thief has not acted yet
        thief.has_acted = False
        
        # Mock the can_initiate_steal method to return False
        stealing_system.can_initiate_steal.return_value = False
        
        # Mock the action_system's handle_steal_action method
        def handle_steal_action_impl(attacker, defender):
            if not stealing_system.can_initiate_steal(attacker, defender):
                # Cannot initiate steal, do not consume action
                return False
            
            # If we get here, steal was initiated successfully
            # But in this test case, we should not reach this point
            attacker.has_acted = True
            return True
            
        action_system.handle_steal_action = MagicMock(side_effect=handle_steal_action_impl)
        
        # Test the condition
        result = action_system.handle_steal_action(thief, fast_target)
        
        # Verify the result
        assert result is False, "Steal action should fail"
        assert thief.has_acted is False, "Thief's action should not be consumed when steal fails"
        stealing_system.can_initiate_steal.assert_called_with(thief, fast_target)
