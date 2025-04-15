import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager, AIBehaviorType, AITargetPriority, AIProfile, AIAction


class TestAIThiefLoot(unittest.TestCase):
    """Test cases for the THIEF_LOOT archetype in the AI Manager."""
    
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
    
    def test_thief_identifies_chest_targets(self):
        """Test that the THIEF_LOOT AI correctly identifies chest targets on the map."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chests
        chest1 = MagicMock(name="Chest1")
        chest1.object_id = "chest1"
        chest1.object_type = "Chest"
        chest1.position = (8, 5)
        chest1.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock map system to return chests
        self.mock_mapSystem.get_map_objects.return_value = [chest1]
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5)]  # Current position and adjacent tile
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock the find_all_thief_targets method to return our chests
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": chest1.position, "type": "CHEST", "object_id": chest1.object_id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE actions towards chests
            chest_move_actions = [a for a in possible_actions if a['type'] == 'MOVE' and 
                                 'context' in a and a['context'].get('target_type') == 'CHEST']
            
            # Assert
            self.assertTrue(len(chest_move_actions) > 0, "No move actions towards chests found")
    
    def test_thief_identifies_door_targets(self):
        """Test that the THIEF_LOOT AI correctly identifies door targets on the map."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock doors
        door1 = MagicMock(name="Door1")
        door1.object_id = "door1"
        door1.object_type = "Door"
        door1.position = (8, 5)
        door1.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock map system to return doors
        self.mock_mapSystem.get_map_objects.return_value = [door1]
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5)]  # Current position and adjacent tile
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock the find_all_thief_targets method to return our doors
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": door1.position, "type": "DOOR", "object_id": door1.object_id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE actions towards doors
            door_move_actions = [a for a in possible_actions if a['type'] == 'MOVE' and 
                                'context' in a and a['context'].get('target_type') == 'DOOR']
            
            # Assert
            self.assertTrue(len(door_move_actions) > 0, "No move actions towards doors found")
    
    def test_thief_identifies_steal_targets(self):
        """Test that the THIEF_LOOT AI correctly identifies units with stealable items."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        thief_unit.stats = {"speed": 12, "con": 8}
        
        # Create mock enemy units with items
        enemy1 = MagicMock(name="Enemy1")
        enemy1.id = "player1"
        enemy1.position = (8, 5)
        enemy1.faction = FactionEnum.PLAYER
        enemy1.stats = {"speed": 8}
        enemy1.calculated_stats = {"attack_speed": 8}
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "thief1": thief_unit,
            "player1": enemy1
        }.get(unit_id)
        
        # Mock stealingSystem to return stealable items
        self.mock_stealingSystem.get_stealable_items.return_value = [
            {"id": "item1", "name": "Vulnerary", "weight": 1}
        ]
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5)]  # Current position and adjacent tile
        self.mock_movementSystem.get_reachable_tiles.return_value = reachable_tiles
        
        # Mock the find_all_thief_targets method to return our steal targets
        with patch.object(self.ai_manager, 'find_all_thief_targets', return_value=[
            {"coord": enemy1.position, "type": "STEAL_TARGET", "unit_id": enemy1.id}
        ]):
            # Act
            possible_actions = self.ai_manager.find_possible_actions("thief1", self.thief_loot_profile)
            
            # Filter for MOVE actions towards steal targets
            steal_move_actions = [a for a in possible_actions if a['type'] == 'MOVE' and 
                                 'context' in a and a['context'].get('target_type') == 'STEAL_TARGET']
            
            # Assert
            self.assertTrue(len(steal_move_actions) > 0, "No move actions towards steal targets found")
    
    def test_thief_prioritizes_chest_over_combat(self):
        """Test that the THIEF_LOOT AI prioritizes opening chests over combat."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': 'player1'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'INTERACT_MAP',
                'score': 200,  # Higher score for chest interaction
                'target_info': {'object_id': 'chest1', 'interact_type': 'CHEST'},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock find_possible_actions to return our predefined actions
        with patch.object(self.ai_manager, 'find_possible_actions', return_value=possible_actions):
            # Act
            best_action = self.ai_manager.select_best_action("thief1", possible_actions, self.thief_loot_profile)
            
            # Assert
            self.assertEqual(best_action.action_type, 'INTERACT_MAP', "AI did not select chest interaction over attack")
            self.assertEqual(best_action.target_data.get('object_id'), 'chest1', "AI did not target the chest")
    
    def test_thief_prioritizes_steal_over_combat(self):
        """Test that the THIEF_LOOT AI prioritizes stealing over combat."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': 'player2'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'STEAL',
                'score': 150,  # Higher score for stealing
                'target_info': {'target_unit_id': 'player1', 'item_id': 'item1'},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock find_possible_actions to return our predefined actions
        with patch.object(self.ai_manager, 'find_possible_actions', return_value=possible_actions):
            # Act
            best_action = self.ai_manager.select_best_action("thief1", possible_actions, self.thief_loot_profile)
            
            # Assert
            self.assertEqual(best_action.action_type, 'STEAL', "AI did not select steal over attack")
            self.assertEqual(best_action.target_data.get('target_unit_id'), 'player1', "AI did not target the enemy with item")
            self.assertEqual(best_action.target_data.get('item_id'), 'item1', "AI did not target the correct item")
    
    def test_thief_moves_towards_chest(self):
        """Test that the THIEF_LOOT AI moves towards a chest when not adjacent."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'MOVE',
                'score': 100,  # High score for moving towards chest
                'target_info': {},
                'move_path': [(5, 5), (6, 5), (7, 5)],  # Move as close as possible to chest
                'is_current_pos': False,
                'context': {"target_type": "CHEST", "target_coord": (8, 5)}
            }
        ]
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock find_possible_actions to return our predefined actions
        with patch.object(self.ai_manager, 'find_possible_actions', return_value=possible_actions):
            # Act
            best_action = self.ai_manager.select_best_action("thief1", possible_actions, self.thief_loot_profile)
            
            # Assert
            self.assertEqual(best_action.action_type, 'MOVE', "AI did not select move towards chest")
            self.assertEqual(best_action.target_data.get('move_path')[-1], (7, 5), "AI did not move to the closest possible position to chest")
    
    def test_thief_executes_chest_interaction(self):
        """Test that the THIEF_LOOT AI executes chest interaction when adjacent to a chest."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chest adjacent to thief
        chest = MagicMock(name="Chest")
        chest.object_id = "chest1"
        chest.object_type = "Chest"
        chest.position = (6, 5)  # Adjacent to thief
        chest.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock map system to return chest
        self.mock_mapSystem.get_map_objects.return_value = [chest]
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.return_value = 1  # Adjacent
        
        # Mock map interaction system to check if thief can interact with chest
        self.mock_mapInteractionSystem.can_interact_with_object.return_value = True
        
        # Mock find_map_interactables_from to return our chest
        with patch.object(self.ai_manager, 'find_map_interactables_from', return_value=[
            (chest.position, "CHEST")
        ]):
            # Act
            possible_actions = self.ai_manager.evaluate_actions_from_tile(
                "thief1", thief_unit.position, self.thief_loot_profile, is_current_pos=True
            )
            
            # Filter for INTERACT_MAP actions
            interact_actions = [a for a in possible_actions if a['type'] == 'INTERACT_MAP']
            
            # Assert
            self.assertTrue(len(interact_actions) > 0, "No INTERACT_MAP actions found")
            self.assertEqual(interact_actions[0]['target_info']['interact_type'], 'CHEST', "AI did not target the chest")
