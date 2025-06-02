import pytest
from src.character_system.character import Character, GameClass, UnitStats

# Define placeholder types if they are not directly part of Character, GameClass, UnitStats
# For simplicity, we'll use basic types or strings where appropriate for these tests.
PortraitID = str
ClassID = str
SkillID = str
ItemID = str
SupportData = None # Or a more complex mock if needed for specific tests

# Sample data for tests
DEFAULT_BASE_STATS = {
    "HP": 20, "Strength": 5, "Magic": 0, "Skill": 5, "Speed": 6,
    "Luck": 7, "Defense": 3, "Constitution": 5, "Movement": 5
}
DEFAULT_GROWTH_RATES = {
    "HP": 70, "Strength": 35, "Magic": 5, "Skill": 30, "Speed": 35,
    "Luck": 25, "Defense": 20, "Constitution": 10, "Movement": 0
}
DEFAULT_INNATE_SKILLS: list[SkillID] = []
DEFAULT_INITIAL_INVENTORY: list[ItemID] = []

# Sample GameClass data
LORD_CLASS_BASE_STATS = {
    "HP": 2, "Strength": 1, "Magic": 0, "Skill": 1, "Speed": 1,
    "Luck": 0, "Defense": 1, "Constitution": 1, "Movement": 1
}
LORD_CLASS_MAX_STATS = {
    "HP": 60, "Strength": 20, "Magic": 20, "Skill": 20, "Speed": 20,
    "Luck": 30, "Defense": 20, "Constitution": 20, "Movement": 12
}
LORD_CLASS_GROWTHS = { # Class growth bonuses
    "HP": 10, "Strength": 5, "Magic": 0, "Skill": 5, "Speed": 5,
    "Luck": 0, "Defense": 5, "Constitution": 0, "Movement": 0
}

MAGE_CLASS_BASE_STATS = {
    "HP": 0, "Strength": 0, "Magic": 3, "Skill": 1, "Speed": 2,
    "Luck": 0, "Defense": 0, "Constitution": 0, "Movement": 0
}
MAGE_CLASS_MAX_STATS = {
    "HP": 50, "Strength": 15, "Magic": 25, "Skill": 20, "Speed": 22,
    "Luck": 30, "Defense": 15, "Constitution": 18, "Movement": 10
}
MAGE_CLASS_GROWTHS = {
    "HP": 5, "Strength": 0, "Magic": 10, "Skill": 5, "Speed": 5,
    "Luck": 0, "Defense": 0, "Constitution": 0, "Movement": 0
}


@pytest.fixture
def sample_character_data():
    return {
        "character_id": "Leif",
        "name": "Leif",
        "portrait": "LeifPortrait",
        "initial_class_id": "Lord",
        "level": 1,
        "base_stats": DEFAULT_BASE_STATS.copy(),
        "growth_rates": DEFAULT_GROWTH_RATES.copy(),
        "innate_skills": DEFAULT_INNATE_SKILLS.copy(),
        "initial_inventory": DEFAULT_INITIAL_INVENTORY.copy(),
        "support_data": None
    }

@pytest.fixture
def sample_lord_class():
    return GameClass(
        class_id="Lord",
        name="Lord",
        base_stats=LORD_CLASS_BASE_STATS.copy(),
        max_stats=LORD_CLASS_MAX_STATS.copy(),
        growth_rates=LORD_CLASS_GROWTHS.copy()
    )

@pytest.fixture
def sample_mage_class():
    return GameClass(
        class_id="Mage",
        name="Mage",
        base_stats=MAGE_CLASS_BASE_STATS.copy(),
        max_stats=MAGE_CLASS_MAX_STATS.copy(),
        growth_rates=MAGE_CLASS_GROWTHS.copy()
    )


