import logging
import random
from typing import TYPE_CHECKING, Optional, Tuple, List, Set

from src.entities.unit import Unit
from src.game_state.ai_controller import AIController
from src.game_state.ai_state import Goal, ObjectiveType, GoalStatus
from src.game_state.game_state_manager import GameStateManager
from src.systems.combat_system import CombatSystem
from src.systems.healing_system import HealingSystem
from src.systems.movement_system import MovementSystem
from src.systems.pathfinding_system import PathfindingSystem
from src.utils.helpers import find_closest_target
from src.utils.prioritization import Prioritization

if TYPE_CHECKING:
    from src.entities.map_tile import MapTile

logger = logging.getLogger(__name__)


class TacticalExecutor:
    """
    Executes tactical decisions based on the current goal of an AI-controlled unit.
    Handles movement, attacks, healing, and other tactical actions.
    """
    def __init__(self,
                 # Removed optional systems from here
                 prioritization: Optional[Prioritization] = None
                 ):
        """
        Initializes the TacticalExecutor.
        Systems will be injected via the initialize method.
        """
        self.prioritization = prioritization if prioritization is not None else Prioritization()
        self.movement_system: Optional[MovementSystem] = None
        self.combat_system: Optional[CombatSystem] = None
        self.healing_system: Optional[HealingSystem] = None
        self.game_state_manager: Optional[GameStateManager] = None
        # self.pathfinding_system: Optional[PathfindingSystem] = None # Assuming pathfinding is accessed via movement_system or game_state_manager

    def initialize(self,
                   movement_system: MovementSystem,
                   combat_system: CombatSystem,
                   healing_system: HealingSystem,
                   game_state_manager: GameStateManager):
        """
        Injects necessary system dependencies after they have been initialized.
        """
        self.movement_system = movement_system
        self.combat_system = combat_system
        self.healing_system = healing_system
        self.game_state_manager = game_state_manager
        # self.pathfinding_system = game_state_manager.pathfinding_system # Example if needed directly
        logger.info("TacticalExecutor initialized with systems.")


    def execute_goal(self, unit: Unit, goal: Goal, ai_controller: 'AIController') -> GoalStatus:
        # Ensure required systems are initialized (excluding optional ones like healing for now)
        if not all([self.movement_system, self.combat_system, self.game_state_manager]):
            logger.error("TacticalExecutor core systems not initialized (Movement, Combat, GSM). Call initialize() first.")
            return GoalStatus.FAILED

        # Check for healing system only if the goal requires it (Example)
        # if goal.objective_type == ObjectiveType.HEAL and not self.healing_system:
        #    logger.error(f"Healing goal received but HealingSystem not available for unit {unit.unit_id}.")
        #    return GoalStatus.FAILED

        logger.debug(f"Executing goal for unit {unit.unit_id} ({unit.name}): {goal}")

        objective_type = goal.objective_type

        # Basic validation
        if not unit or not goal or not goal.target:
            logger.warning(f"Invalid parameters for execute_goal for unit {unit.unit_id if unit else 'None'}. Goal: {goal}")
            return GoalStatus.FAILED

        # Ensure target is valid based on objective
        if isinstance(goal.target, tuple): # Target is a position
            target_pos = goal.target
            target_unit = None
            if not self.game_state_manager or not self.game_state_manager.map_system: # Ensure GSM and MapSystem exist
                 logger.error("GameStateManager or MapSystem not available for position validation.")
                 return GoalStatus.FAILED
            if not self.game_state_manager.map_system.is_valid_and_passable(target_pos):
                logger.warning(f"Target position {target_pos} is invalid or impassable for unit {unit.unit_id}.")
                # TODO: Should AI re-evaluate or just fail?
                return GoalStatus.FAILED # Or IN_PROGRESS if AI should find a new target/path
        elif isinstance(goal.target, Unit): # Target is a unit
            target_unit = goal.target
            target_pos = target_unit.position
            if not target_unit.is_alive():
                logger.info(f"Target unit {target_unit.unit_id} is already dead. Goal cannot be completed.")
                # ai_controller.complete_goal(unit, goal) # Mark as completed maybe?
                return GoalStatus.COMPLETED # Or FAILED? Depending on desired AI behavior
        else:
            logger.error(f"Invalid target type {type(goal.target)} for goal: {goal}")
            return GoalStatus.FAILED

        # --- Action Execution based on Objective Type ---
        current_pos = unit.position

        if objective_type == ObjectiveType.MOVE_TO:
            # Use MovementSystem to handle movement
            if not self.movement_system:
                 logger.error("MovementSystem not available for MOVE_TO goal.") # Redundant check, but safe
                 return GoalStatus.FAILED
                 
            status = self.movement_system.move_unit_towards(unit, target_pos)
            # TODO: Refine status check based on MovementSystem return values
            if status == "completed":
                 logger.debug(f"Unit {unit.unit_id} reached target {target_pos}.")
                 return GoalStatus.COMPLETED
            elif status == "in_progress":
                 logger.debug(f"Unit {unit.unit_id} moving towards {target_pos}.")
                 return GoalStatus.IN_PROGRESS
            else: # Failed or blocked
                 logger.warning(f"Unit {unit.unit_id} failed to move towards {target_pos}.")
                 # TODO: Consider pathfinding failure, temporary blockage etc.
                 # Maybe return IN_PROGRESS if blockage is temporary?
                 return GoalStatus.FAILED # Simple failure for now

        elif objective_type == ObjectiveType.ATTACK:
            if not target_unit:
                logger.warning(f"Attack goal for unit {unit.unit_id} has no valid target unit.")
                return GoalStatus.FAILED
            if not self.combat_system:
                 logger.error("CombatSystem not available for ATTACK goal.")
                 return GoalStatus.FAILED

            # 1. Check range
            in_range = self.combat_system.is_unit_in_attack_range(unit, target_unit)

            if in_range:
                # 2. Execute attack
                logger.debug(f"Unit {unit.unit_id} attacking target {target_unit.unit_id} at {target_pos}.")
                # Assuming combat system handles AP deduction, damage, etc.
                attack_successful = self.combat_system.execute_attack(unit, target_unit)
                if attack_successful:
                    logger.info(f"Unit {unit.unit_id} successfully attacked {target_unit.unit_id}.")
                    # Check if target died? Maybe GSM handles this via events.
                    # Goal might be completed, or AI might want to attack again if possible.
                    # For now, assume one attack completes the immediate goal step.
                    return GoalStatus.COMPLETED
                else:
                    logger.warning(f"Unit {unit.unit_id} failed to attack {target_unit.unit_id}. Attack prevented or missed?")
                    # Maybe AP was insufficient, or target dodged, etc.
                    return GoalStatus.FAILED
            else:
                # 3. Move towards target if not in range
                logger.debug(f"Unit {unit.unit_id} needs to move closer to attack {target_unit.unit_id}.")
                if not self.movement_system:
                     logger.error("MovementSystem not available to move towards attack target.")
                     return GoalStatus.FAILED
                     
                # Find best position to attack from (adjacent or within range)
                # This requires pathfinding and movement calculation
                attack_positions = self.combat_system.get_valid_attack_positions(unit, target_unit.position)
                if not attack_positions:
                    logger.warning(f"No valid positions for unit {unit.unit_id} to attack target {target_unit.unit_id}.")
                    return GoalStatus.FAILED # Cannot reach target
                    
                # Use MovementSystem to find path and move to closest valid attack position
                move_status = self.movement_system.move_unit_towards_closest(unit, attack_positions)

                if move_status == "completed" or move_status == "in_progress":
                    # Even if move completed, we are still IN_PROGRESS towards the ATTACK goal
                    # The attack itself will happen next turn/evaluation
                    logger.debug(f"Unit {unit.unit_id} moved towards attack position. Status: {move_status}")
                    return GoalStatus.IN_PROGRESS
                else: # Failed move
                    logger.warning(f"Unit {unit.unit_id} failed to move towards attack position for target {target_unit.unit_id}.")
                    return GoalStatus.FAILED

        elif objective_type == ObjectiveType.HEAL:
            # Placeholder for healing logic
            if not target_unit:
                logger.warning(f"Heal goal for unit {unit.unit_id} has no valid target unit.")
                return GoalStatus.FAILED
            if not self.healing_system:
                logger.error(f"HealingSystem not available for HEAL goal for unit {unit.unit_id}.")
                return GoalStatus.FAILED
            
            # Similar logic to attack: check range, move if needed, then heal
            logger.warning("HEAL objective execution not fully implemented yet.")
            # Example:
            # if self.healing_system.is_in_heal_range(unit, target_unit):
            #     success = self.healing_system.execute_heal(unit, target_unit)
            #     return GoalStatus.COMPLETED if success else GoalStatus.FAILED
            # else:
            #     heal_positions = self.healing_system.get_valid_heal_positions(unit, target_unit.position)
            #     move_status = self.movement_system.move_unit_towards_closest(unit, heal_positions)
            #     return GoalStatus.IN_PROGRESS if move_status in ["completed", "in_progress"] else GoalStatus.FAILED
            return GoalStatus.FAILED # Not implemented
            
        elif objective_type == ObjectiveType.DEFEND:
            # Placeholder for defend logic (e.g., move to defend point, adopt defensive stance)
            if isinstance(goal.target, tuple):
                defend_pos = goal.target
                logger.warning(f"DEFEND objective execution at {defend_pos} not fully implemented.")
                # Example: Move to position, maybe use a skill?
                # move_status = self.movement_system.move_unit_towards(unit, defend_pos)
                # if move_status == "completed": return GoalStatus.COMPLETED # Or maybe IN_PROGRESS if defending is ongoing
                # elif move_status == "in_progress": return GoalStatus.IN_PROGRESS
                # else: return GoalStatus.FAILED
            else:
                 logger.warning(f"DEFEND objective requires a position target, got {type(goal.target)}.")
            return GoalStatus.FAILED # Not implemented
            
        elif objective_type == ObjectiveType.EXPLORE:
            # Placeholder for exploration logic (e.g., move towards unexplored area)
            if isinstance(goal.target, tuple):
                explore_pos = goal.target
                logger.warning(f"EXPLORE objective execution towards {explore_pos} not fully implemented.")
                # Example: Move towards target position
                # move_status = self.movement_system.move_unit_towards(unit, explore_pos)
                # return GoalStatus.IN_PROGRESS if move_status in ["completed", "in_progress"] else GoalStatus.FAILED
            else:
                 logger.warning(f"EXPLORE objective requires a position target, got {type(goal.target)}.")
            return GoalStatus.FAILED # Not implemented

        # --- Default case if objective type is unknown --- 
        else:
            logger.error(f"Unknown objective type {objective_type} for unit {unit.unit_id}. Goal: {goal}")
            return GoalStatus.FAILED 