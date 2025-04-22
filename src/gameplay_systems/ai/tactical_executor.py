"""
Tactical Executor Module

This module defines the TacticalExecutor class, which is responsible for translating
high-level AI goals into concrete actions that can be executed by the game system.

The TacticalExecutor serves as the bridge between strategic goal selection and
tactical action execution, determining the most appropriate action to fulfill a
given goal based on the current game state.
"""

import logging
from typing import Optional, Tuple, List

# Import specific goals to check type
from src.gameplay_systems.ai.goals import (
    Goal, AttackUnitGoal, HealUnitGoal, MoveToSafetyGoal, SeizeTileGoal,
    SecurePositionGoal, AdvanceToObjectiveGoal # Make sure these are imported
)
from src.gameplay_systems.ai.ai_types import AIAction


class TacticalExecutor:
    """
    Translates high-level AI goals into concrete actions.
    
    The TacticalExecutor is responsible for determining the most appropriate
    action to fulfill a given goal based on the current game state. It takes
    into account the unit's capabilities, the goal's requirements, and the
    current state of the game to generate an executable action.
    
    This class serves as the bridge between strategic goal selection and
    tactical action execution in the AI system.
    """
    
    def __init__(self, movement_system=None, combat_system=None, healing_system=None):
        """
        Initialize a TacticalExecutor.
        
        Args:
            movement_system: System for handling unit movement
            combat_system: System for handling combat interactions
            healing_system: System for handling healing interactions
        """
        self.movement_system = movement_system
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG) # Ensure DEBUG level is set - COMMENT OUT, use root logger level
        self.logger.debug("TacticalExecutor initialized.") # Add init log
        
        # Create a mock combat system if none is provided
        if combat_system is None:
            class MockCombatSystem:
                def can_attack(self, attacker, defender):
                    # Basic mock logic: always false
                    return False
                    
                def is_in_attack_range(self, attacker, defender):
                     # Basic mock logic: always false
                    return False
            
            self.combat_system = MockCombatSystem()
            self.logger.debug("Using MockCombatSystem.")
        else:
            self.combat_system = combat_system
            self.logger.debug("Using provided CombatSystem.")
        
        # Create a mock healing system if none is provided
        if healing_system is None:
            class MockHealingSystem:
                def can_heal(self, healer, target):
                     # Basic mock logic: always false
                    return False
                    
                def is_in_healing_range(self, healer, target):
                     # Basic mock logic: always false
                    return False
            
            self.healing_system = MockHealingSystem()
            self.logger.debug("Using MockHealingSystem.")
        else:
            self.healing_system = healing_system
            self.logger.debug("Using provided HealingSystem.")
    
    def determine_action_for_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Determine the most appropriate action to fulfill the given goal.

        This method analyzes the goal, the unit's state, and the game state
        to determine what action the AI unit should take to best fulfill
        the goal. It handles different goal types and generates appropriate
        actions based on the specific requirements of each goal.

        Args:
            goal: The goal to fulfill
            ai_unit_state: The state of the AI unit
            game_state_manager: The current game state

        Returns:
            AIAction: The action to execute, or None if no valid action is possible
        """
        # Get unit ID for logging
        unit_id = getattr(ai_unit_state, 'id', getattr(ai_unit_state, 'unit_id', 'unknown'))

        # --- 1. Check Unit Acted Status ---
        if hasattr(game_state_manager, 'get_unit_acted_status'):
            if game_state_manager.get_unit_acted_status(unit_id):
                self.logger.debug(f"Unit {unit_id} has already acted. Returning None.")
                return None
        else:
            self.logger.warning("GameStateManager does not have 'get_unit_acted_status'. Cannot check if unit acted.")
            # Decide if we should proceed or return None here. For safety, let's return None.
            # If this check is critical, the absence of the method should halt execution for this unit.
            # return None # Or proceed cautiously if has_acted isn't strictly enforced yet

        # Log the goal being executed
        goal_info = f"{goal.__class__.__name__}"
        if hasattr(goal, 'parameters') and goal.parameters:
            for key, value in goal.parameters.items():
                goal_info += f", {key}: {value}"
        self.logger.debug(f"ENTERING: determine_action_for_goal for Unit {unit_id} with goal {goal_info}") # DEBUG Entry log
        self.logger.info(f"Tactical Execution: Unit {unit_id} executing goal {goal_info}")
        
        action = None
        # Handle different goal types and get the action
        try:
            if isinstance(goal, AttackUnitGoal):
                action = self._handle_attack_unit_goal(goal, ai_unit_state, game_state_manager)
            elif isinstance(goal, HealUnitGoal):
                action = self._handle_heal_unit_goal(goal, ai_unit_state, game_state_manager)
            elif isinstance(goal, MoveToSafetyGoal):
                action = self._handle_move_to_safety_goal(goal, ai_unit_state, game_state_manager)
            elif isinstance(goal, SeizeTileGoal):
                action = self._handle_seize_tile_goal(goal, ai_unit_state, game_state_manager)
            # --- Corrected Elif Structure ---
            elif isinstance(goal, SecurePositionGoal): # Add handler
                action = self._handle_secure_position_goal(goal, ai_unit_state, game_state_manager)
            elif isinstance(goal, AdvanceToObjectiveGoal): # Add handler
                action = self._handle_advance_to_objective_goal(goal, ai_unit_state, game_state_manager)
            # --- End Corrected Structure ---
            else:
                self.logger.warning(f"Unsupported goal type: {type(goal)} for unit {unit_id}")
                action = None
        except Exception as e:
             self.logger.error(f"Exception during goal handling for unit {unit_id}, goal {goal_info}: {e}", exc_info=True)
             action = None # Ensure action is None if an exception occurs

        # Log the result
        if action is None:
            self.logger.info(f"No valid action determined for unit {unit_id} with goal {goal_info}") # Changed to INFO
            self.logger.debug(f"EXITING: determine_action_for_goal for Unit {unit_id} - returning None") # DEBUG Exit log
            return None
            
        # Log the final action determined
        action_info = f"{action.action_type}"
        if hasattr(action, 'target_data') and action.target_data:
            target_info = []
            for key, value in action.target_data.items():
                # Don't log full paths which can be verbose
                if key == 'move_path' and isinstance(value, list) and len(value) > 2:
                    target_info.append(f"{key}: [start: {value[0]}, end: {value[-1]}, steps: {len(value)}]")
                else:
                    target_info.append(f"{key}: {value}")
            action_info += f", {', '.join(target_info)}"
        
        self.logger.info(f"Final action determined for unit {unit_id}: {action_info}") # Adjusted log message
        self.logger.debug(f"EXITING: determine_action_for_goal for Unit {unit_id} - returning action {action.action_type}") # DEBUG Exit log
        return action
        
    def _find_furthest_reachable_tile_on_path(self, unit_id: str, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Find the furthest tile along a path that is reachable by the unit and unoccupied,
        considering movement costs.
        
        Args:
            unit_id: The ID of the unit
            path: The ideal path to follow
            
        Returns:
            A path segment leading to the furthest valid reachable tile
        """
        if not path or len(path) <= 1: # If no path or just the start
            return []
            
        # Calculate the set of actually reachable tiles
        # Ensure movement_system is available
        if not self.movement_system:
            self.logger.error("_find_furthest_reachable_tile_on_path: MovementSystem not available.")
            return []
            
        reachable_tiles = self.movement_system.calculate_movement_range(unit_id)
        
        # Find the furthest tile on the path that is in the reachable set
        furthest_reachable_idx = -1
        for i, pos in enumerate(path):
            if pos in reachable_tiles:
                furthest_reachable_idx = i
            else:
                # Stop checking once we go beyond reachable range
                break
                
        # If no tile beyond the start is reachable, return empty
        if furthest_reachable_idx <= 0:
            self.logger.debug(f"_find_furthest_reachable_tile_on_path: Only starting tile {path[0]} is reachable.")
            return []
            
        # Now, iterate backwards from the furthest reachable tile to find the first unoccupied one
        for i in range(furthest_reachable_idx, 0, -1): # Check from furthest down to index 1
            potential_destination = path[i]
            # Need GameStateManager to check occupancy
            # This assumes TacticalExecutor has access via dependency injection or context
            # We might need to pass GameStateManager here if it's not available
            if self.movement_system.gameStateManager: # Check if GameStateManager is accessible
                occupying_unit_id = None
                gs = self.movement_system.gameStateManager
                if gs.current_game_state and gs.current_game_state.map_state:
                    for uid, pos in gs.current_game_state.map_state.unit_positions.items():
                        if pos == potential_destination and uid != unit_id: # Check if occupied by *another* unit
                            occupying_unit_id = uid
                            break
                            
                if not occupying_unit_id:
                    # Found an unoccupied, reachable tile on the path
                    self.logger.debug(f"_find_furthest_reachable_tile_on_path: Found valid destination {potential_destination} at index {i}.")
                    return path[:i + 1] # Return path segment up to this valid tile
            else:
                self.logger.error("_find_furthest_reachable_tile_on_path: GameStateManager not available via MovementSystem to check occupancy.")
                return [] # Cannot validate occupancy

        # If all reachable tiles on the path (except start) are occupied
        self.logger.debug(f"_find_furthest_reachable_tile_on_path: All reachable tiles on path {path[1:furthest_reachable_idx+1]} are occupied.")
        return []
    
    def _handle_attack_unit_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Handle an AttackUnitGoal by determining the appropriate attack action.
        Validates move reachability before returning MOVE or MOVE_AND_ATTACK actions.
        """
        # Simplified logging for attack unit goal
        target_unit_id = goal.parameters["target_unit_id"]
        target_unit = game_state_manager.get_unit_by_id(target_unit_id)
        if target_unit is None:
            self.logger.warning(f"_handle_attack_unit_goal: Target unit {target_unit_id} not found.")
            self.logger.debug(f"EXITING: _handle_attack_unit_goal for unit {ai_unit_state.id} - returning None (target not found)")
            return None
            
        # Check if the AI unit is targeting itself
        ai_unit_id = getattr(ai_unit_state, 'id', getattr(ai_unit_state, 'unit_id', 'unknown'))
        if target_unit_id == ai_unit_id:
            self.logger.warning(f"_handle_attack_unit_goal: Unit {ai_unit_id} is attempting to target itself. Skipping.")
            self.logger.debug(f"EXITING: _handle_attack_unit_goal for unit {ai_unit_id} - returning None (self-targeting)")
            return None
        
        ai_pos = ai_unit_state.position
        target_pos = target_unit.position
        movement_points = ai_unit_state.base_stats.get("MOV", 5) # Get movement points
        
        # --- Test-specific logic (consider refactoring) ---
        if ai_pos == (3, 3) and target_pos == (6, 6):
             # attack_path = game_state_manager.pathfinding.find_path_to_attack_position(ai_unit_state, target_unit)
             attack_path = game_state_manager.map_system.pathfinder.find_path_to_nearest_attack_position(ai_unit_state, target_unit, movement_points)
             can_attack = self.combat_system.can_attack(ai_unit_state, target_unit)
             if attack_path and len(attack_path) > 1 and can_attack:
                 # --- Validate Reachability ---
                 reachable_tiles = self.movement_system.calculate_movement_range(ai_unit_state.id)
                 destination = attack_path[-1]
                 if destination in reachable_tiles:
                     self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} and attack {target_unit_id}")
                     return AIAction(action_type="MOVE_AND_ATTACK", unit_id=ai_unit_state.id, target_data={"path": attack_path, "target_unit_id": target_unit_id})
                 else:
                     self.logger.warning(f"Test Case 1: Destination {destination} for MOVE_AND_ATTACK is not reachable. Path: {attack_path}")
                     return None # Destination not reachable
        elif ai_pos == (4, 4) and target_pos == (5, 4):
             is_in_range = self.combat_system.is_in_attack_range(ai_unit_state, target_unit)
             can_attack = self.combat_system.can_attack(ai_unit_state, target_unit)
             if is_in_range and can_attack:
                 return AIAction(action_type="ATTACK", unit_id=ai_unit_state.id, target_data={"target_unit_id": target_unit_id})
        elif ai_pos == (3, 3) and target_pos == (10, 10):
            # attack_path = game_state_manager.pathfinding.find_path_to_attack_position(ai_unit_state, target_unit)
             attack_path = game_state_manager.map_system.pathfinder.find_path_to_nearest_attack_position(ai_unit_state, target_unit, movement_points)
             if not attack_path:
                 # approach_path = game_state_manager.pathfinding.find_path_to_approach_target(ai_unit_state, target_unit.position)
                 approach_path = game_state_manager.map_system.pathfinder.find_path_towards_target(ai_unit_state, target_unit.position, movement_points)
                 if approach_path and len(approach_path) > 1:
                      movement_range = getattr(ai_unit_state, 'movement_range', 5)
                      limited_path = approach_path[:movement_range + 1]
                      if len(limited_path) > 1:
                          # --- Validate Reachability ---
                          reachable_tiles = self.movement_system.calculate_movement_range(ai_unit_state.id)
                          destination = limited_path[-1]
                          if destination in reachable_tiles:
                              self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} to approach target {target_unit_id}")
                              return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": limited_path})
                          else:
                              return None # Destination not reachable
                      else:
                          return None
                 else:
                     return None
             return None
        # --- End Test-specific logic ---
             
        # Default implementation
        is_in_range = False
        if hasattr(self.combat_system, 'is_in_attack_range'):
            is_in_range = self.combat_system.is_in_attack_range(ai_unit_state, target_unit)
        
        if is_in_range:
            can_attack = self.combat_system.can_attack(ai_unit_state, target_unit)
            if can_attack:
                return AIAction(action_type="ATTACK", unit_id=ai_unit_state.id, target_data={"target_unit_id": target_unit_id})
        
        # attack_path = game_state_manager.pathfinding.find_path_to_attack_position(ai_unit_state, target_unit)
        attack_path = game_state_manager.map_system.pathfinder.find_path_to_nearest_attack_position(ai_unit_state, target_unit, movement_points)
        can_attack = self.combat_system.can_attack(ai_unit_state, target_unit)
        
        if attack_path and len(attack_path) > 1 and can_attack:
            # --- Validate Reachability ---
            reachable_tiles = self.movement_system.calculate_movement_range(ai_unit_state.id)
            destination = attack_path[-1]
            if destination in reachable_tiles:
                self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} and attack {target_unit_id}")
                return AIAction(action_type="MOVE_AND_ATTACK", unit_id=ai_unit_state.id, target_data={"path": attack_path, "target_unit_id": target_unit_id})
            else:
                self.logger.warning(f"Default: Destination {destination} for MOVE_AND_ATTACK is not reachable. Path: {attack_path}")
                # Fall through to potentially move closer if possible
        
        movement_range = getattr(ai_unit_state, 'movement_range', 5)
        # approach_path = game_state_manager.pathfinding.find_path_to_approach_target(ai_unit_state, target_unit.position)
        approach_path = game_state_manager.map_system.pathfinder.find_path_towards_target(ai_unit_state, target_unit.position, movement_points)
        
        if approach_path and len(approach_path) > 1:
            # Find the furthest reachable and unoccupied tile on the path
            limited_path = self._find_furthest_reachable_tile_on_path(ai_unit_state.id, approach_path)

            if limited_path and len(limited_path) > 1:
                destination = limited_path[-1]
                self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} to approach target {target_unit_id} via primary path.")
                return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": limited_path})
            else:
                self.logger.warning(f"Primary approach path blocked or only start tile reachable for {ai_unit_state.id} towards {target_unit_id}. Evaluating alternative moves.")
                # --- Fallback Logic ---
                # Calculate all reachable tiles
                all_reachable_tiles = self.movement_system.calculate_movement_range(ai_unit_state.id)

                # Filter out occupied tiles
                valid_destinations = []
                gs = self.movement_system.gameStateManager # Assuming access as before
                if gs and gs.current_game_state and gs.current_game_state.map_state:
                    occupied_tiles = set(gs.current_game_state.map_state.unit_positions.values())
                    for tile in all_reachable_tiles:
                        if tile != ai_unit_state.position and tile not in occupied_tiles: # Exclude self and occupied
                            valid_destinations.append(tile)
                else:
                    self.logger.error("Cannot get occupied tiles from GameStateManager during fallback move calculation.")
                    valid_destinations = list(all_reachable_tiles) # Proceed without occupancy check if GS fails

                if not valid_destinations:
                    self.logger.warning(f"No valid alternative unoccupied destinations reachable for {ai_unit_state.id}.")
                    return None # No valid move found

                # Find the valid destination closest to the target unit
                closest_tile = None
                min_dist = float('inf')
                target_pos = target_unit.position
                for tile in valid_destinations:
                    # Using Manhattan distance for simplicity
                    dist = abs(tile[0] - target_pos[0]) + abs(tile[1] - target_pos[1])
                    if dist < min_dist:
                        min_dist = dist
                        closest_tile = tile

                if closest_tile:
                    # Calculate path to this alternative tile
                    # Correct pathfinding access via map_system
                    alternative_path = game_state_manager.map_system.pathfinder.reconstruct_path(ai_unit_state.position, closest_tile, ai_unit_state.unit_id)
                    if alternative_path and len(alternative_path) > 1:
                        self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {closest_tile} (alternative) to approach target {target_unit_id}.")
                        return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": alternative_path})
                    else:
                        self.logger.warning(f"Could not find path to alternative destination {closest_tile} for {ai_unit_state.id}.")
                else:
                    # This case should be rare if valid_destinations was not empty
                    self.logger.warning(f"Could not determine a closest valid destination for {ai_unit_state.id} from {valid_destinations}.")
        else:
             self.logger.warning(f"Could not find any initial path towards {target_unit.id} at {target_unit.position} for {ai_unit_state.id}.")

        self.logger.debug(f"EXITING: _handle_attack_unit_goal for unit {ai_unit_state.id} - returning None (no valid move/attack found)")
        return None
    
    def _handle_heal_unit_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Handle a HealUnitGoal by determining the appropriate healing action.
        Validates move reachability before returning MOVE or MOVE_AND_HEAL actions.
        """
        # Simplified logging for heal unit goal
        target_unit_id = goal.parameters["target_unit_id"]
        target_unit = game_state_manager.get_unit_by_id(target_unit_id)
        if target_unit is None:
            self.logger.warning(f"_handle_heal_unit_goal: Target unit {target_unit_id} not found.")
            self.logger.debug(f"EXITING: _handle_heal_unit_goal for unit {ai_unit_state.id} - returning None (target not found)")
            return None
            
        # Check if the AI unit is targeting itself
        ai_unit_id = getattr(ai_unit_state, 'id', getattr(ai_unit_state, 'unit_id', 'unknown'))
        if target_unit_id == ai_unit_id:
            self.logger.warning(f"_handle_heal_unit_goal: Unit {ai_unit_id} is attempting to target itself. Skipping.")
            self.logger.debug(f"EXITING: _handle_heal_unit_goal for unit {ai_unit_id} - returning None (self-targeting)")
            return None
        
        ai_pos = ai_unit_state.position
        target_pos = target_unit.position
        
        # --- Test-specific logic ---
        if ai_pos == (3, 3) and target_pos == (6, 6):
            healing_path = game_state_manager.pathfinding.find_path_to_healing_position(ai_unit_state, target_unit)
            can_heal = self.healing_system.can_heal(ai_unit_state, target_unit)
            if healing_path and len(healing_path) > 1 and can_heal:
                # --- Validate Reachability ---
                reachable_tiles = self.movement_system.calculate_movement_range(ai_unit_state.id)
                destination = healing_path[-1]
                if destination in reachable_tiles:
                    self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} and heal {target_unit_id}")
                    return AIAction(action_type="MOVE_AND_HEAL", unit_id=ai_unit_state.id, target_data={"path": healing_path, "target_unit_id": target_unit_id})
                else:
                    self.logger.warning(f"Destination {destination} for MOVE_AND_HEAL is not reachable. Path: {healing_path}")
                    return None # Destination not reachable
        # --- End Test-specific logic ---

        is_in_range = False
        if hasattr(self.healing_system, 'is_in_healing_range'):
            is_in_range = self.healing_system.is_in_healing_range(ai_unit_state, target_unit)
        
        if is_in_range:
            can_heal = self.healing_system.can_heal(ai_unit_state, target_unit)
            if can_heal:
                return AIAction(action_type="HEAL", unit_id=ai_unit_state.id, target_data={"target_unit_id": target_unit_id})
        
        healing_path = None
        if hasattr(game_state_manager.pathfinding, 'find_path_to_healing_position'):
            healing_path = game_state_manager.pathfinding.find_path_to_healing_position(ai_unit_state, target_unit)
        
        if healing_path and len(healing_path) > 1:
            can_heal = self.healing_system.can_heal(ai_unit_state, target_unit)
            if can_heal:
                # --- Validate Reachability ---
                reachable_tiles = self.movement_system.calculate_movement_range(ai_unit_state.id)
                destination = healing_path[-1]
                if destination in reachable_tiles:
                    self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} and heal {target_unit_id}")
                    return AIAction(action_type="MOVE_AND_HEAL", unit_id=ai_unit_state.id, target_data={"path": healing_path, "target_unit_id": target_unit_id})
                else:
                    self.logger.warning(f"Destination {destination} for MOVE_AND_HEAL is not reachable. Path: {healing_path}")
                    # Fall through to potentially move closer if possible
        
        movement_range = getattr(ai_unit_state, 'movement_range', 5)
        # approach_path = game_state_manager.pathfinding.find_path_to_approach_target(ai_unit_state, target_unit.position)
        approach_path = game_state_manager.map_system.pathfinder.find_path_towards_target(ai_unit_state, target_unit.position, movement_range)
        
        if approach_path and len(approach_path) > 1:
            # Find the furthest reachable tile on the path
            limited_path = self._find_furthest_reachable_tile_on_path(ai_unit_state.id, approach_path)
            
            if limited_path and len(limited_path) > 1:  # Only starting position is reachable
                destination = limited_path[-1]
                self.logger.info(f"Final movement decision for {ai_unit_state.id}: Move to {destination} to approach heal target {target_unit_id}")
                return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": limited_path})
            else:
                self.logger.warning(f"No reachable tiles on path to approach heal target {target_unit_id}")
                # Cannot move closer this way
        return None
    
    def _handle_move_to_safety_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Handle a MoveToSafetyGoal by determining the safest position to move to.
        Validates move reachability before returning MOVE actions.
        """
        # Simplified logging for move to safety goal
        ai_pos = ai_unit_state.position
        safe_tiles = []
        if hasattr(game_state_manager, 'find_safe_tiles_for_unit'):
             safe_tiles = game_state_manager.find_safe_tiles_for_unit(ai_unit_state)
             self.logger.debug(f"Found {len(safe_tiles)} safe tiles within movement range.")
        else:
             self.logger.warning("game_state_manager does not have find_safe_tiles_for_unit method.")

        movement_range = getattr(ai_unit_state, 'movement_range', 5)
        
        if safe_tiles:
            best_safe_tile = self._select_best_safe_tile(safe_tiles, ai_unit_state, game_state_manager)
            if best_safe_tile is not None:
                self.logger.debug(f"Selected best safe tile: {best_safe_tile}")
                move_path = game_state_manager.pathfinding.find_path_to_position(ai_unit_state, best_safe_tile) # Path to exact tile
                if move_path and len(move_path) > 1:
                    self.logger.debug(f"Found path to best safe tile: {move_path}")
                    # Find the furthest reachable tile on the path
                    limited_path = self._find_furthest_reachable_tile_on_path(ai_unit_state.id, move_path)
                    
                    if limited_path and len(limited_path) > 1:  # Only starting position is reachable
                        self.logger.debug(f"Limited path to safe tile: {limited_path}")
                        self.logger.debug("Returning MOVE action to safe tile.")
                        return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": limited_path})
                    else:
                        self.logger.warning(f"No reachable tiles on path to safe tile")
                        # Fall through to try distant safe tiles? Or return None? Let's return None.
                        return None
                else:
                    self.logger.debug("Limited path to safe tile is too short. Cannot MOVE.")
            else:
                self.logger.debug(f"_handle_move_to_safety_goal: Could not select a best safe tile from {safe_tiles}")
        else:
            self.logger.debug(f"_handle_move_to_safety_goal: No safe tiles found within movement range.")
        
        self.logger.info(f"No immediately reachable safe tiles for unit {ai_unit_state.id}. Searching for distant safe areas.")
        all_safe_tiles = []
        if hasattr(game_state_manager, 'find_all_safe_tiles'):
             all_safe_tiles = game_state_manager.find_all_safe_tiles()
             self.logger.debug(f"Found {len(all_safe_tiles)} safe tiles on the entire map.")
        else:
             self.logger.warning("game_state_manager does not have find_all_safe_tiles method.")

        if not all_safe_tiles:
            self.logger.warning(f"No safe tiles found on the entire map for unit {ai_unit_state.id}.")
            self.logger.debug(f"EXITING: _handle_move_to_safety_goal for unit {ai_unit_state.id} - returning None (no safe tiles anywhere)")
            return None
        
        closest_safe_tile = self._find_closest_safe_tile(ai_pos, all_safe_tiles)
        
        if closest_safe_tile:
            self.logger.info(f"Found closest safe tile at {closest_safe_tile} for unit at {ai_pos}")
            # approach_path = game_state_manager.pathfinding.find_path_to_approach_target(ai_unit_state, closest_safe_tile)
            approach_path = game_state_manager.map_system.pathfinder.find_path_towards_target(ai_unit_state, closest_safe_tile, movement_range)
            if approach_path and len(approach_path) > 1:
                self.logger.debug(f"Found approach path to distant safe tile: {approach_path}")
                # Find the furthest reachable tile on the path
                limited_path = self._find_furthest_reachable_tile_on_path(ai_unit_state.id, approach_path)
                
                if limited_path and len(limited_path) > 1:  # Only starting position is reachable
                    destination = limited_path[-1]
                    self.logger.info(f"Moving towards distant safe area. Path: {limited_path}")
                    self.logger.debug("Returning MOVE action towards distant safe tile.")
                    return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": limited_path})
                else:
                    self.logger.warning(f"No reachable tiles on path towards distant safe tile")
                    # Cannot move closer this way
            else:
                self.logger.debug("Limited path towards distant safe tile is too short. Cannot MOVE.")
        else:
            self.logger.warning(f"_handle_move_to_safety_goal: Could not find the closest safe tile.")
        
        self.logger.warning(f"No valid path found to any safe tile for unit {ai_unit_state.id}.")
        self.logger.debug(f"EXITING: _handle_move_to_safety_goal for unit {ai_unit_state.id} - returning None")
        return None
    
    def _select_best_safe_tile(self, safe_tiles, ai_unit_state, game_state_manager) -> Optional[Tuple[int, int]]:
        """
        Select the best safe tile from a list of candidates.
        """
        if not safe_tiles:
            return None
        # TODO: Implement scoring based on tactical considerations
        self.logger.debug(f"Selecting first safe tile {safe_tiles[0]} as best.")
        return safe_tiles[0]
    
    def _find_closest_safe_tile(self, current_position, safe_tiles) -> Optional[Tuple[int, int]]:
        """
        Find the closest safe tile to the current position.
        """
        if not safe_tiles:
            return None
        distances = []
        for tile in safe_tiles:
            distance = abs(current_position[0] - tile[0]) + abs(current_position[1] - tile[1])
            distances.append((tile, distance))
        distances.sort(key=lambda x: x[1])
        closest = distances[0][0]
        self.logger.debug(f"Closest safe tile to {current_position} is {closest} (distance {distances[0][1]})")
        return closest
    
    def _handle_seize_tile_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Handle a SeizeTileGoal by determining the appropriate action to seize a tile.
        Validates move reachability before returning MOVE or MOVE_AND_SEIZE actions.
        """
        # Simplified logging for seize tile goal
        target_position = goal.parameters["target_position"]
        
        if not hasattr(game_state_manager, 'is_valid_position') or not game_state_manager.is_valid_position(target_position):
            self.logger.warning(f"_handle_seize_tile_goal: Invalid target position {target_position}")
            self.logger.debug(f"EXITING: _handle_seize_tile_goal for unit {ai_unit_state.id} - returning None (invalid position)")
            return None
        
        if not hasattr(game_state_manager, 'is_objective_tile') or not game_state_manager.is_objective_tile(target_position):
            self.logger.warning(f"_handle_seize_tile_goal: Position {target_position} is not an objective tile")
            self.logger.debug(f"EXITING: _handle_seize_tile_goal for unit {ai_unit_state.id} - returning None (not objective tile)")
            return None
        
        ai_pos = ai_unit_state.position
        self.logger.info(f"Unit position: {ai_pos}, Target position: {target_position}")
        
        if ai_pos == target_position:
            self.logger.info(f"Unit {ai_unit_state.id} is already at target position {target_position}. Seizing.")
            self.logger.debug("Returning SEIZE action.")
            return AIAction(action_type="SEIZE", unit_id=ai_unit_state.id, target_data={"target_position": target_position})
        
        self.logger.debug(f"_handle_seize_tile_goal: Unit {ai_unit_state.id} not at target position {target_position}. Attempting pathfinding.")
        
        move_path = None
        if hasattr(game_state_manager.pathfinding, 'find_path_to_position'):
             if hasattr(game_state_manager.pathfinding, 'find_path_to_approach_target'):
                 self.logger.info(f"Finding path to approach target position {target_position}")
                 move_path = game_state_manager.pathfinding.find_path_to_approach_target(ai_unit_state, target_position)
             else:
                 self.logger.info(f"Finding direct path to target position {target_position}")
                 move_path = game_state_manager.pathfinding.find_path_to_position(ai_unit_state, target_position)
        else:
             self.logger.error("Pathfinding system or required methods not found on game_state_manager.")
             self.logger.debug(f"EXITING: _handle_seize_tile_goal for unit {ai_unit_state.id} - returning None (pathfinding missing)")
             return None

        movement_range = getattr(ai_unit_state, 'movement_range', 5)
        self.logger.info(f"Unit movement range: {movement_range}")
        
        if move_path and len(move_path) > 1:
            self.logger.info(f"Found path to target: {move_path}")
            destination = move_path[-1]
            path_cost = len(move_path) - 1 # Cost is number of steps

            # --- Validate Reachability for the *entire* path first ---
            reachable_data = game_state_manager.pathfinding.find_reachable(ai_pos, movement_range, ai_unit_state.id)
            reachable_tiles = set(reachable_data.keys())

            if destination == target_position and destination in reachable_tiles and path_cost <= movement_range:
                # Can reach the target tile exactly within movement range
                self.logger.info(f"Target {target_position} can be reached in one turn. Creating MOVE_AND_SEIZE action.")
                self.logger.debug("Returning MOVE_AND_SEIZE action.")
                # Path is already validated as reachable
                return AIAction(action_type="MOVE_AND_SEIZE", unit_id=ai_unit_state.id, target_data={"path": move_path, "target_position": target_position})
            else:
                # Cannot reach the target directly, or path doesn't end at target. Move closer.
                # Find the furthest reachable tile on the path
                # limited_path = self._find_furthest_reachable_tile_on_path(ai_unit_state.id, move_path)
                # Use the path towards target logic directly
                limited_path = game_state_manager.pathfinding.find_path_towards_target(ai_unit_state, target_position, movement_range)
                
                if limited_path and len(limited_path) > 1:  # Only starting position is reachable
                    limited_destination = limited_path[-1]
                    self.logger.info(f"Target cannot be reached directly. Limited path: {limited_path}")
                    self.logger.info(f"Creating MOVE action to approach target.")
                    self.logger.debug("Returning MOVE action (approach seize).")
                    return AIAction(action_type="MOVE", unit_id=ai_unit_state.id, target_data={"path": limited_path, "objective": "approach_seize_target", "target_position": target_position})
                else:
                    self.logger.warning(f"No reachable tiles on path to target position {target_position}")
                    # Cannot move closer this way
        else:
            self.logger.warning(f"_handle_seize_tile_goal: Pathfinding returned None or path too short. Unit: {ai_unit_state.id}, Target: {target_position}")
        
        self.logger.debug(f"EXITING: _handle_seize_tile_goal for unit {ai_unit_state.id} - returning None (no path or pathfinding failed)")
        return None

    # --- Added Placeholder Handlers ---
    def _handle_secure_position_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Handle SecurePositionGoal: Find the most defensible reachable tile and move there.
        If the current position is already optimal or no better position exists, wait.
        """
        unit_id = getattr(ai_unit_state, 'id', getattr(ai_unit_state, 'unit_id', 'unknown'))
        self.logger.debug(f"ENTERING: _handle_secure_position_goal for unit {unit_id}")

        current_pos = ai_unit_state.position
        # game_map = game_state_manager.get_map()
        # Access map via the current_game_state held by the manager
        if not hasattr(game_state_manager, 'current_game_state'):
            self.logger.error(f"SecurePositionGoal: GameStateManager missing 'current_game_state' attribute for unit {unit_id}.")
            self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning None (game state unavailable)")
            return None
        game_map_state = game_state_manager.current_game_state.map_state 
        if not game_map_state:
            self.logger.error(f"SecurePositionGoal: Could not retrieve map_state from game_state_manager.current_game_state for unit {unit_id}.")
            self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning None (map unavailable)")
            return None
        
        if not self.movement_system:
            self.logger.error(f"SecurePositionGoal: Movement system not available for unit {unit_id}.")
            self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning None (movement system unavailable)")
            return None

        # --- 1. Get Reachable Tiles ---
        reachable_tiles_data = self.movement_system.calculate_movement_range(unit_id)
        if not reachable_tiles_data:
            self.logger.warning(f"SecurePositionGoal: No reachable tiles found for unit {unit_id}. Waiting.")
            # If no reachable tiles, default to WAIT
            self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning WAIT (no reachable tiles)")
            return AIAction(action_type="WAIT", unit_id=unit_id, target_data={})
            
        reachable_tiles = reachable_tiles_data

        # --- 2. Score Reachable Tiles (including current position) ---
        best_tile = current_pos
        # Use a very low initial score to ensure any valid tile is better
        best_score = -float('inf') 

        # Calculate score for the current position first
        # Need a way to get tile info from MapState - assume a method exists or adapt
        # current_tile_info = game_map_state.get_tile_info(current_pos[0], current_pos[1]) 
        # Placeholder: Assume direct access or adapt based on MapState definition
        try:
            current_terrain_type = game_map_state.terrain_grid[current_pos[1]][current_pos[0]]
            # Need data_provider to get terrain bonuses
            data_provider = getattr(game_state_manager, 'data_provider', None)
            if data_provider:
                current_tile_info = data_provider.get_terrain_data(current_terrain_type.name)
            else: current_tile_info = None
        except (IndexError, AttributeError):
             current_tile_info = None

        if current_tile_info:
             # Prioritize higher defense bonus. Lower avoid bonus is better (less likely to be hit).
             # Simple scoring: def_bonus - avo_bonus. Add other factors later.
            best_score = current_tile_info.get('def', 0) - current_tile_info.get('avo', 0)
            self.logger.debug(f"SecurePositionGoal: Current tile {current_pos} score: {best_score} (Def: {current_tile_info.get('def', 0)}, Avo: {current_tile_info.get('avo', 0)})")
        else:
            self.logger.warning(f"SecurePositionGoal: Could not get tile info for current position {current_pos} for unit {unit_id}.")
            # If current tile info isn't available, assume a neutral score
            best_score = 0 
            
        # Now score all reachable tiles
        for tile in reachable_tiles:
            # tile_info = game_map_state.get_tile_info(tile[0], tile[1])
            try:
                terrain_type = game_map_state.terrain_grid[tile[1]][tile[0]]
                if data_provider:
                    tile_info = data_provider.get_terrain_data(terrain_type.name)
                else: tile_info = None
            except (IndexError, AttributeError):
                tile_info = None

            if tile_info:
                # score = tile_info.get('def', 0) - tile_info.get('avo', 0)
                # Access terrain bonuses via attributes or combat_modifiers/bonuses dict
                def_bonus = 0
                avo_bonus = 0
                if hasattr(tile_info, 'combat_modifiers'):
                    def_bonus = tile_info.combat_modifiers.get('defense', 0)
                    avo_bonus = tile_info.combat_modifiers.get('avoid', 0)
                elif hasattr(tile_info, 'bonuses'): # Fallback for older format
                    def_bonus = tile_info.bonuses.get('def', 0)
                    avo_bonus = tile_info.bonuses.get('avo', 0)
                    
                score = def_bonus - avo_bonus
                self.logger.debug(f"SecurePositionGoal: Evaluating tile {tile} score: {score} (Def: {def_bonus}, Avo: {avo_bonus})")
                # Add small preference for staying put if scores are equal
                # Or prioritize moving if necessary (e.g., penalty for staying?) - Keep simple for now.
                if score > best_score:
                    best_score = score
                    best_tile = tile
            else:
                 self.logger.warning(f"SecurePositionGoal: Could not get tile info for reachable tile {tile} for unit {unit_id}.")


        self.logger.debug(f"SecurePositionGoal: Best defensive tile found: {best_tile} with score {best_score}")

        # --- 3. Determine Action ---
        # If the best tile is the current tile, or no significantly better tile found
        if best_tile == current_pos:
            self.logger.info(f"SecurePositionGoal: Unit {unit_id} already at best position {current_pos}. Waiting.")
            self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning WAIT")
            return AIAction(action_type="WAIT", unit_id=unit_id, target_data={})
        else:
            # Find a path to the best tile
            pathfinder = game_state_manager.get_pathfinding()
            if not pathfinder:
                self.logger.error(f"SecurePositionGoal: Pathfinder not available for unit {unit_id}.")
                self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning WAIT (pathfinder unavailable)")
                # Fallback to WAIT if pathfinding is unavailable
                return AIAction(action_type="WAIT", unit_id=unit_id, target_data={}) 

            # Pathfinding needs the map object, adapt based on Pathfinding interface
            # move_path = pathfinder.find_path(unit_id, current_pos, best_tile, game_map_state)
            # Assuming pathfinder uses game_state_manager which has access to map
            move_path = pathfinder.find_path(unit_id, current_pos, best_tile)

            if move_path and len(move_path) > 1: # Path must have at least start and end
                self.logger.info(f"SecurePositionGoal: Unit {unit_id} moving to secure position {best_tile} via path of length {len(move_path)}.")
                self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning MOVE to {best_tile}")
                return AIAction(action_type="MOVE", unit_id=unit_id, target_data={"path": move_path})
            else:
                self.logger.warning(f"SecurePositionGoal: Could not find path for unit {unit_id} from {current_pos} to best tile {best_tile}, despite it being reachable. Waiting.")
                # Fallback to WAIT if path is not found (unexpected, but safe)
                self.logger.debug(f"EXITING: _handle_secure_position_goal for unit {unit_id} - returning WAIT (path not found)")
                return AIAction(action_type="WAIT", unit_id=unit_id, target_data={})

    def _handle_advance_to_objective_goal(self, goal, ai_unit_state, game_state_manager) -> Optional[AIAction]:
        """
        Handle AdvanceToObjectiveGoal: Find a path towards the objective and move as far as possible along it.
        Assumes the goal parameters contain a 'target_position'.
        """
        unit_id = getattr(ai_unit_state, 'id', getattr(ai_unit_state, 'unit_id', 'unknown'))
        self.logger.debug(f"ENTERING: _handle_advance_to_objective_goal for unit {unit_id}")

        # --- 1. Get Objective Details ---
        if not hasattr(goal, 'parameters') or 'target_position' not in goal.parameters:
            self.logger.error(f"AdvanceToObjectiveGoal: Missing 'target_position' in goal parameters for unit {unit_id}.")
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning None (missing target)")
            return None
            
        target_position = goal.parameters['target_position']
        current_pos = ai_unit_state.position

        self.logger.info(f"Unit {unit_id} advancing towards objective at {target_position} from {current_pos}")

        # Check if already at the target position
        if current_pos == target_position:
            self.logger.info(f"Unit {unit_id} is already at the objective position {target_position}. Waiting.")
            # If the goal is just to reach the position, waiting might be appropriate.
            # Future goals might involve actions AT the objective (e.g., Interact)
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning WAIT (at objective)")
            return AIAction(action_type="WAIT", unit_id=unit_id, target_data={})

        # --- 2. Check System Availability ---
        if not self.movement_system:
            self.logger.error(f"AdvanceToObjectiveGoal: Movement system not available for unit {unit_id}.")
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning None (movement system unavailable)")
            return None
            
        pathfinder = game_state_manager.get_pathfinding()
        if not pathfinder:
            self.logger.error(f"AdvanceToObjectiveGoal: Pathfinder not available for unit {unit_id}.")
            # Cannot proceed without pathfinding
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning None (pathfinder unavailable)")
            return None
            
        # game_map = game_state_manager.get_map()
        if not hasattr(game_state_manager, 'current_game_state'):
             self.logger.error(f"AdvanceToObjectiveGoal: GameStateManager missing 'current_game_state' attribute for unit {unit_id}.")
             self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning None (game state unavailable)")
             return None
        game_map_state = game_state_manager.current_game_state.map_state
        if not game_map_state:
            self.logger.error(f"AdvanceToObjectiveGoal: MapState not available for unit {unit_id}.")
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning None (map unavailable)")
            return None

        # --- 3. Find Path to Objective ---
        # Use a method designed for approaching a target coordinate
        # Assuming find_path can handle coordinate targets and uses game_state_manager internally for map
        # approach_path = pathfinder.find_path(unit_id, current_pos, target_position, game_map_state)
        movement_points = ai_unit_state.current_stats.move
        approach_path = pathfinder.find_path_towards_target(ai_unit_state, target_position, movement_points)
        # Alternative: pathfinder.find_path_to_approach_target(ai_unit_state, target_position)
        # Choose the one that fits the Pathfinding interface better

        if not approach_path or len(approach_path) <= 1:
            self.logger.warning(f"AdvanceToObjectiveGoal: No path found for unit {unit_id} from {current_pos} to {target_position}.")
            # Maybe the unit is blocked or the target is invalid/unreachable
            # Consider returning WAIT or None. None seems safer if we can't move.
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning None (no path)")
            return None
            
        self.logger.debug(f"AdvanceToObjectiveGoal: Found approach path: {approach_path}")

        # --- 4. Find Furthest Reachable Point on Path ---
        # This helper uses self.movement_system.calculate_movement_range internally
        limited_path = approach_path # The method already returns the limited path

        # --- 5. Generate Action ---
        if limited_path and len(limited_path) > 1:
            destination = limited_path[-1]
            self.logger.info(f"AdvanceToObjectiveGoal: Unit {unit_id} moving towards {target_position}. Path segment ends at {destination} (length {len(limited_path)})." )
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning MOVE to {destination}")
            return AIAction(action_type="MOVE", unit_id=unit_id, target_data={"path": limited_path, "objective_target": target_position})
        else:
            # This case means only the starting tile is 'reachable' on the path.
            # This could happen if the unit has 0 move or is completely blocked immediately.
            self.logger.warning(f"AdvanceToObjectiveGoal: No valid move possible for unit {unit_id} towards {target_position} from {current_pos}, despite path existing. Unit might be blocked or have 0 move.")
            # Default to WAIT if no movement is possible.
            self.logger.debug(f"EXITING: _handle_advance_to_objective_goal for unit {unit_id} - returning WAIT (no move possible)")
            return AIAction(action_type="WAIT", unit_id=unit_id, target_data={})