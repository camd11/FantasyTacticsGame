"""
Utility Functions Module

This module provides utility functions used throughout the game engine.
"""

from typing import Tuple

def are_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """
    Check if two positions are adjacent (Manhattan distance = 1).
    
    Args:
        pos1: First position as (x, y)
        pos2: Second position as (x, y)
        
    Returns:
        True if positions are adjacent, False otherwise
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1