import pytest

from src.character_system.game_class import GameClass # WeaponRankEntry removed as it's imported from weapon_rank
from src.character_system.weapon_rank import WeaponRankEntry, WeaponTypeID, RankLevel

# Dummy types for now, replace with actual imports when available
ClassID = str # Should be from game_class or a common types file
ItemID = str  # Should be from item_system or a common types file
SkillID = str # Should be from skill or a common types file
MovementTypeID = str # Should be from map_system or a common types file


class TestGameClass:
    def test_game_class_create_valid(self):
        """
        // TEST: Class_Create_Valid: Successfully creates a game class with valid base data.
        // TEST: ClassID must be unique. (Uniqueness handled by manager, not class itself)
        // TEST: Name must not be empty. (Tested in test_game_class_name_not_empty)
        """
        base_stats_dict = {"HP": 18, "Strength": 4, "Magic": 0, "Skill": 5, "Speed": 6, "Luck": 2, "Defense": 3, "Constitution": 7, "Movement": 5}
        max_stats_dict = {"HP": 60, "Strength": 20, "Magic": 20, "Skill": 20, "Speed": 20, "Luck": 30, "Defense": 20, "Constitution": 20, "Movement": 15}
        class_growths_dict = {"HP": 70, "Strength": 30, "Magic": 5, "Skill": 40, "Speed": 35, "Luck": 20, "Defense": 15, "Constitution": 10, "Movement": 0} # Added movement growth

        game_class = GameClass(
            class_id="Swordfighter",
            name_str="Swordfighter",
            promotion_info={"PromotesToClassID": "Myrmidon", "PromotionItem": None},
            base_stats_dict=base_stats_dict,
            max_stats_dict=max_stats_dict,
            class_growths_dict=class_growths_dict,
            class_skills=[],
            movement_type="Infantry",
            weapon_ranks=[WeaponRankEntry(WeaponTypeID.SWORD, RankLevel.E, RankLevel.A)],
            mounted_info={"IsMounted": False, "DismountedClassID": None}
        )
        assert game_class is not None
        assert game_class.id == "Swordfighter"
        assert game_class.name == "Swordfighter"
        assert game_class.base_hp == 18
        assert game_class.max_movement == 15
        assert game_class.growth_speed == 35
        assert game_class.movement_type == "Infantry"
        assert not game_class.is_mounted

    @pytest.mark.skip(reason="GameClass ID uniqueness enforcement handled by a manager class, not yet implemented.")
    def test_game_class_id_unique(self):
        """
        // TEST: ClassID must be unique.
        Similar to Character, this might be managed by a higher-level system.
        """
        # manager = ClassManager()
        # manager.add_class(GameClass(ID="UniqueClass1", ...))
        # with pytest.raises(SomeUniquenessError):
        #     manager.add_class(GameClass(ID="UniqueClass1", ...))
        pass # Skipped by decorator

    def test_game_class_name_not_empty(self):
        """
        // TEST: Name must not be empty.
        """
        base_stats = {"HP": 18, "Strength": 4, "Magic": 0, "Skill": 5, "Speed": 6, "Luck": 2, "Defense": 3, "Constitution": 7, "Movement": 5}
        max_stats_dict = {"HP": 60, "Strength": 20, "Magic": 20, "Skill": 20, "Speed": 20, "Luck": 30, "Defense": 20, "Constitution": 20, "Movement": 15}
        with pytest.raises(ValueError, match="Class Name must not be empty."):
            GameClass(
                class_id="SomeID",
                name_str="",
                promotion_info={}, base_stats_dict=base_stats, max_stats_dict=max_stats_dict, class_growths_dict={},
                class_skills=[], movement_type="Infantry", weapon_ranks=[], mounted_info={"IsMounted": False}
            )

    @pytest.mark.skip(reason="PromotesToClassID validation requires a class management/validation system, not yet implemented.")
    def test_game_class_promotes_to_valid_class_id_or_null(self):
        """
        // TEST: PromotesToClassID must be a valid ClassID or null.
        """
        # GameClass(PromotionInfo={"PromotesToClassID": "ValidClass", ...}) # Should pass if ValidClass exists
        # GameClass(PromotionInfo={"PromotesToClassID": None, ...}) # Should pass
        # with pytest.raises(InvalidClassIDError):
        #     GameClass(PromotionInfo={"PromotesToClassID": "InvalidClassXXX", ...})
        pass # Skipped by decorator

    @pytest.mark.skip(reason="PromotionItem validation requires Item system, not yet implemented.")
    def test_game_class_promotion_item_valid_or_null(self):
        """
        // TEST: PromotionItem must be a valid ItemID or null.
        """
        # GameClass(PromotionInfo={"PromotionItem": "KnightCrest", ...}) # Should pass if ItemID is valid
        # GameClass(PromotionInfo={"PromotionItem": None, ...}) # Should pass
        # with pytest.raises(InvalidItemIDError):
        #     GameClass(PromotionInfo={"PromotionItem": "InvalidItemXXX", ...})
        pass # Skipped by decorator

    def test_game_class_max_stats_ge_base_stats(self):
        """
        // TEST: Max stats must be >= base stats.
        """
        base_stats_ok = {"HP": 20, "Strength": 10}
        max_stats_ok = {"HP": 20, "Strength": 11, "Movement": 10} # Movement only in max_stats
        base_stats_bad = {"HP": 20, "Strength": 10}
        max_stats_bad = {"HP": 19, "Strength": 10} # HP max < base

        # Valid: Max HP == Base HP, Max Strength > Base Strength
        GameClass(
            class_id="TestClass1", name_str="Test Class 1", promotion_info={},
            base_stats_dict=base_stats_ok, max_stats_dict=max_stats_ok, class_growths_dict={},
            class_skills=[], movement_type="Infantry", weapon_ranks=[], mounted_info={"IsMounted": False}
        )

        # GameClass __init__ now populates all stats with defaults if missing,
        # so the "missing stat" cases are covered by the direct comparison.
        # The ValueError for max_stat < base_stat is still relevant.
        # The match string for ValueError should be updated to reflect internal stat keys.
        with pytest.raises(ValueError, match="MaxStat for hp \\(19\\) in class TestClassBad must be greater than or equal to BaseStat \\(20\\)."):
            GameClass(
                class_id="TestClassBad", name_str="Test Class Bad", promotion_info={},
                base_stats_dict=base_stats_bad, max_stats_dict=max_stats_bad, class_growths_dict={},
                class_skills=[], movement_type="Infantry", weapon_ranks=[], mounted_info={"IsMounted": False}
            )
        
        # These cases are now implicitly handled by the default stat initialization in GameClass.
        # If a stat is not in the input dict, it gets a default (0 for base/growth, specific for max).
        # The max_stat >= base_stat check will then use these initialized values.
        # For example, if "Strength" is in base_stats_dict but not max_stats_dict,
        # self.max_strength will get a default from DEFAULT_MAX_STATS, and self.base_strength from input.
        # The check self.max_strength >= self.base_strength will proceed.

        # Example: Strength base 10, default max_strength 20. 20 >= 10 is true.
        GameClass(
            class_id="TestClassMissingMaxStatAllowed", name_str="Test Missing Max Stat Allowed", promotion_info={},
            base_stats_dict={"Strength": 10, "HP": 20}, max_stats_dict={"HP": 20}, class_growths_dict={},
            class_skills=[], movement_type="Infantry", weapon_ranks=[], mounted_info={"IsMounted": False}
        )

        # Example: Movement max 5, default base_movement 0. 5 >= 0 is true.
        GameClass(
            class_id="TestClassMissingBaseStatAllowed", name_str="Test Missing Base Stat Allowed", promotion_info={},
            base_stats_dict={"HP": 10}, max_stats_dict={"HP": 20, "Movement": 5}, class_growths_dict={},
            class_skills=[], movement_type="Infantry", weapon_ranks=[], mounted_info={"IsMounted": False}
        )


    @pytest.mark.skip(reason="MovementType validation requires MovementType system/enum, not yet implemented.")
    def test_game_class_valid_movement_type(self):
        """
        // TEST: MovementType must be a valid MovementTypeID.
        """
        # with pytest.raises(InvalidMovementTypeError):
        #     GameClass(MovementType="InvalidMovementType", ...)
        pass # Skipped by decorator

    def test_game_class_dismounted_class_id_valid_if_mounted(self):
        """
        // TEST: DismountedClassID must be valid if class is mounted.
        """
        base_stats = {"HP": 18}
        max_stats = {"HP": 60}
        # OK: Mounted with DismountedClassID
        GameClass(
            class_id="MountedClass", name_str="Mounted Class", promotion_info={},
            base_stats_dict=base_stats, max_stats_dict=max_stats, class_growths_dict={}, class_skills=[], movement_type="Mounted",
            weapon_ranks=[], mounted_info={"IsMounted": True, "DismountedClassID": "ValidInfantryClass"}
        )
        # OK: Not mounted, DismountedClassID is None
        GameClass(
            class_id="InfantryClass", name_str="Infantry Class", promotion_info={},
            base_stats_dict=base_stats, max_stats_dict=max_stats, class_growths_dict={}, class_skills=[], movement_type="Infantry",
            weapon_ranks=[], mounted_info={"IsMounted": False, "DismountedClassID": None}
        )
        # OK: Not mounted, DismountedClassID is also provided (though perhaps unusual, not invalid by current rule)
        GameClass(
            class_id="InfantryClass2", name_str="Infantry Class 2", promotion_info={},
            base_stats_dict=base_stats, max_stats_dict=max_stats, class_growths_dict={}, class_skills=[], movement_type="Infantry",
            weapon_ranks=[], mounted_info={"IsMounted": False, "DismountedClassID": "SomeOtherClass"}
        )

        # Fail: Mounted but DismountedClassID is None
        with pytest.raises(ValueError, match="Mounted class 'MountedNoDismount' must have a DismountedClassID if IsMounted is True."):
           GameClass(
                class_id="MountedNoDismount", name_str="Mounted No Dismount", promotion_info={},
                base_stats_dict=base_stats, max_stats_dict=max_stats, class_growths_dict={}, class_skills=[], movement_type="Mounted",
                weapon_ranks=[], mounted_info={"IsMounted": True, "DismountedClassID": None}
            )
        # Fail: Mounted but MountedInfo doesn't contain DismountedClassID
        with pytest.raises(ValueError, match="Mounted class 'MountedNoDismountKey' must have a DismountedClassID if IsMounted is True."):
           GameClass(
                class_id="MountedNoDismountKey", name_str="Mounted No Dismount Key", promotion_info={},
                base_stats_dict=base_stats, max_stats_dict=max_stats, class_growths_dict={}, class_skills=[], movement_type="Mounted",
                weapon_ranks=[], mounted_info={"IsMounted": True} # Missing DismountedClassID key
            )


    def test_game_class_weapon_ranks_valid(self):
        """
        Test for valid WeaponRankEntry in WeaponRanks.
        This will depend on WeaponRankEntry tests.
        """
        valid_rank_entry = WeaponRankEntry(weapon_type=WeaponTypeID.SWORD, initial_rank=RankLevel.E, max_rank_in_class=RankLevel.A)
        game_class = GameClass(
            class_id="TestClassRanks", name_str="Test Class Ranks", promotion_info={},
            base_stats_dict={"HP": 10}, max_stats_dict={"HP": 60}, class_growths_dict={},
            class_skills=[], movement_type="Infantry",
            weapon_ranks=[valid_rank_entry],
            mounted_info={"IsMounted": False}
        )
        assert game_class.weapon_ranks is not None
        assert len(game_class.weapon_ranks) == 1
        assert game_class.weapon_ranks[0].weapon_type == WeaponTypeID.SWORD # Check against enum member

        # Test with empty list
        game_class_no_ranks = GameClass(
            class_id="TestClassNoRanks", name_str="Test Class No Ranks", promotion_info={},
            base_stats_dict={"HP": 10}, max_stats_dict={"HP": 60}, class_growths_dict={},
            class_skills=[], movement_type="Infantry",
            weapon_ranks=[], # Empty list
            mounted_info={"IsMounted": False}
        )
        assert game_class_no_ranks.weapon_ranks is not None
        assert len(game_class_no_ranks.weapon_ranks) == 0

        # Test with multiple entries
        rank_entry_axe = WeaponRankEntry(weapon_type=WeaponTypeID.AXE, initial_rank=RankLevel.D, max_rank_in_class=RankLevel.S)
        game_class_multi_ranks = GameClass(
            class_id="TestClassMultiRanks", name_str="Test Class Multi Ranks", promotion_info={},
            base_stats_dict={"HP": 10}, max_stats_dict={"HP": 60}, class_growths_dict={},
            class_skills=[], movement_type="Infantry",
            weapon_ranks=[valid_rank_entry, rank_entry_axe],
            mounted_info={"IsMounted": False}
        )
        assert game_class_multi_ranks.weapon_ranks is not None
        assert len(game_class_multi_ranks.weapon_ranks) == 2