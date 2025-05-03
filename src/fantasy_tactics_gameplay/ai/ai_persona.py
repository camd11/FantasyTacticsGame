"""
AI Persona Module

This module defines the AIPersona class, which represents the behavioral characteristics
of different AI unit types through weighted preferences for different goals and considerations.

Personas are loaded from configuration files and provide weights that influence both
the Strategic and Tactical phases of AI decision-making, creating more distinct and
believable behavior patterns.
"""

import os
import yaml
from typing import Dict, List, Any, Optional


class AIPersona:
    """
    Represents the behavioral characteristics of an AI unit.
    
    AI personas define how different unit types behave through weighted preferences
    for different goals and considerations. They influence both the Strategic and
    Tactical phases of AI decision-making.
    
    Personas are loaded from configuration files and can be accessed by name.
    """
    
    # Class variable to store loaded personas
    _personas: Dict[str, 'AIPersona'] = {}
    _personas_loaded = False
    
    def __init__(self, name: str, goal_weights: Dict[str, float], 
                 strategic_weights: Dict[str, float], tactical_weights: Dict[str, float]):
        """
        Initialize an AIPersona.
        
        Args:
            name: The name/identifier of the persona
            goal_weights: Weights for different goal types
            strategic_weights: Weights for strategic considerations
            tactical_weights: Weights for tactical considerations
        """
        self.name = name
        self.goal_weights = goal_weights
        self.strategic_weights = strategic_weights
        self.tactical_weights = tactical_weights
    
    @classmethod
    def load_personas(cls, file_path: str = None) -> None:
        """
        Load all personas from the configuration file.
        
        Args:
            file_path: Path to the persona configuration file. If None, uses the default path.
        """
        if cls._personas_loaded:
            return
            
        if file_path is None:
            # Default path is in the data directory
            file_path = os.path.join('data', 'ai_personas.yaml')
            
        try:
            with open(file_path, 'r') as file:
                persona_data = yaml.safe_load(file)
                
            for persona_name, persona_config in persona_data.items():
                cls._personas[persona_name] = AIPersona(
                    name=persona_name,
                    goal_weights=persona_config.get('goal_weights', {}),
                    strategic_weights=persona_config.get('strategic_weights', {}),
                    tactical_weights=persona_config.get('tactical_weights', {})
                )
                
            cls._personas_loaded = True
        except FileNotFoundError:
            print(f"Warning: AI persona configuration file not found at {file_path}")
            # Create default personas
            cls._create_default_personas()
            cls._personas_loaded = True
    
    @classmethod
    def _create_default_personas(cls) -> None:
        """
        Create default personas if the configuration file is not found.
        
        This ensures the system can still function without a configuration file.
        """
        # Aggressor persona
        cls._personas['AGGRESSOR'] = AIPersona(
            name='AGGRESSOR',
            goal_weights={
                'ATTACK_UNIT': 1.0,
                'ADVANCE_TO_OBJECTIVE': 0.7,
                'SECURE_POSITION': 0.4,
                'RETREAT_AND_RECOVER': 0.3,
                'HEAL_UNIT': 0.2
            },
            strategic_weights={
                'ThreatLevel': 1.0,
                'KillOpportunity': 0.9,
                'ObjectiveProgress': 0.7,
                'TerrainAdvantage': 0.5,
                'AlliedSupport': 0.3
            },
            tactical_weights={
                'DamageDealt': 1.0,
                'KillPotential': 0.9,
                'SelfPreservation': 0.6,
                'TerrainDefense': 0.5,
                'AlliedFormation': 0.4
            }
        )
        
        # Defender persona
        cls._personas['DEFENDER'] = AIPersona(
            name='DEFENDER',
            goal_weights={
                'SECURE_POSITION': 1.0,
                'ATTACK_UNIT': 0.7,
                'HEAL_UNIT': 0.6,
                'RETREAT_AND_RECOVER': 0.5,
                'ADVANCE_TO_OBJECTIVE': 0.3
            },
            strategic_weights={
                'TerrainAdvantage': 1.0,
                'AlliedSupport': 0.8,
                'ThreatLevel': 0.7,
                'KillOpportunity': 0.6,
                'ObjectiveProgress': 0.3
            },
            tactical_weights={
                'TerrainDefense': 1.0,
                'SelfPreservation': 0.9,
                'AlliedFormation': 0.8,
                'DamageDealt': 0.7,
                'KillPotential': 0.6
            }
        )
        
        # Support persona
        cls._personas['SUPPORT'] = AIPersona(
            name='SUPPORT',
            goal_weights={
                'HEAL_UNIT': 1.0,
                'RETREAT_AND_RECOVER': 0.8,
                'SECURE_POSITION': 0.7,
                'ATTACK_UNIT': 0.3,
                'ADVANCE_TO_OBJECTIVE': 0.2
            },
            strategic_weights={
                'AlliedSupport': 1.0,
                'TerrainAdvantage': 0.7,
                'SelfPreservation': 0.9,
                'ThreatLevel': 0.5,
                'ObjectiveProgress': 0.2
            },
            tactical_weights={
                'HealAllyAmount': 1.0,
                'HealAllyPriority': 0.9,
                'SelfPreservation': 0.8,
                'TerrainDefense': 0.7,
                'AlliedFormation': 0.6
            }
        )
        
        # Objective-Focused persona
        cls._personas['OBJECTIVE-FOCUSED'] = AIPersona(
            name='OBJECTIVE-FOCUSED',
            goal_weights={
                'ADVANCE_TO_OBJECTIVE': 1.0,
                'ATTACK_UNIT': 0.7,
                'SECURE_POSITION': 0.6,
                'RETREAT_AND_RECOVER': 0.4,
                'HEAL_UNIT': 0.3
            },
            strategic_weights={
                'ObjectiveProgress': 1.0,
                'ThreatLevel': 0.7,
                'KillOpportunity': 0.6,
                'TerrainAdvantage': 0.5,
                'AlliedSupport': 0.3
            },
            tactical_weights={
                'ObjectiveProximity': 1.0,
                'DamageDealt': 0.7,
                'KillPotential': 0.6,
                'SelfPreservation': 0.5,
                'TerrainDefense': 0.4
            }
        )
        
        # Balanced persona (default)
        cls._personas['BALANCED'] = AIPersona(
            name='BALANCED',
            goal_weights={
                'ATTACK_UNIT': 0.8,
                'ADVANCE_TO_OBJECTIVE': 0.8,
                'SECURE_POSITION': 0.7,
                'RETREAT_AND_RECOVER': 0.6,
                'HEAL_UNIT': 0.6
            },
            strategic_weights={
                'ThreatLevel': 0.8,
                'KillOpportunity': 0.8,
                'ObjectiveProgress': 0.8,
                'TerrainAdvantage': 0.7,
                'AlliedSupport': 0.7
            },
            tactical_weights={
                'DamageDealt': 0.8,
                'KillPotential': 0.8,
                'SelfPreservation': 0.8,
                'TerrainDefense': 0.7,
                'AlliedFormation': 0.7
            }
        )
    
    @classmethod
    def get_persona(cls, persona_name: str) -> 'AIPersona':
        """
        Get a persona by name.
        
        Args:
            persona_name: The name of the persona to get
            
        Returns:
            AIPersona: The requested persona, or a default persona if not found
        """
        if not cls._personas_loaded:
            cls.load_personas()
            
        # If the persona doesn't exist, return the BALANCED persona as default
        return cls._personas.get(persona_name, cls._personas.get('BALANCED'))
    
    def get_goal_weight(self, goal_type: str) -> float:
        """
        Get the weight for a specific goal type.
        
        Args:
            goal_type: The type of goal to get the weight for
            
        Returns:
            float: The weight for the goal type, or 0.5 if not defined
        """
        return self.goal_weights.get(goal_type, 0.5)
    
    def get_strategic_weight(self, consideration: str) -> float:
        """
        Get the weight for a specific strategic consideration.
        
        Args:
            consideration: The strategic consideration to get the weight for
            
        Returns:
            float: The weight for the consideration, or 0.5 if not defined
        """
        return self.strategic_weights.get(consideration, 0.5)
    
    def get_tactical_weight(self, consideration: str) -> float:
        """
        Get the weight for a specific tactical consideration.
        
        Args:
            consideration: The tactical consideration to get the weight for
            
        Returns:
            float: The weight for the consideration, or 0.5 if not defined
        """
        return self.tactical_weights.get(consideration, 0.5)
    
    def get_scorers_for_goal(self, goal_type: str) -> List[Dict[str, Any]]:
        """
        Get the tactical scorers for a specific goal type.
        
        This method returns a list of scorer configurations that include
        the appropriate weights for this persona.
        
        Args:
            goal_type: The type of goal to get scorers for
            
        Returns:
            List[Dict[str, Any]]: A list of scorer configurations
        """
        # This is a simplified implementation
        # In a real implementation, this would return more complex scorer configurations
        if goal_type == "ATTACK_UNIT":
            return [
                {"name": "DamageDealt", "weight": self.get_tactical_weight("DamageDealt")},
                {"name": "KillPotential", "weight": self.get_tactical_weight("KillPotential")},
                {"name": "SelfPreservation", "weight": self.get_tactical_weight("SelfPreservation")}
            ]
        elif goal_type == "HEAL_UNIT":
            return [
                {"name": "HealAllyAmount", "weight": self.get_tactical_weight("HealAllyAmount")},
                {"name": "HealAllyPriority", "weight": self.get_tactical_weight("HealAllyPriority")},
                {"name": "SelfPreservation", "weight": self.get_tactical_weight("SelfPreservation")}
            ]
        elif goal_type == "MOVE_TO_SAFETY":
            return [
                {"name": "SelfPreservation", "weight": self.get_tactical_weight("SelfPreservation")},
                {"name": "TerrainDefense", "weight": self.get_tactical_weight("TerrainDefense")},
                {"name": "AlliedFormation", "weight": self.get_tactical_weight("AlliedFormation")}
            ]
        elif goal_type == "SEIZE_TILE":
            return [
                {"name": "ObjectiveProximity", "weight": self.get_tactical_weight("ObjectiveProximity")},
                {"name": "SelfPreservation", "weight": self.get_tactical_weight("SelfPreservation")},
                {"name": "TerrainDefense", "weight": self.get_tactical_weight("TerrainDefense")}
            ]
        else:
            # Default scorers for unknown goal types
            return [
                {"name": "SelfPreservation", "weight": self.get_tactical_weight("SelfPreservation")},
                {"name": "DamageDealt", "weight": self.get_tactical_weight("DamageDealt")},
                {"name": "TerrainDefense", "weight": self.get_tactical_weight("TerrainDefense")}
            ]