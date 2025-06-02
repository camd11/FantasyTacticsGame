import pytest
from enum import Enum

# Placeholder for actual imports when implementation exists
# from src.item_system.item import Item, ItemType, RangeData, ItemStatBonuses
# from src.character_system.unit_instance import UnitInstance # Assuming this will exist

# --- Enums and Data Classes (mirrored for testing until actuals are importable) ---

class ItemType(Enum):
    Sword = "Sword"
    Lance = "Lance"
    Axe = "Axe"
    Bow = "Bow"
    Dagger = "Dagger"
    FireTome = "FireTome"
    ThunderTome = "ThunderTome"
    WindTome = "WindTome"
    LightTome = "LightTome"
    DarkTome = "DarkTome"
    Staff = "Staff"
    Consumable = "Consumable"
    Scroll = "Scroll"
    Key = "Key"
    Valuable = "Valuable"
    # Ring = "Ring" # If implemented
    # Shield = "Shield" # If implemented

class RangeData:
    def __init__(self, min_range: int, max_range: int):
        if not isinstance(min_range, int) or min_range <= 0:
            raise ValueError("MinRange must be a positive integer.")
        if not isinstance(max_range, int) or max_range < min_range:
            raise ValueError("MaxRange must be an integer and not less than MinRange.")
        self.min_range = min_range
        self.max_range = max_range

class ItemStatBonuses:
    def __init__(self, hp: int = 0, strength: int = 0, magic: int = 0, skill: int = 0,
                 speed: int = 0, defense: int = 0, constitution: int = 0,
                 luck: int = 0, movement: int = 0):
        for stat_name, stat_val in locals().items():
            if stat_name == "self":
                continue
            if not isinstance(stat_val, int):
                raise ValueError(f"{stat_name} bonus must be an integer.")
        self.hp_bonus = hp
        self.str_bonus = strength
        self.mag_bonus = magic
        self.skl_bonus = skill
        self.spd_bonus = speed
        self.def_bonus = defense
        self.con_bonus = constitution
        self.luk_bonus = luck
        self.mov_bonus = movement

class Item:
    # Minimal placeholder for Item class to allow tests to be written
    # Actual implementation will be in src/item_system/item.py
    _existing_item_ids = set()

    def __init__(self, item_id: str, name: str, item_type: ItemType, uses: int, max_uses: int,
                 cost: int, icon_id: str, description: str):
        if not item_id or not isinstance(item_id, str):
            raise ValueError("ItemID must be a non-empty string.")
        if item_id in Item._existing_item_ids:
            raise ValueError(f"ItemID '{item_id}' is not unique.")
        Item._existing_item_ids.add(item_id)

        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        if not isinstance(item_type, ItemType):
            raise ValueError("Type must be a valid ItemType.")
        if not isinstance(uses, int) or (uses < 0 and uses != -1):
            raise ValueError("Uses must be a non-negative integer or -1 for infinite.")
        if not isinstance(max_uses, int) or (max_uses < 0 and max_uses != -1) or (max_uses != -1 and uses > max_uses and uses != -1) :
             raise ValueError("MaxUses must be a non-negative integer or -1, and not less than current uses unless infinite.")
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Cost must be a non-negative integer.")
        # IconID and Description checks can be added as needed

        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.uses = uses
        self.max_uses = max_uses
        self.cost = cost
        self.icon_id = icon_id
        self.description = description

    def can_be_used_by(self, unit) -> bool:
        # Placeholder: Actual logic will depend on UnitInstance and item-specific rules
        # For base item, assume any unit can "hold" it if not further restricted.
        # Specific item types (Weapon, Staff) will override this.
        if unit is None: # Replace with actual UnitInstance check
            return False
        return True

    @classmethod
    def reset_item_ids_for_test(cls):
        cls._existing_item_ids.clear()

# --- Test Fixtures ---
@pytest.fixture
def basic_item_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "TestItem001",
        "name": "Test Item",
        "item_type": ItemType.Consumable,
        "uses": 1,
        "max_uses": 1,
        "cost": 100,
        "icon_id": "icon_test",
        "description": "A test item."
    }

