import pytest
from enum import Enum

# Placeholder for actual imports when implementation exists
# from src.item_system.item import Item, ItemType, RangeData, ItemStatBonuses # Base classes
# from src.item_system.weapon import Weapon, WeaponTypeID, TargetAttribute, WeaponRankID, WeaponSpecialProperty
# from src.character_system.unit_instance import UnitInstance # Assuming this will exist
# from src.character_system.skill import SkillID # Assuming this will exist

# --- Mirrored Enums and Data Classes from test_item.py (or future item.py) ---
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
    _existing_item_ids = set()

    def __init__(self, item_id: str, name: str, item_type: ItemType, uses: int, max_uses: int,
                 cost: int, icon_id: str, description: str):
        if not item_id or not isinstance(item_id, str):
            raise ValueError("ItemID must be a non-empty string.")
        if item_id in Item._existing_item_ids and not getattr(self, '_is_reinitializing_for_test', False):
             # Allow re-init for tests if a flag is set, useful for derived class tests
            raise ValueError(f"ItemID '{item_id}' is not unique.")
        Item._existing_item_ids.add(item_id)

        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        if not isinstance(item_type, ItemType):
            raise ValueError("Type must be a valid ItemType.")
        if not isinstance(uses, int) or (uses < 0 and uses != -1):
            raise ValueError("Uses must be a non-negative integer or -1 for infinite.")
        if not isinstance(max_uses, int) or (max_uses < 0 and max_uses != -1) or \
           (max_uses != -1 and uses > max_uses and uses != -1 and max_uses !=0 ): # Allow uses=0, max_uses=0
             raise ValueError("MaxUses must be a non-negative integer or -1, and not less than current uses unless infinite or both are zero.")
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Cost must be a non-negative integer.")
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.uses = uses
        self.max_uses = max_uses
        self.cost = cost
        self.icon_id = icon_id
        self.description = description

    def can_be_used_by(self, unit) -> bool:
        if unit is None:
            return False
        return True

    @classmethod
    def reset_item_ids_for_test(cls):
        cls._existing_item_ids.clear()

    def __del__(self):
        # Ensure ItemID is removed from the set when an Item instance is deleted,
        # important for test isolation if fixtures create and tear down items.
        if hasattr(self, 'item_id') and self.item_id in Item._existing_item_ids:
            Item._existing_item_ids.remove(self.item_id)

# --- Enums specific to Weapon ---
class WeaponTypeID(Enum):
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
    Ballista = "Ballista"

class TargetAttribute(Enum):
    Armored = "Armored"
    Flying = "Flying"
    Mounted = "Mounted"
    Dragon = "Dragon"
    MagicalBeast = "MagicalBeast"
    Infantry = "Infantry"

class WeaponRankID(Enum):
    E_Rank = "E"
    D_Rank = "D"
    C_Rank = "C"
    B_Rank = "B"
    A_Rank = "A"
    S_Rank = "S"
    PRF_Rank = "PRF" # Assuming PRF is a distinct rank

class WeaponSpecialProperty(Enum):
    BraveEffect = "BraveEffect"
    PoisonStrike = "PoisonStrike"
    DevilEffect = "DevilEffect"
    Unbreakable = "Unbreakable"
    NegatesCriticals = "NegatesCriticals"
    Eclipse = "Eclipse"
    StealsHP = "StealsHP"
    CannotBeCountered = "CannotBeCountered"
    ReaverEffect = "ReaverEffect"
    CriticalBoost = "CriticalBoost"
    MovementCostModifier = "MovementCostModifier"
    EffectiveDamageOnly = "EffectiveDamageOnly"

# Placeholder for SkillID if needed for GrantedSkills
class SkillID(Enum):
    Vantage = "Vantage"
    Wrath = "Wrath"
    # Add other skill IDs as necessary

