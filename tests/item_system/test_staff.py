import pytest
from enum import Enum

# Placeholder for actual imports
# from src.item_system.item import Item, ItemType, RangeData
# from src.item_system.staff import Staff, StaffEffectType
# from src.item_system.weapon import WeaponRankID # Staffs also use WeaponRankID
# from src.character_system.unit_instance import UnitInstance # For UserStats in CalculateRange

# --- Mirrored Enums and Data Classes from other test files / future item.py ---
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
        if not isinstance(min_range, int) or min_range <= 0: # Staves can have 0 range for self-target? Spec says >0 for RangeData. Assume 1 for now.
            raise ValueError("MinRange must be a positive integer.")
        if not isinstance(max_range, int) or max_range < min_range:
            raise ValueError("MaxRange must be an integer and not less than MinRange.")
        self.min_range = min_range
        self.max_range = max_range

class WeaponRankID(Enum): # Staffs use this for rank
    E_Rank = "E"
    D_Rank = "D"
    C_Rank = "C"
    B_Rank = "B"
    A_Rank = "A"
    S_Rank = "S"
    PRF_Rank = "PRF"

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
        if not isinstance(uses, int) or (uses < 0 and uses != -1):
            raise ValueError("Uses must be a non-negative integer or -1 for infinite.")
        if not isinstance(max_uses, int) or (max_uses < 0 and max_uses != -1) or \
           (max_uses != -1 and uses > max_uses and uses != -1 and max_uses !=0 ):
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
    @classmethod
    def reset_item_ids_for_test(cls):
        cls._existing_item_ids.clear()
    def __del__(self):
        if hasattr(self, 'item_id') and self.item_id in Item._existing_item_ids:
            Item._existing_item_ids.remove(self.item_id)

# --- Enums specific to Staff ---
class StaffEffectType(Enum):
    HealSingleFixed = "HealSingleFixed"
    HealSingleUserMag = "HealSingleUserMag"
    HealAreaFixed = "HealAreaFixed"
    Fortify = "Fortify"
    RestoreSingle = "RestoreSingle"
    RestoreAllInRange = "RestoreAllInRange"
    SilenceTarget = "SilenceTarget"
    SleepTarget = "SleepTarget"
    BerserkTarget = "BerserkTarget"
    WarpAlly = "WarpAlly"
    RescueAlly = "RescueAlly"
    RewarpSelf = "RewarpSelf"
    Unlock = "Unlock"
    RepairItem = "RepairItem"
    TorchStaff = "TorchStaff"
    Barrier = "Barrier"
    Hammerne = "Hammerne"
    ThiefStaff = "ThiefStaff"
    # Add other specific Thracia 776 staff effects as identified

# --- Staff Class (Minimal Placeholder) ---
class Staff(Item):
    def __init__(self, item_id: str, name: str, uses: int, max_uses: int, cost: int, icon_id: str, description: str,
                 effect: StaffEffectType, effect_potency: int, item_range: RangeData,
                 required_rank: WeaponRankID, experience_gain: int):

        self._is_reinitializing_for_test = True # Allow re-init for testing
        super().__init__(item_id, name, ItemType.Staff, uses, max_uses, cost, icon_id, description)
        del self._is_reinitializing_for_test

        if not isinstance(effect, StaffEffectType):
            raise ValueError("Effect must be a valid StaffEffectType.")
        if not isinstance(effect_potency, int): # Potency can be 0 or negative for some effects? Assume non-negative for now.
            raise ValueError("EffectPotency must be an integer.")
        if not isinstance(item_range, RangeData):
            raise ValueError("Range must be a valid RangeData object.")
        if not isinstance(required_rank, WeaponRankID):
            raise ValueError("RequiredRank must be a valid WeaponRankID.")
        if not isinstance(experience_gain, int) or experience_gain < 0:
            raise ValueError("ExperienceGain must be a non-negative integer.")

        self.effect = effect
        self.effect_potency = effect_potency
        self.range = item_range # This might be a base range, overridden by CalculateRange
        self.required_rank = required_rank
        self.experience_gain = experience_gain

    def calculate_range(self, user_stats) -> RangeData:
        # Placeholder for actual range calculation logic
        # e.g., if self.effect == StaffEffectType.HealAreaUserMag:
        # return RangeData(1, user_stats.magic // 2)
        # For now, returns the base item_range
        if user_stats is None: # Replace with actual UserStats check
            # Potentially return a default/error range or raise error
            return self.range # Or specific handling for no user
        return self.range # Default to fixed range if no specific logic

# --- Mock UserStats for testing calculate_range ---
class MockUserStats:
    def __init__(self, magic: int):
        self.magic = magic

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def basic_staff_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "HealStaff", "name": "Heal", "uses": 30, "max_uses": 30, "cost": 600,
        "icon_id": "heal_icon", "description": "Restores a small amount of HP to an ally.",
        "effect": StaffEffectType.HealSingleFixed, "effect_potency": 10, # Heals 10 HP
        "item_range": RangeData(1, 1), "required_rank": WeaponRankID.E_Rank, "experience_gain": 10
    }

@pytest.fixture(scope="function")
def mag_based_staff_data():
    Item.reset_item_ids_for_test()
    return {
        "item_id": "PhysicStaff", "name": "Physic", "uses": 15, "max_uses": 15, "cost": 1000,
        "icon_id": "physic_icon", "description": "Restores HP to a distant ally. Range based on MAG.",
        "effect": StaffEffectType.HealAreaFixed, # Or a specific Mag-based range type
        "effect_potency": 15,
        "item_range": RangeData(1, 5), # Base range, to be modified by calculate_range
        "required_rank": WeaponRankID.D_Rank, "experience_gain": 12
    }