@pytest.fixture
def infinite_uses_item_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "InfiniteTestItem001",
        "name": "Infinite Test Item",
        "item_type": ItemType.Scroll,
        "uses": -1,
        "max_uses": -1,
        "cost": 1000,
        "icon_id": "icon_infinite",
        "description": "An infinite use test item."
    }

# --- Test Cases for Item Class ---

class TestItemCreation:
    def test_item_create_valid(self, basic_item_data):
        # TEST: Item_Create_Valid (from spec)
        item = Item(**basic_item_data)
        assert item.item_id == basic_item_data["item_id"]
        assert item.name == basic_item_data["name"]
        assert item.item_type == basic_item_data["item_type"]
        assert item.uses == basic_item_data["uses"]
        assert item.max_uses == basic_item_data["max_uses"]
        assert item.cost == basic_item_data["cost"]
        assert item.description == basic_item_data["description"]

    def test_item_create_infinite_uses(self, infinite_uses_item_data):
        item = Item(**infinite_uses_item_data)
        assert item.uses == -1
        assert item.max_uses == -1

    def test_item_id_must_be_unique(self, basic_item_data):
        # TEST: ItemID must be unique. (from spec)
        Item(**basic_item_data) # Create first item
        with pytest.raises(ValueError, match="ItemID 'TestItem001' is not unique."):
            Item(**basic_item_data) # Attempt to create another with same ID

    def test_item_name_must_not_be_empty(self, basic_item_data):
        # TEST: Name must not be empty. (from spec)
        invalid_data = basic_item_data.copy()
        invalid_data["name"] = ""
        with pytest.raises(ValueError, match="Name must be a non-empty string."):
            Item(**invalid_data)

    def test_item_uses_must_be_non_negative_or_infinite(self, basic_item_data):
        # TEST: Uses must be non-negative (or special value for infinite). (from spec)
        invalid_data = basic_item_data.copy()
        invalid_data["uses"] = -2
        with pytest.raises(ValueError, match="Uses must be a non-negative integer or -1 for infinite."):
            Item(**invalid_data)

        valid_data_zero = basic_item_data.copy()
        valid_data_zero["item_id"] = "TestItem002" # unique ID
        valid_data_zero["uses"] = 0
        valid_data_zero["max_uses"] = 0
        item = Item(**valid_data_zero)
        assert item.uses == 0

    def test_item_max_uses_validation(self, basic_item_data):
        # Test max_uses < uses
        invalid_data = basic_item_data.copy()
        invalid_data["item_id"] = "TestItem003"
        invalid_data["uses"] = 5
        invalid_data["max_uses"] = 3
        with pytest.raises(ValueError, match="MaxUses must be a non-negative integer or -1, and not less than current uses unless infinite."):
            Item(**invalid_data)

        # Test max_uses = -1 with uses > 0
        valid_data = basic_item_data.copy()
        valid_data["item_id"] = "TestItem004"
        valid_data["uses"] = 5
        valid_data["max_uses"] = -1 # This implies it was originally infinite, but now has finite uses? Spec might need clarification or this is an edge case.
                                    # For now, assuming if max_uses is -1, uses should also be -1 or it's a state after repair/special change.
                                    # The current check allows max_uses=-1 if uses is also -1.
                                    # If uses is positive, max_uses must be >= uses or -1.
                                    # Let's assume max_uses can be -1 (infinite potential) even if current uses are finite (e.g. a partially used unbreakable item if that makes sense)
                                    # The current rule is: (max_uses < 0 and max_uses != -1) or (max_uses != -1 and uses > max_uses and uses != -1)
        # This should pass if max_uses can be -1 while uses is positive.
        # item = Item(**valid_data)
        # assert item.max_uses == -1

        # Test max_uses < 0 and not -1
        invalid_data_neg = basic_item_data.copy()
        invalid_data_neg["item_id"] = "TestItem005"
        invalid_data_neg["max_uses"] = -2
        with pytest.raises(ValueError, match="MaxUses must be a non-negative integer or -1"):
            Item(**invalid_data_neg)


    def test_item_cost_must_be_non_negative(self, basic_item_data):
        invalid_data = basic_item_data.copy()
        invalid_data["item_id"] = "TestItem006" # unique ID
        invalid_data["cost"] = -100
        with pytest.raises(ValueError, match="Cost must be a non-negative integer."):
            Item(**invalid_data)

    def test_item_invalid_type(self, basic_item_data):
        invalid_data = basic_item_data.copy()
        invalid_data["item_id"] = "TestItem007" # unique ID
        invalid_data["item_type"] = "NotAnItemType"
        with pytest.raises(ValueError, match="Type must be a valid ItemType."):
            Item(**invalid_data)

