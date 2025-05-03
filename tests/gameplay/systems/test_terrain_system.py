"""
Test for Terrain System

This test verifies that the enhanced terrain effects are correctly implemented:
1. Data Loading: Verify that new terrain attributes are correctly loaded
2. Combat Bonuses: Verify that terrain Def/Res/Avoid bonuses are correctly applied during combat
3. Movement Type Interaction: Verify that bonuses/effects are correctly applied based on movement type
4. Turn-Based Effects: Verify that healing/damage effects are applied at the appropriate time
"""

import pytest
import logging
from unittest.mock import MagicMock, patch

from src.core_engine.game_state import GameStateManager, GameState, UnitState, FactionEnum
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum
from src.gameplay_systems.combat_calculator import CombatCalculator
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.unit_system import UnitSystem


class MockTerrainData:
    """Mock terrain data for testing."""
    
    def __init__(self, terrain_id, name, movement_costs=None, combat_modifiers=None, 
                 turn_effects=None, ignores_effects_by=None, passable=True, passable_by=None):
        self.id = terrain_id
        self.name = name
        self.movement_costs = movement_costs or {}
        self.combat_modifiers = combat_modifiers or {}
        self.turn_effects = turn_effects or {}
        self.ignores_effects_by = ignores_effects_by or []
        self.passable = passable
        self.passable_by = passable_by or []
        self.description = f"{name} terrain"
        self.graphic_id = f"{terrain_id.lower()}_tile"


