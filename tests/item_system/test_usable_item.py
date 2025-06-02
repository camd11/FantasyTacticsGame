import pytest
from enum import Enum

# Placeholder for actual imports
# from src.item_system.item import Item, ItemType
# from src.item_system.usable_item import UsableItem, UsableEffectType
# from src.character_system.unit_instance import UnitInstance
# from src.character_system.game_class import ClassID # Assuming ClassID enum/type

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
    Scroll = "Scroll"
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
        if not isinstance(item_type, ItemType): # Ensure item_type is an ItemType instance
            raise ValueError("Type must be a valid ItemType.")
        if not isinstance(uses, int) or (uses < 0 and uses != -1):
            raise ValueError("Uses must be a non-negative integer or -1 for infinite.")
        if not isinstance(max_uses, int) or (max_uses < 0 and max_uses != -1) or \
           (max_uses != -1 and uses > max_uses and uses != -1 and max_uses !=0 ):
             raise ValueError("MaxUses must be a non-negative integer or -1, and not less than current uses unless infinite or both are zero.")
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Cost must be a non-negative integer.")
        self.item_id = item_id
        self.name = name
        # Ensure that the item_type passed to UsableItem is actually ItemType.Consumable or similar
        # Forcing it here for the base class, UsableItem will use ItemType.Consumable
        self.item_type = item_type
        self.uses = uses
        self.max_uses = max_uses
        self.cost = cost
        self.icon_id = icon_id
        self.description = description
    @classmethod
    def reset_item_ids_for_test(cls):
        cls._existing_item_ids.clear()
    def __del__(self):
        if hasattr(self, 'item_id') and self.item_id in Item._existing_item_ids:
            Item._existing_item_ids.remove(self.item_id)

# --- Enums specific to UsableItem ---
class UsableEffectType(Enum):
    HealFixedHP = "HealFixedHP"
    HealMaxHP = "HealMaxHP"
    Antitoxin = "Antitoxin"
    PureWater = "PureWater"
    TorchItem = "TorchItem"
    Lockpick = "Lockpick"
    ChestKey = "ChestKey"
    DoorKey = "DoorKey"
    BridgeKey = "BridgeKey"
    StaminaDrink = "StaminaDrink"
    EnergyRing = "EnergyRing" # STR
    SecretBook = "SecretBook" # SKL
    SpeedRing = "SpeedRing"   # SPD
    GoddessIcon = "GoddessIcon" # LCK
    Dracoshield = "Dracoshield" # DEF
    BodyRing = "BodyRing"     # CON
    MagicRing = "MagicRing"   # MAG
    LifeRing = "LifeRing"     # Max HP
    SkillBook = "SkillBook"   # Weapon Rank EXP
    PromotionItem = "PromotionItem"
    StatDropItem = "StatDropItem"
    MemberCard = "MemberCard"
    LightRune = "LightRune"
    Mine = "Mine"

# Placeholder for ClassID enum, will be defined in character system
class ClassID(Enum):
    Fighter = "Fighter"
    Mage = "Mage"
    Lord = "Lord"
    Cavalier = "Cavalier"
    Knight = "Knight"
    # Add more as needed for testing promotion items

# --- UsableItem Class (Minimal Placeholder) ---
class UsableItem(Item):
    def __init__(self, item_id: str, name: str, uses: int, max_uses: int, cost: int, icon_id: str, description: str,
                 effect: UsableEffectType, effect_potency: int,
                 promotion_target_classes: list[ClassID] = None,
                 duration_turns: int = 0):

        self._is_reinitializing_for_test = True
        # Usable items are typically of ItemType.Consumable, or ItemType.Key etc.
        # Forcing Consumable here for simplicity in the placeholder.
        # Actual implementation might determine ItemType based on UsableEffectType or pass it.
        super().__init__(item_id, name, ItemType.Consumable, uses, max_uses, cost, icon_id, description)
        del self._is_reinitializing_for_test

        if not isinstance(effect, UsableEffectType):
            raise ValueError("Effect must be a valid UsableEffectType.")
        if not isinstance(effect_potency, int): # Potency can be 0.
            raise ValueError("EffectPotency must be an integer.")
        if promotion_target_classes is not None and not all(isinstance(c, ClassID) for c in promotion_target_classes):
            raise ValueError("PromotionTargetClasses must be a list of ClassID enums.")
        if effect == UsableEffectType.PromotionItem and not promotion_target_classes:
            raise ValueError("PromotionItem must have PromotionTargetClasses.")
        if not isinstance(duration_turns, int) or duration_turns < -1: # 0 for instant/permanent, -1 for special cases, >0 for turns
            raise ValueError("DurationTurns must be an integer >= -1.")

        self.effect = effect
        self.effect_potency = effect_potency
        self.promotion_target_classes = promotion_target_classes if promotion_target_classes else []
        self.duration_turns = duration_turns

    def apply_effect(self, target_unit) -> bool:
        # Placeholder for actual effect application logic
        # This will interact with TargetUnit's stats, status, etc.
        # And consume the item (self.uses -= 1)
        if target_unit is None: # Replace with actual UnitInstance check
            return False # Cannot apply to no one

        if self.uses == 0:
            return False # Cannot use item with 0 uses

        # Simulate consumption
        if self.uses > 0:
            self.uses -= 1
        
        # Actual effect logic would go here based on self.effect
        # e.g., if self.effect == UsableEffectType.HealFixedHP:
        # target_unit.heal(self.effect_potency)
        return True # Placeholder for success

