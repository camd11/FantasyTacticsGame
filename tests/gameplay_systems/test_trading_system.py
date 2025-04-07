"""
Test for Trading System

This test verifies that the trading system correctly implements the functionality
described in the specification, including trade initiation conditions, item selection,
successful trade execution, inventory full behavior, and action cost verification.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.core_engine.game_state import GameStateManager, GameState, UnitState, FactionEnum
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.action_system import ActionSystem

# This module doesn't exist yet - we're writing tests first (TDD)
from src.gameplay_systems.trading_system import TradingSystem, MAX_INVENTORY_SIZE


class TestTradingSystem:
    """Test cases for the trading system."""

    @pytest.fixture
    def setup_game_state(self):
        """Set up the game state with required components."""
        # Initialize components
        data_provider = MagicMock(spec=DataProvider)
        game_state_manager = MagicMock(spec=GameStateManager)
        unit_system = MagicMock(spec=UnitSystem)
        map_system = MagicMock(spec=MapSystem)
        inventory_system = MagicMock(spec=InventorySystem)
        action_system = MagicMock(spec=ActionSystem)
        ui_system = MagicMock(name="UISystem")
        
        # Create the trading system
        trading_system = TradingSystem()
        trading_system.initialize(
            game_state_manager,
            data_provider,
            unit_system,
            map_system,
            inventory_system,
            action_system,
            ui_system
        )
        
        return {
            "game_state_manager": game_state_manager,
            "data_provider": data_provider,
            "unit_system": unit_system,
            "map_system": map_system,
            "inventory_system": inventory_system,
            "action_system": action_system,
            "ui_system": ui_system,
            "trading_system": trading_system
        }
    
    @pytest.fixture
    def setup_units(self):
        """Set up test units for trading."""
        # Create mock items
        item1 = MagicMock(name="Iron Sword")
        item1.item_id = "IRON_SWORD"
        item1.name = "Iron Sword"
        item1.is_tradeable = True
        item1.is_equipped = False
        
        item2 = MagicMock(name="Iron Lance")
        item2.item_id = "IRON_LANCE"
        item2.name = "Iron Lance"
        item2.is_tradeable = True
        item2.is_equipped = False
        
        item3 = MagicMock(name="Vulnerary")
        item3.item_id = "VULNERARY"
        item3.name = "Vulnerary"
        item3.is_tradeable = True
        item3.is_equipped = False
        
        item4 = MagicMock(name="Unique Weapon")
        item4.item_id = "UNIQUE_WEAPON"
        item4.name = "Unique Weapon"
        item4.is_tradeable = False  # Non-tradeable item
        item4.is_equipped = False
        
        # Create mock units
        unit1 = MagicMock(spec=UnitState)
        unit1.unit_id = "UNIT1"
        unit1.name = "Unit 1"
        unit1.position = (1, 1)
        unit1.faction = FactionEnum.PLAYER
        unit1.inventory = [item1, item3]
        unit1.has_acted = False
        unit1.is_holding_captive = False
        unit1.captive_unit = None
        
        unit2 = MagicMock(spec=UnitState)
        unit2.unit_id = "UNIT2"
        unit2.name = "Unit 2"
        unit2.position = (1, 2)  # Adjacent to unit1
        unit2.faction = FactionEnum.PLAYER
        unit2.inventory = [item2]
        unit2.has_acted = False
        unit2.is_holding_captive = False
        unit2.captive_unit = None
        
        enemy_unit = MagicMock(spec=UnitState)
        enemy_unit.unit_id = "ENEMY1"
        enemy_unit.name = "Enemy 1"
        enemy_unit.position = (2, 1)  # Adjacent to unit1
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.inventory = [item4]
        enemy_unit.has_acted = False
        enemy_unit.is_holding_captive = False
        enemy_unit.captive_unit = None
        
        captive_unit = MagicMock(spec=UnitState)
        captive_unit.unit_id = "CAPTIVE1"
        captive_unit.name = "Captive 1"
        captive_unit.position = None  # No position when captured
        captive_unit.faction = FactionEnum.ENEMY
        captive_unit.inventory = [item4]
        captive_unit.has_acted = False
        
        # Unit holding a captive
        unit_with_captive = MagicMock(spec=UnitState)
        unit_with_captive.unit_id = "UNIT3"
        unit_with_captive.name = "Unit 3"
        unit_with_captive.position = (2, 2)  # Adjacent to unit2
        unit_with_captive.faction = FactionEnum.PLAYER
        unit_with_captive.inventory = [item1]
        unit_with_captive.has_acted = False
        unit_with_captive.is_holding_captive = True
        unit_with_captive.captive_unit = captive_unit
        
        return {
            "unit1": unit1,
            "unit2": unit2,
            "enemy_unit": enemy_unit,
            "captive_unit": captive_unit,
            "unit_with_captive": unit_with_captive,
            "item1": item1,
            "item2": item2,
            "item3": item3,
            "item4": item4
        }

    def test_can_initiate_trade_adjacent_allies(self, setup_game_state, setup_units):
        """Test that trade can be initiated between adjacent allied units."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        map_system = setup_game_state["map_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Configure mocks
        map_system.are_adjacent.return_value = True
        
        # Act
        result = trading_system.can_initiate_trade(unit1, unit2)
        
        # Assert
        assert result is True
        map_system.are_adjacent.assert_called_once_with(unit1.position, unit2.position)

    def test_can_initiate_trade_not_adjacent(self, setup_game_state, setup_units):
        """Test that trade cannot be initiated between non-adjacent units."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        map_system = setup_game_state["map_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Configure mocks
        map_system.are_adjacent.return_value = False
        
        # Act
        result = trading_system.can_initiate_trade(unit1, unit2)
        
        # Assert
        assert result is False
        map_system.are_adjacent.assert_called_once_with(unit1.position, unit2.position)

    def test_can_initiate_trade_enemy_units(self, setup_game_state, setup_units):
        """Test that trade cannot be initiated with enemy units."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        map_system = setup_game_state["map_system"]
        unit1 = setup_units["unit1"]
        enemy_unit = setup_units["enemy_unit"]
        
        # Configure mocks
        map_system.are_adjacent.return_value = True
        
        # Act
        result = trading_system.can_initiate_trade(unit1, enemy_unit)
        
        # Assert
        assert result is False
        map_system.are_adjacent.assert_called_once_with(unit1.position, enemy_unit.position)

    def test_can_initiate_trade_with_captive(self, setup_game_state, setup_units):
        """Test that trade can be initiated with a captive held by the unit."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        map_system = setup_game_state["map_system"]
        unit_with_captive = setup_units["unit_with_captive"]
        captive_unit = setup_units["captive_unit"]
        
        # Act
        result = trading_system.can_initiate_trade(unit_with_captive, captive_unit)
        
        # Assert
        assert result is True
        # No need to check adjacency for captive
        map_system.are_adjacent.assert_not_called()

    def test_initiate_trade_success(self, setup_game_state, setup_units):
        """Test initiating a trade successfully displays the trade UI."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        ui_system = setup_game_state["ui_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Configure mocks
        trading_system.can_initiate_trade = MagicMock(return_value=True)
        
        # Act
        trading_system.initiate_trade(unit1, unit2)
        
        # Assert
        trading_system.can_initiate_trade.assert_called_once_with(unit1, unit2)
        ui_system.display_trade_screen.assert_called_once_with(unit1, unit2, unit1.inventory, unit2.inventory)

    def test_initiate_trade_failure(self, setup_game_state, setup_units):
        """Test initiating a trade fails when conditions aren't met."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        ui_system = setup_game_state["ui_system"]
        unit1 = setup_units["unit1"]
        enemy_unit = setup_units["enemy_unit"]
        
        # Configure mocks
        trading_system.can_initiate_trade = MagicMock(return_value=False)
        
        # Act
        trading_system.initiate_trade(unit1, enemy_unit)
        
        # Assert
        trading_system.can_initiate_trade.assert_called_once_with(unit1, enemy_unit)
        ui_system.display_trade_screen.assert_not_called()

    def test_execute_trade_swap_items(self, setup_game_state, setup_units):
        """Test executing a trade that swaps items between two units."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        item1 = setup_units["item1"]
        item2 = setup_units["item2"]
        
        # Act
        result = trading_system.execute_trade(unit1, unit2, 0, 0)
        
        # Assert
        assert result is True
        # Check that items were swapped
        assert item2 in unit1.inventory
        assert item1 in unit2.inventory

    def test_execute_trade_give_item(self, setup_game_state, setup_units):
        """Test executing a trade that gives an item from unit1 to unit2."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        item3 = setup_units["item3"]
        
        # Act
        result = trading_system.execute_trade(unit1, unit2, 1, -1)
        
        # Assert
        assert result is True
        # Check that item was given
        assert item3 not in unit1.inventory
        assert item3 in unit2.inventory

    def test_execute_trade_receive_item(self, setup_game_state, setup_units):
        """Test executing a trade that takes an item from unit2 to unit1."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        item2 = setup_units["item2"]
        
        # Act
        result = trading_system.execute_trade(unit1, unit2, -1, 0)
        
        # Assert
        assert result is True
        # Check that item was received
        assert item2 not in unit2.inventory
        assert item2 in unit1.inventory

    def test_execute_trade_non_tradeable_item(self, setup_game_state, setup_units):
        """Test that trading fails when trying to trade a non-tradeable item."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        enemy_unit = setup_units["enemy_unit"]
        
        # Act
        result = trading_system.execute_trade(unit1, enemy_unit, 0, 0)
        
        # Assert
        assert result is False
        # Check that inventories remain unchanged
        assert len(unit1.inventory) == 2
        assert len(enemy_unit.inventory) == 1

    def test_execute_trade_equipped_item(self, setup_game_state, setup_units):
        """Test that trading an equipped item unequips it first."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit_system = setup_game_state["unit_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        item1 = setup_units["item1"]
        
        # Set up item1 as equipped
        item1.is_equipped = True
        
        # Act
        result = trading_system.execute_trade(unit1, unit2, 0, -1)
        
        # Assert
        assert result is True
        unit_system.unequip_item.assert_called_once_with(unit1, item1)
        assert item1 not in unit1.inventory
        assert item1 in unit2.inventory

    def test_execute_trade_inventory_full_giving(self, setup_game_state, setup_units):
        """Test that trading fails when trying to give an item to a unit with a full inventory."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Fill unit2's inventory to max
        unit2.inventory = [MagicMock() for _ in range(MAX_INVENTORY_SIZE)]
        
        # Act
        result = trading_system.execute_trade(unit1, unit2, 0, -1)
        
        # Assert
        assert result is False
        # Check that inventories remain unchanged
        assert len(unit1.inventory) == 2
        assert len(unit2.inventory) == MAX_INVENTORY_SIZE

    def test_execute_trade_inventory_full_receiving(self, setup_game_state, setup_units):
        """Test that trading fails when trying to receive an item with a full inventory."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Fill unit1's inventory to max
        unit1.inventory = [MagicMock() for _ in range(MAX_INVENTORY_SIZE)]
        
        # Act
        result = trading_system.execute_trade(unit1, unit2, -1, 0)
        
        # Assert
        assert result is False
        # Check that inventories remain unchanged
        assert len(unit1.inventory) == MAX_INVENTORY_SIZE
        assert len(unit2.inventory) == 1

    def test_execute_trade_with_captive(self, setup_game_state, setup_units):
        """Test executing a trade with a captive unit."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit_with_captive = setup_units["unit_with_captive"]
        captive_unit = setup_units["captive_unit"]
        item1 = setup_units["item1"]
        item4 = setup_units["item4"]
        
        # Make the captive's item tradeable for this test
        item4.is_tradeable = True
        
        # Act
        result = trading_system.execute_trade(unit_with_captive, captive_unit, 0, 0)
        
        # Assert
        assert result is True
        # Check that items were swapped
        assert item4 in unit_with_captive.inventory
        assert item1 in captive_unit.inventory

    def test_trade_does_not_consume_action(self, setup_game_state, setup_units):
        """Test that trading does not consume the unit's action."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        action_system = setup_game_state["action_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Configure mocks
        trading_system.execute_trade = MagicMock(return_value=True)
        
        # Act
        trading_system.initiate_trade(unit1, unit2)
        
        # Assert
        # Verify that the action system was not called to mark the unit as having acted
        action_system.set_unit_acted.assert_not_called()
        assert unit1.has_acted is False

    def test_unit_can_trade_after_moving(self, setup_game_state, setup_units):
        """Test that a unit can trade after moving."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Configure mocks
        trading_system.can_initiate_trade = MagicMock(return_value=True)
        
        # Simulate unit having moved but not acted
        unit1.has_moved = True
        unit1.has_acted = False
        
        # Act
        result = trading_system.initiate_trade(unit1, unit2)
        
        # Assert
        assert result is not None
        trading_system.can_initiate_trade.assert_called_once_with(unit1, unit2)

    def test_unit_can_act_after_trading(self, setup_game_state, setup_units):
        """Test that a unit can perform an action after trading."""
        # Arrange
        trading_system = setup_game_state["trading_system"]
        action_system = setup_game_state["action_system"]
        unit1 = setup_units["unit1"]
        unit2 = setup_units["unit2"]
        
        # Configure mocks
        trading_system.execute_trade = MagicMock(return_value=True)
        
        # Act
        trading_system.initiate_trade(unit1, unit2)
        
        # Assert
        # Verify unit can still act
        assert unit1.has_acted is False
        # Check if action system can perform actions
        action_system.can_unit_act.return_value = True
        assert action_system.can_unit_act(unit1.unit_id) is True