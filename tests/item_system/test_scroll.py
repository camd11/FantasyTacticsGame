import pytest
from enum import Enum

# Placeholder for actual imports
# from src.item_system.item import Item, ItemType
# from src.item_system.scroll import Scroll
# from src.character_system.unit_instance import UnitInstance # For growth rate application

# --- Mirrored Enums and Data Classes ---
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
    Scroll = "Scroll" # Important for this test file
    Key = "Key"
    Valuable = "Valuable"

class Item:
    _existing_item_ids = set()
    def __init__(self, item_id: str, name: str, item_type: ItemType, uses: int, max_uses: int,
                 cost: int, icon_id: str, description: str):
        if not item_id or not isinstance(item_id, str):
            raise ValueError("ItemID must be a non-empty string.")
        if item_id in Item._existing_item_ids and not getattr(self, '_is_reinitializing_for_test', False):
            raise ValueError(f"ItemID '{item_id}' is not unique.")
        Item._existing_item_ids.add(item_id)

        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        if not isinstance(item_type, ItemType):
            raise ValueError("Type must be a valid ItemType.")
        if not isinstance(uses, int) or (uses < 0 and uses != -1): # Scrolls are usually infinite use
            raise ValueError("Uses must be a non-negative integer or -1 for infinite.")
        if not isinstance(max_uses, int) or (max_uses < 0 and max_uses != -1) or \
           (max_uses != -1 and uses > max_uses and uses != -1 and max_uses !=0 ):
             raise ValueError("MaxUses must be a non-negative integer or -1, and not less than current uses unless infinite or both are zero.")
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Cost must be a non-negative integer.")
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.uses = uses # Typically -1 for scrolls
        self.max_uses = max_uses # Typically -1 for scrolls
        self.cost = cost
        self.icon_id = icon_id
        self.description = description
    @classmethod
    def reset_item_ids_for_test(cls):
        cls._existing_item_ids.clear()
    def __del__(self):
        if hasattr(self, 'item_id') and self.item_id in Item._existing_item_ids:
            Item._existing_item_ids.remove(self.item_id)

# --- Scroll Class (Minimal Placeholder) ---
class Scroll(Item):
    def __init__(self, item_id: str, name: str, cost: int, icon_id: str, description: str,
                 growth_hp_modifier: int = 0,
                 growth_strength_modifier: int = 0,
                 growth_magic_modifier: int = 0,
                 growth_skill_modifier: int = 0,
                 growth_speed_modifier: int = 0,
                 growth_defense_modifier: int = 0,
                 growth_constitution_modifier: int = 0,
                 growth_luck_modifier: int = 0,
                 growth_movement_modifier: int = 0):

        self._is_reinitializing_for_test = True
        # Scrolls are infinite use by default as per FE conventions and spec hints
        super().__init__(item_id, name, ItemType.Scroll, -1, -1, cost, icon_id, description)
        del self._is_reinitializing_for_test

        modifiers = {
            "HP": growth_hp_modifier, "Strength": growth_strength_modifier,
            "Magic": growth_magic_modifier, "Skill": growth_skill_modifier,
            "Speed": growth_speed_modifier, "Defense": growth_defense_modifier,
            "Constitution": growth_constitution_modifier, "Luck": growth_luck_modifier,
            "Movement": growth_movement_modifier
        }
        for stat_name, mod_val in modifiers.items():
            if not isinstance(mod_val, int):
                raise ValueError(f"Growth modifier for {stat_name} must be an integer.")

        self.growth_hp_modifier = growth_hp_modifier
        self.growth_strength_modifier = growth_strength_modifier
        self.growth_magic_modifier = growth_magic_modifier
        self.growth_skill_modifier = growth_skill_modifier
        self.growth_speed_modifier = growth_speed_modifier
        self.growth_defense_modifier = growth_defense_modifier
        self.growth_constitution_modifier = growth_constitution_modifier
        self.growth_luck_modifier = growth_luck_modifier
        self.growth_movement_modifier = growth_movement_modifier

    # Scrolls don't have an "apply_effect" method in the same way consumables do.
    # Their effect is passive and checked during level-up by the CharacterSystem.

# --- Mock UnitInstance for testing growth modification ---
class MockUnitWithGrowths:
    def __init__(self, base_growths=None):
        self.base_growths = base_growths if base_growths else {
            "hp": 30, "str": 30, "mag": 10, "skl": 30,
            "spd": 30, "def": 20, "con": 10, "lck": 20, "mov": 0
        }
        self.inventory = [] # List to hold items, including scrolls

    def get_effective_growth_rates(self):
        effective_growths = self.base_growths.copy()
        for item in self.inventory:
            if isinstance(item, Scroll):
                effective_growths["hp"] += item.growth_hp_modifier
                effective_growths["str"] += item.growth_strength_modifier
                effective_growths["mag"] += item.growth_magic_modifier
                effective_growths["skl"] += item.growth_skill_modifier
                effective_growths["spd"] += item.growth_speed_modifier
                effective_growths["def"] += item.growth_defense_modifier
                effective_growths["con"] += item.growth_constitution_modifier
                effective_growths["lck"] += item.growth_luck_modifier
                effective_growths["mov"] += item.growth_movement_modifier
        return effective_growths

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def odos_scroll_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "OdosScroll", "name": "Odos Scroll", "cost": 0, # Typically not bought/sold
        "icon_id": "scroll_icon_odos", "description": "A holy scroll bearing the teachings of Odos. Boosts HP, SKL, SPD growth.",
        "growth_hp_modifier": 10,
        "growth_skill_modifier": 5,
        "growth_speed_modifier": 5,
        # Other growths are 0 by default in the fixture
    }