# --- Weapon Class (Minimal Placeholder) ---
class Weapon(Item):
    def __init__(self, item_id: str, name: str, item_type: ItemType, uses: int, max_uses: int, cost: int, icon_id: str, description: str,
                 weapon_type: WeaponTypeID, might: int, hit_rate: int, critical_rate: int, weight: int,
                 item_range: RangeData, required_rank: WeaponRankID,
                 effectiveness: list[TargetAttribute] = None,
                 granted_skills: list[SkillID] = None, # Using placeholder SkillID
                 stat_bonuses: ItemStatBonuses = None,
                 is_magic_damage: bool = False,
                 transforms_to_id: str = None, # ItemID
                 special_properties: list[WeaponSpecialProperty] = None):

        # Hack to allow re-initialization for testing derived classes without unique ID error
        self._is_reinitializing_for_test = True
        super().__init__(item_id, name, item_type, uses, max_uses, cost, icon_id, description)
        del self._is_reinitializing_for_test


        if not isinstance(weapon_type, WeaponTypeID):
            raise ValueError("WeaponType must be a valid WeaponTypeID.")
        if not isinstance(might, int): # Allow 0 or negative might? Spec implies positive.
            raise ValueError("Might must be an integer.")
        if not isinstance(hit_rate, int) or hit_rate < 0:
            raise ValueError("HitRate must be a non-negative integer.")
        if not isinstance(critical_rate, int) or critical_rate < 0:
            raise ValueError("CriticalRate must be a non-negative integer.")
        if not isinstance(weight, int) or weight < 0:
            raise ValueError("Weight must be a non-negative integer.")
        if not isinstance(item_range, RangeData):
            raise ValueError("Range must be a valid RangeData object.")
        if not isinstance(required_rank, WeaponRankID):
            raise ValueError("RequiredRank must be a valid WeaponRankID.")
        if effectiveness is not None and not all(isinstance(e, TargetAttribute) for e in effectiveness):
            raise ValueError("Effectiveness must be a list of TargetAttribute enums.")
        if granted_skills is not None and not all(isinstance(s, SkillID) for s in granted_skills):
            raise ValueError("GrantedSkills must be a list of SkillID enums.")
        if stat_bonuses is not None and not isinstance(stat_bonuses, ItemStatBonuses):
            raise ValueError("StatBonuses must be an ItemStatBonuses object.")
        if not isinstance(is_magic_damage, bool):
            raise ValueError("IsMagicDamage must be a boolean.")
        if transforms_to_id is not None and not isinstance(transforms_to_id, str):
            raise ValueError("TransformsToID must be a string (ItemID) or None.")
        if special_properties is not None and not all(isinstance(sp, WeaponSpecialProperty) for sp in special_properties):
            raise ValueError("SpecialProperties must be a list of WeaponSpecialProperty enums.")


        self.weapon_type = weapon_type
        self.might = might
        self.hit_rate = hit_rate
        self.critical_rate = critical_rate
        self.weight = weight
        self.range = item_range
        self.required_rank = required_rank
        self.effectiveness = effectiveness if effectiveness else []
        self.granted_skills = granted_skills if granted_skills else []
        self.stat_bonuses = stat_bonuses if stat_bonuses else ItemStatBonuses()
        self.is_magic_damage = is_magic_damage
        self.transforms_to_id = transforms_to_id
        self.special_properties = special_properties if special_properties else []

    # Override can_be_used_by for weapon-specific checks (e.g., rank)
    # def can_be_used_by(self, unit: UnitInstance) -> bool:
    #     if not super().can_be_used_by(unit):
    #         return False
    #     # Add logic for checking weapon rank, class restrictions, etc.
    #     # For now, placeholder:
    #     # return unit.get_weapon_rank(self.weapon_type) >= self.required_rank
    #     return True


# --- Test Fixtures ---
@pytest.fixture(scope="function")
def basic_weapon_data():
    Item.reset_item_ids_for_test() # Reset for each test using this fixture
    return {
        "item_id": "IronSword", "name": "Iron Sword", "item_type": ItemType.Sword,
        "uses": 40, "max_uses": 40, "cost": 400, "icon_id": "sword_icon", "description": "A basic sword.",
        "weapon_type": WeaponTypeID.Sword, "might": 5, "hit_rate": 90, "critical_rate": 0, "weight": 3,
        "item_range": RangeData(1, 1), "required_rank": WeaponRankID.E_Rank,
        "effectiveness": [], "granted_skills": [], "stat_bonuses": ItemStatBonuses(),
        "is_magic_damage": False, "transforms_to_id": None, "special_properties": []
    }

@pytest.fixture(scope="function")
def magic_weapon_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "FireTome", "name": "Fire", "item_type": ItemType.FireTome,
        "uses": 30, "max_uses": 30, "cost": 500, "icon_id": "fire_icon", "description": "Basic fire magic.",
        "weapon_type": WeaponTypeID.FireTome, "might": 6, "hit_rate": 85, "critical_rate": 0, "weight": 2,
        "item_range": RangeData(1, 2), "required_rank": WeaponRankID.E_Rank,
        "is_magic_damage": True
    }

