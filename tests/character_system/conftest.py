import pytest
from unittest.mock import MagicMock

from src.character_system.character import Character
from src.character_system.game_class import GameClass # Added import

@pytest.fixture
def mock_character():
    """
    Provides a basic, usable mock of the Character class.
    """
    mock = MagicMock(spec=Character)
    mock.character_id = "test_char_001"
    mock.name = "Mock Character"
    mock.portrait = None  # Placeholder for PortraitID
    mock.initial_class_id = "TestClass" # Placeholder for ClassID
    mock.level = 1
    mock.experience_points = 0

    mock.base_hp = 20
    mock.base_strength = 5
    mock.base_magic = 2
    mock.base_skill = 4
    mock.base_speed = 6
    mock.base_luck = 3
    mock.base_defense = 4
    mock.base_constitution = 5
    mock.base_movement = 5

    mock.growth_hp = 50
    mock.growth_strength = 30
    mock.growth_magic = 10
    mock.growth_skill = 40
    mock.growth_speed = 45
    mock.growth_luck = 25
    mock.growth_defense = 20
    mock.growth_constitution = 10

    mock.innate_skills = [] # Placeholder for List[SkillID]
    mock.initial_inventory = [] # Placeholder for List[ItemID]
    mock.character_support_data = None # Placeholder for SupportData

    # Mock methods if they are called by UnitInstance initialization or basic tests
    mock.get_current_stats = MagicMock(return_value={
        "MaxHP": 20, "CurrentHP": 20,
        "Strength": 5, "Magic": 2, "Skill": 4, "Speed": 6,
        "Luck": 3, "Defense": 4, "Constitution": 5, "Movement": 5,
        "AttackPower": 0, "MagicAttackPower": 0, "HitRate": 0,
        "AvoidRate": 0, "CriticalRate": 0, "AttackSpeed": 0
    }) # Placeholder for UnitStats
    mock.level_up = MagicMock()

    return mock

@pytest.fixture
def mock_game_class():
    """
    Provides a basic, usable mock of the GameClass.
    """
    mock = MagicMock(spec=GameClass)
    mock.id = "TestClass"
    mock.name = "Test Class"
    
    mock.base_hp = 20
    mock.base_strength = 5
    mock.base_magic = 2
    mock.base_skill = 4
    mock.base_speed = 6
    mock.base_luck = 3
    mock.base_defense = 4
    mock.base_constitution = 5
    mock.base_movement = 5

    mock.max_hp = 60
    mock.max_strength = 20
    mock.max_magic = 20
    mock.max_skill = 20
    mock.max_speed = 20
    mock.max_luck = 30
    mock.max_defense = 20
    mock.max_constitution = 20
    mock.max_movement = 10

    mock.growth_hp = 10
    mock.growth_strength = 5
    mock.growth_magic = 0
    mock.growth_skill = 5
    mock.growth_speed = 5
    mock.growth_luck = 0
    mock.growth_defense = 5
    mock.growth_constitution = 0
    
    mock.class_skills = []
    mock.movement_type = "Infantry" # Placeholder for MovementTypeID
    mock.weapon_ranks = [] # Placeholder for List[WeaponRankEntry]
    mock.promotes_to_class_id = None
    mock.promotion_item = None
    mock.dismounted_class_id = None
    mock.is_mounted = False
    
    return mock