# --- Mock TargetUnit for testing apply_effect ---
class MockTargetUnit:
    def __init__(self, current_hp=10, max_hp=20, current_class=ClassID.Fighter):
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.current_class = current_class
        self.stats = {"str": 5, "skl": 5, "spd": 5, "lck": 5, "def": 5, "con": 5, "mag": 5} # basic stats
        self.status_effects = [] # for antitoxin, purewater duration etc.

    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def boost_stat(self, stat_name, amount):
        if stat_name in self.stats:
            self.stats[stat_name] += amount
        elif stat_name == "max_hp":
            self.max_hp += amount
            self.current_hp += amount # Typically also heals by the boosted amount

    def can_promote_to(self, target_class: ClassID) -> bool:
        # Simplified mock logic
        if self.current_class == ClassID.Fighter and target_class == ClassID.Knight: # Example rule
            return True
        if self.current_class == ClassID.Mage and target_class == ClassID.Lord: # Another example
            return True
        return False
    
    def promote(self, target_class: ClassID):
        if self.can_promote_to(target_class):
            self.current_class = target_class
            return True
        return False


# --- Test Fixtures ---
@pytest.fixture(scope="function")
def vulnerary_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "Vulnerary01", "name": "Vulnerary", "uses": 3, "max_uses": 3, "cost": 300,
        "icon_id": "vulnerary_icon", "description": "Heals 10 HP.",
        "effect": UsableEffectType.HealFixedHP, "effect_potency": 10,
        "promotion_target_classes": [], "duration_turns": 0
    }

@pytest.fixture(scope="function")
def energy_ring_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "EnergyRing01", "name": "Energy Ring", "uses": 1, "max_uses": 1, "cost": 2000,
        "icon_id": "stat_boost_icon", "description": "Permanently boosts STR by 2.",
        "effect": UsableEffectType.EnergyRing, "effect_potency": 2,
        "duration_turns": 0 # Permanent
    }

@pytest.fixture(scope="function")
def promotion_item_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "KnightCrest01", "name": "Knight Crest", "uses": 1, "max_uses": 1, "cost": 4000,
        "icon_id": "promo_icon", "description": "Promotes eligible units.",
        "effect": UsableEffectType.PromotionItem, "effect_potency": 0, # Potency might be unused
        "promotion_target_classes": [ClassID.Knight, ClassID.Lord],
        "duration_turns": 0
    }

@pytest.fixture(scope="function")
def pure_water_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "PureWater01", "name": "Pure Water", "uses": 1, "max_uses": 1, "cost": 600,
        "icon_id": "pure_water_icon", "description": "Temporarily boosts MAG.",
        "effect": UsableEffectType.PureWater, "effect_potency": 7,
        "duration_turns": 5
    }


# --- Test Cases for UsableItem Class ---
class TestUsableItemCreation:
    def test_usable_item_create_valid_heal(self, vulnerary_data):
        item = UsableItem(**vulnerary_data)
        assert item.item_id == "Vulnerary01"
        assert item.name == "Vulnerary"
        assert item.item_type == ItemType.Consumable # Set by UsableItem init
        assert item.effect == UsableEffectType.HealFixedHP
        assert item.effect_potency == 10
        assert item.uses == 3
        assert item.duration_turns == 0

    def test_usable_item_create_valid_stat_booster(self, energy_ring_data):
        item = UsableItem(**energy_ring_data)
        assert item.effect == UsableEffectType.EnergyRing
        assert item.effect_potency == 2

    def test_usable_item_create_valid_promotion(self, promotion_item_data):
        item = UsableItem(**promotion_item_data)
        assert item.effect == UsableEffectType.PromotionItem
        assert ClassID.Knight in item.promotion_target_classes
        assert ClassID.Lord in item.promotion_target_classes

    def test_usable_item_create_valid_temporary(self, pure_water_data):
        item = UsableItem(**pure_water_data)
        assert item.effect == UsableEffectType.PureWater
        assert item.duration_turns == 5

    def test_usable_item_effect_validation(self, vulnerary_data):
        # TEST: Effect must be a valid UsableEffectType. (from spec)
        data = vulnerary_data.copy()
        data["item_id"] = "UseTest1"
        with pytest.raises(ValueError, match="Effect must be a valid UsableEffectType."):
            UsableItem(**{**data, "effect": "NotAnEffect"})

    def test_usable_item_promotion_target_validation(self, promotion_item_data):
        # TEST: If Effect is PromotionItem, PromotionTargetClasses must not be empty and contain valid ClassIDs. (from spec)
        data = promotion_item_data.copy()
        data["item_id"] = "UseTest2"
        with pytest.raises(ValueError, match="PromotionItem must have PromotionTargetClasses."):
            UsableItem(**{**data, "promotion_target_classes": []})

        data["item_id"] = "UseTest3"
        with pytest.raises(ValueError, match="PromotionTargetClasses must be a list of ClassID enums."):
            UsableItem(**{**data, "promotion_target_classes": ["NotAClassID"]})

    def test_usable_item_duration_validation(self, vulnerary_data):
        # TEST: If DurationTurns > 0, effect should be temporary. (from spec) - this is more about behavior.
        # Test creation with invalid duration
        data = vulnerary_data.copy()
        data["item_id"] = "UseTest4"
        with pytest.raises(ValueError, match="DurationTurns must be an integer >= -1."):
            UsableItem(**{**data, "duration_turns": -2})

        item_temp = UsableItem(**{**vulnerary_data, "item_id": "UseTest5", "duration_turns": 3})
        assert item_temp.duration_turns == 3