# --- Test Cases for Weapon Class ---
class TestWeaponCreation:
    def test_weapon_create_valid(self, basic_weapon_data):
        weapon = Weapon(**basic_weapon_data)
        assert weapon.item_id == "IronSword"
        assert weapon.name == "Iron Sword"
        assert weapon.weapon_type == WeaponTypeID.Sword
        assert weapon.might == 5
        assert weapon.hit_rate == 90
        assert weapon.critical_rate == 0
        assert weapon.weight == 3
        assert weapon.range.min_range == 1 and weapon.range.max_range == 1
        assert weapon.required_rank == WeaponRankID.E_Rank
        assert weapon.is_magic_damage is False
        assert weapon.uses == 40
        # Test a few more inherited properties
        assert weapon.cost == 400
        assert weapon.item_type == ItemType.Sword

    def test_weapon_create_magic_damage(self, magic_weapon_data):
        weapon = Weapon(**magic_weapon_data)
        assert weapon.is_magic_damage is True
        assert weapon.weapon_type == WeaponTypeID.FireTome

    def test_weapon_properties_validation(self, basic_weapon_data):
        # TEST: Weapon properties (Mt, Hit, Wt, Range) must be within reasonable game balance. (Spec - implies valid types/values)
        # This is partially covered by type checks in __init__
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest1"

        with pytest.raises(ValueError, match="Might must be an integer"):
            Weapon(**{**data, "might": "invalid"})
        with pytest.raises(ValueError, match="HitRate must be a non-negative integer"):
            Weapon(**{**data, "hit_rate": -5})
        with pytest.raises(ValueError, match="Weight must be a non-negative integer"):
            Weapon(**{**data, "weight": -1})
        with pytest.raises(ValueError, match="Range must be a valid RangeData object"):
            Weapon(**{**data, "item_range": "not_range_data"})

    def test_weapon_required_rank_validation(self, basic_weapon_data):
        # TEST: RequiredRank must be a valid WeaponRankID. (from spec)
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest2"
        with pytest.raises(ValueError, match="RequiredRank must be a valid WeaponRankID"):
            Weapon(**{**data, "required_rank": "NotARank"})

    def test_weapon_uses_unbreakable(self, basic_weapon_data):
        # TEST: Uses should be -1 for unbreakable weapons, or a positive integer. (from spec)
        data = basic_weapon_data.copy()
        data["item_id"] = "UnbreakableSword"
        data["uses"] = -1
        data["max_uses"] = -1
        data["special_properties"] = [WeaponSpecialProperty.Unbreakable]
        weapon = Weapon(**data)
        assert weapon.uses == -1
        assert WeaponSpecialProperty.Unbreakable in weapon.special_properties

    def test_weapon_effectiveness_validation(self, basic_weapon_data):
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest3"
        with pytest.raises(ValueError, match="Effectiveness must be a list of TargetAttribute enums."):
            Weapon(**{**data, "effectiveness": ["NotAnAttribute"]})
        weapon = Weapon(**{**data, "item_id": "WTest4", "effectiveness": [TargetAttribute.Armored, TargetAttribute.Flying]})
        assert TargetAttribute.Armored in weapon.effectiveness
        assert TargetAttribute.Flying in weapon.effectiveness

    def test_weapon_granted_skills_validation(self, basic_weapon_data):
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest5"
        with pytest.raises(ValueError, match="GrantedSkills must be a list of SkillID enums."):
            Weapon(**{**data, "granted_skills": ["NotASkill"]})
        weapon = Weapon(**{**data, "item_id": "WTest6", "granted_skills": [SkillID.Vantage]})
        assert SkillID.Vantage in weapon.granted_skills

    def test_weapon_stat_bonuses_validation(self, basic_weapon_data):
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest7"
        with pytest.raises(ValueError, match="StatBonuses must be an ItemStatBonuses object."):
            Weapon(**{**data, "stat_bonuses": "NotStatBonuses"})

        bonuses = ItemStatBonuses(strength=5)
        weapon = Weapon(**{**data, "item_id": "WTest8", "stat_bonuses": bonuses})
        assert weapon.stat_bonuses.str_bonus == 5

    def test_weapon_special_properties_validation(self, basic_weapon_data):
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest9"
        with pytest.raises(ValueError, match="SpecialProperties must be a list of WeaponSpecialProperty enums."):
            Weapon(**{**data, "special_properties": ["NotASpecialProperty"]})

        props = [WeaponSpecialProperty.BraveEffect, WeaponSpecialProperty.PoisonStrike]
        weapon = Weapon(**{**data, "item_id": "WTest10", "special_properties": props})
        assert WeaponSpecialProperty.BraveEffect in weapon.special_properties
        assert WeaponSpecialProperty.PoisonStrike in weapon.special_properties

    def test_weapon_transforms_to_id_validation(self, basic_weapon_data):
        data = basic_weapon_data.copy()
        data["item_id"] = "WTest11"
        weapon = Weapon(**{**data, "transforms_to_id": "BrokenSword"})
        assert weapon.transforms_to_id == "BrokenSword"

        with pytest.raises(ValueError, match="TransformsToID must be a string"):
            Weapon(**{**data, "item_id": "WTest12", "transforms_to_id": 123})


