"""
Test script to demonstrate the updated rescue mechanics.

This script showcases the Constitution mechanics for rescue operations,
including the following rules:
- Rescuer Con must be > Target Con
- Mounted units and ballistas are considered to have 20 Con for rescue purposes
- Movement penalty applies if Carried Con > Carrier Con / 2
  (using actual Con, not effective Con for mounted units)
"""

from dataclasses import dataclass
from typing import Tuple, Optional, List

@dataclass
class Unit:
    """Simple Unit class for demonstration purposes."""
    name: str
    con: int
    is_mounted: bool = False
    is_dismounted: bool = False
    unit_type: str = "infantry"
    
    def effective_con(self) -> int:
        """Calculate unit's effective constitution for rescue operations."""
        # Mounted units that aren't dismounted and ballistas have effective Con of 20
        # This is only used for determining ability to rescue, not for movement penalties
        if (self.is_mounted and not self.is_dismounted) or self.unit_type == "ballista":
            return 20
        return self.con


def can_rescue(rescuer: Unit, target: Unit) -> bool:
    """
    Check if a rescuer can rescue a target.
    
    Args:
        rescuer: The rescuing unit
        target: The unit to be rescued
        
    Returns:
        True if the rescue is possible, False otherwise
    """
    # Rule: Rescuer's effective Con > Target's Con
    # Mounted units use their effective Con of 20, not their actual Con
    return rescuer.effective_con() > target.con


def get_movement_penalty(carrier: Unit, carried: Unit) -> bool:
    """
    Check if carrying the unit results in a movement penalty.
    
    Args:
        carrier: The carrying unit
        carried: The carried unit
        
    Returns:
        True if movement should be halved, False otherwise
    """
    # Rule: Movement is halved if Carried Con > Carrier's ACTUAL Con / 2
    # Note: For movement penalties, we use the ACTUAL Con, not the effective Con
    return carried.con > (carrier.con / 2)


def print_rescue_scenario(rescuer: Unit, target: Unit):
    """Print details of a rescue scenario."""
    can_rescue_result = can_rescue(rescuer, target)
    movement_penalty = get_movement_penalty(rescuer, target) if can_rescue_result else "N/A"
    
    print(f"Rescuer: {rescuer.name} (Con: {rescuer.con}, Mounted: {rescuer.is_mounted})")
    print(f"Target: {target.name} (Con: {target.con})")
    print(f"Effective rescuer Con: {rescuer.effective_con()}")
    print(f"Can rescue: {can_rescue_result}")
    
    if can_rescue_result:
        print(f"Movement penalty: {movement_penalty}")
        print(f"Threshold for movement penalty: {rescuer.con / 2:.1f} (half of actual Con)")
    
    print("-" * 50)


def main():
    """Run rescue mechanics demonstration."""
    print("\n=== RESCUE MECHANICS DEMONSTRATION ===\n")
    
    # Create some units for testing
    infantry = Unit("Infantry Soldier", con=8)
    knight = Unit("Knight", con=12)
    pegasus = Unit("Pegasus Knight", con=6, is_mounted=True)
    paladin = Unit("Paladin", con=10, is_mounted=True)
    general = Unit("Armored General", con=14)
    mage = Unit("Mage", con=5)
    dismounted_cavalier = Unit("Dismounted Cavalier", con=9, is_mounted=True, is_dismounted=True)
    ballista = Unit("Ballista Operator", con=8, unit_type="ballista")
    
    # Test various rescue scenarios
    print("SCENARIO 1: Infantry rescuing Mage")
    print_rescue_scenario(infantry, mage)
    
    print("SCENARIO 2: Infantry trying to rescue Knight")
    print_rescue_scenario(infantry, knight)
    
    print("SCENARIO 3: Mounted Paladin rescuing Knight")
    print_rescue_scenario(paladin, knight)
    
    print("SCENARIO 4: Pegasus Knight rescuing Infantry")
    print_rescue_scenario(pegasus, infantry)
    
    print("SCENARIO 5: Dismounted Cavalier trying to rescue General")
    print_rescue_scenario(dismounted_cavalier, general)
    
    print("SCENARIO 6: Knight rescuing Mage")
    print_rescue_scenario(knight, mage)
    
    print("SCENARIO 7: Paladin rescuing General")
    print_rescue_scenario(paladin, general)
    
    print("SCENARIO 8: Ballista Operator rescuing Knight")
    print_rescue_scenario(ballista, knight)


if __name__ == "__main__":
    main() 