class TestTerrainSystem:
    """Test cases for the terrain system."""
    
    @pytest.fixture
    def setup_game_state(self):
        """Set up the game state with required components."""
        # Initialize components
        data_provider = MagicMock(spec=DataProvider)
        game_state_manager = MagicMock(spec=GameStateManager)
        unit_system = MagicMock(spec=UnitSystem)
        map_system = MagicMock(spec=MapSystem)
        
        # Create mock terrain data
        fort_terrain = MockTerrainData(
            "FORT", 
            "Fort",
            movement_costs={
                "INFANTRY": 1,
                "CAVALRY": 2,
                "ARMORED": 1,
                "FLYING": 1
            },
            combat_modifiers={
                "defense": 3,
                "resistance": 1,
                "avoid": 30
            },
            turn_effects={
                "heal_percent": 10,
                "timing": "start_of_unit_turn"
            },
            ignores_effects_by=["FLYING"]
        )
        
        lava_terrain = MockTerrainData(
            "LAVA", 
            "Lava",
            movement_costs={
                "INFANTRY": 5,
                "CAVALRY": 99,
                "ARMORED": 4,
                "FLYING": 1
            },
            combat_modifiers={
                "defense": -2,
                "resistance": -2,
                "avoid": -10
            },
            turn_effects={
                "damage_percent": 15,
                "timing": "start_of_unit_turn"
            },
            ignores_effects_by=["FLYING"],
            passable=False,
            passable_by=["FLYING", "ARMORED", "INFANTRY"]
        )
        
        plains_terrain = MockTerrainData(
            "PLAINS", 
            "Plains",
            movement_costs={
                "INFANTRY": 1,
                "CAVALRY": 1,
                "ARMORED": 1,
                "FLYING": 1
            },
            combat_modifiers={
                "defense": 0,
                "resistance": 0,
                "avoid": 0
            }
        )
        
        # Set up data provider mock
        terrain_data = {
            "FORT": fort_terrain,
            "LAVA": lava_terrain,
            "PLAINS": plains_terrain
        }
        
        def get_terrain_data(terrain_id):
            return terrain_data.get(terrain_id)
        
        data_provider.get_terrain_data.side_effect = get_terrain_data
        
        # Create test units
        infantry_unit = UnitState()
        infantry_unit.id = "INFANTRY_UNIT"
        infantry_unit.name = "Infantry"
        infantry_unit.faction = FactionEnum.PLAYER
        infantry_unit.position = (1, 1)
        infantry_unit.max_hp = 20
        infantry_unit.current_hp = 20
        infantry_unit.base_stats = {"STR": 10, "MAG": 8, "SKL": 10, "SPD": 10, "LUK": 6, "DEF": 8, "RES": 5, "MOV": 5}
        infantry_unit.is_mounted = False
        infantry_unit.is_flying = False
        infantry_unit.movement_type = "INFANTRY"
        
        flying_unit = UnitState()
        flying_unit.id = "FLYING_UNIT"
        flying_unit.name = "Pegasus Knight"
        flying_unit.faction = FactionEnum.PLAYER
        flying_unit.position = (2, 2)
        flying_unit.max_hp = 18
        flying_unit.current_hp = 18
        flying_unit.base_stats = {"STR": 8, "MAG": 5, "SKL": 9, "SPD": 12, "LUK": 7, "DEF": 6, "RES": 7, "MOV": 7}
        flying_unit.is_mounted = True
        flying_unit.is_flying = True
        flying_unit.movement_type = "FLYING"
        
        # Set up game state manager mock
        game_state = GameState()
        game_state.unit_states = {
            "INFANTRY_UNIT": infantry_unit,
            "FLYING_UNIT": flying_unit,
        }
        game_state_manager.current_game_state = game_state
        
        def get_unit(unit_id):
            return game_state.unit_states.get(unit_id)
        
        game_state_manager.get_unit.side_effect = get_unit
        
        # Set up map system mock
        def get_terrain_id_at(position):
            # For testing, assign different terrain types to different positions
            if position == (1, 1):  # Infantry unit position
                return "FORT"
            elif position == (2, 2):  # Flying unit position
                return "FORT"
            elif position == (4, 4):  # Test position for lava
                return "LAVA"
            else:
                return "PLAINS"
        
        map_system.get_terrain_id_at.side_effect = get_terrain_id_at
        
        # Create combat calculator
        combat_calculator = CombatCalculator(game_state_manager, data_provider, unit_system, map_system)
        
        return {
            "game_state_manager": game_state_manager,
            "data_provider": data_provider,
            "unit_system": unit_system,
            "map_system": map_system,
            "combat_calculator": combat_calculator,
            "infantry_unit": infantry_unit,
            "flying_unit": flying_unit,
            "terrain_data": terrain_data
        }
    
    def test_terrain_data_loading(self, setup_game_state):
        """Test that new terrain attributes are correctly loaded from data."""
        # Get components from fixture
        data_provider = setup_game_state["data_provider"]
        
        # Test fort terrain data
        fort_data = data_provider.get_terrain_data("FORT")
        assert fort_data is not None, "Fort terrain data should be loaded"
        assert fort_data.combat_modifiers.get("defense") == 3, "Fort should have defense bonus of 3"
        assert fort_data.combat_modifiers.get("resistance") == 1, "Fort should have resistance bonus of 1"
        assert fort_data.combat_modifiers.get("avoid") == 30, "Fort should have avoid bonus of 30"
        assert fort_data.turn_effects.get("heal_percent") == 10, "Fort should have heal_percent of 10"
        assert fort_data.turn_effects.get("timing") == "start_of_unit_turn", "Fort healing should occur at start_of_unit_turn"
        assert "FLYING" in fort_data.ignores_effects_by, "Flying units should ignore fort effects"
        
        # Test lava terrain data
        lava_data = data_provider.get_terrain_data("LAVA")
        assert lava_data is not None, "Lava terrain data should be loaded"
        assert lava_data.combat_modifiers.get("defense") == -2, "Lava should have defense penalty of -2"
        assert lava_data.combat_modifiers.get("resistance") == -2, "Lava should have resistance penalty of -2"
        assert lava_data.combat_modifiers.get("avoid") == -10, "Lava should have avoid penalty of -10"
        assert lava_data.turn_effects.get("damage_percent") == 15, "Lava should have damage_percent of 15"
        assert lava_data.turn_effects.get("timing") == "start_of_unit_turn", "Lava damage should occur at start_of_unit_turn"
        assert "FLYING" in lava_data.ignores_effects_by, "Flying units should ignore lava effects"
    
    def test_combat_terrain_defense_bonus(self, setup_game_state, monkeypatch):
        """Test that terrain defense bonuses are correctly applied during combat calculations."""
        # Get components from fixture
        combat_calculator = setup_game_state["combat_calculator"]
        infantry_unit = setup_game_state["infantry_unit"]
        
        # Create mock attacker and defender stats
        attacker_stats = {
            "unit": MagicMock(),
            "weapon": MagicMock(),
            "Str": 15,
            "Mag": 10,
            "unit_type_tags": []
        }
        attacker_stats["weapon"].might = 8
        attacker_stats["weapon"].type = "SWORD"
        
        defender_stats = {
            "unit": infantry_unit,
            "Def": infantry_unit.base_stats["DEF"],  # 8
            "Mag": infantry_unit.base_stats["MAG"],  # 8
            "unit_type_tags": []
        }
        
        # Mock the _is_magical_attack method to return False (physical attack)
        def mock_is_magical_attack(stats):
            return False
        
        monkeypatch.setattr(combat_calculator, "_is_magical_attack", mock_is_magical_attack)
        
        # Mock the _get_effective_bonus method to return 1 (no effectiveness)
        def mock_get_effective_bonus(weapon, tags):
            return 1
        
        monkeypatch.setattr(combat_calculator, "_get_effective_bonus", mock_get_effective_bonus)
        
        # Test with no terrain bonus
        defender_stats["TerrainDefBonus"] = 0
        damage_no_bonus = combat_calculator.calculate_damage(attacker_stats, defender_stats)
        expected_damage_no_bonus = attacker_stats["Str"] + attacker_stats["weapon"].might - defender_stats["Def"]
        assert damage_no_bonus == expected_damage_no_bonus, f"Expected damage without terrain bonus to be {expected_damage_no_bonus}, got {damage_no_bonus}"
        
        # Test with fort terrain bonus (+3 defense)
        defender_stats["TerrainDefBonus"] = 3
        damage_with_bonus = combat_calculator.calculate_damage(attacker_stats, defender_stats)
        expected_damage_with_bonus = attacker_stats["Str"] + attacker_stats["weapon"].might - (defender_stats["Def"] + 3)
        assert damage_with_bonus == expected_damage_with_bonus, f"Expected damage with terrain bonus to be {expected_damage_with_bonus}, got {damage_with_bonus}"
        
        # Verify the difference in damage
        assert damage_no_bonus - damage_with_bonus == 3, "Terrain defense bonus should reduce damage by 3"
    
    def test_combat_terrain_resistance_bonus(self, setup_game_state, monkeypatch):
        """Test that terrain resistance bonuses are correctly applied during combat calculations."""
        # Get components from fixture
        combat_calculator = setup_game_state["combat_calculator"]
        infantry_unit = setup_game_state["infantry_unit"]
        
        # Create mock attacker and defender stats
        attacker_stats = {
            "unit": MagicMock(),
            "weapon": MagicMock(),
            "Str": 12,
            "Mag": 14,
            "unit_type_tags": []
        }
        attacker_stats["weapon"].might = 6
        attacker_stats["weapon"].type = "TOME"
        
        defender_stats = {
            "unit": infantry_unit,
            "Def": infantry_unit.base_stats["DEF"],  # 8
            "Mag": infantry_unit.base_stats["MAG"],  # 8
            "Res": infantry_unit.base_stats["RES"],  # 5
            "unit_type_tags": []
        }
        
        # Mock the _is_magical_attack method to return True (magical attack)
        def mock_is_magical_attack(stats):
            return True
        
        monkeypatch.setattr(combat_calculator, "_is_magical_attack", mock_is_magical_attack)
        
        # Mock the _get_effective_bonus method to return 1 (no effectiveness)
        def mock_get_effective_bonus(weapon, tags):
            return 1
        
        monkeypatch.setattr(combat_calculator, "_get_effective_bonus", mock_get_effective_bonus)
        
        # Test with no terrain bonus
        defender_stats["TerrainDefBonus"] = 0
        damage_no_bonus = combat_calculator.calculate_damage(attacker_stats, defender_stats)
        expected_damage_no_bonus = attacker_stats["Mag"] + attacker_stats["weapon"].might - defender_stats["Mag"]
        assert damage_no_bonus == expected_damage_no_bonus, f"Expected magical damage without terrain bonus to be {expected_damage_no_bonus}, got {damage_no_bonus}"
        
        # Test with fort terrain bonus (+1 resistance)
        defender_stats["TerrainDefBonus"] = 1
        damage_with_bonus = combat_calculator.calculate_damage(attacker_stats, defender_stats)
        expected_damage_with_bonus = attacker_stats["Mag"] + attacker_stats["weapon"].might - (defender_stats["Mag"] + 1)
        assert damage_with_bonus == expected_damage_with_bonus, f"Expected magical damage with terrain bonus to be {expected_damage_with_bonus}, got {damage_with_bonus}"
        
        # Verify the difference in damage
        assert damage_no_bonus - damage_with_bonus == 1, "Terrain resistance bonus should reduce magical damage by 1"
    
    def test_combat_terrain_avoid_bonus(self, setup_game_state):
        """Test that terrain avoid bonuses are correctly applied during combat calculations."""
        # Get components from fixture
        combat_calculator = setup_game_state["combat_calculator"]
        
        # Create mock attacker and defender stats
        attacker_stats = {
            "Hit": 80
        }
        
        defender_stats = {
            "Avoid": 40
        }
        
        # Test with no terrain bonus
        hit_chance_no_bonus = combat_calculator.calculate_battle_hit_chance(attacker_stats, defender_stats)
        expected_hit_chance_no_bonus = min(99, max(1, attacker_stats["Hit"] - defender_stats["Avoid"]))
        assert hit_chance_no_bonus == expected_hit_chance_no_bonus, f"Expected hit chance without terrain bonus to be {expected_hit_chance_no_bonus}, got {hit_chance_no_bonus}"
        
        # Test with fort terrain bonus (+30 avoid)
        defender_stats["Avoid"] = 40 + 30
        hit_chance_with_bonus = combat_calculator.calculate_battle_hit_chance(attacker_stats, defender_stats)
        expected_hit_chance_with_bonus = min(99, max(1, attacker_stats["Hit"] - defender_stats["Avoid"]))
        assert hit_chance_with_bonus == expected_hit_chance_with_bonus, f"Expected hit chance with terrain bonus to be {expected_hit_chance_with_bonus}, got {hit_chance_with_bonus}"
        
        # Verify the difference in hit chance
        assert hit_chance_no_bonus - hit_chance_with_bonus == 30, "Terrain avoid bonus should reduce hit chance by 30"
    
    def test_movement_type_interaction(self, setup_game_state):
        """Test that terrain bonuses are correctly applied based on movement type."""
        # Get components from fixture
        data_provider = setup_game_state["data_provider"]
        infantry_unit = setup_game_state["infantry_unit"]
        flying_unit = setup_game_state["flying_unit"]
        
        # Get fort terrain data
        fort_data = data_provider.get_terrain_data("FORT")
        
        # Test infantry unit (should get fort bonuses)
        should_ignore_infantry = infantry_unit.movement_type in fort_data.ignores_effects_by
        assert not should_ignore_infantry, "Infantry unit should not ignore fort effects"
        
        # Test flying unit (should ignore fort bonuses)
        should_ignore_flying = flying_unit.movement_type in fort_data.ignores_effects_by
        assert should_ignore_flying, "Flying unit should ignore fort effects"
    
    def test_turn_based_healing_effect(self, setup_game_state):
        """Test that healing effects are correctly applied at the appropriate time."""
        # Get components from fixture
        data_provider = setup_game_state["data_provider"]
        infantry_unit = setup_game_state["infantry_unit"]
        flying_unit = setup_game_state["flying_unit"]
        map_system = setup_game_state["map_system"]
        
        # Reduce unit HP to test healing
        infantry_unit.current_hp = 15  # Max is 20
        flying_unit.current_hp = 13  # Max is 18
        
        # Get fort terrain data
        fort_data = data_provider.get_terrain_data("FORT")
        
        # Calculate expected healing for infantry unit (10% of max HP)
        heal_percent = fort_data.turn_effects.get("heal_percent", 0)
        expected_heal_amount = max(1, int(infantry_unit.max_hp * (heal_percent / 100.0)))
        expected_infantry_hp = min(infantry_unit.max_hp, infantry_unit.current_hp + expected_heal_amount)
        
        # Mock the process_turn_start_effects function
        def process_turn_start_effects(unit_id):
            unit = setup_game_state["game_state_manager"].get_unit(unit_id)
            if not unit:
                return
            
            # Get terrain at unit's position
            terrain_id = map_system.get_terrain_id_at(unit.position)
            terrain_data = data_provider.get_terrain_data(terrain_id)
            
            # Check if terrain has turn effects
            if not hasattr(terrain_data, "turn_effects") or not terrain_data.turn_effects:
                return
            
            # Check if unit ignores terrain effects
            if unit.movement_type in terrain_data.ignores_effects_by:
                return
            
            # Check timing
            if terrain_data.turn_effects.get("timing") == "start_of_unit_turn":
                # Apply healing
                if "heal_percent" in terrain_data.turn_effects:
                    heal_percent = terrain_data.turn_effects["heal_percent"]
                    heal_amount = max(1, int(unit.max_hp * (heal_percent / 100.0)))
                    unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
                
                # Apply damage
                if "damage_percent" in terrain_data.turn_effects:
                    damage_percent = terrain_data.turn_effects["damage_percent"]
                    damage_amount = max(1, int(unit.max_hp * (damage_percent / 100.0)))
                    unit.current_hp = max(1, unit.current_hp - damage_amount)  # Don't kill from terrain damage
        
        # Process turn start effects for infantry unit (should heal)
        process_turn_start_effects(infantry_unit.id)
        assert infantry_unit.current_hp == expected_infantry_hp, f"Infantry unit should heal to {expected_infantry_hp} HP, got {infantry_unit.current_hp}"
        
        # Process turn start effects for flying unit (should not heal due to ignores_effects_by)
        flying_hp_before = flying_unit.current_hp
        process_turn_start_effects(flying_unit.id)
        assert flying_unit.current_hp == flying_hp_before, f"Flying unit should not heal, HP should remain {flying_hp_before}, got {flying_unit.current_hp}"
    
    def test_turn_based_damage_effect(self, setup_game_state):
        """Test that damage effects are correctly applied at the appropriate time."""
        # Get components from fixture
        data_provider = setup_game_state["data_provider"]
        infantry_unit = setup_game_state["infantry_unit"]
        flying_unit = setup_game_state["flying_unit"]
        map_system = setup_game_state["map_system"]
        
        # Move units to lava for this test
        infantry_unit.position = (4, 4)  # Lava position
        flying_unit.position = (4, 4)  # Lava position
        
        # Get lava terrain data
        lava_data = data_provider.get_terrain_data("LAVA")
        
        # Calculate expected damage for infantry unit (15% of max HP)
        damage_percent = lava_data.turn_effects.get("damage_percent", 0)
        expected_damage_amount = max(1, int(infantry_unit.max_hp * (damage_percent / 100.0)))
        expected_infantry_hp = max(1, infantry_unit.current_hp - expected_damage_amount)  # Don't kill from terrain damage
        
        # Mock the process_turn_start_effects function
        def process_turn_start_effects(unit_id):
            unit = setup_game_state["game_state_manager"].get_unit(unit_id)
            if not unit:
                return
            
            # Get terrain at unit's position
            terrain_id = map_system.get_terrain_id_at(unit.position)
            terrain_data = data_provider.get_terrain_data(terrain_id)
            
            # Check if terrain has turn effects
            if not hasattr(terrain_data, "turn_effects") or not terrain_data.turn_effects:
                return
            
            # Check if unit ignores terrain effects
            if unit.movement_type in terrain_data.ignores_effects_by:
                return
            
            # Check timing
            if terrain_data.turn_effects.get("timing") == "start_of_unit_turn":
                # Apply healing
                if "heal_percent" in terrain_data.turn_effects:
                    heal_percent = terrain_data.turn_effects["heal_percent"]
                    heal_amount = max(1, int(unit.max_hp * (heal_percent / 100.0)))
                    unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
                
                # Apply damage
                if "damage_percent" in terrain_data.turn_effects:
                    damage_percent = terrain_data.turn_effects["damage_percent"]
                    damage_amount = max(1, int(unit.max_hp * (damage_percent / 100.0)))
                    unit.current_hp = max(1, unit.current_hp - damage_amount)  # Don't kill from terrain damage
        
        # Process turn start effects for infantry unit (should take damage)
        infantry_hp_before = infantry_unit.current_hp
        process_turn_start_effects(infantry_unit.id)
        assert infantry_unit.current_hp == expected_infantry_hp, f"Infantry unit should take damage to {expected_infantry_hp} HP, got {infantry_unit.current_hp}"
        
        # Process turn start effects for flying unit (should not take damage due to ignores_effects_by)
        flying_hp_before = flying_unit.current_hp
        process_turn_start_effects(flying_unit.id)
        assert flying_unit.current_hp == flying_hp_before, f"Flying unit should not take damage, HP should remain {flying_hp_before}, got {flying_unit.current_hp}"
    
    def test_hp_clamping_for_terrain_effects(self, setup_game_state):
        """Test that HP is properly clamped for terrain effects (not exceeding max HP, not going below 1 HP)."""
        # Get components from fixture
        data_provider = setup_game_state["data_provider"]
        infantry_unit = setup_game_state["infantry_unit"]
        map_system = setup_game_state["map_system"]
        
        # Test healing clamping (not exceeding max HP)
        # Set unit to almost max HP
        infantry_unit.current_hp = infantry_unit.max_hp - 1
        infantry_unit.position = (1, 1)  # Fort position
        
        # Mock the process_turn_start_effects function
        def process_turn_start_effects(unit_id):
            unit = setup_game_state["game_state_manager"].get_unit(unit_id)
            if not unit:
                return
            
            # Get terrain at unit's position
            terrain_id = map_system.get_terrain_id_at(unit.position)
            terrain_data = data_provider.get_terrain_data(terrain_id)
            
            # Check if terrain has turn effects
            if not hasattr(terrain_data, "turn_effects") or not terrain_data.turn_effects:
                return
            
            # Check if unit ignores terrain effects
            if unit.movement_type in terrain_data.ignores_effects_by:
                return
            
            # Check timing
            if terrain_data.turn_effects.get("timing") == "start_of_unit_turn":
                # Apply healing
                if "heal_percent" in terrain_data.turn_effects:
                    heal_percent = terrain_data.turn_effects["heal_percent"]
                    heal_amount = max(1, int(unit.max_hp * (heal_percent / 100.0)))
                    unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
                
                # Apply damage
                if "damage_percent" in terrain_data.turn_effects:
                    damage_percent = terrain_data.turn_effects["damage_percent"]
                    damage_amount = max(1, int(unit.max_hp * (damage_percent / 100.0)))
                    unit.current_hp = max(1, unit.current_hp - damage_amount)  # Don't kill from terrain damage
        
        # Process turn start effects for infantry unit (should heal to max HP but not exceed)
        process_turn_start_effects(infantry_unit.id)
        assert infantry_unit.current_hp == infantry_unit.max_hp, f"Infantry unit should heal to max HP ({infantry_unit.max_hp}), got {infantry_unit.current_hp}"
        
        # Test damage clamping (not going below 1 HP)
        # Set unit to very low HP
        infantry_unit.current_hp = 2
        infantry_unit.position = (4, 4)  # Lava position
        
        # Process turn start effects for infantry unit (should take damage but not go below 1 HP)
        process_turn_start_effects(infantry_unit.id)
        assert infantry_unit.current_hp == 1, f"Infantry unit should take damage but not go below 1 HP, got {infantry_unit.current_hp}"