# --- Test Cases for Weapon Enums ---
class TestWeaponEnums:
    def test_weapon_type_id_values(self):
        assert WeaponTypeID.Sword.value == "Sword"
        assert WeaponTypeID.Ballista.value == "Ballista"

    def test_target_attribute_values(self):
        assert TargetAttribute.Armored.value == "Armored"
        assert TargetAttribute.Flying.value == "Flying"

    def test_weapon_rank_id_values(self):
        assert WeaponRankID.E_Rank.value == "E"
        assert WeaponRankID.S_Rank.value == "S"

    def test_weapon_special_property_values(self):
        assert WeaponSpecialProperty.BraveEffect.value == "BraveEffect"
        assert WeaponSpecialProperty.Unbreakable.value == "Unbreakable"

# --- TDD Anchors from Spec ---
# These will require more setup, mocks, and potentially integration with other systems.
# For now, they serve as placeholders for future test development.

@pytest.mark.skip(reason="Requires UnitInstance and full combat system integration")
def test_weapon_equip_valid_rank(basic_weapon_data):
    # TEST: Weapon_Equip_ValidRank: Unit can equip a weapon if they meet the rank requirement.
    # Mock UnitInstance with E rank in Swords
    # weapon = Weapon(**basic_weapon_data)
    # mock_unit = MockUnitInstance(sword_rank=WeaponRankID.E_Rank)
    # assert weapon.can_be_used_by(mock_unit) is True
    pass

@pytest.mark.skip(reason="Requires UnitInstance and full combat system integration")
def test_weapon_equip_invalid_rank(basic_weapon_data):
    # TEST: Weapon_Equip_InvalidRank: Unit cannot equip a weapon if rank is too low.
    # data = basic_weapon_data.copy()
    # data["item_id"] = "SilverSword"
    # data["required_rank"] = WeaponRankID.A_Rank
    # weapon = Weapon(**data)
    # mock_unit = MockUnitInstance(sword_rank=WeaponRankID.E_Rank) # Unit has E rank
    # assert weapon.can_be_used_by(mock_unit) is False
    pass

@pytest.mark.skip(reason="Requires CombatSystem integration")
def test_weapon_combat_damage_calculation():
    # TEST: Weapon_Combat_DamageCalculation: Damage dealt by a weapon is calculated correctly (Mt + Str/Mag - Def/Res).
    pass

@pytest.mark.skip(reason="Requires CombatSystem and UnitInstance with attributes")
def test_weapon_effectiveness_applies_bonus():
    # TEST: Weapon_Effectiveness_AppliesBonus: Effective weapons deal bonus damage to appropriate targets.
    pass

@pytest.mark.skip(reason="Requires CombatSystem integration")
def test_weapon_brave_effect_attacks_twice():
    # TEST: Weapon_BraveEffect_AttacksTwice: Brave weapons allow two consecutive attacks if AS permits.
    pass

@pytest.mark.skip(reason="Requires UnitInstance and stat calculation logic")
def test_weapon_stat_bonus_applied():
    # TEST: Weapon_StatBonus_Applied: Stat bonuses from equipped weapons are correctly applied to unit stats.
    pass

@pytest.mark.skip(reason="Requires item transformation logic and conditions")
def test_item_transform_poison_to_normal():
    # TEST: Item_Transform_PoisonToNormal: Poisoned weapon transforms to its normal version under correct conditions.
    pass