@pytest.fixture(scope="function")
def neir_scroll_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "NeirScroll", "name": "Neir Scroll", "cost": 0,
        "icon_id": "scroll_icon_neir", "description": "A holy scroll. Boosts DEF growth, reduces SPD growth.",
        "growth_defense_modifier": 20,
        "growth_speed_modifier": -5,
    }

# --- Test Cases for Scroll Class ---
class TestScrollCreation:
    def test_scroll_create_valid(self, odos_scroll_data):
        scroll = Scroll(**odos_scroll_data)
        assert scroll.item_id == "OdosScroll"
        assert scroll.name == "Odos Scroll"
        assert scroll.item_type == ItemType.Scroll
        assert scroll.uses == -1 # Scrolls are infinite use
        assert scroll.max_uses == -1
        assert scroll.growth_hp_modifier == 10
        assert scroll.growth_strength_modifier == 0 # Default from fixture
        assert scroll.growth_magic_modifier == 0
        assert scroll.growth_skill_modifier == 5
        assert scroll.growth_speed_modifier == 5
        assert scroll.growth_defense_modifier == 0
        assert scroll.growth_constitution_modifier == 0
        assert scroll.growth_luck_modifier == 0
        assert scroll.growth_movement_modifier == 0

    def test_scroll_all_growth_modifiers_must_be_integers(self, odos_scroll_data):
        # TEST: All growth modifiers must be integers (can be 0, positive, or negative). (from spec)
        invalid_data = odos_scroll_data.copy()
        invalid_data["item_id"] = "ScrollTest1"
        invalid_data["growth_hp_modifier"] = "invalid"
        with pytest.raises(ValueError, match="Growth modifier for HP must be an integer."):
            Scroll(**invalid_data)

        invalid_data_float = odos_scroll_data.copy()
        invalid_data_float["item_id"] = "ScrollTest2"
        invalid_data_float["growth_skill_modifier"] = 5.5
        with pytest.raises(ValueError, match="Growth modifier for Skill must be an integer."):
            Scroll(**invalid_data_float)

    def test_scroll_negative_growth_modifier(self, neir_scroll_data):
        scroll = Scroll(**neir_scroll_data)
        assert scroll.growth_defense_modifier == 20
        assert scroll.growth_speed_modifier == -5 # Negative modifier is valid

class TestScrollEffectApplication:
    def test_scroll_in_inventory_modifies_growth_rates(self, odos_scroll_data, neir_scroll_data):
        # TEST: Scroll in inventory correctly modifies growth rates on level up. (from spec)
        # This test simulates the CharacterSystem's check.
        Item.reset_item_ids_for_test() # Ensure clean slate for item IDs

        odos_scroll = Scroll(**odos_scroll_data)
        neir_scroll = Scroll(**neir_scroll_data) # item_id will be NeirScroll

        unit = MockUnitWithGrowths(base_growths={
            "hp": 50, "str": 30, "mag": 10, "skl": 25,
            "spd": 30, "def": 15, "con": 10, "lck": 20, "mov": 0
        })

        # No scrolls
        growths_no_scroll = unit.get_effective_growth_rates()
        assert growths_no_scroll["hp"] == 50
        assert growths_no_scroll["skl"] == 25
        assert growths_no_scroll["spd"] == 30
        assert growths_no_scroll["def"] == 15

        # With Odos Scroll
        unit.inventory.append(odos_scroll)
        growths_with_odos = unit.get_effective_growth_rates()
        assert growths_with_odos["hp"] == 50 + odos_scroll.growth_hp_modifier # 50 + 10 = 60
        assert growths_with_odos["skl"] == 25 + odos_scroll.growth_skill_modifier # 25 + 5 = 30
        assert growths_with_odos["spd"] == 30 + odos_scroll.growth_speed_modifier # 30 + 5 = 35
        assert growths_with_odos["def"] == 15 # Unchanged by Odos

        # With Odos and Neir Scroll (stacking)
        unit.inventory.append(neir_scroll)
        growths_with_both = unit.get_effective_growth_rates()
        assert growths_with_both["hp"] == 50 + odos_scroll.growth_hp_modifier # 60
        assert growths_with_both["skl"] == 25 + odos_scroll.growth_skill_modifier # 30
        assert growths_with_both["spd"] == 30 + odos_scroll.growth_speed_modifier + neir_scroll.growth_speed_modifier # 35 - 5 = 30
        assert growths_with_both["def"] == 15 + neir_scroll.growth_defense_modifier # 15 + 20 = 35

        # Remove Odos, only Neir
        unit.inventory.remove(odos_scroll)
        growths_with_neir_only = unit.get_effective_growth_rates()
        assert growths_with_neir_only["hp"] == 50 # Back to base
        assert growths_with_neir_only["skl"] == 25 # Back to base
        assert growths_with_neir_only["spd"] == 30 + neir_scroll.growth_speed_modifier # 30 - 5 = 25
        assert growths_with_neir_only["def"] == 15 + neir_scroll.growth_defense_modifier # 15 + 20 = 35

# --- TDD Anchors from Spec ---
@pytest.mark.skip(reason="Covered by test_scroll_in_inventory_modifies_growth_rates")
def test_scroll_growth_modifier_applied():
    # TEST: Scroll_GrowthModifier_Applied: Character holding a scroll has their growth rates correctly modified for level-ups.
    pass