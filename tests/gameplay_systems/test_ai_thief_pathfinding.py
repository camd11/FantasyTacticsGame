import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager, AIBehaviorType, AITargetPriority, AIProfile, AIAction


class TestAIThiefPathfinding(unittest.TestCase):
    """Test cases for the pathfinding behavior of the THIEF_LOOT archetype in the AI Manager."""
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_actionHandler = MagicMock(name="ActionHandler")
        self.mock_dataProvider = MagicMock(name="DataProvider")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        self.mock_mapInteractionSystem = MagicMock(name="MapInteractionSystem")
        self.mock_stealingSystem = MagicMock(name="StealingSystem")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.ENEMY
        self.mock_game_state.unit_states = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
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
            self.mock_dataProvider
        )
        
        # Add additional systems to the AI manager
        self.ai_manager.inventorySystem = self.mock_inventorySystem
        self.ai_manager.mapInteractionSystem = self.mock_mapInteractionSystem
        self.ai_manager.stealingSystem = self.mock_stealingSystem
        
        # Create a THIEF_LOOT AI profile
        self.thief_loot_profile = AIProfile(
            behavior_type=AIBehaviorType.THIEF_LOOT,
            target_priority=AITargetPriority.CLOSEST,
            aggression=30  # Low aggression to prioritize looting over combat
        )
    
    def test_thief_pathfinds_to_nearest_chest(self):
        """Test that the THIEF_LOOT AI pathfinds to the nearest chest when multiple are available."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chests at different distances
        near_chest = MagicMock(name="NearChest")
        near_chest.object_id = "chest1"
        near_chest.object_type = "Chest"
        near_chest.position = (8, 5)  # 3 tiles away horizontally
        near_chest.state = "Locked"
        
        far_chest = MagicMock(name="FarChest")
        far_chest.object_id = "chest2"
        far_chest.object_type = "Chest"
        far_chest.position = (5, 10)  # 5 tiles away vertically
        far_chest.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock map system to return chests
        self.mock_mapSystem.get_map_objects.return_value = [near_chest, far_chest]
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5), (7, 5)]  # Can move up to 2 tiles right
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: (
            abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        )
        
        # Mock pathfinder to return paths to chests
        self.mock_mapSystem.pathfinder.find_path.side_effect = lambda start, end, unit_id: (
            [start, (6, 5), (7, 5), end] if end == near_chest.position else
            [start, (5, 6), (5, 7), (5, 8), (5, 9), end]
        )
        
        # Mock the find_all_thief_targets method to return our chests
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": near_chest.position, "type": "CHEST", "object_id": near_chest.object_id},
            {"coord": far_chest.position, "type": "CHEST", "object_id": far_chest.object_id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE actions towards chests
            chest_move_actions = [a for a in possible_actions if a['type'] == 'MOVE' and 
                                 'context' in a and a['context'].get('target_type') == 'CHEST']
            
            # Sort by score (descending)
            chest_move_actions.sort(key=lambda a: a['score'], reverse=True)
        
        # Assert
        self.assertTrue(len(chest_move_actions) >= 2, "Should find at least 2 move actions towards chests")
        
        # Verify the highest scoring action is towards the nearest chest
        highest_scoring_action = chest_move_actions[0]
        self.assertEqual(highest_scoring_action['context']['target_coord'], near_chest.position, 
                         "Highest scoring action should be towards the nearest chest")
    
    def test_thief_pathfinds_around_obstacles(self):
        """Test that the THIEF_LOOT AI pathfinds around obstacles to reach a chest."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chest
        chest = MagicMock(name="Chest")
        chest.object_id = "chest1"
        chest.object_type = "Chest"
        chest.position = (9, 5)  # 4 tiles away horizontally
        chest.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock map system to return chest
        self.mock_mapSystem.get_map_objects.return_value = [chest]
        
        # Mock movement system to return reachable tiles
        # Simulate an obstacle at (6, 5) by not including it in reachable tiles
        reachable_tiles = [(5, 5), (5, 6), (6, 6), (7, 6), (7, 5)]  # Path around obstacle
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: (
            abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        )
        
        # Mock pathfinder to return path around obstacle
        obstacle_path = [(5, 5), (5, 6), (6, 6), (7, 6), (7, 5), (8, 5), (9, 5)]
        self.mock_mapSystem.pathfinder.find_path.return_value = obstacle_path
        
        # Mock reconstruct_path to return the expected path
        self.mock_mapSystem.pathfinder.reconstruct_path.return_value = [(5, 5), (5, 6), (6, 6), (7, 6), (7, 5)]
        
        # Mock the find_all_thief_targets method to return our chest
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": chest.position, "type": "CHEST", "object_id": chest.object_id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE actions towards chests
            chest_move_actions = [a for a in possible_actions if a['type'] == 'MOVE' and 
                                 'context' in a and a['context'].get('target_type') == 'CHEST']
        
        # Assert
        self.assertTrue(len(chest_move_actions) > 0, "Should find move actions towards chest")
        
        # Verify the path goes around the obstacle
        move_path = chest_move_actions[0]['move_path']
        self.assertNotIn((6, 5), move_path, "Path should not go through obstacle")
        self.assertIn((5, 6), move_path, "Path should go around obstacle")
    
    def test_thief_prioritizes_closer_targets(self):
        """Test that the THIEF_LOOT AI prioritizes closer targets when multiple types are available."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        thief_unit.stats = {"speed": 12, "con": 8}
        
        # Create mock targets at different distances
        chest = MagicMock(name="Chest")
        chest.object_id = "chest1"
        chest.object_type = "Chest"
        chest.position = (10, 5)  # 5 tiles away
        chest.state = "Locked"
        
        door = MagicMock(name="Door")
        door.object_id = "door1"
        door.object_type = "Door"
        door.position = (5, 10)  # 5 tiles away
        door.state = "Locked"
        
        enemy_with_item = MagicMock(name="EnemyWithItem")
        enemy_with_item.id = "player1"
        enemy_with_item.position = (7, 5)  # 2 tiles away
        enemy_with_item.faction = FactionEnum.PLAYER
        enemy_with_item.stats = {"speed": 8}
        enemy_with_item.calculated_stats = {"attack_speed": 8}
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "thief1": thief_unit,
            "player1": enemy_with_item
        }.get(unit_id)
        
        # Mock map system to return map objects
        self.mock_mapSystem.get_map_objects.side_effect = lambda type: [chest] if type == "Chest" else [door]
        
        # Mock stealingSystem to return stealable items
        self.mock_stealingSystem.get_stealable_items.return_value = [
            {"id": "item1", "name": "Vulnerary", "weight": 1}
        ]
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5), (7, 5)]  # Can move up to 2 tiles right
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: (
            abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        )
        
        # Mock the find_all_thief_targets method to return all targets
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": chest.position, "type": "CHEST", "object_id": chest.object_id},
            {"coord": door.position, "type": "DOOR", "object_id": door.object_id},
            {"coord": enemy_with_item.position, "type": "STEAL_TARGET", "unit_id": enemy_with_item.id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE and STEAL actions
            move_actions = [a for a in possible_actions if a['type'] == 'MOVE' and 'context' in a]
            steal_actions = [a for a in possible_actions if a['type'] == 'STEAL']
            
            # Sort by score (descending)
            all_actions = move_actions + steal_actions
            all_actions.sort(key=lambda a: a['score'], reverse=True)
        
        # Assert
        self.assertTrue(len(all_actions) > 0, "Should find actions towards targets")
        
        # Verify the highest scoring action is towards the closest target (enemy with item)
        highest_scoring_action = all_actions[0]
        if highest_scoring_action['type'] == 'MOVE':
            target_coord = highest_scoring_action['context']['target_coord']
            self.assertEqual(target_coord, enemy_with_item.position, 
                            "Highest scoring action should be towards the closest target")
        else:  # STEAL action
            self.assertEqual(highest_scoring_action['target_info']['target_unit_id'], enemy_with_item.id,
                            "Highest scoring action should be to steal from the closest target")
    
    def test_thief_avoids_combat_while_pathfinding(self):
        """Test that the THIEF_LOOT AI avoids combat while pathfinding to targets."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chest
        chest = MagicMock(name="Chest")
        chest.object_id = "chest1"
        chest.object_type = "Chest"
        chest.position = (9, 5)  # 4 tiles away horizontally
        chest.state = "Locked"
        
        # Create mock enemy unit in the path
        enemy = MagicMock(name="Enemy")
        enemy.id = "player1"
        enemy.position = (7, 5)  # In the direct path to chest
        enemy.faction = FactionEnum.PLAYER
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "thief1": thief_unit,
            "player1": enemy
        }.get(unit_id)
        
        # Mock map system to return chest
        self.mock_mapSystem.get_map_objects.return_value = [chest]
        
        # Mock movement system to return reachable tiles
        # Direct path and path around enemy
        reachable_tiles = [(5, 5), (6, 5), (7, 5), (6, 6), (7, 6)]
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: (
            abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        )
        
        # Mock combat system to return prediction
        combat_prediction = {
            'attacker': {
                'dmg': 5,
                'hit': 70,
                'crit': 0,
                'doubles': False
            },
            'defender': {
                'dmg': 8,  # Enemy deals more damage
                'hit': 80,
                'crit': 0,
                'doubles': False
            }
        }
        self.mock_combatSystem.simulate_combat.return_value = combat_prediction
        
        # Mock the find_all_thief_targets method to return our chest
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": chest.position, "type": "CHEST", "object_id": chest.object_id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE and ATTACK actions
            move_actions = [a for a in possible_actions if a['type'] == 'MOVE']
            attack_actions = [a for a in possible_actions if a['type'] == 'ATTACK']
            
            # Sort by score (descending)
            all_actions = move_actions + attack_actions
            all_actions.sort(key=lambda a: a['score'], reverse=True)
        
        # Assert
        self.assertTrue(len(all_actions) > 0, "Should find actions")
        
        # Verify the highest scoring action is a move action, not an attack
        highest_scoring_action = all_actions[0]
        self.assertEqual(highest_scoring_action['type'], 'MOVE', 
                         "Highest scoring action should be MOVE, not ATTACK")
        
        # If there are attack actions, verify they have lower scores than move actions
        if attack_actions:
            highest_attack_score = max(a['score'] for a in attack_actions)
            highest_move_score = max(a['score'] for a in move_actions)
            self.assertLess(highest_attack_score, highest_move_score, 
                           "Attack actions should have lower scores than move actions")