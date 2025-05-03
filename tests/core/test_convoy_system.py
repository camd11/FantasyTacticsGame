import unittest
from unittest.mock import MagicMock, patch
from enum import Enum, auto

# Create our own enums for testing
class GamePhaseEnum(Enum):
    PREPARATION = auto()
    BATTLE = auto()

from src.core_engine.game_state import (
    GameState, UnitState, ItemInstance, FactionEnum
)

# Import the actual implementation
from tests.core_engine.convoy_system_impl import (
    MAX_CONVOY_SIZE,
    is_adjacent,
    can_access_convoy,
    deposit_item,
    withdraw_item,
    convoy_is_full
)

class TestConvoySystem(unittest.TestCase):
    """Test cases for the Convoy/Supply System."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock GameState without spec to allow adding any attributes
        self.game_state = MagicMock()
        self.game_state.player_convoy = []
        
        # Create mock units without spec to allow adding any attributes
        self.lord_unit = MagicMock()
        self.lord_unit.id = "LEIF"
        self.lord_unit.name = "Leif"
        self.lord_unit.inventory = []
        self.lord_unit.position = (5, 5)
        
        self.regular_unit = MagicMock()
        self.regular_unit.id = "FINN"
        self.regular_unit.name = "Finn"
        self.regular_unit.inventory = []
        self.regular_unit.position = (6, 5)  # Adjacent to lord
        
        self.distant_unit = MagicMock()
        self.distant_unit.id = "NANNA"
        self.distant_unit.name = "Nanna"
        self.distant_unit.inventory = []
        self.distant_unit.position = (8, 8)  # Not adjacent to lord
        
        self.supply_unit = MagicMock()
        self.supply_unit.id = "SUPPLY"
        self.supply_unit.name = "Supply Unit"
        self.supply_unit.inventory = []
        self.supply_unit.position = (8, 7)  # Adjacent to distant_unit
        self.supply_unit.has_command = MagicMock(return_value=True)
        
        # Mock items
        self.iron_sword = ItemInstance("IRON_SWORD", 46)
        self.vulnerary = ItemInstance("VULNERARY", 3)
        self.unique_item = ItemInstance("LIGHT_BRAND", 20)
        self.unique_item.is_unique = True
        
        # Setup game_state methods
        self.game_state.get_player_lord.return_value = self.lord_unit
        self.game_state.get_units_with_trait.return_value = [self.supply_unit]
        self.game_state.current_phase = GamePhaseEnum.PREPARATION

    # TDD Anchor: test_convoy_initialization_empty
    def test_convoy_initialization_empty(self):
        """Test that the convoy starts empty by default."""
        self.assertEqual(len(self.game_state.player_convoy), 0, 
                         "Convoy should start empty")

    # TDD Anchor: test_convoy_stores_item_objects
    def test_convoy_stores_item_objects(self):
        """Test that the convoy stores ItemInstance objects."""
        # Add an item to the convoy
        self.game_state.player_convoy.append(self.iron_sword)
        
        self.assertEqual(len(self.game_state.player_convoy), 1,
                         "Convoy should have one item")
        self.assertIsInstance(self.game_state.player_convoy[0], ItemInstance,
                             "Convoy should store ItemInstance objects")
        self.assertEqual(self.game_state.player_convoy[0].item_id, "IRON_SWORD",
                        "Convoy should store the correct item")

    # TDD Anchor: test_convoy_stackable_items_as_separate_entries
    def test_convoy_stackable_items_as_separate_entries(self):
        """Test that stackable items are stored as separate entries in the convoy."""
        # Add multiple of the same item to the convoy
        vulnerary1 = ItemInstance("VULNERARY", 3)
        vulnerary2 = ItemInstance("VULNERARY", 3)
        vulnerary3 = ItemInstance("VULNERARY", 3)
        
        self.game_state.player_convoy.append(vulnerary1)
        self.game_state.player_convoy.append(vulnerary2)
        self.game_state.player_convoy.append(vulnerary3)
        
        self.assertEqual(len(self.game_state.player_convoy), 3,
                         "Convoy should have three separate entries for stackable items")
        
        # Verify all entries are separate objects
        self.assertIsNot(self.game_state.player_convoy[0], self.game_state.player_convoy[1],
                        "Each stackable item should be a separate object")
        self.assertIsNot(self.game_state.player_convoy[1], self.game_state.player_convoy[2],
                        "Each stackable item should be a separate object")

    # TDD Anchor: test_convoy_access_allowed_in_prep_phase
    def test_convoy_access_allowed_in_prep_phase(self):
        """Test that convoy access is allowed during preparation phase."""
        # Setup
        self.game_state.current_phase = GamePhaseEnum.PREPARATION
        
        # Test function
        result = can_access_convoy(self.regular_unit, self.game_state)
        
        self.assertTrue(result, "Any unit should be able to access convoy during preparation phase")

    # TDD Anchor: test_convoy_access_denied_in_battle_by_default
    def test_convoy_access_denied_in_battle_by_default(self):
        """Test that convoy access is denied during battle phase by default."""
        # Setup
        self.game_state.current_phase = GamePhaseEnum.BATTLE
        
        # Test with a unit that is not adjacent to lord or supply unit
        result = can_access_convoy(self.distant_unit, self.game_state)
        
        self.assertFalse(result, "Units not adjacent to lord or supply should not access convoy during battle")

    # TDD Anchor: test_convoy_access_via_lord_adjacency
    def test_convoy_access_via_lord_adjacency(self):
        """Test that units adjacent to the lord can access convoy during battle."""
        # Setup
        self.game_state.current_phase = GamePhaseEnum.BATTLE
        
        # Use patch decorator to mock is_adjacent
        with patch('tests.core_engine.test_convoy_system.is_adjacent', return_value=True):
            result = can_access_convoy(self.regular_unit, self.game_state)
            self.assertTrue(result, "Units adjacent to lord should be able to access convoy during battle")

    # TDD Anchor: test_convoy_access_via_supply_unit_adjacency
    def test_convoy_access_via_supply_unit_adjacency(self):
        """Test that units adjacent to a supply unit can access convoy during battle."""
        # Setup
        self.game_state.current_phase = GamePhaseEnum.BATTLE
        
        # Mock is_adjacent function to return True for supply unit, False for lord
        def mock_is_adjacent(pos1, pos2, map_data):
            # Return True if checking against supply unit position
            if pos2 == self.supply_unit.position:
                return True
            # Return False if checking against lord position
            if pos2 == self.lord_unit.position:
                return False
            return False
        
        # Use patch decorator to mock is_adjacent
        with patch('tests.core_engine.test_convoy_system.is_adjacent', side_effect=mock_is_adjacent):
            result = can_access_convoy(self.distant_unit, self.game_state)
            self.assertTrue(result, "Units adjacent to supply unit should be able to access convoy during battle")

    # TDD Anchor: test_convoy_access_via_supply_command
    def test_convoy_access_via_supply_command(self):
        """Test that units with the 'Supply' command can access convoy during battle."""
        # Setup
        self.game_state.current_phase = GamePhaseEnum.BATTLE
        
        # Mock unit with Supply command but not adjacent to lord or supply unit
        command_unit = MagicMock()
        command_unit.id = "COMMAND_UNIT"
        command_unit.position = (10, 10)  # Far from everyone
        command_unit.has_command = MagicMock(return_value=True)
        
        # Use patch decorator to mock is_adjacent
        with patch('tests.core_engine.test_convoy_system.is_adjacent', return_value=False):
            # Mock has_command to return True for 'Supply'
            command_unit.has_command.return_value = True
            result = can_access_convoy(command_unit, self.game_state)
            self.assertTrue(result, "Units with Supply command should be able to access convoy during battle")

    # TDD Anchor: test_convoy_access_costs_action_in_battle
    def test_convoy_access_costs_action_in_battle(self):
        """Test that accessing convoy during battle costs an action."""
        # Setup
        self.game_state.current_phase = GamePhaseEnum.BATTLE
        action_system = MagicMock()
        self.game_state.action_system = action_system
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call deposit function
            deposit_item(self.regular_unit, 0, self.game_state)
            
            # Verify action was consumed
            action_system.consume_action.assert_called_once_with(self.regular_unit)

    # TDD Anchor: test_deposit_item_successful
    def test_deposit_item_successful(self):
        """Test that an item can be successfully deposited into the convoy."""
        # Setup
        self.regular_unit.inventory = [self.iron_sword]
        self.regular_unit.is_item_equipped.return_value = False
        
        # Use patch decorators to mock functions
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True), \
             patch('tests.core_engine.test_convoy_system.convoy_is_full', return_value=False):
            # Call deposit function
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertTrue(result, "Deposit should succeed")
        self.assertEqual(len(self.game_state.player_convoy), 1, "Item should be added to convoy")
        self.assertEqual(self.game_state.player_convoy[0], self.iron_sword, "Correct item should be in convoy")
        self.assertEqual(len(self.regular_unit.inventory), 0, "Item should be removed from unit inventory")

    # TDD Anchor: test_deposit_item_fail_if_no_access
    def test_deposit_item_fail_if_no_access(self):
        """Test that deposit fails if unit cannot access convoy."""
        # Setup
        self.regular_unit.inventory = [self.iron_sword]
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=False):
            # Call deposit function
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Deposit should fail without access")
        self.assertEqual(len(self.game_state.player_convoy), 0, "No item should be added to convoy")
        self.assertEqual(len(self.regular_unit.inventory), 1, "Item should remain in unit inventory")

    # TDD Anchor: test_deposit_item_fail_if_equipped
    def test_deposit_item_fail_if_equipped(self):
        """Test that deposit fails if item is equipped."""
        # Setup
        self.regular_unit.inventory = [self.iron_sword]
        self.regular_unit.is_item_equipped.return_value = True
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call deposit function
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Deposit should fail for equipped items")
        self.assertEqual(len(self.game_state.player_convoy), 0, "No item should be added to convoy")
        self.assertEqual(len(self.regular_unit.inventory), 1, "Item should remain in unit inventory")

    # TDD Anchor: test_deposit_item_fail_if_unique
    def test_deposit_item_fail_if_unique(self):
        """Test that deposit fails if item is unique."""
        # Setup
        self.regular_unit.inventory = [self.unique_item]
        self.regular_unit.is_item_equipped.return_value = False
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call deposit function
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Deposit should fail for unique items")
        self.assertEqual(len(self.game_state.player_convoy), 0, "No item should be added to convoy")
        self.assertEqual(len(self.regular_unit.inventory), 1, "Item should remain in unit inventory")

    # TDD Anchor: test_deposit_item_fail_if_convoy_full
    def test_deposit_item_fail_if_convoy_full(self):
        """Test that deposit fails if convoy is full."""
        # Setup
        self.regular_unit.inventory = [self.iron_sword]
        self.regular_unit.is_item_equipped.return_value = False
        
        # Use patch decorators to mock functions
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True), \
             patch('tests.core_engine.test_convoy_system.convoy_is_full', return_value=True):
            # Call deposit function
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Deposit should fail if convoy is full")
        self.assertEqual(len(self.game_state.player_convoy), 0, "No item should be added to convoy")
        self.assertEqual(len(self.regular_unit.inventory), 1, "Item should remain in unit inventory")

    # TDD Anchor: test_deposit_item_updates_unit_inventory
    def test_deposit_item_updates_unit_inventory(self):
        """Test that depositing an item updates the unit's inventory correctly."""
        # Setup
        self.regular_unit.inventory = [self.iron_sword, self.vulnerary]
        self.regular_unit.is_item_equipped.return_value = False
        
        # Use patch decorators to mock functions
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True), \
             patch('tests.core_engine.test_convoy_system.convoy_is_full', return_value=False):
            # Call deposit function to deposit the first item
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertTrue(result, "Deposit should succeed")
        self.assertEqual(len(self.regular_unit.inventory), 1, "Unit should have one item left")
        self.assertEqual(self.regular_unit.inventory[0], self.vulnerary, "Correct item should remain in inventory")

    # TDD Anchor: test_deposit_item_updates_convoy_inventory
    def test_deposit_item_updates_convoy_inventory(self):
        """Test that depositing an item updates the convoy inventory correctly."""
        # Setup
        self.regular_unit.inventory = [self.iron_sword]
        self.regular_unit.is_item_equipped.return_value = False
        self.game_state.player_convoy = [self.vulnerary]
        
        # Use patch decorators to mock functions
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True), \
             patch('tests.core_engine.test_convoy_system.convoy_is_full', return_value=False):
            # Call deposit function
            result = deposit_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertTrue(result, "Deposit should succeed")
        self.assertEqual(len(self.game_state.player_convoy), 2, "Convoy should have two items")
        self.assertEqual(self.game_state.player_convoy[0], self.vulnerary, "First item should be unchanged")
        self.assertEqual(self.game_state.player_convoy[1], self.iron_sword, "Second item should be the deposited item")

    # TDD Anchor: test_withdraw_item_successful
    def test_withdraw_item_successful(self):
        """Test that an item can be successfully withdrawn from the convoy."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword]
        self.regular_unit.inventory = []  # Use a real list instead of MagicMock
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call withdraw function
            result = withdraw_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertTrue(result, "Withdraw should succeed")
        self.assertEqual(len(self.game_state.player_convoy), 0, "Item should be removed from convoy")
        self.assertEqual(len(self.regular_unit.inventory), 1, "Item should be added to unit inventory")
        self.assertEqual(self.regular_unit.inventory[0], self.iron_sword, "Correct item should be in unit inventory")

    # TDD Anchor: test_withdraw_item_fail_if_no_access
    def test_withdraw_item_fail_if_no_access(self):
        """Test that withdraw fails if unit cannot access convoy."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword]
        self.regular_unit.inventory = MagicMock()
        self.regular_unit.inventory.is_full = MagicMock(return_value=False)
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=False):
            # Call withdraw function
            result = withdraw_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Withdraw should fail without access")
        self.assertEqual(len(self.game_state.player_convoy), 1, "Item should remain in convoy")
        self.assertEqual(len(self.regular_unit.inventory), 0, "No item should be added to unit inventory")

    # TDD Anchor: test_withdraw_item_fail_if_unit_inventory_full
    def test_withdraw_item_fail_if_unit_inventory_full(self):
        """Test that withdraw fails if unit inventory is full."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword]
        self.regular_unit.inventory = MagicMock()
        self.regular_unit.inventory.is_full = MagicMock(return_value=True)
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call withdraw function
            result = withdraw_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Withdraw should fail if unit inventory is full")
        self.assertEqual(len(self.game_state.player_convoy), 1, "Item should remain in convoy")

    # TDD Anchor: test_withdraw_item_updates_unit_inventory
    def test_withdraw_item_updates_unit_inventory(self):
        """Test that withdrawing an item updates the unit's inventory correctly."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword]
        self.regular_unit.inventory = [self.vulnerary]  # Use a real list with the vulnerary
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call withdraw function
            result = withdraw_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertTrue(result, "Withdraw should succeed")
        self.assertEqual(len(self.regular_unit.inventory), 2, "Unit should have two items")
        self.assertEqual(self.regular_unit.inventory[0], self.vulnerary, "First item should be unchanged")
        self.assertEqual(self.regular_unit.inventory[1], self.iron_sword, "Second item should be the withdrawn item")

    # TDD Anchor: test_withdraw_item_updates_convoy_inventory
    def test_withdraw_item_updates_convoy_inventory(self):
        """Test that withdrawing an item updates the convoy inventory correctly."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword, self.vulnerary]
        self.regular_unit.inventory = MagicMock()
        self.regular_unit.inventory.is_full = MagicMock(return_value=False)
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call withdraw function
            result = withdraw_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertTrue(result, "Withdraw should succeed")
        self.assertEqual(len(self.game_state.player_convoy), 1, "Convoy should have one item left")
        self.assertEqual(self.game_state.player_convoy[0], self.vulnerary, "Correct item should remain in convoy")

    # TDD Anchor: test_withdraw_item_handles_failed_add_to_unit
    def test_withdraw_item_handles_failed_add_to_unit(self):
        """Test that withdraw handles failed add to unit inventory by returning item to convoy."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword]
        self.regular_unit.inventory = MagicMock()
        self.regular_unit.inventory.is_full = MagicMock(return_value=False)
        
        # Mock add_item to fail
        self.regular_unit.inventory.add_item = MagicMock(return_value=False)
        
        # Use patch decorator to mock can_access_convoy
        with patch('tests.core_engine.test_convoy_system.can_access_convoy', return_value=True):
            # Call withdraw function
            result = withdraw_item(self.regular_unit, 0, self.game_state)
        
        # Verify results
        self.assertFalse(result, "Withdraw should fail if adding to unit inventory fails")
        self.assertEqual(len(self.game_state.player_convoy), 1, "Item should be returned to convoy")
        self.assertEqual(self.game_state.player_convoy[0], self.iron_sword, "Correct item should be in convoy")

    # TDD Anchor: test_convoy_is_full_false_when_below_limit
    def test_convoy_is_full_false_when_below_limit(self):
        """Test that convoy_is_full returns False when convoy is below the limit."""
        # Setup
        self.game_state.player_convoy = [self.iron_sword]  # One item
        
        # Use patch decorator to mock MAX_CONVOY_SIZE
        with patch('tests.core_engine.test_convoy_system.MAX_CONVOY_SIZE', 100):
            result = convoy_is_full(self.game_state.player_convoy)
        
        self.assertFalse(result, "Convoy should not be considered full when below limit")

    # TDD Anchor: test_convoy_is_full_true_when_at_limit
    def test_convoy_is_full_true_when_at_limit(self):
        """Test that convoy_is_full returns True when convoy is at the limit."""
        # Setup - create a convoy with MAX_CONVOY_SIZE items
        self.game_state.player_convoy = [
            ItemInstance("ITEM1", 1),
            ItemInstance("ITEM2", 1),
            ItemInstance("ITEM3", 1)
        ]
        
        # Use patch decorator to mock MAX_CONVOY_SIZE
        with patch('tests.core_engine.test_convoy_system.MAX_CONVOY_SIZE', 3):
            result = convoy_is_full(self.game_state.player_convoy)
        
        self.assertTrue(result, "Convoy should be considered full when at limit")

    # TDD Anchor: test_convoy_is_full_false_when_unlimited
    def test_convoy_is_full_false_when_unlimited(self):
        """Test that convoy_is_full returns False when convoy has unlimited capacity."""
        # Setup - create a convoy with many items
        self.game_state.player_convoy = [ItemInstance(f"ITEM{i}", 1) for i in range(100)]
        
        # Use patch decorator to mock MAX_CONVOY_SIZE
        with patch('tests.core_engine.test_convoy_system.MAX_CONVOY_SIZE', -1):
            result = convoy_is_full(self.game_state.player_convoy)
        
        self.assertFalse(result, "Convoy should never be considered full when capacity is unlimited")

# Empty line to maintain line numbers


if __name__ == '__main__':
    unittest.main()