class TestCharacter:
    def test_character_create_valid(self, sample_character_data):
        character = Character(**sample_character_data)
        assert character is not None
        assert character.character_id == "Leif"
        assert character.name == "Leif"
        assert character.portrait == "LeifPortrait"
        assert character.initial_class_id == "Lord"
        assert character.level == 1
        assert character.base_hp == DEFAULT_BASE_STATS["HP"]
        assert character.growth_hp == DEFAULT_GROWTH_RATES["HP"]
        assert character.innate_skills == DEFAULT_INNATE_SKILLS
        assert character.initial_inventory == DEFAULT_INITIAL_INVENTORY
        assert character.experience_points == 0

    @pytest.mark.skip(reason="Global CharacterID uniqueness is a CharacterManager/system-level concern, not Character class itself.")
    def test_character_creation_unique_id(self, sample_character_data):
        # This test would require a manager to track created IDs.
        # Character(**sample_character_data)
        # with pytest.raises(SomeUniquenessViolationError): # Replace with actual error
        #     Character(**sample_character_data) # Attempt to create with same ID
        pass

    @pytest.mark.skip(reason="InitialClassID validation against a registry is a system-level concern.")
    def test_character_creation_valid_initial_class_id(self, sample_character_data):
        # This test would require a ClassManager or similar to validate ClassID.
        # sample_character_data["initial_class_id"] = "InvalidClass"
        # with pytest.raises(InvalidClassIDError): # Replace with actual error
        #     Character(**sample_character_data)
        pass

    def test_character_creation_non_negative_stats_growths(self, sample_character_data):
        # Test negative base stat
        invalid_stats_data = sample_character_data.copy()
        invalid_stats_data["base_stats"] = DEFAULT_BASE_STATS.copy()
        invalid_stats_data["base_stats"]["HP"] = -5
        with pytest.raises(ValueError, match="Base stat HP cannot be negative: -5"):
            Character(**invalid_stats_data)

        # Test negative growth rate
        invalid_growth_data = sample_character_data.copy()
        invalid_growth_data["growth_rates"] = DEFAULT_GROWTH_RATES.copy()
        invalid_growth_data["growth_rates"]["Strength"] = -10
        with pytest.raises(ValueError, match="Growth rate Strength cannot be negative: -10"):
            Character(**invalid_growth_data)
        
        # Test empty character_id
        invalid_id_data = sample_character_data.copy()
        invalid_id_data["character_id"] = ""
        with pytest.raises(ValueError, match="CharacterID cannot be empty."):
            Character(**invalid_id_data)

    def test_character_get_current_stats_accurate_calculation(self, sample_character_data, sample_lord_class):
        character = Character(**sample_character_data)
        current_stats = character.get_current_stats(sample_lord_class)

        expected_hp = min(character.base_hp + sample_lord_class.base_hp, sample_lord_class.max_hp)
        expected_strength = min(character.base_strength + sample_lord_class.base_strength, sample_lord_class.max_strength)
        # ... and so on for other stats

        assert current_stats.hp == expected_hp
        assert current_stats.strength == expected_strength
        assert current_stats.magic == min(character.base_magic + sample_lord_class.base_magic, sample_lord_class.max_magic)
        assert current_stats.skill == min(character.base_skill + sample_lord_class.base_skill, sample_lord_class.max_skill)
        assert current_stats.speed == min(character.base_speed + sample_lord_class.base_speed, sample_lord_class.max_speed)
        assert current_stats.luck == min(character.base_luck + sample_lord_class.base_luck, sample_lord_class.max_luck)
        assert current_stats.defense == min(character.base_defense + sample_lord_class.base_defense, sample_lord_class.max_defense)
        assert current_stats.constitution == min(character.base_constitution + sample_lord_class.base_constitution, sample_lord_class.max_constitution)
        assert current_stats.movement == min(character.base_movement + sample_lord_class.base_movement, sample_lord_class.max_movement)


    def test_character_level_up_applies_growths(self, sample_character_data, sample_lord_class):
        char_data = sample_character_data.copy()
        # Ensure high growth for a stat to guarantee increase
        char_data["growth_rates"] = {"HP": 100, "Strength": 100, "Magic": 0, "Skill": 0, "Speed": 0, "Luck": 0, "Defense": 0, "Constitution": 0, "Movement": 0}
        char_data["base_stats"] = {"HP": 10, "Strength": 5, "Magic": 0, "Skill": 0, "Speed": 0, "Luck": 0, "Defense": 0, "Constitution": 0, "Movement": 5}
        
        character = Character(**char_data)
        initial_personal_hp = character.base_hp
        initial_personal_strength = character.base_strength

        # Use fixed_growths to ensure stats increase
        increases = character.level_up(sample_lord_class, fixed_growths={"hp": True, "strength": True})

        assert character.level == 2
        assert character.experience_points == 0
        assert increases["hp"] == 1
        assert increases["strength"] == 1
        assert character.base_hp == initial_personal_hp + 1
        assert character.base_strength == initial_personal_strength + 1

        # Test with 0% growth, ensuring no increase
        char_data["growth_rates"] = {"HP": 0, "Strength": 0, "Magic": 0, "Skill": 0, "Speed": 0, "Luck": 0, "Defense": 0, "Constitution": 0, "Movement": 0}
        character_no_growth = Character(**char_data)
        initial_hp_no_growth = character_no_growth.base_hp
        increases_no_growth = character_no_growth.level_up(sample_lord_class, fixed_growths={"hp": False, "strength": False})
        assert increases_no_growth["hp"] == 0
        assert character_no_growth.base_hp == initial_hp_no_growth


    def test_character_level_up_respects_class_max_stats(self, sample_character_data, sample_lord_class):
        char_data = sample_character_data.copy()
        # Set personal base strength close to class max when combined with class base
        # Lord Max Strength: 20, Lord Base Strength: 1. Character personal base should be 18 for this test.
        # Character personal growth: 100%
        char_data["base_stats"] = DEFAULT_BASE_STATS.copy()
        char_data["base_stats"]["Strength"] = 18 # Personal base
        char_data["growth_rates"] = DEFAULT_GROWTH_RATES.copy()
        char_data["growth_rates"]["Strength"] = 100 # Guaranteed growth

        character = Character(**char_data)
        
        # Current combined strength: 18 (char) + 1 (class base) = 19. Max is 20.
        # Level up should increase personal strength by 1 to 19.
        # Combined strength becomes 19 (char) + 1 (class base) = 20.
        character.level_up(sample_lord_class, fixed_growths={"strength": True})
        current_stats_after_lv1 = character.get_current_stats(sample_lord_class)
        assert character.base_strength == 19 # Personal stat increased
        assert current_stats_after_lv1.strength == 20 # Combined stat hits max

        # Try to level up again. Personal strength is 19.
        # Combined is 19 + 1 = 20. Already at max. Personal stat should not increase.
        character.level_up(sample_lord_class, fixed_growths={"strength": True})
        current_stats_after_lv2 = character.get_current_stats(sample_lord_class)
        assert character.base_strength == 19 # Personal stat should NOT have increased further
        assert current_stats_after_lv2.strength == 20 # Still at max

    def test_character_innate_skills_are_present(self, sample_character_data):
        skills_data = sample_character_data.copy()
        skills_data["innate_skills"] = ["Vantage", "Wrath"]
        character = Character(**skills_data)
        assert "Vantage" in character.innate_skills
        assert "Wrath" in character.innate_skills
        assert len(character.innate_skills) == 2

    def test_character_initial_inventory_is_set(self, sample_character_data):
        inventory_data = sample_character_data.copy()
        inventory_data["initial_inventory"] = ["IronSword", "Vulnerary"]
        character = Character(**inventory_data)
        assert "IronSword" in character.initial_inventory
        assert "Vulnerary" in character.initial_inventory
        assert len(character.initial_inventory) == 2

    def test_add_experience_and_level_up(self, sample_character_data, sample_lord_class):
        character = Character(**sample_character_data)
        initial_level = character.level
        initial_hp = character.base_hp

        # Add enough EXP for one level up, with 100% HP growth for character and 0% for class
        character.growth_hp = 100
        sample_lord_class.growth_hp = 0 # Ensure only character growth applies

        level_up_history = character.add_experience(100, sample_lord_class, fixed_growths={"hp": True})
        
        assert character.level == initial_level + 1
        assert character.experience_points == 0
        assert len(level_up_history) == 1
        assert level_up_history[0]["hp"] == 1
        assert character.base_hp == initial_hp + 1

        # Add EXP for multiple level ups
        character.level = 1 # Reset level for simplicity
        character.base_hp = DEFAULT_BASE_STATS["HP"] # Reset hp
        character.experience_points = 0
        initial_hp_multi = character.base_hp

        level_up_history_multi = character.add_experience(250, sample_lord_class, fixed_growths={"hp": True}) # Should be 2 level ups
        assert character.level == 1 + 2
        assert character.experience_points == 50 # 250 - 200
        assert len(level_up_history_multi) == 2
        assert level_up_history_multi[0]["hp"] == 1
        assert level_up_history_multi[1]["hp"] == 1
        assert character.base_hp == initial_hp_multi + 2
        
    def test_get_current_stats_with_type_error(self, sample_character_data):
        character = Character(**sample_character_data)
        with pytest.raises(TypeError, match="game_class must be an instance of GameClass."):
            character.get_current_stats(None) # type: ignore

    def test_level_up_with_type_error(self, sample_character_data):
        character = Character(**sample_character_data)
        with pytest.raises(TypeError, match="game_class must be an instance of GameClass."):
            character.level_up(None) # type: ignore