class TestItemMethods:
    def test_can_be_used_by_placeholder(self, basic_item_data):
        # TEST: Correctly determines usability based on unit. (from spec, for base Item)
        Item.reset_item_ids_for_test()
        item = Item(**basic_item_data)
        mock_unit = "MockUnit" # Replace with a proper mock UnitInstance later
        assert item.can_be_used_by(mock_unit) is True # Base item, placeholder logic

        assert item.can_be_used_by(None) is False # Example of a basic check

# --- Test Cases for ItemType Enum ---
class TestItemTypeEnum:
    def test_item_type_values(self):
        assert ItemType.Sword.value == "Sword"
        assert ItemType.Consumable.value == "Consumable"
        # Add more checks if necessary for all enum values

# --- Test Cases for RangeData Class ---
class TestRangeData:
    def test_range_data_valid(self):
        rd = RangeData(1, 2)
        assert rd.min_range == 1
        assert rd.max_range == 2

        rd_equal = RangeData(1, 1)
        assert rd_equal.min_range == 1
        assert rd_equal.max_range == 1

    def test_range_data_min_range_must_be_positive(self):
        # TEST: MinRange must be > 0. (from spec)
        with pytest.raises(ValueError, match="MinRange must be a positive integer."):
            RangeData(0, 2)
        with pytest.raises(ValueError, match="MinRange must be a positive integer."):
            RangeData(-1, 2)

    def test_range_data_max_range_ge_min_range(self):
        # TEST: MaxRange must be >= MinRange. (from spec)
        with pytest.raises(ValueError, match="MaxRange must be an integer and not less than MinRange."):
            RangeData(2, 1)

    def test_range_data_invalid_types(self):
        with pytest.raises(ValueError):
            RangeData("1", 2)
        with pytest.raises(ValueError):
            RangeData(1, "2")

# --- Test Cases for ItemStatBonuses Class ---
class TestItemStatBonuses:
    def test_item_stat_bonuses_valid_creation(self):
        # TEST: All bonus values must be integers. (from spec)
        bonuses = ItemStatBonuses(hp=1, strength=2, magic=-1, skill=0, speed=5, defense=0, constitution=1, luck=0, movement=1)
        assert bonuses.hp_bonus == 1
        assert bonuses.str_bonus == 2
        assert bonuses.mag_bonus == -1
        assert bonuses.skl_bonus == 0
        assert bonuses.spd_bonus == 5
        assert bonuses.def_bonus == 0
        assert bonuses.con_bonus == 1
        assert bonuses.luk_bonus == 0
        assert bonuses.mov_bonus == 1

    def test_item_stat_bonuses_default_values(self):
        bonuses = ItemStatBonuses()
        assert bonuses.hp_bonus == 0
        assert bonuses.str_bonus == 0
        # ... and so on for all stats

    def test_item_stat_bonuses_invalid_type(self):
        with pytest.raises(ValueError, match="hp bonus must be an integer."):
            ItemStatBonuses(hp="invalid")
        with pytest.raises(ValueError, match="strength bonus must be an integer."):
            ItemStatBonuses(strength=1.5)

# TODO: Add more tests as per spec for Item class, e.g. IconID, Description validation if strict rules apply.
# TODO: Prepare for mocking UnitInstance for `can_be_used_by`