class TestUsableItemMethods:
    def test_apply_effect_consumes_item(self, vulnerary_data):
        # TEST: Effect applies correctly and item is consumed. (from spec) - testing consumption part
        item = UsableItem(**vulnerary_data)
        mock_unit = MockTargetUnit()
        initial_uses = item.uses
        
        applied = item.apply_effect(mock_unit)
        assert applied is True
        assert item.uses == initial_uses - 1

        item.uses = 0 # Set uses to 0
        applied_again = item.apply_effect(mock_unit)
        assert applied_again is False # Should not apply if no uses
        assert item.uses == 0


    @pytest.mark.skip(reason="Requires full effect logic in apply_effect")
    def test_apply_effect_heal_fixed_hp(self, vulnerary_data):
        # TEST: UsableItem_Vulnerary_HealsHP: Vulnerary correctly heals HP and is consumed. (from spec)
        item = UsableItem(**vulnerary_data)
        unit = MockTargetUnit(current_hp=5, max_hp=20)
        
        item.apply_effect(unit) # This needs the actual healing logic
        # assert unit.current_hp == 15 # 5 + 10
        # assert item.uses == vulnerary_data["uses"] - 1
        pass

    @pytest.mark.skip(reason="Requires full effect logic for stat boosters")
    def test_apply_effect_stat_booster(self, energy_ring_data):
        # TEST: UsableItem_StatBooster_PermanentIncrease: Stat booster item permanently increases the target stat. (from spec)
        item = UsableItem(**energy_ring_data)
        unit = MockTargetUnit()
        initial_str = unit.stats["str"]
        
        item.apply_effect(unit) # Needs actual stat boosting logic
        # assert unit.stats["str"] == initial_str + item.effect_potency
        # assert item.uses == 0
        pass

    @pytest.mark.skip(reason="Requires full effect logic for promotion")
    def test_apply_effect_promotion_item(self, promotion_item_data):
        # TEST: Promotion items correctly check class eligibility. (from spec)
        item = UsableItem(**promotion_item_data)
        
        # Unit eligible for Knight
        unit_fighter = MockTargetUnit(current_class=ClassID.Fighter)
        # item.apply_effect(unit_fighter) # Needs promotion logic
        # assert unit_fighter.current_class == ClassID.Knight
        # assert item.uses == 0

        # Unit not eligible
        # item_knight_crest = UsableItem(**promotion_item_data) # fresh item
        # item_knight_crest.item_id = "KnightCrest02" # new id
        # unit_mage = MockTargetUnit(current_class=ClassID.Mage)
        # item_knight_crest.apply_effect(unit_mage)
        # assert unit_mage.current_class == ClassID.Mage # No change
        # assert item_knight_crest.uses == 1 # Not consumed if not eligible
        pass

    @pytest.mark.skip(reason="Requires full effect logic for temporary effects")
    def test_apply_effect_temporary_effect_duration(self, pure_water_data):
        # TEST: Temporary effects apply for correct duration. (from spec)
        item = UsableItem(**pure_water_data)
        unit = MockTargetUnit()
        
        item.apply_effect(unit) # Needs logic to add status with duration
        # assert any(eff.name == "PureWater" and eff.duration == item.duration_turns for eff in unit.status_effects)
        # assert item.uses == 0
        pass

# --- Test Cases for UsableEffectType Enum ---
class TestUsableEffectTypeEnum:
    def test_usable_effect_type_values(self):
        assert UsableEffectType.HealFixedHP.value == "HealFixedHP"
        assert UsableEffectType.PromotionItem.value == "PromotionItem"
        assert UsableEffectType.EnergyRing.value == "EnergyRing"
        # Add more checks if necessary