# --- Test Cases for Staff Class ---
class TestStaffCreation:
    def test_staff_create_valid(self, basic_staff_data):
        staff = Staff(**basic_staff_data)
        assert staff.item_id == "HealStaff"
        assert staff.name == "Heal"
        assert staff.item_type == ItemType.Staff # Set by Staff class init
        assert staff.effect == StaffEffectType.HealSingleFixed
        assert staff.effect_potency == 10
        assert staff.range.min_range == 1 and staff.range.max_range == 1
        assert staff.required_rank == WeaponRankID.E_Rank
        assert staff.experience_gain == 10
        assert staff.uses == 30

    def test_staff_effect_validation(self, basic_staff_data):
        # TEST: Effect must be a valid StaffEffectType. (from spec)
        data = basic_staff_data.copy()
        data["item_id"] = "StaffTest1"
        with pytest.raises(ValueError, match="Effect must be a valid StaffEffectType."):
            Staff(**{**data, "effect": "NotAnEffect"})

    def test_staff_required_rank_validation(self, basic_staff_data):
        # TEST: RequiredRank must be a valid WeaponRankID. (from spec)
        data = basic_staff_data.copy()
        data["item_id"] = "StaffTest2"
        with pytest.raises(ValueError, match="RequiredRank must be a valid WeaponRankID."):
            Staff(**{**data, "required_rank": "NotARank"})

    def test_staff_potency_validation(self, basic_staff_data):
        data = basic_staff_data.copy()
        data["item_id"] = "StaffTest3"
        with pytest.raises(ValueError, match="EffectPotency must be an integer."):
            Staff(**{**data, "effect_potency": "invalid"})
        # Consider if potency can be negative or zero for some staves. Assuming non-negative for now.

    def test_staff_experience_gain_validation(self, basic_staff_data):
        data = basic_staff_data.copy()
        data["item_id"] = "StaffTest4"
        with pytest.raises(ValueError, match="ExperienceGain must be a non-negative integer."):
            Staff(**{**data, "experience_gain": -5})

    def test_staff_range_validation(self, basic_staff_data):
        data = basic_staff_data.copy()
        data["item_id"] = "StaffTest5"
        with pytest.raises(ValueError, match="Range must be a valid RangeData object."):
            Staff(**{**data, "item_range": "not_range"})


class TestStaffMethods:
    def test_staff_calculate_range_placeholder(self, basic_staff_data):
        # TEST: Range calculation must be correct. (from spec)
        # This test uses the placeholder implementation which returns base range.
        staff = Staff(**basic_staff_data)
        mock_user = MockUserStats(magic=10)
        calculated_range = staff.calculate_range(mock_user)
        assert calculated_range.min_range == basic_staff_data["item_range"].min_range
        assert calculated_range.max_range == basic_staff_data["item_range"].max_range

    @pytest.mark.skip(reason="Requires actual implementation of calculate_range with MAG dependency")
    def test_staff_calculate_range_mag_based(self, mag_based_staff_data):
        # This test would be for a staff whose range *actually* depends on MAG.
        # The current placeholder Staff.calculate_range doesn't implement this.
        # staff = Staff(**mag_based_staff_data)
        # user_low_mag = MockUserStats(magic=4) # e.g. Mag/2 = 2
        # user_high_mag = MockUserStats(magic=20) # e.g. Mag/2 = 10

        # Assuming a staff effect that has range Mag/2, min 1
        # range_low = staff.calculate_range(user_low_mag)
        # assert range_low.min_range == 1
        # assert range_low.max_range == 2 # Example: Mag/2

        # range_high = staff.calculate_range(user_high_mag)
        # assert range_high.min_range == 1
        # assert range_high.max_range == 10 # Example: Mag/2
        pass

    def test_staff_calculate_range_no_user(self, basic_staff_data):
        staff = Staff(**basic_staff_data)
        # Test behavior when no user_stats are provided (e.g., viewing staff info outside of unit context)
        # Current placeholder returns base range. This might need specific handling.
        calculated_range = staff.calculate_range(None)
        assert calculated_range.min_range == basic_staff_data["item_range"].min_range
        assert calculated_range.max_range == basic_staff_data["item_range"].max_range


# --- Test Cases for StaffEffectType Enum ---
class TestStaffEffectTypeEnum:
    def test_staff_effect_type_values(self):
        assert StaffEffectType.HealSingleFixed.value == "HealSingleFixed"
        assert StaffEffectType.WarpAlly.value == "WarpAlly"
        # Add more checks if necessary

# --- TDD Anchors from Spec ---
@pytest.mark.skip(reason="Requires UnitInstance and game state for healing effect")
def test_staff_heal_correct_amount(basic_staff_data):
    # TEST: Staff_Heal_CorrectAmount: Healing staff restores the correct amount of HP.
    # staff = Staff(**basic_staff_data)
    # target_unit = MockUnitInstance(current_hp=5, max_hp=20)
    # healer_unit = MockUnitInstance()
    # game_context.apply_staff_effect(healer_unit, staff, target_unit)
    # assert target_unit.current_hp == 15 # 5 + 10
    pass

@pytest.mark.skip(reason="Requires UnitInstance with Magic stat and specific staff logic")
def test_staff_range_mag_based(mag_based_staff_data):
    # TEST: Staff_Range_MagBased: Staff range is correctly calculated based on user's Magic stat.
    # This is covered by test_staff_calculate_range_mag_based once implemented.
    pass