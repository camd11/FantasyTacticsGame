import pytest

from src.character_system.weapon_rank import WeaponRankEntry, RankLevel, WeaponTypeID

class TestWeaponRankEntry:
    def test_weapon_rank_entry_creation_valid(self):
        """
        // TEST: InitialRank and MaxRankInClass must be valid RankLevel values.
        // TEST: MaxRankInClass must be >= InitialRank if InitialRank is not None.
        """
        # entry = WeaponRankEntry(
        #     WeaponType="Sword", # Placeholder for WeaponTypeID
        #     InitialRank=RankLevel.E,
        #     MaxRankInClass=RankLevel.A
        # )
        # assert entry.WeaponType == "Sword"
        # assert entry.InitialRank == RankLevel.E
        # assert entry.MaxRankInClass == RankLevel.A
        entry = WeaponRankEntry(
            weapon_type=WeaponTypeID.SWORD,
            initial_rank=RankLevel.E,
            max_rank_in_class=RankLevel.A
        )
        assert entry.weapon_type == WeaponTypeID.SWORD
        assert entry.initial_rank == RankLevel.E
        assert entry.max_rank_in_class == RankLevel.A

    def test_weapon_rank_entry_invalid_initial_rank(self):
        """
        // TEST: InitialRank and MaxRankInClass must be valid RankLevel values.
        """
        with pytest.raises(TypeError): # Changed from ValueError due to implementation
            WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank="InvalidRank", max_rank_in_class=RankLevel.A)

    def test_weapon_rank_entry_invalid_max_rank(self):
        """
        // TEST: InitialRank and MaxRankInClass must be valid RankLevel values.
        """
        with pytest.raises(TypeError): # Changed from ValueError due to implementation
            WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank=RankLevel.E, max_rank_in_class="InvalidRank")

    def test_weapon_rank_entry_max_rank_lt_initial_rank(self):
        """
        // TEST: MaxRankInClass must be >= InitialRank if InitialRank is not None.
        """
        with pytest.raises(ValueError):
            WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank=RankLevel.A, max_rank_in_class=RankLevel.E)

    def test_weapon_rank_entry_max_rank_eq_initial_rank(self):
        """
        MaxRankInClass can be equal to InitialRank.
        """
        entry = WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank=RankLevel.C, max_rank_in_class=RankLevel.C)
        assert entry.max_rank_in_class == entry.initial_rank

    def test_weapon_rank_entry_initial_rank_none(self):
        """
        Test case where InitialRank is None. MaxRankInClass can be anything or also None.
        """
        entry1 = WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank=RankLevel.NONE, max_rank_in_class=RankLevel.A)
        assert entry1.initial_rank == RankLevel.NONE
        assert entry1.max_rank_in_class == RankLevel.A

        entry2 = WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank=RankLevel.NONE, max_rank_in_class=RankLevel.NONE)
        assert entry2.initial_rank == RankLevel.NONE
        assert entry2.max_rank_in_class == RankLevel.NONE

class TestRankLevelEnum:
    def test_rank_level_order(self):
        """Test the order of rank levels if they are comparable."""
        # This assumes RankLevel enum values might have inherent order or comparison logic.
        # If they are just simple enum members, direct comparison might not be meaningful
        # without explicit value assignment or a helper function.
        # For now, this is a conceptual test.
        assert RankLevel.S > RankLevel.A
        assert RankLevel.A > RankLevel.B
        assert RankLevel.B > RankLevel.C
        assert RankLevel.C > RankLevel.D
        assert RankLevel.D > RankLevel.E
        assert RankLevel.E > RankLevel.NONE # RankLevel.NONE is lowest due to IntEnum

    def test_rank_level_members_exist(self):
        """Ensure all specified rank levels exist in the enum."""
        levels = ["NONE", "E", "D", "C", "B", "A", "S"] # Enum members are uppercase
        for level_name in levels:
            assert hasattr(RankLevel, level_name)

        # Test WeaponTypeID members
        weapon_types = ["SWORD", "LANCE", "AXE", "BOW", "FIRE", "THUNDER", "WIND", "LIGHT", "DARK", "STAFF"]
        for wt_name in weapon_types:
            assert hasattr(WeaponTypeID, wt_name)