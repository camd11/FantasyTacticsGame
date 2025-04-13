"""
Convoy System Functions

This module provides the core functions for the convoy system, including
checking access, depositing and withdrawing items, and checking if the convoy is full.
"""

from typing import Optional, Tuple

# Constants
MAX_CONVOY_SIZE = 500  # Default value

def is_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int], map_data=None) -> bool:
    """
    Check if two positions are adjacent.
    
    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)
        map_data: Map data (optional, not used in this implementation)
        
    Returns:
        True if the positions are adjacent, False otherwise
    """
    # Calculate Manhattan distance
    dx = abs(pos1[0] - pos2[0])
    dy = abs(pos1[1] - pos2[1])
    return (dx + dy) == 1

def can_access_convoy(unit, game_state) -> bool:
    """
    Check if a unit can access the convoy.
    
    Args:
        unit: Unit trying to access the convoy
        game_state: Current game state
        
    Returns:
        True if the unit can access the convoy, False otherwise
    """
    # Check 1: Preparation Phase
    if hasattr(game_state, 'current_phase') and game_state.current_phase.__class__.__name__ == 'GamePhaseEnum':
        if game_state.current_phase.name == 'PREPARATION':
            return True
    
    # Check 2: Battle Phase Conditions
    if hasattr(game_state, 'current_phase') and game_state.current_phase.__class__.__name__ == 'GamePhaseEnum':
        if game_state.current_phase.name == 'BATTLE':
            # Condition A: Adjacency to Lord
            lord_unit = game_state.get_player_lord()
            if lord_unit and is_adjacent(unit.position, lord_unit.position, game_state):
                return True
            
            # Condition B: Adjacency to Supply Units
            supply_units = game_state.get_units_with_trait('Supply')
            for supply_unit in supply_units:
                if is_adjacent(unit.position, supply_unit.position, game_state):
                    return True
            
            # Condition C: Unit has 'Supply' command
            if hasattr(unit, 'has_command') and unit.has_command('Supply'):
                return True
    
    # Default: No access
    return False

def deposit_item(unit, item_index_in_unit_inventory: int, game_state) -> bool:
    """
    Deposit an item from a unit's inventory to the convoy.
    
    Args:
        unit: Unit depositing the item
        item_index_in_unit_inventory: Index of the item in the unit's inventory
        game_state: Current game state
        
    Returns:
        True if the deposit was successful, False otherwise
    """
    # 1. Check Access
    if not can_access_convoy(unit, game_state):
        return False
    
    # 2. Validate Item Selection
    if item_index_in_unit_inventory < 0 or item_index_in_unit_inventory >= len(unit.inventory):
        return False
    
    item_to_deposit = unit.inventory[item_index_in_unit_inventory]
    
    # 3. Check Restrictions
    if hasattr(unit, 'is_item_equipped') and unit.is_item_equipped(item_to_deposit):
        return False
    
    if hasattr(item_to_deposit, 'is_unique') and item_to_deposit.is_unique:
        return False
    
    # 4. Check Convoy Limit
    if convoy_is_full(game_state.player_convoy):
        return False
    
    # 5. Perform Transfer
    removed_item = unit.inventory.pop(item_index_in_unit_inventory)
    game_state.player_convoy.append(removed_item)
    
    # 6. Consume action if in battle phase
    if hasattr(game_state, 'current_phase') and game_state.current_phase.__class__.__name__ == 'GamePhaseEnum':
        if game_state.current_phase.name == 'BATTLE' and hasattr(game_state, 'action_system'):
            game_state.action_system.consume_action(unit)
    
    return True

def withdraw_item(unit, item_index_in_convoy: int, game_state) -> bool:
    """
    Withdraw an item from the convoy to a unit's inventory.
    
    Args:
        unit: Unit withdrawing the item
        item_index_in_convoy: Index of the item in the convoy
        game_state: Current game state
        
    Returns:
        True if the withdrawal was successful, False otherwise
    """
    # 1. Check Access
    if not can_access_convoy(unit, game_state):
        return False
    
    # 2. Validate Item Selection
    if item_index_in_convoy < 0 or item_index_in_convoy >= len(game_state.player_convoy):
        return False
    
    # 3. Check Unit Inventory Space
    if hasattr(unit.inventory, 'is_full') and unit.inventory.is_full():
        return False
    
    # 4. Perform Transfer
    # Remove from convoy first
    removed_item = game_state.player_convoy.pop(item_index_in_convoy)
    
    # Try adding to unit
    if hasattr(unit.inventory, 'add_item'):
        was_added = unit.inventory.add_item(removed_item)
    else:
        # Fallback for test cases
        unit.inventory.append(removed_item)
        was_added = True
    
    if was_added:
        # 5. Consume action if in battle phase
        if hasattr(game_state, 'current_phase') and game_state.current_phase.__class__.__name__ == 'GamePhaseEnum':
            if game_state.current_phase.name == 'BATTLE' and hasattr(game_state, 'action_system'):
                game_state.action_system.consume_action(unit)
        
        return True
    else:
        # Critical error: Failed to add to unit after removing from convoy. Attempt rollback.
        game_state.player_convoy.insert(item_index_in_convoy, removed_item)
        return False

def convoy_is_full(convoy) -> bool:
    """
    Check if the convoy is full.
    
    Args:
        convoy: The convoy to check
        
    Returns:
        True if the convoy is full, False otherwise
    """
    # Check for unlimited capacity
    if MAX_CONVOY_SIZE < 0:
        return False
    
    return len(convoy) >= MAX_CONVOY_SIZE