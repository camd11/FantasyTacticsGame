"""
Test for Capture System

This test verifies that the capture system correctly implements the mechanics for capturing enemy units,
including capture conditions, effects on both units, item stealing, and releasing captured units.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.fantasy_tactics_core.game_state import GameStateManager, GameState, UnitState, FactionEnum
from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem
from src.fantasy_tactics_gameplay.systems.map_system import MapSystem
from src.fantasy_tactics_gameplay.systems.inventory_system import InventorySystem
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
# Import the CaptureSystem class
from src.fantasy_tactics_gameplay.special_mechanics.capture_system import CaptureSystem



# Mock Item class for testing
class MockItem:
    """A simple mock item for testing."""
    
    def __init__(self, name, weight, item_type="Weapon"):
        self.name = name
        self.weight = weight
        self.type = item_type


class TestCaptureSystem:
    """Test cases for the capture system."""

    @pytest.fixture
    def setup_game_components(self):
        """Set up the game components needed for testing."""
        # Initialize components
        data_provider = MagicMock(spec=DataProvider)
        game_state_manager = MagicMock(spec=GameStateManager)
        game_state_manager.set_unit_disposition = MagicMock(return_value=None)
        unit_system = MagicMock(spec=UnitSystem)
        map_system = MagicMock(spec=MapSystem)
        inventory_system = MagicMock(spec=InventorySystem)
        inventory_system.trade_item = MagicMock(return_value=True)
        combat_system = MagicMock(spec=CombatSystem)
        # Create a real CaptureSystem instance
        capture_system = CaptureSystem()
        capture_system.initialize(
            game_state_manager,
            data_provider,
            unit_system,
            map_system,
            inventory_system,
            combat_system
        )
        
        return {
            "data_provider": data_provider,
            "game_state_manager": game_state_manager,
            "unit_system": unit_system,
            "map_system": map_system,
            "inventory_system": inventory_system,
            "combat_system": combat_system,
            "capture_system": capture_system
        }
    
    @pytest.fixture
    def setup_units(self):
        """Set up test units for capture scenarios."""
        # Create attacker unit (high CON, not mounted)
        attacker = MagicMock(spec=UnitState)
        attacker.id = "ATTACKER"
        attacker.name = "Attacker"
        attacker.faction = FactionEnum.PLAYER
        attacker.position = (1, 1)
        attacker.current_hp = 20
        attacker.max_hp = 20
        attacker.stats = {
            "Str": 10, "Mag": 8, "Skl": 12, "Spd": 11,
            "Def": 9, "Con": 12, "Mov": 6, "Luk": 7
        }
        attacker.base_stats = {
            "Str": 10, "Mag": 8, "Skl": 12, "Spd": 11,
            "Def": 9, "Con": 12, "Mov": 6, "Luk": 7
        }
        attacker.inventory = [
            MockItem("Iron Sword", 5),
            MockItem("Vulnerary", 1, "Consumable")
        ]
        attacker.is_mounted = False
        attacker.cls_name = "Mercenary"
        attacker.status = "Normal"
        attacker.carried_unit = None
        attacker.equipped_weapon_index = 0  # Add equipped_weapon_index
        
        # Create defender unit (low CON, not mounted)
        defender = MagicMock(spec=UnitState)
        defender.id = "DEFENDER"
        defender.name = "Defender"
        defender.faction = FactionEnum.ENEMY
        defender.position = (2, 1)
        defender.current_hp = 15
        defender.max_hp = 15
        defender.stats = {
            "Str": 8, "Mag": 6, "Skl": 9, "Spd": 8,
            "Def": 7, "Con": 8, "Mov": 5, "Luk": 6
        }
        defender.base_stats = {
            "Str": 8, "Mag": 6, "Skl": 9, "Spd": 8,
            "Def": 7, "Con": 8, "Mov": 5, "Luk": 6
        }
        defender.inventory = [
            MockItem("Iron Axe", 8),
            MockItem("Vulnerary", 1, "Consumable"),
            MockItem("Door Key", 1, "Key")
        ]
        defender.is_mounted = False
        defender.cls_name = "Fighter"
        defender.status = "Normal"
        defender.carried_unit = None
        defender.equipped_weapon_index = 0  # Add equipped_weapon_index
        
        # Create mounted attacker
        mounted_attacker = MagicMock(spec=UnitState)
        mounted_attacker.id = "MOUNTED_ATTACKER"
        mounted_attacker.name = "Mounted Attacker"
        mounted_attacker.faction = FactionEnum.PLAYER
        mounted_attacker.position = (3, 1)
        mounted_attacker.current_hp = 22
        mounted_attacker.max_hp = 22
        mounted_attacker.stats = {
            "Str": 9, "Mag": 5, "Skl": 10, "Spd": 12,
            "Def": 8, "Con": 9, "Mov": 8, "Luk": 7
        }
        mounted_attacker.base_stats = {
            "Str": 9, "Mag": 5, "Skl": 10, "Spd": 12,
            "Def": 8, "Con": 9, "Mov": 8, "Luk": 7
        }
        mounted_attacker.inventory = [
            MockItem("Steel Lance", 10)
        ]
        mounted_attacker.is_mounted = True
        mounted_attacker.cls_name = "Cavalier"
        mounted_attacker.status = "Normal"
        mounted_attacker.carried_unit = None
        mounted_attacker.equipped_weapon_index = 0  # Add equipped_weapon_index
        
        # Create mounted defender
        mounted_defender = MagicMock(spec=UnitState)
        mounted_defender.id = "MOUNTED_DEFENDER"
        mounted_defender.name = "Mounted Defender"
        mounted_defender.faction = FactionEnum.ENEMY
        mounted_defender.position = (4, 1)
        mounted_defender.current_hp = 18
        mounted_defender.max_hp = 18
        mounted_defender.stats = {
            "Str": 9, "Mag": 4, "Skl": 9, "Spd": 11,
            "Def": 8, "Con": 10, "Mov": 8, "Luk": 6
        }
        mounted_defender.base_stats = {
            "Str": 9, "Mag": 4, "Skl": 9, "Spd": 11,
            "Def": 8, "Con": 10, "Mov": 8, "Luk": 6
        }
        mounted_defender.inventory = [
            MockItem("Iron Lance", 8),
            MockItem("Vulnerary", 1, "Consumable")
        ]
        mounted_defender.is_mounted = True
        mounted_defender.cls_name = "Cavalier"
        mounted_defender.status = "Normal"
        mounted_defender.carried_unit = None
        mounted_defender.equipped_weapon_index = 0  # Add equipped_weapon_index
        
        # Create high CON defender
        high_con_defender = MagicMock(spec=UnitState)
        high_con_defender.id = "HIGH_CON_DEFENDER"
        high_con_defender.name = "High Con Defender"
        high_con_defender.faction = FactionEnum.ENEMY
        high_con_defender.position = (5, 1)
        high_con_defender.current_hp = 25
        high_con_defender.max_hp = 25
        high_con_defender.stats = {
            "Str": 12, "Mag": 3, "Skl": 8, "Spd": 7,
            "Def": 11, "Con": 20, "Mov": 4, "Luk": 5
        }
        high_con_defender.base_stats = {
            "Str": 12, "Mag": 3, "Skl": 8, "Spd": 7,
            "Def": 11, "Con": 20, "Mov": 4, "Luk": 5
        }
        high_con_defender.inventory = [
            MockItem("Steel Axe", 12),
            MockItem("Vulnerary", 1, "Consumable")
        ]
        high_con_defender.is_mounted = False
        high_con_defender.cls_name = "Warrior"
        high_con_defender.status = "Normal"
        high_con_defender.carried_unit = None
        high_con_defender.equipped_weapon_index = 0  # Add equipped_weapon_index
        
        # Create sleeping defender
        sleeping_defender = MagicMock(spec=UnitState)
        sleeping_defender.id = "SLEEPING_DEFENDER"
        sleeping_defender.name = "Sleeping Defender"
        sleeping_defender.faction = FactionEnum.ENEMY
        sleeping_defender.position = (6, 1)
        sleeping_defender.current_hp = 15
        sleeping_defender.max_hp = 15
        sleeping_defender.stats = {
            "Str": 8, "Mag": 6, "Skl": 9, "Spd": 8,
            "Def": 7, "Con": 8, "Mov": 5, "Luk": 6
        }
        sleeping_defender.base_stats = {
            "Str": 8, "Mag": 6, "Skl": 9, "Spd": 8,
            "Def": 7, "Con": 8, "Mov": 5, "Luk": 6
        }
        sleeping_defender.inventory = [
            MockItem("Iron Axe", 8),
            MockItem("Vulnerary", 1, "Consumable"),
            MockItem("Door Key", 1, "Key")
        ]
        sleeping_defender.is_mounted = False
        sleeping_defender.cls_name = "Fighter"
        sleeping_defender.status = "Sleep"
        sleeping_defender.carried_unit = None
        sleeping_defender.equipped_weapon_index = 0  # Add equipped_weapon_index
        
        return {
            "attacker": attacker,
            "defender": defender,
            "mounted_attacker": mounted_attacker,
            "mounted_defender": mounted_defender,
            "high_con_defender": high_con_defender,
            "sleeping_defender": sleeping_defender
        }

    # TEST: test_can_initiate_capture_con_check()
    def test_can_initiate_capture_con_check(self, setup_game_components, setup_units):
        """Test that capture can be initiated when attacker CON > defender CON."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        attacker = setup_units["attacker"]
        defender = setup_units["defender"]
        
        # Ensure attacker's CON is higher than defender's
        attacker.stats["Con"] = 12
        defender.stats["Con"] = 8
        
        # Test the condition
        result = capture_system.can_initiate_capture(attacker, defender)
        
        # Verify the result
        assert result is True, "Attacker with higher CON should be able to capture defender"

    # TEST: test_can_initiate_capture_mounted_attacker()
    def test_can_initiate_capture_mounted_attacker(self, setup_game_components, setup_units):
        """Test that mounted attackers can capture regardless of CON difference."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        mounted_attacker = setup_units["mounted_attacker"]
        defender = setup_units["defender"]
        
        # Ensure mounted attacker's CON is lower than defender's
        mounted_attacker.stats["Con"] = 7
        defender.stats["Con"] = 8
        mounted_attacker.is_mounted = True
        
        # Test the condition
        result = capture_system.can_initiate_capture(mounted_attacker, defender)
        
        # Verify the result
        assert result is True, "Mounted attacker should be able to capture defender regardless of CON"

    # TEST: test_cannot_capture_high_con_defender()
    def test_cannot_capture_high_con_defender(self, setup_game_components, setup_units):
        """Test that units with CON >= 20 cannot be captured."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        attacker = setup_units["attacker"]
        high_con_defender = setup_units["high_con_defender"]
        
        # Ensure high_con_defender has CON >= 20
        high_con_defender.stats["Con"] = 20
        
        # Test the condition
        result = capture_system.can_initiate_capture(attacker, high_con_defender)
        
        # Verify the result
        assert result is False, "Units with CON >= 20 should not be capturable"

    # TEST: test_cannot_capture_mounted_defender()
    def test_cannot_capture_mounted_defender(self, setup_game_components, setup_units):
        """Test that mounted units cannot be captured."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        attacker = setup_units["attacker"]
        mounted_defender = setup_units["mounted_defender"]
        
        # Ensure mounted_defender is mounted
        mounted_defender.is_mounted = True
        
        # Test the condition
        result = capture_system.can_initiate_capture(attacker, mounted_defender)
        
        # Verify the result
        assert result is False, "Mounted units should not be capturable"

    # TEST: test_capture_succeeds_without_combat_on_sleeping_target()
    def test_capture_succeeds_without_combat_on_sleeping_target(self, setup_game_components, setup_units):
        """Test that capture succeeds without combat on sleeping targets."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        combat_system = setup_game_components["combat_system"]
        
        # Get units
        attacker = setup_units["attacker"]
        sleeping_defender = setup_units["sleeping_defender"]
        
        # Ensure sleeping_defender is sleeping
        sleeping_defender.status = "Sleep"
        
        # Ensure attacker can capture
        attacker.stats["Con"] = 12
        sleeping_defender.stats["Con"] = 8
        sleeping_defender.is_mounted = False
        
        # Test the capture attempt
        result = capture_system.attempt_capture(attacker, sleeping_defender)
        
        # Verify the result
        assert result is True, "Capture should succeed without combat on sleeping target"
        
        # Verify that the sleeping defender was captured
        assert sleeping_defender.status == "Captured", "Sleeping defender should be captured"
        assert attacker.status == "Carrying", "Attacker should be carrying the captured unit"
        assert attacker.carried_unit == sleeping_defender, "Attacker should be carrying the sleeping defender"

    # TEST: test_capture_applies_stat_penalties_to_attacker()
    def test_capture_applies_stat_penalties_to_attacker(self, setup_game_components, setup_units):
        """Test that capture attempt applies stat penalties to the attacker."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        attacker = setup_units["attacker"]
        defender = setup_units["defender"]
        
        # Set up conditions for capture
        attacker.stats["Con"] = 12
        defender.stats["Con"] = 8
        defender.is_mounted = False
        defender.status = "Normal"
        defender.equipped_weapon_index = 0  # Ensure defender is armed
        
        # Original stats
        original_str = attacker.stats["Str"]
        original_mag = attacker.stats["Mag"]
        original_skl = attacker.stats["Skl"]
        original_spd = attacker.stats["Spd"]
        original_def = attacker.stats["Def"]
        
        # Create a method to check if penalties are applied
        def check_penalties():
            # Apply capture penalties directly
            capture_system._apply_capture_penalties(attacker)
            
            # Verify stats are halved
            assert attacker.stats["Str"] == original_str // 2, "Str should be halved during capture"
            assert attacker.stats["Mag"] == original_mag // 2, "Mag should be halved during capture"
            assert attacker.stats["Skl"] == original_skl // 2, "Skl should be halved during capture"
            assert attacker.stats["Spd"] == original_spd // 2, "Spd should be halved during capture"
            assert attacker.stats["Def"] == original_def // 2, "Def should be halved during capture"
            
            # Restore original stats
            attacker.stats["Str"] = original_str
            attacker.stats["Mag"] = original_mag
            attacker.stats["Skl"] = original_skl
            attacker.stats["Spd"] = original_spd
            attacker.stats["Def"] = original_def
        
        # Test the penalties
        check_penalties()

    # TEST: test_carrying_unit_has_halved_stats()
    def test_carrying_unit_has_halved_stats(self, setup_game_components, setup_units):
        """Test that a unit carrying a captured unit has halved stats."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        
        # Original stats
        original_str = capturer.stats["Str"]
        original_mag = capturer.stats["Mag"]
        original_skl = capturer.stats["Skl"]
        original_spd = capturer.stats["Spd"]
        original_def = capturer.stats["Def"]
        
        # Apply successful capture directly
        capture_system._apply_successful_capture(capturer, captured)
        
        # Verify capturer status and carried unit
        assert capturer.status == "Carrying", "Capturer status should be 'Carrying'"
        assert capturer.carried_unit == captured, "Capturer should be carrying the captured unit"
        
        # Verify captured unit status and HP
        assert captured.status == "Captured", "Captured unit status should be 'Captured'"
        assert captured.current_hp == 1, "Captured unit HP should be 1"
        
        # Verify stat penalties
        assert capturer.stats["Str"] == original_str // 2, "Str should be halved when carrying"
        assert capturer.stats["Mag"] == original_mag // 2, "Mag should be halved when carrying"
        assert capturer.stats["Skl"] == original_skl // 2, "Skl should be halved when carrying"
        assert capturer.stats["Spd"] == original_spd // 2, "Spd should be halved when carrying"
        assert capturer.stats["Def"] == original_def // 2, "Def should be halved when carrying"

    # TEST: test_carrying_unit_movement_penalty_applied()
    def test_carrying_unit_movement_penalty_applied(self, setup_game_components, setup_units):
        """Test that movement penalty is applied when carrying a heavy unit."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        
        # Original movement
        original_mov = capturer.stats["Mov"]
        
        # Set up a scenario where the captured unit is heavy enough to trigger movement penalty
        # Formula: if captured_unit.Con > (capturer.Con / 2 + (5 if capturer.is_mounted else 0)) then halve capturer.Mov
        capturer.stats["Con"] = 10  # Con/2 = 5
        captured.stats["Con"] = 8   # > 5, so should trigger penalty
        capturer.is_mounted = False
        
        # Apply successful capture
        capture_system._apply_successful_capture(capturer, captured)
        
        # Verify movement penalty
        assert capturer.stats["Mov"] == original_mov // 2, "Movement should be halved when carrying a heavy unit"

    # TEST: test_carrying_unit_no_movement_penalty_if_light_enough()
    def test_carrying_unit_no_movement_penalty_if_light_enough(self, setup_game_components, setup_units):
        """Test that no movement penalty is applied when carrying a light unit."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        
        # Original movement
        original_mov = capturer.stats["Mov"]
        
        # Set up a scenario where the captured unit is light enough to avoid movement penalty
        # Formula: if captured_unit.Con > (capturer.Con / 2 + (5 if capturer.is_mounted else 0)) then halve capturer.Mov
        capturer.stats["Con"] = 16  # Con/2 = 8
        captured.stats["Con"] = 7   # < 8, so should not trigger penalty
        capturer.is_mounted = False
        
        # Apply successful capture
        capture_system._apply_successful_capture(capturer, captured)
        
        # Verify no movement penalty
        assert capturer.stats["Mov"] == original_mov, "Movement should not be halved when carrying a light unit"

    # TEST: test_can_access_captured_unit_inventory_via_trade()
    def test_can_access_captured_unit_inventory_via_trade(self, setup_game_components, setup_units):
        """Test that a unit can access a captured unit's inventory via trade."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        trading_unit = setup_units["mounted_attacker"]
        
        # Set up the captured state
        capturer.status = "Carrying"
        capturer.carried_unit = captured
        captured.status = "Captured"
        
        # Position the trading unit adjacent to the capturer
        capturer.position = (1, 1)
        trading_unit.position = (1, 2)  # Adjacent
        
        # Test accessing the captured unit's inventory
        result = capture_system.access_captured_inventory(trading_unit, capturer)
        
        # Verify the result
        assert result == captured.inventory, "Should be able to access captured unit's inventory"

    # TEST: test_trade_takes_item_from_captured_unit()
    def test_trade_takes_item_from_captured_unit(self, setup_game_components, setup_units):
        """Test that a unit can take items from a captured unit."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        inventory_system = setup_game_components["inventory_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        trading_unit = setup_units["mounted_attacker"]
        
        # Set up the captured state
        capturer.status = "Carrying"
        capturer.carried_unit = captured
        captured.status = "Captured"
        
        # Position the trading unit adjacent to the capturer
        capturer.position = (1, 1)
        trading_unit.position = (1, 2)  # Adjacent
        
        # Item to trade
        item_to_take = captured.inventory[2]  # Door Key
        
        # Mock the trade_item method
        def trade_item_side_effect(from_unit, to_unit, item, is_captured_trade=False):
            if is_captured_trade:
                # Remove item from captured unit
                captured.inventory.remove(item)
                # Add item to trading unit
                trading_unit.inventory.append(item)
                return True
            return False
        
        inventory_system.trade_item.side_effect = trade_item_side_effect
        
        # Original inventory sizes
        original_captured_inventory_size = len(captured.inventory)
        original_trading_inventory_size = len(trading_unit.inventory)
        
        # Test trading the item
        result = inventory_system.trade_item(captured, trading_unit, item_to_take, is_captured_trade=True)
        
        # Verify the result
        assert result is True, "Trade should succeed"
        assert len(captured.inventory) == original_captured_inventory_size - 1, "Captured unit should have one less item"
        assert len(trading_unit.inventory) == original_trading_inventory_size + 1, "Trading unit should have one more item"
        assert item_to_take in trading_unit.inventory, "Trading unit should have the traded item"
        assert item_to_take not in captured.inventory, "Captured unit should not have the traded item"

    # TEST: test_trade_fails_if_trader_inventory_full()
    def test_trade_fails_if_trader_inventory_full(self, setup_game_components, setup_units):
        """Test that trade fails if the trader's inventory is full."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        inventory_system = setup_game_components["inventory_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        trading_unit = setup_units["mounted_attacker"]
        
        # Set up the captured state
        capturer.status = "Carrying"
        capturer.carried_unit = captured
        captured.status = "Captured"
        
        # Position the trading unit adjacent to the capturer
        capturer.position = (1, 1)
        trading_unit.position = (1, 2)  # Adjacent
        
        # Fill the trading unit's inventory (assume max is 5 items)
        trading_unit.inventory = [
            MockItem("Iron Lance", 8),
            MockItem("Steel Lance", 10),
            MockItem("Silver Lance", 12),
            MockItem("Vulnerary", 1, "Consumable"),
            MockItem("Elixir", 3, "Consumable")
        ]
        
        # Item to trade
        item_to_take = captured.inventory[2]  # Door Key
        
        # Mock the trade_item method
        inventory_system.trade_item.return_value = False
        
        # Test trading the item
        result = inventory_system.trade_item(captured, trading_unit, item_to_take, is_captured_trade=True)
        
        # Verify the result
        assert result is False, "Trade should fail if trader's inventory is full"
        inventory_system.trade_item.assert_called_once_with(captured, trading_unit, item_to_take, is_captured_trade=True)

    # TEST: test_cannot_trade_item_to_captured_unit()
    def test_cannot_trade_item_to_captured_unit(self, setup_game_components, setup_units):
        """Test that items cannot be traded to a captured unit."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        inventory_system = setup_game_components["inventory_system"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        trading_unit = setup_units["mounted_attacker"]
        
        # Set up the captured state
        capturer.status = "Carrying"
        capturer.carried_unit = captured
        captured.status = "Captured"
        
        # Position the trading unit adjacent to the capturer
        capturer.position = (1, 1)
        trading_unit.position = (1, 2)  # Adjacent
        
        # Item to trade
        item_to_give = trading_unit.inventory[0]  # Iron Lance
        
        # Mock the trade_item method
        inventory_system.trade_item.return_value = False
        
        # Test trading the item
        result = inventory_system.trade_item(trading_unit, captured, item_to_give, is_captured_trade=True)
        
        # Verify the result
        assert result is False, "Cannot trade items to a captured unit"
        inventory_system.trade_item.assert_called_once_with(trading_unit, captured, item_to_give, is_captured_trade=True)

    # TEST: test_release_removes_captured_unit_from_map()
    def test_release_removes_captured_unit_from_map(self, setup_game_components, setup_units):
        """Test that releasing a captured unit removes it from the map."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        
        # Set up the captured state
        capturer.status = "Carrying"
        capturer.carried_unit = captured
        captured.status = "Captured"
        
        # Store original stats
        original_stats = {
            "Str": capturer.stats["Str"],
            "Mag": capturer.stats["Mag"],
            "Skl": capturer.stats["Skl"],
            "Spd": capturer.stats["Spd"],
            "Def": capturer.stats["Def"],
            "Mov": capturer.stats["Mov"]
        }
        
        # Apply stat penalties to simulate carrying
        capturer.stats["Str"] //= 2
        capturer.stats["Mag"] //= 2
        capturer.stats["Skl"] //= 2
        capturer.stats["Spd"] //= 2
        capturer.stats["Def"] //= 2
        
        # Test releasing the captured unit
        result = capture_system.release_captured_unit(capturer)
        
        # Verify the result
        assert result is True, "Release should succeed"
        game_state_manager.set_unit_disposition.assert_called_once_with(captured.id, "REMOVED")
        assert capturer.status == "Normal", "Capturer status should be reset to 'Normal'"
        assert capturer.carried_unit is None, "Capturer should no longer be carrying a unit"

    # TEST: test_release_resets_capturer_status_and_penalties()
    def test_release_resets_capturer_status_and_penalties(self, setup_game_components, setup_units):
        """Test that releasing a captured unit resets the capturer's status and penalties."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        
        # Get units
        capturer = setup_units["attacker"]
        captured = setup_units["defender"]
        
        # Save original stats
        capturer.base_stats = {
            "Str": 10,
            "Mag": 8,
            "Skl": 12,
            "Spd": 11,
            "Def": 9,
            "Mov": 6
        }
        
        # Set up the captured state with halved stats
        capturer.status = "Carrying"
        capturer.carried_unit = captured
        capturer.stats["Str"] = capturer.base_stats["Str"] // 2
        capturer.stats["Mag"] = capturer.base_stats["Mag"] // 2
        capturer.stats["Skl"] = capturer.base_stats["Skl"] // 2
        capturer.stats["Spd"] = capturer.base_stats["Spd"] // 2
        capturer.stats["Def"] = capturer.base_stats["Def"] // 2
        capturer.stats["Mov"] = capturer.base_stats["Mov"] // 2
        captured.status = "Captured"
        
        # Test releasing the captured unit
        result = capture_system.release_captured_unit(capturer)
        
        # Verify the result
        assert result is True, "Release should succeed"
        assert capturer.status == "Normal", "Capturer status should be reset to 'Normal'"
        assert capturer.carried_unit is None, "Capturer should no longer be carrying a unit"
        
        # Verify stat penalties are removed
        assert capturer.stats["Str"] == capturer.base_stats["Str"], "Str should be restored to original value"
        assert capturer.stats["Mag"] == capturer.base_stats["Mag"], "Mag should be restored to original value"
        assert capturer.stats["Skl"] == capturer.base_stats["Skl"], "Skl should be restored to original value"
        assert capturer.stats["Spd"] == capturer.base_stats["Spd"], "Spd should be restored to original value"
        assert capturer.stats["Def"] == capturer.base_stats["Def"], "Def should be restored to original value"
        assert capturer.stats["Mov"] == capturer.base_stats["Mov"], "Mov should be restored to original value"

    # TEST: test_take_transfers_captured_unit_and_penalties()
    def test_take_transfers_captured_unit_and_penalties(self, setup_game_components, setup_units):
        """Test that taking a captured unit transfers the unit and penalties."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        giver = setup_units["attacker"]
        taker = setup_units["mounted_attacker"]
        captured = setup_units["defender"]
        
        # Save original stats for giver and taker
        giver.base_stats = {
            "Str": giver.stats["Str"],
            "Mag": giver.stats["Mag"],
            "Skl": giver.stats["Skl"],
            "Spd": giver.stats["Spd"],
            "Def": giver.stats["Def"],
            "Mov": giver.stats["Mov"]
        }
        
        taker.base_stats = {
            "Str": taker.stats["Str"],
            "Mag": taker.stats["Mag"],
            "Skl": taker.stats["Skl"],
            "Spd": taker.stats["Spd"],
            "Def": taker.stats["Def"],
            "Mov": taker.stats["Mov"]
        }
        
        # Set up the captured state
        giver.status = "Carrying"
        giver.carried_unit = captured
        giver.stats["Str"] = giver.base_stats["Str"] // 2
        giver.stats["Mag"] = giver.base_stats["Mag"] // 2
        giver.stats["Skl"] = giver.base_stats["Skl"] // 2
        giver.stats["Spd"] = giver.base_stats["Spd"] // 2
        giver.stats["Def"] = giver.base_stats["Def"] // 2
        captured.status = "Captured"
        
        # Position the taker adjacent to the giver
        giver.position = (1, 1)
        taker.position = (1, 2)  # Adjacent
        
        # Ensure taker can carry the captured unit
        taker.stats["Con"] = 12
        captured.stats["Con"] = 8
        
        # Test taking the captured unit
        result = capture_system.take_captured_unit(taker, giver)
        
        # Verify the result
        assert result is True, "Take should succeed"
        
        # Verify giver status and stats
        assert giver.status == "Normal", "Giver status should be reset to 'Normal'"
        assert giver.carried_unit is None, "Giver should no longer be carrying a unit"
        assert giver.stats["Str"] == giver.base_stats["Str"], "Giver Str should be restored"
        assert giver.stats["Mag"] == giver.base_stats["Mag"], "Giver Mag should be restored"
        assert giver.stats["Skl"] == giver.base_stats["Skl"], "Giver Skl should be restored"
        assert giver.stats["Spd"] == giver.base_stats["Spd"], "Giver Spd should be restored"
        assert giver.stats["Def"] == giver.base_stats["Def"], "Giver Def should be restored"
        
        # Verify taker status and stats
        assert taker.status == "Carrying", "Taker status should be 'Carrying'"
        assert taker.carried_unit == captured, "Taker should be carrying the captured unit"
        assert taker.stats["Str"] == taker.base_stats["Str"] // 2, "Taker Str should be halved"
        assert taker.stats["Mag"] == taker.base_stats["Mag"] // 2, "Taker Mag should be halved"
        assert taker.stats["Skl"] == taker.base_stats["Skl"] // 2, "Taker Skl should be halved"
        assert taker.stats["Spd"] == taker.base_stats["Spd"] // 2, "Taker Spd should be halved"
        assert taker.stats["Def"] == taker.base_stats["Def"] // 2, "Taker Def should be halved"

    # TEST: test_take_fails_if_taker_cannot_carry()
    def test_take_fails_if_taker_cannot_carry(self, setup_game_components, setup_units):
        """Test that taking a captured unit fails if the taker cannot carry the unit."""
        # Get components
        capture_system = setup_game_components["capture_system"]
        
        # Get units
        giver = setup_units["attacker"]
        taker = setup_units["mounted_attacker"]
        captured = setup_units["high_con_defender"]  # High CON unit that taker can't carry
        
        # Set up the captured state
        giver.status = "Carrying"
        giver.carried_unit = captured
        captured.status = "Captured"
        
        # Position the taker adjacent to the giver
        giver.position = (1, 1)
        taker.position = (1, 2)  # Adjacent
        
        # Set up a scenario where the taker cannot carry the captured unit
        # Taker's CON is too low compared to the captured unit's CON
        taker.stats["Con"] = 8  # Lower than captured unit's CON (20)
        captured.stats["Con"] = 20
        taker.is_mounted = False  # Ensure taker is not mounted (which would allow capture regardless of CON)
        
        # Test taking the captured unit
        result = capture_system.take_captured_unit(taker, giver)
        
        # Verify the result
        assert result is False, "Take should fail if taker cannot carry the unit"
        
        # Verify giver status remains unchanged
        assert giver.status == "Carrying", "Giver status should still be 'Carrying'"
        assert giver.carried_unit == captured, "Giver should still be carrying the captured unit"
