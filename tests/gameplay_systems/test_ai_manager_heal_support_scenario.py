import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum
from src.gameplay_systems.ai_manager import AIManager, AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.core_engine.data_provider import DataProvider


class TestAIManagerHealSupportScenario(unittest.TestCase):
    """Integration test for the HEAL_SUPPORT archetype using a test scenario."""
    
    def setUp(self):
        """Set up the test environment with a loaded scenario."""
        # Create real DataProvider to load the scenario
        self.data_provider = DataProvider()
        
        # Mock other systems
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_actionHandler = MagicMock(name="ActionHandler")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        self.mock_staffSystem = MagicMock(name="StaffSystem")
        self.mock_statusEffectsSystem = MagicMock(name="StatusEffectsSystem")
        
        # Create the AIManager instance
        self.ai_manager = AIManager()
        
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.data_provider
        )
        
        # Add inventorySystem to the AI manager
        self.ai_manager.inventorySystem = self.mock_inventorySystem
        
        # Load the test scenario
        self.scenario = self.data_provider.load_scenario("heal_support_ai_test")
        
        # Set up the mock game state based on the scenario
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.ENEMY
        
        # Create unit states from scenario
        self.unit_states = {}
        for unit_data in self.scenario.get('units', []):
            unit = MagicMock(name=unit_data['name'])
            unit.id = unit_data['id']
            unit.name = unit_data['name']
            unit.position = tuple(unit_data['position'])
            unit.faction = getattr(FactionEnum, unit_data['faction'])
            unit.current_hp = unit_data.get('current_hp', unit_data['stats']['HP'])
            unit.max_hp = unit_data['stats']['HP']
            
            # Add status effects if present
            if 'status_effects' in unit_data:
                unit.status_effects = []
                for status in unit_data['status_effects']:
                    unit.status_effects.append({
                        'type': getattr(StatusEffectEnum, status['type']),
                        'duration': status['duration']
                    })
            
            self.unit_states[unit.id] = unit
        
        self.mock_game_state.unit_states = self.unit_states
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
        # Set up mock unit system
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: self.unit_states.get(unit_id)
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        self.mock_unitSystem.has_status.side_effect = lambda unit_id, status: any(
            s['type'] == status for s in getattr(self.unit_states.get(unit_id), 'status_effects', [])
        )
        # Mock get_units_in_range to return all unit IDs (range check happens later)
        self.mock_unitSystem.get_units_in_range.side_effect = lambda unit_id, tile: list(self.unit_states.keys())
        
        # Set up mock inventory system
        def mock_get_usable_items(unit_id):
            unit_data = next((u for u in self.scenario['units'] if u['id'] == unit_id), None)
            if unit_data:
                return [item['item'] for item in unit_data.get('inventory', [])]
            return []
        
        self.mock_inventorySystem.get_usable_items.side_effect = mock_get_usable_items
        
        # Set up mock map system
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Set up mock movement system
        def mock_calculate_movement_range(unit_id):
            unit = self.unit_states.get(unit_id)
            if not unit:
                return []
            
            # Simple implementation: return all tiles within MOV range
            unit_data = next((u for u in self.scenario['units'] if u['id'] == unit_id), None)
            if not unit_data:
                return [unit.position]
            
            mov = unit_data['stats'].get('MOV', 5)
            x, y = unit.position
            
            # Generate tiles within movement range
            tiles = []
            for dx in range(-mov, mov + 1):
                for dy in range(-mov, mov + 1):
                    if abs(dx) + abs(dy) <= mov:  # Manhattan distance
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self.scenario['map_size'][0] and 0 <= new_y < self.scenario['map_size'][1]:
                            tiles.append((new_x, new_y))
            
            return tiles
        
        self.mock_movementSystem.calculate_movement_range.side_effect = mock_calculate_movement_range
    
    def test_healer_prioritizes_critically_injured_ally(self):
        """Test that the healer prioritizes healing the critically injured ally first."""
        # Arrange
        healer_id = "enemy_healer"
        critical_fighter_id = "enemy_fighter2"  # 20% HP
        
        # Mock find_item_targets to return all allies
        def mock_find_item_targets(unit_id, from_tile, item_id, item_data, potential_targets):
            if item_id.endswith("_STAFF") and item_data.get('heals_hp', False):
                return ["enemy_fighter1", "enemy_fighter2", "enemy_mage"]
            elif item_id == "RESTORE_STAFF":
                return ["enemy_mage"]  # Only mage has status effect
            return []
        
        with patch.object(self.ai_manager, 'find_item_targets', side_effect=mock_find_item_targets):
            # Act
            possible_actions = self.ai_manager.find_possible_actions(healer_id, AIProfile(
                behavior_type=AIBehaviorType.HEAL_SUPPORT,
                target_priority=AITargetPriority.WEAKEST,
                aggression=30,
                heal_threshold_ally=0.7
            ))
            
            # Filter for ITEM actions (healing)
            heal_actions = [a for a in possible_actions if a['type'] == 'ITEM' and 'target_unit_id' in a.get('target_info', {})]
            
            # Sort by score to find the highest priority
            heal_actions.sort(key=lambda a: a['score'], reverse=True)
            best_action = heal_actions[0] if heal_actions else None
            
            # Assert
            self.assertIsNotNone(best_action, "No healing action found")
            self.assertEqual(best_action['target_info'].get('target_unit_id'), critical_fighter_id, 
                            "AI did not prioritize the critically injured fighter")
    
    def test_healer_prioritizes_status_removal_after_critical_healing(self):
        """Test that after critical healing is done, the healer prioritizes removing status effects."""
        # Arrange
        healer_id = "enemy_healer"
        sleeping_mage_id = "enemy_mage"  # Has SLEEP status
        
        # Update the critically injured fighter to be at full health
        self.unit_states["enemy_fighter2"].current_hp = self.unit_states["enemy_fighter2"].max_hp
        
        # Mock find_item_targets to return all allies
        def mock_find_item_targets(unit_id, from_tile, item_id, item_data, potential_targets):
            if item_id.endswith("_STAFF") and item_data.get('heals_hp', False):
                return ["enemy_fighter1"]  # Only fighter1 needs healing now
            elif item_id == "RESTORE_STAFF":
                return ["enemy_mage"]  # Only mage has status effect
            return []
        
        with patch.object(self.ai_manager, 'find_item_targets', side_effect=mock_find_item_targets):
            # Override score_item_action to give a high score for restore staff
            def mock_score_item_action(unit_id, target_id, from_tile, item_id, item_data, profile):
                if item_id == "RESTORE_STAFF" and target_id == "enemy_mage":
                    return 100  # High score for removing status effect
                elif item_id.endswith("_STAFF") and target_id == "enemy_fighter1":
                    return 80  # Good score for healing injured ally
                return 0
            
            with patch.object(self.ai_manager, 'score_item_action', side_effect=mock_score_item_action):
                # Act
                possible_actions = self.ai_manager.find_possible_actions(healer_id, AIProfile(
                    behavior_type=AIBehaviorType.HEAL_SUPPORT,
                    target_priority=AITargetPriority.WEAKEST,
                    aggression=30,
                    heal_threshold_ally=0.7,
                    use_status_staves=True
                ))
                
                # Filter for ITEM actions
                item_actions = [a for a in possible_actions if a['type'] == 'ITEM' and 'target_unit_id' in a.get('target_info', {})]
                
                # Sort by score to find the highest priority
                item_actions.sort(key=lambda a: a['score'], reverse=True)
                best_action = item_actions[0] if item_actions else None
                
                # Assert
                self.assertIsNotNone(best_action, "No item action found")
                self.assertEqual(best_action['target_info'].get('item_id'), "RESTORE_STAFF", 
                                "AI did not select restore staff")
                self.assertEqual(best_action['target_info'].get('target_unit_id'), sleeping_mage_id, 
                                "AI did not target the ally with status effect")
    
    def test_healer_moves_to_reach_healing_target(self):
        """Test that the healer moves to reach a healing target that is out of range."""
        # Arrange
        healer_id = "enemy_healer"
        injured_fighter_id = "enemy_fighter1"
        
        # Move the injured fighter out of initial staff range
        self.unit_states["enemy_fighter1"].position = (8, 3)  # Further away
        
        # Mock find_item_targets to return targets based on position
        def mock_find_item_targets(unit_id, from_tile, item_id, item_data, potential_targets):
            # Only return the fighter as target if healer is close enough
            distance = abs(from_tile[0] - self.unit_states["enemy_fighter1"].position[0]) + \
                      abs(from_tile[1] - self.unit_states["enemy_fighter1"].position[1])
            
            if item_id.endswith("_STAFF") and item_data.get('heals_hp', False):
                if distance <= 1:  # Adjacent
                    return ["enemy_fighter1"]
                elif item_id == "PHYSIC_STAFF" and distance <= 4:  # Within Physic range
                    return ["enemy_fighter1"]
            return []
        
        with patch.object(self.ai_manager, 'find_item_targets', side_effect=mock_find_item_targets):
            # Mock pathfinder to return a path
            self.mock_mapSystem.pathfinder.reconstruct_path.side_effect = lambda start, end, unit_id: [start, (6, 2), (7, 3), end]
            
            # Act
            possible_actions = self.ai_manager.find_possible_actions(healer_id, AIProfile(
                behavior_type=AIBehaviorType.HEAL_SUPPORT,
                target_priority=AITargetPriority.WEAKEST,
                aggression=30,
                heal_threshold_ally=0.7
            ))
            
            # Filter for actions that involve movement and healing
            move_heal_actions = [a for a in possible_actions if a['type'] == 'ITEM' and 
                                'move_path' in a and a['move_path'] is not None]
            
            # Sort by score to find the highest priority
            move_heal_actions.sort(key=lambda a: a['score'], reverse=True)
            best_action = move_heal_actions[0] if move_heal_actions else None
            
            # Assert
            self.assertIsNotNone(best_action, "No move-and-heal action found")
            self.assertEqual(best_action['target_info'].get('target_unit_id'), injured_fighter_id, 
                            "AI did not target the injured fighter after moving")
            self.assertIsNotNone(best_action.get('move_path'), "No movement path in the action")


if __name__ == '__main__':
    unittest.main()