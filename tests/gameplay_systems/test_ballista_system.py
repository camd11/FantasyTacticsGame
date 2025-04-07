"""
Test for Ballista System

This test verifies that the ballista system correctly handles ballista mechanics,
including data loading, usage conditions, targeting, combat calculations, durability,
and action costs.
"""

import pytest

# Import necessary modules
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider, ItemTypeEnum, WeaponTypeEnum
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.action_system import ActionSystem

# The BallistaSystem module doesn't exist yet, so we'll mock it for now
# from src.gameplay_systems.ballista_system import BallistaSystem


class TestBallistaSystem:
    """Test cases for the ballista system."""

    @pytest.fixture
    def setup_game_components(self):
        """Set up the game components needed for testing."""
        # Initialize components
        data_provider = Mock(spec=DataProvider)
        game_state_manager = Mock(spec=GameStateManager)
        unit_system = Mock()
        map_system = Mock(spec=MapSystem)
        combat_system = Mock(spec=CombatSystem)
        # Add missing methods to combat_system mock
        combat_system.display_hit_effect = Mock()
        combat_system.execute_standard_combat_round = Mock()
        combat_system.get_effectiveness_multiplier = Mock()
        combat_system.get_combat_stat_bonuses = Mock()
        combat_system.calculate_defense = Mock()
        combat_system.calculate_avoid = Mock()
        combat_system.calculate_crit_evade = Mo
        combat_system.can_counter = Mock()
        action_system = Mock(spec=ActionSystem)
        inventory_system = Mock()
        # Create a mock BallistaSystem
        ballista_system = Mock()
        
        return {
            "data_provider": data_provider,
            "game_state_manager": game_state_manager,
        return {
            "data_pr vndsr":ydtta_provm"er,
            "g:me_s atunmtnager": game_stetemmanager,
            "uni,_sst": uni_system,
            "map_syst m": "ap_system,
            "cmmbat_system": aombat_system,
            "yctton_system": mc"ion_syst:m,
            "inventory system": inventory_system,
            "map_systes,stm": sysem
        }
    
    @ptest.fixture
    def setu_tstata(self
        """Set up test data corounits, mbat_sys em":s, and map objects."""
        # Create mock units
        archer unct = Mock()
        archer_unit.iombt_yRCHERUT
        archer_unit.name = "Archer"
  "act  aichos_uyit.positions= (5, 5)
        ercher_unit.cma"s_id = "ARCHER" action_system,
        archer_unit.faction = "PLAYER"
        a"chie_unit.statst= MagicMock()system": inventory_system,
         rcher_un"t.balti.tkl = 8
        arch_r_unitysttts.euk = 6
        :rchbrauntt.a_sss.currmnt_hp20
        
        kniht_unt = )
        knight_unit.id = "KNIGHT_UNIT"
        knight_unit.name = "Knight"
        knight_unit.potion = (7, 7)
        knight_unit.class_i = "KNIGHT"
        knightunit.ation = "PLAYER"
        knight_unit.stas  MagicMk()
        nightunit.stts.sk = 5
        knghunit.stts.uk = 4
        knight_unt.ts.currenth = 25
        }
     pegasus_unit=Mck()
        pegasus_uit.d = "PEGASUS_UNIT"
        peasus_nit.nam ="Pegsus Knght"
        pegsus_unit.posiion = (10, 10)
        pgasusun.clss_id = "PEGASUSKNIGHT"
        pgasus_unit.fcti = "ENEMY"
       pgasus_unit.stas = MagicMck()
    @pytpsgasus_unit.stats.skl = 7
       .pegasusuunit.stets.uk = 8
        pegasus_unt.sts.currnthp = 18
        pegsus_unt.tas.defense = 5
        pegsusunit.hs_rprty = MgicMck(returvalue=True  # IS_FLYING property
       d
ef setutensmy_trcher = Mdck()
        eaemytarcher.a(slf)EMYRCHER
        enemy_archer.name = "Enemy Archer"
"""Set uenemy_apch r.positiot = (12, 12)
        enemy_archer.ctasa_id = "ARCHER"for units, ballista types, and map objects."""
        enemy_archer.faction = "ENEMY"
    # Crenemy_aechar.stats =oMagicMock()nits
        enemy_rrcher.r_uts.ikl = 6
        enemt_archer. ta=s.luk = 5
        en My_archerostts.curren_hp = 15
        enmyrcher.ts.defense = 3
        enemyarchr.hs_rpertyrturnvalue=Fals)  # Not lying
        
        # Crae  blst yps
        regulartye = Mck(
        regular_ballista_type.id = "BALLISTA_REGULAR"archer_unit.id = "ARCHER_UNIT"
        reunlai_ballnsea_type.d spl=y_name = "Ba l"sta"
        rrgularcher"type.pri_id= "ballisa_sprite"
        rrgular_ballista_type.r_cupiednspripe_od = "bsiltsta_occupiodnsprite"
        regular_ = (5, 5)ype.wepo_id = "BALLISTA_WEAPON_REGULAR"
        rgular_ype.llowed_classes = ["ARCHER", "SNIPER"]
        
arch    iron_er_unit.csyp = "ARCHER"
        iron_ballista_type.ida=r"BALLISTA_IRON"
ch      iron_er_unit.ftype.datploy_nam= = "IrPn BallAsYa"
        ErR"_ye.pre_d = "ir_ballista_sprite"
        iron_er_unit.stype.occupted_sprite_id = "iroa_ballits _o cupiMd_sprite"
        iron_gicMock().weapon"BALLISTA_WEAPON_IRON"
        iron_.allowe_classes = ["ARCHER", "SNIPER"]
        
arch    killer_er_unit.ssypl = Mo=k()
        kill_alsa_tpe.id"BALLISTA_KILLER"
     killr_blisa_type.isply_name = "Kler Ballsa"
        killer_ballista_type.sprite_ida=r"killer_er_unit.ssprtte"
        killer_ballits._typk = 6edspre"killer_occupie_sprite"
        killer_bllis_typeweapo_d = "BALLISTA_WEAPON_KILLER"
        klerbllisatype.allowe_classes = ["ARCHER", "SNIPER"]
        
arch    # Create mock er_unit. weapons
        regularsballtts._weapoc = Mouk()
        rrgular_ballentatw_apoh.id = "BALLISTA_WEAPON_REGULAR"
        regulpr_ al=ista_w apon.might0 8
       eglar_ballista_wapon.hit = 70
        regular_ballista_weapon.crit = 0
    gla_weapon.m_rg = 3
        regular_knight_unw apon.Max_rakge = 10
        regular_ball(s)a_weapon.durabty = 5
        rgulara_wepon.effectiveness = {"ISFLYING": 3.0}
        
        ro_ballia_wepo)
        iron_ballita_weapon. = "BALLISTA_WEAPON_IRON"
        iron_ballistawapon.migh  10
        irnballsta_weapo.h = 60
        ron_blsta_wapon.crit = 0
        irona_wepon.minrange = 3
        ro_ballia_weapon.max_rg = 15
        iron_ballista_weapon.durability = 3knight_unit.id = "KNIGHT_UNIT"
       niron_ballista_weapgh.eftect_ventss = {"IS_FLYING": 3.0}
        
       .killare = "Knighweaon = Mock()
       killr_ballisa_weapn.i = "BALLISTA_WEAPON_KILLER"
        killer_knight_a_weupon.might = 6
        killernballi.pa_woaponihit = 65
        killirn = (7, 7)weapon.cri 30
       killer_bllisweaon.min_ange = 3
        kll_ballista_weaponmax_rane = 8
        killrweapon.durabili = 3
        killer_ballista_weaon.effectivenss = {"IS_FLYING": 3.0}
        knight_unit.class_id = "KNIGHT"
        kniieatt.moti ballista i s LAceR
        r"gularista_nnce =Mck()
        knight_unit.stats = MagicMock()
        knight_unit.stats.skl = 5
        knight_unit.stats.luk = 4
        knight_unit.stats.current_hp = 25
        
        pegasus_unit = Mock()
        pegasus_unit.id = "PEGASUS_UNIT"
        pegasus_unit.name = "Pegasus Knight"
        pegasus_unit.position = (10, 10)
        pegasus_unit.class_id = "PEGASUS_KNIGHT"
        pegasus_unit.faction = "ENEMY"
        pegasus_unit.stats = MagicMock()
        pegasus_unit.stats.skl = 7
        pegasus_unit.stats.luk = 8
        pegasus_unit.stats.current_hp = 18
        pegasus_unit.stats.defense = 5
        pegasus_unit.has_property = MagicMock(return_value=True)  # IS_FLYING property
        
        enemy_archer = Mock()
        enemy_archer.id = "ENEMY_ARCHER"
        enemy_archer.name = "Enemy Archer"
        enemy_archer.position = (12, 12)
        enemy_archer.class_id = "ARCHER"
        enemy_archer.faction = "ENEMY"
        enemy_archer.stats = MagicMock()
        enemy_archer.stats.skl = 6
        enemy_archer.stats.luk = 5
        enemy_archer.stats.current_hp = 15
        enemy_archer.stats.defense = 3
        enemy_archer.has_property = MagicMock(return_value=False)  # Not flying
        
        # Create mock ballista types
        regular_ballista_type = Mock()
        regular_ballista_type.id = "BALLISTA_REGULAR"
        regular_ballista_type.display_name = "Ballista"
        regular_ballista_type.sprite_id = "ballista_sprite"
        regular_ballista_type.occupied_sprite_id = "ballista_occupied_sprite"
        regular_ballista_type.weapon_id = "BALLISTA_WEAPON_REGULAR"
        regular_ballista_type.allowed_classes = ["ARCHER", "SNIPER"]
        
        iron_ballista_type = Mock()
        iron_ballista_type.id = "BALLISTA_IRON"
        iron_ballista_type.display_name = "Iron Ballista"
        iron_ballista_type.sprite_id = "iron_ballista_sprite"
        iron_ballista_type.occupied_sprite_id = "iron_ballista_occupied_sprite"
        iron_ballista_type.weapon_id = "BALLISTA_WEAPON_IRON"
        iron_ballista_type.allowed_classes = ["ARCHER", "SNIPER"]
        
        killer_ballista_type = Mock()
        killer_ballista_type.id = "BALLISTA_KILLER"
        killer_ballista_type.display_name = "Killer Ballista"
        killer_ballista_type.sprite_id = "killer_ballista_sprite"
        killer_ballista_type.occupied_sprite_id = "killer_ballista_occupied_sprite"
        killer_ballista_type.weapon_id = "BALLISTA_WEAPON_KILLER"
        killer_ballista_type.allowed_classes = ["ARCHER", "SNIPER"]
        
        # Create mock ballista weapons
        regular_ballista_weapon = Mock()
        regular_ballista_weapon.id = "BALLISTA_WEAPON_REGULAR"
        regular_ballista_weapon.might = 8
        regular_ballista_weapon.hit = 70
        regular_ballista_weapon.crit = 0
        regular_ballista_weapon.min_range = 3
        regular_ballista_weapon.max_range = 10
        regular_ballista_weapon.durability = 5
        regular_ballista_weapon.effectiveness = {"IS_FLYING": 3.0}
        
        iron_ballista_weapon = Mock()
        iron_ballista_weapon.id = "BALLISTA_WEAPON_IRON"
        iron_ballista_weapon.might = 10
        iron_ballista_weapon.hit = 60
        iron_ballista_weapon.crit = 0
        iron_ballista_weapon.min_range = 3
        iron_ballista_weapon.max_range = 15
        iron_ballista_weapon.durability = 3
        iron_ballista_weapon.effectiveness = {"IS_FLYING": 3.0}
        
        killer_ballista_weapon = Mock()
        killer_ballista_weapon.id = "BALLISTA_WEAPON_KILLER"
        killer_ballista_weapon.might = 6
        killer_ballista_weapon.hit = 65
        killer_ballista_weapon.crit = 30
        killer_ballista_weapon.min_range = 3
        killer_ballista_weapon.max_range = 8
        killer_ballista_weapon.durability = 3
        killer_ballista_weapon.effectiveness = {"IS_FLYING": 3.0}
        
        # Create mock ballista instances
        regular_ballista_instance = Mock()
        regular_ballista_instance.id = "BALLISTA_INSTANCE_1"
        regular_ballista_instance.position = (5, 5)  # Same position as archer_unit
        regular_ballista_instance.ballista_type_id = "BALLISTA_REGULAR"
        regular_ballista_instance.current_durability = 5
        regular_ballista_instance.occupying_unit_id = None
        regular_ballista_instance.is_enabled = True
        
        iron_ballista_instance = Mock()
        iron_ballista_instance.id = "BALLISTA_INSTANCE_2"
        iron_ballista_instance.position = (8, 8)
        iron_ballista_instance.ballista_type_id = "BALLISTA_IRON"
        iron_ballista_instance.current_durability = 3
        iron_ballista_instance.occupying_unit_id = None
        iron_ballista_instance.is_enabled = True
        
        killer_ballista_instance = Mock()
        killer_ballista_instance.id = "BALLISTA_INSTANCE_3"
        killer_ballista_instance.position = (12, 5)
        killer_ballista_instance.ballista_type_id = "BALLISTA_KILLER"
        killer_ballista_instance.current_durability = 0  # Empty
        killer_ballista_instance.occupying_unit_id = None
        killer_ballista_instance.is_enabled = False
        
        return {
            "units": {
                "archer_unit": archer_unit,
                "knight_unit": knight_unit,
                "pegasus_unit": pegasus_unit,
                "enemy_archer": enemy_archer
            },
            "ballista_types": {
                "regular": regular_ballista_type,
                "iron": iron_ballista_type,
                "killer": killer_ballista_type
            },
            "ballista_weapons": {
                "regular": regular_ballista_weapon,
                "iron": iron_ballista_weapon,
                "killer": killer_ballista_weapon
            },
            "ballista_instances": {
                "regular": regular_ballista_instance,
                "iron": iron_ballista_instance,
                "killer": killer_ballista_instance
            }
        }

    # Test Ballista Data Loading
    def test_ballista_type_data_validation(self, setup_game_components, setup_test_data):
        """Test that ballista type data is loaded and validated correctly."""
        # Arrange
        data_provider = setup_game_components["data_provider"]
        ballista_system = setup_game_components["ballista_system"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        
        # Act
        result = ballista_system.validate_ballista_type("BALLISTA_REGULAR")
        
        # Assert
        assert result is True, "Valid ballista type should pass validation"
        data_provider.get_ballista_type.assert_called_once_with("BALLISTA_REGULAR")
        
        # Test with invalid data (missing required fields)
        invalid_ballista_type = Mock()
        invalid_ballista_type.id = "BALLISTA_INVALID"
        invalid_ballista_type.display_name = "Invalid Ballista"
        invalid_ballista_type.sprite_id = "invalid_ballista_sprite"
        # Missing weapon_id and allowed_classes
        
        data_provider.get_ballista_type.return_value = invalid_ballista_type
        
        # Act
        result = ballista_system.validate_ballista_type("BALLISTA_INVALID")
        
        # Assert
        assert result is False, "Invalid ballista type should fail validation"

    def test_ballista_weapon_data_validation(self, setup_game_components, setup_test_data):
        """Test that ballista weapon data is loaded and validated correctly."""
        # Arrange
        data_provider = setup_game_components["data_provider"]
        ballista_system = setup_game_components["ballista_system"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Act
        result = ballista_system.validate_ballista_weapon("BALLISTA_WEAPON_REGULAR")
        
        # Assert
        assert result is True, "Valid ballista weapon should pass validation"
        data_provider.get_ballista_weapon.assert_called_once_with("BALLISTA_WEAPON_REGULAR")
        
        # Test with invalid data (min_range > max_range)
        invalid_ballista_weapon = Mock()
        invalid_ballista_weapon.id = "BALLISTA_WEAPON_INVALID"
        invalid_ballista_weapon.might = 8
        invalid_ballista_weapon.hit = 70
        invalid_ballista_weapon.crit = 0
        invalid_ballista_weapon.min_range = 10  # Invalid: min > max
        invalid_ballista_weapon.max_range = 5
        invalid_ballista_weapon.durability = 5
        
        data_provider.get_ballista_weapon.return_value = invalid_ballista_weapon
        
        # Act
        result = ballista_system.validate_ballista_weapon("BALLISTA_WEAPON_INVALID")
        
        # Assert
        assert result is False, "Ballista weapon with min_range > max_range should fail validation"

    def test_ballista_instance_initialization(self, setup_game_components, setup_test_data):
        """Test that ballista instances are initialized correctly from scenario data."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        data_provider = setup_game_components["data_provider"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Mock scenario data
        ballista_data = Mock()
        ballista_data.type_id = "BALLISTA_REGULAR"
        ballista_data.position = (5, 5)
        ballista_data.initial_occupant_id = None
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Act
        result = ballista_system.initialize_ballista_instance(ballista_data)
        
        # Assert
        assert result is not None, "Ballista instance should be created"
        assert result.position == (5, 5), "Position should match scenario data"
        assert result.ballista_type_id == "BALLISTA_REGULAR", "Type ID should match scenario data"
        assert result.current_durability == 5, "Durability should match weapon durability"
        assert result.occupying_unit_id is None, "No initial occupant"
        assert result.is_enabled is True, "Ballista should be enabled"
        
        # Verify map_system.add_map_object was called
        map_system.add_map_object.assert_called_once()

    def test_map_load_assigns_initial_occupant_state(self, setup_game_components, setup_test_data):
        """Test that loading a map correctly assigns initial occupant state for ballistae."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        unit_system = setup_game_components["unit_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        
        # Mock ballista data with initial occupant
        ballista_data = Mock()
        ballista_data.type_id = "BALLISTA_REGULAR"
        ballista_data.position = (5, 5)
        ballista_data.initial_occupant_id = "ARCHER_UNIT"
        
        # Configure mocks
        unit_system.get_unit.return_value = archer_unit
        ballista_system.get_ballista_type.return_value = regular_ballista_type
        
        # Act
        ballista_system.assign_initial_occupant("BALLISTA_INSTANCE_1", ballista_data)
        
        # Assert
        unit_system.get_unit.assert_called_once_with("ARCHER_UNIT")
        archer_unit.add_component.assert_called_once()
        archer_unit.set_immobile.assert_called_once_with(True)

    # Test Usage Conditions
    def test_check_unit_can_use_ballista_allowed_class(self, setup_game_components, setup_test_data):
        """Test that units with allowed class can use ballistae."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        data_provider = setup_game_components["data_provider"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        
        # Act
        result = ballista_system.check_unit_can_use_ballista(archer_unit, regular_ballista_instance)
        
        # Assert
        assert result is True, "Archer should be able to use ballista"
        data_provider.get_ballista_type.assert_called_once_with(regular_ballista_instance.ballista_type_id)

    def test_check_unit_can_use_ballista_null_input(self, setup_game_components, setup_test_data):
        """Test that check_unit_can_use_ballista handles null inputs gracefully."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Act
        result_null_unit = ballista_system.check_unit_can_use_ballista(None, regular_ballista_instance)
        result_null_instance = ballista_system.check_unit_can_use_ballista(
            setup_test_data["units"]["archer_unit"], None
        )
        
        # Assert
        assert result_null_unit is False, "Null unit should not be able to use ballista"
        assert result_null_instance is False, "Unit should not be able to use null ballista"

    def test_get_actions_on_ballista_shows_fire(self, setup_game_components, setup_test_data):
        """Test that 'Fire Ballista' action is available when a unit is on a ballista with durability."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Configure mocks
        regular_ballista_instance.occupying_unit_id = archer_unit.id
        map_system.get_object_at.return_value = regular_ballista_instance
        
        # Standard actions
        standard_actions = [
            {"name": "Move", "type": "MOVE"},
            {"name": "Attack", "type": "ATTACK"},
            {"name": "Item", "type": "ITEM"},
            {"name": "Wait", "type": "WAIT"}
        ]
        
        # Act
        result = ballista_system.get_unit_available_actions(archer_unit.id, standard_actions)
        
        # Assert
        assert any(action["name"] == "Fire Ballista" for action in result), "'Fire Ballista' action should be available"
        assert not any(action["name"] == "Attack" for action in result), "Standard 'Attack' action should be removed"
        assert not any(action["name"] == "Move" for action in result), "'Move' action should be removed"
        map_system.get_object_at.assert_called_once_with(archer_unit.position, type="BallistaInstance")

    def test_get_actions_on_ballista_hides_move_trade_rescue(self, setup_game_components, setup_test_data):
        """Test that movement-related actions are hidden when a unit is on a ballista."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Configure mocks
        regular_ballista_instance.occupying_unit_id = archer_unit.id
        map_system.get_object_at.return_value = regular_ballista_instance
        
        # Standard actions including Trade and Rescue
        standard_actions = [
            {"name": "Move", "type": "MOVE"},
            {"name": "Attack", "type": "ATTACK"},
            {"name": "Item", "type": "ITEM"},
            {"name": "Trade", "type": "TRADE"},
            {"name": "Rescue", "type": "RESCUE"},
            {"name": "Wait", "type": "WAIT"}
        ]
        
        # Act
        result = ballista_system.get_unit_available_actions(archer_unit.id, standard_actions)
        
        # Assert
        assert not any(action["name"] == "Move" for action in result), "'Move' action should be removed"
        assert not any(action["name"] == "Trade" for action in result), "'Trade' action should be removed"
        assert not any(action["name"] == "Rescue" for action in result), "'Rescue' action should be removed"
        assert any(action["name"] == "Wait" for action in result), "'Wait' action should still be available"

    def test_get_actions_on_empty_ballista_hides_fire(self, setup_game_components, setup_test_data):
        """Test that 'Fire Ballista' action is not available when a ballista has no durability."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]  # 0 durability
        
        # Configure mocks
        killer_ballista_instance.occupying_unit_id = archer_unit.id
        map_system.get_object_at.return_value = killer_ballista_instance
        
        # Standard actions
        standard_actions = [
            {"name": "Move", "type": "MOVE"},
            {"name": "Attack", "type": "ATTACK"},
            {"name": "Item", "type": "ITEM"},
            {"name": "Wait", "type": "WAIT"}
        ]
        
        # Act
        result = ballista_system.get_unit_available_actions(archer_unit.id, standard_actions)
        
        # Assert
        assert not any(action["name"] == "Fire Ballista" for action in result), "'Fire Ballista' action should not be available"
        assert not any(action["name"] == "Attack" for action in result), "Standard 'Attack' action should be removed"
        assert not any(action["name"] == "Move" for action in result), "'Move' action should be removed"

    def test_get_actions_not_on_ballista(self, setup_game_components, setup_test_data):
        """Test that standard actions are shown when a unit is not on a ballista."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        knight_unit = setup_test_data["units"]["knight_unit"]
        
        # Configure mocks
        map_system.get_object_at.return_value = None  # No ballista at position
        
        # Standard actions
        standard_actions = [
            {"name": "Move", "type": "MOVE"},
            {"name": "Attack", "type": "ATTACK"},
            {"name": "Item", "type": "ITEM"},
            {"name": "Wait", "type": "WAIT"}
        ]
        
        # Act
        result = ballista_system.get_unit_available_actions(knight_unit.id, standard_actions)
        
        # Assert
        assert result == standard_actions, "Standard actions should be unchanged"
        map_system.get_object_at.assert_called_once_with(knight_unit.position, type="BallistaInstance")

    def test_get_actions_on_disabled_ballista(self, setup_game_components, setup_test_data):
        """Test that 'Fire Ballista' action is not available when a ballista is disabled."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]  # is_enabled = False
        
        # Configure mocks
        killer_ballista_instance.occupying_unit_id = archer_unit.id
        map_system.get_object_at.return_value = killer_ballista_instance
        
        # Standard actions
        standard_actions = [
            {"name": "Move", "type": "MOVE"},
            {"name": "Attack", "type": "ATTACK"},
            {"name": "Item", "type": "ITEM"},
            {"name": "Wait", "type": "WAIT"}
        ]
        
        # Act
        result = ballista_system.get_unit_available_actions(archer_unit.id, standard_actions)
        
        # Assert
        assert not any(action["name"] == "Fire Ballista" for action in result), "'Fire Ballista' action should not be available"
        assert not any(action["name"] == "Attack" for action in result), "Standard 'Attack' action should be removed"

    # Test Targeting and Range
    def test_get_ballista_range_calculation_min_max(self, setup_game_components, setup_test_data):
        """Test that ballista range calculation respects min and max range."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        data_provider = setup_game_components["data_provider"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock map dimensions and LOS checker
        map_system.calculate_tiles_in_range.return_value = {
            (2, 5), (3, 5), (4, 5), (6, 5), (7, 5), (8, 5),  # Horizontal
            (5, 2), (5, 3), (5, 4), (5, 6), (5, 7), (5, 8),  # Vertical
            # Diagonal and other tiles within range
            (3, 3), (4, 4), (6, 6), (7, 7), (3, 7), (4, 6), (6, 4), (7, 3)
        }
        
        # Act
        result = ballista_system.get_ballista_attack_range(regular_ballista_instance)
        
        # Assert
        assert result is not None, "Range calculation should return a set of tiles"
        map_system.calculate_tiles_in_range.assert_called_once_with(
            origin=regular_ballista_instance.position,
            min_range=regular_ballista_weapon.min_range,
            max_range=regular_ballista_weapon.max_range,
            map_data=map_system.current_map,
            los_checker=map_system.get_los_checker()
        )

    def test_get_ballista_range_respects_los(self, setup_game_components, setup_test_data):
        """Test that ballista range calculation respects line of sight."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        data_provider = setup_game_components["data_provider"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock map dimensions and LOS checker
        # Simulate some tiles being blocked by obstacles
        visible_tiles = {
            (2, 5), (3, 5), (4, 5), (6, 5), (7, 5),  # Horizontal (8,5 blocked)
            (5, 2), (5, 3), (5, 4), (5, 6), (5, 7),  # Vertical (5,8 blocked)
            # Some diagonals
            (3, 3), (4, 4), (6, 6), (7, 7)
        }
        map_system.calculate_tiles_in_range.return_value = visible_tiles
        
        # Act
        result = ballista_system.get_ballista_attack_range(regular_ballista_instance)
        
        # Assert
        assert result == visible_tiles, "Range should respect line of sight"
        assert (8, 5) not in result, "Blocked horizontal tile should not be in range"
        assert (5, 8) not in result, "Blocked vertical tile should not be in range"

    def test_get_ballista_range_disabled_or_empty(self, setup_game_components, setup_test_data):
        """Test that get_ballista_attack_range returns empty set if ballista cannot fire."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]  # 0 durability, disabled
        
        # Act
        result = ballista_system.get_ballista_attack_range(killer_ballista_instance)
        
        # Assert
        assert result == set(), "Empty or disabled ballista should have no attack range"

    def test_get_valid_ballista_targets_ground_and_air(self, setup_game_components, setup_test_data):
        """Test that get_valid_ballista_targets finds both ground and flying units."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        unit_system = setup_game_components["unit_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        pegasus_unit = setup_test_data["units"]["pegasus_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        # Mock the range calculation to include positions of both enemy units
        ballista_system.get_ballista_attack_range.return_value = {
            (10, 10),  # pegasus_unit position
            (12, 12)   # enemy_archer position
        }
        
        # Mock unit system to return units at those positions
        unit_system.get_units_on_tiles.return_value = [pegasus_unit, enemy_archer]
        unit_system.are_hostile.return_value = True
        
        # Mock map system for line of sight
        map_system = setup_game_components["map_system"]
        map_system.has_line_of_sight.return_value = True
        
        # Act
        result = ballista_system.get_valid_ballista_targets(archer_unit, regular_ballista_instance)
        
        # Assert
        assert len(result) == 2, "Should find both ground and flying enemy units"
        assert pegasus_unit in result, "Should include flying unit"
        assert enemy_archer in result, "Should include ground unit"
        ballista_system.get_ballista_attack_range.assert_called_once_with(regular_ballista_instance)
        unit_system.get_units_on_tiles.assert_called_once_with({(10, 10), (12, 12)})

    def test_get_valid_ballista_targets_excludes_allies_neutrals(self, setup_game_components, setup_test_data):
        """Test that get_valid_ballista_targets excludes allied and neutral units."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        unit_system = setup_game_components["unit_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        knight_unit = setup_test_data["units"]["knight_unit"]  # Allied unit
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        # Mock the range calculation to include positions of both units
        ballista_system.get_ballista_attack_range.return_value = {
            (7, 7),    # knight_unit position (ally)
            (12, 12)   # enemy_archer position
        }
        
        # Mock unit system to return units at those positions
        unit_system.get_units_on_tiles.return_value = [knight_unit, enemy_archer]
        
        # Mock are_hostile to return True only for enemy_archer
        def mock_are_hostile(unit1, unit2):
            return unit2 == enemy_archer
        
        unit_system.are_hostile.side_effect = mock_are_hostile
        
        # Mock map system for line of sight
        map_system = setup_game_components["map_system"]
        map_system.has_line_of_sight.return_value = True
        
        # Mock is_attackable
        knight_unit.is_attackable = MagicMock(return_value=True)
        enemy_archer.is_attackable = MagicMock(return_value=True)
        
        # Act
        result = ballista_system.get_valid_ballista_targets(archer_unit, regular_ballista_instance)
        
        # Assert
        assert len(result) == 1, "Should only find enemy units"
        assert enemy_archer in result, "Should include enemy unit"
        assert knight_unit not in result, "Should exclude allied unit"
        ballista_system.get_ballista_attack_range.assert_called_once_with(regular_ballista_instance)
        unit_system.get_units_on_tiles.assert_called_once_with({(7, 7), (12, 12)})

    def test_get_valid_ballista_targets_respects_range_and_los(self, setup_game_components, setup_test_data):
        """Test that get_valid_ballista_targets respects range and line of sight."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        unit_system = setup_game_components["unit_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        pegasus_unit = setup_test_data["units"]["pegasus_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        # Mock the range calculation to include positions of both enemy units
        ballista_system.get_ballista_attack_range.return_value = {
            (10, 10),  # pegasus_unit position
            (12, 12)   # enemy_archer position
        }
        
        # Mock unit system to return units at those positions
        unit_system.get_units_on_tiles.return_value = [pegasus_unit, enemy_archer]
        unit_system.are_hostile.return_value = True
        
        # Mock map system for line of sight - only pegasus is visible
        map_system = setup_game_components["map_system"]
        def mock_has_line_of_sight(pos1, pos2):
            return pos2 == (10, 10)  # Only pegasus unit is visible
        
        map_system.has_line_of_sight.side_effect = mock_has_line_of_sight
        
        # Mock is_attackable
        pegasus_unit.is_attackable = MagicMock(return_value=True)
        enemy_archer.is_attackable = MagicMock(return_value=True)
        
        # Act
        result = ballista_system.get_valid_ballista_targets(archer_unit, regular_ballista_instance)
        
        # Assert
        assert len(result) == 1, "Should only find units with line of sight"
        assert pegasus_unit in result, "Should include unit with line of sight"
        assert enemy_archer not in result, "Should exclude unit without line of sight"
        ballista_system.get_ballista_attack_range.assert_called_once_with(regular_ballista_instance)
        map_system.has_line_of_sight.assert_has_calls([
            call(regular_ballista_instance.position, (10, 10)),
            call(regular_ballista_instance.position, (12, 12))
        ])

    def test_get_valid_ballista_targets_empty_if_disabled(self, setup_game_components, setup_test_data):
        """Test that get_valid_ballista_targets returns empty list if ballista is disabled."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        unit_system = setup_game_components["unit_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]  # disabled
        
        # Configure mocks
        # Mock the range calculation to return empty set for disabled ballista
        ballista_system.get_ballista_attack_range.return_value = set()
        
        # Act
        result = ballista_system.get_valid_ballista_targets(archer_unit, killer_ballista_instance)
        
        # Assert
        assert result == [], "Should return empty list for disabled ballista"
        ballista_system.get_ballista_attack_range.assert_called_once_with(killer_ballista_instance)
        unit_system.get_units_on_tiles.assert_not_called()

    # Test Combat Calculation
    def test_ballista_preview_damage_calc(self, setup_game_components, setup_test_data):
        """Test that ballista combat preview correctly calculates damage."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        combat_system = setup_game_components["combat_system"]
        data_provider = setup_game_components["data_provider"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock effectiveness calculation (no effectiveness against ground units)
        combat_system.get_effectiveness_multiplier.return_value = 1.0
        
        # Mock defense calculation
        combat_system.calculate_defense.return_value = 3  # enemy_archer.stats.defense
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        assert result["attacker_potential_dmg"] == 5, "Damage should be ballista might (8) - target defense (3)"
        combat_system.get_effectiveness_multiplier.assert_called_once_with(
            regular_ballista_weapon.effectiveness, enemy_archer
        )
        combat_system.calculate_defense.assert_called_once()

    def test_ballista_preview_effectiveness_applied(self, setup_game_components, setup_test_data):
        """Test that ballista combat preview correctly applies effectiveness multipliers."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        combat_system = setup_game_components["combat_system"]
        data_provider = setup_game_components["data_provider"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        pegasus_unit = setup_test_data["units"]["pegasus_unit"]  # Flying unit
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock effectiveness calculation (3x against flying units)
        combat_system.get_effectiveness_multiplier.return_value = 3.0
        
        # Mock defense calculation
        combat_system.calculate_defense.return_value = 5  # pegasus_unit.stats.defense
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, pegasus_unit, regular_ballista_instance)
        
        # Assert
        # Damage = (Might * Effectiveness) - Defense = (8 * 3) - 5 = 19
        assert result["attacker_potential_dmg"] == 19, "Damage should apply effectiveness multiplier"
        combat_system.get_effectiveness_multiplier.assert_called_once_with(
            regular_ballista_weapon.effectiveness, pegasus_unit
        )
        combat_system.calculate_defense.assert_called_once()

    def test_ballista_preview_hit_calc(self, setup_game_components, setup_test_data):
        """Test that ballista combat preview correctly calculates hit rate."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        combat_system = setup_game_components["combat_system"]
        data_provider = setup_game_components["data_provider"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock hit bonuses
        combat_system.get_combat_stat_bonuses.return_value = 5  # Support, skills, etc.
        
        # Mock target avoid
        combat_system.calculate_avoid.return_value = 20
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        # Hit = Weapon Hit + (Skill * 2) + Luck + Bonuses - Avoid
        # 70 + (8 * 2) + 6 + 5 - 20 = 77
        assert result["attacker_hit"] == 77, "Hit calculation should be correct"
        combat_system.get_combat_stat_bonuses.assert_any_call(
            archer_unit, enemy_archer, stat="hit", context="ballista_attack"
        )
        combat_system.calculate_avoid.assert_called_once_with(
            enemy_archer, archer_unit, context="ballista_defense"
        )

    def test_ballista_preview_crit_calc(self, setup_game_components, setup_test_data):
        """Test that ballista combat preview correctly calculates critical hit rate."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        combat_system = setup_game_components["combat_system"]
        data_provider = setup_game_components["data_provider"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]
        killer_ballista_type = setup_test_data["ballista_types"]["killer"]
        killer_ballista_weapon = setup_test_data["ballista_weapons"]["killer"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = killer_ballista_type
        data_provider.get_ballista_weapon.return_value = killer_ballista_weapon
        
        # Mock crit bonuses
        combat_system.get_combat_stat_bonuses.return_value = 10  # Support, skills, etc.
        
        # Mock target crit evade
        combat_system.calculate_crit_evade.return_value = 15
        
        # Override killer_ballista_instance properties for this test
        killer_ballista_instance.current_durability = 3
        killer_ballista_instance.is_enabled = True
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, enemy_archer, killer_ballista_instance)
        
        # Assert
        # Crit = Weapon Crit + Skill + Bonuses - Crit Evade
        # 30 + 8 + 10 - 15 = 33
        assert result["attacker_crit"] == 33, "Crit calculation should be correct"
        combat_system.get_combat_stat_bonuses.assert_any_call(
            archer_unit, enemy_archer, stat="crit", context="ballista_attack"
        )
        combat_system.calculate_crit_evade.assert_called_once_with(
            enemy_archer, archer_unit, context="ballista_defense"
        )

    def test_ballista_preview_counter_check(self, setup_game_components, setup_test_data):
        """Test that ballista combat preview correctly checks if target can counter."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        combat_system = setup_game_components["combat_system"]
        data_provider = setup_game_components["data_provider"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock map system for distance calculation
        map_system = setup_game_components["map_system"]
        map_system.distance.return_value = 8  # Within ballista range
        
        # Test case 1: Target cannot counter (typical case)
        combat_system.can_counter.return_value = False
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        assert result["can_defender_counter"] is False, "Target should not be able to counter"
        combat_system.can_counter.assert_called_with(enemy_archer, archer_unit, distance=8)
        
        # Test case 2: Target can counter (e.g., long-range magic)
        combat_system.can_counter.return_value = True
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        assert result["can_defender_counter"] is True, "Target should be able to counter"

    def test_ballista_attack_disables_on_zero_durability(self, setup_game_components, setup_test_data):
        """Test that ballista is disabled when durability reaches zero after attack."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Set ballista to have 1 durability left
        regular_ballista_instance.current_durability = 1
        
        # Mock combat preview
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": regular_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 0,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Mock random roll to ensure hit
        with patch('random.random', return_value=0.1):  # Return a low value to ensure hit success
            # Act
            ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        assert regular_ballista_instance.current_durability == 0, "Durability should be decremented"
        assert regular_ballista_instance.is_enabled is False, "Ballista should be disabled at 0 durability"

    def test_ballista_attack_deals_damage_on_hit(self, setup_game_components, setup_test_data):
        """Test that ballista attack deals the correct damage on hit."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        combat_system = setup_game_components["combat_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Mock combat preview
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": regular_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 0,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Mock random roll to ensure hit
        with patch('random.random', side_effect=[0.1, 0.9]):  # Hit (0.1 < 0.8) but no crit (0.9 > 0.0)
            # Act
            ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        game_state_manager.apply_damage.assert_called_once_with(enemy_archer.id, 5)
        combat_system.display_hit_effect.assert_called_once()

    def test_ballista_attack_deals_crit_damage(self, setup_game_components, setup_test_data):
        """Test that ballista attack deals double damage on critical hit."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        combat_system = setup_game_components["combat_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]
        
        # Override killer_ballista_instance properties for this test
        killer_ballista_instance.current_durability = 3
        killer_ballista_instance.is_enabled = True
        
        # Mock combat preview
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": killer_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 30,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Mock random roll to ensure hit and crit
        with patch('random.random', return_value=0.1):  # Return a low value to ensure both hit and crit succeed
            # Act
            ballista_system.execute_ballista_attack(archer_unit, enemy_archer, killer_ballista_instance)
        
        # Assert
        game_state_manager.apply_damage.assert_called_once_with(enemy_archer.id, 10)  # Double damage
        combat_system.display_hit_effect.assert_called_once_with(enemy_archer, 10, True)  # True for crit

    def test_ballista_attack_misses(self, setup_game_components, setup_test_data):
        """Test that ballista attack handles misses correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        combat_system = setup_game_components["combat_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Mock combat preview
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": regular_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 20,  # Low hit chance
            "attacker_crit": 0,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Mock random roll to ensure miss
        with patch('random.random', return_value=0.9):  # Return a high value to ensure miss
            # Act
            ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        game_state_manager.apply_damage.assert_not_called()
        combat_system.display_miss_effect.assert_called_once_with(enemy_archer)
        # Durability should still be consumed on miss
        assert regular_ballista_instance.current_durability == regular_ballista_instance.current_durability - 1

    def test_ballista_target_can_counter(self, setup_game_components, setup_test_data):
        """Test that targets can counter-attack if in range."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        combat_system = setup_game_components["combat_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Mock combat preview with counter-attack possible
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": regular_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 0,
            "can_defender_counter": True,  # Target can counter
            "defender_potential_dmg": 4,
            "defender_hit": 70,
            "defender_crit": 0
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Mock random roll to ensure hit but not defeat
        with patch('random.random', return_value=0.1):  # Return a low value to ensure hit success
            # Set enemy_archer HP high enough to survive
            enemy_archer.stats.current_hp = 10
            
            # Act
            ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        # First the ballista attack
        game_state_manager.apply_damage.assert_any_call(enemy_archer.id, 5)
        
        # Then the counter-attack
        combat_system.execute_standard_combat_round.assert_called_once_with(
            enemy_archer, archer_unit, is_counter=True
        )

    # Test Durability
    def test_ballista_durability_decrements_on_fire(self, setup_game_components, setup_test_data):
        """Test that ballista durability decrements by 1 after firing."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Set initial durability
        initial_durability = 5
        regular_ballista_instance.current_durability = initial_durability
        
        # Mock combat preview
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": regular_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 0,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Act
        ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        assert regular_ballista_instance.current_durability == initial_durability - 1, "Durability should decrease by 1"

    def test_ballista_cannot_fire_at_zero_durability(self, setup_game_components, setup_test_data):
        """Test that ballista cannot be fired when durability is 0."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        killer_ballista_instance = setup_test_data["ballista_instances"]["killer"]  # 0 durability
        
        # Ensure durability is 0
        killer_ballista_instance.current_durability = 0
        
        # Act
        result = ballista_system.get_ballista_attack_range(killer_ballista_instance)
        
        # Assert
        assert result == set(), "Empty ballista should have no attack range"
        
        # Try to execute attack
        with pytest.raises(ValueError, match="Cannot fire ballista with 0 durability"):
            ballista_system.execute_ballista_attack(archer_unit, enemy_archer, killer_ballista_instance)

    def test_ballista_initial_durability_set_correctly(self, setup_game_components, setup_test_data):
        """Test that ballista instance starts with the weapon's durability."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        data_provider = setup_game_components["data_provider"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        data_provider.get_ballista_weapon.return_value = regular_ballista_weapon
        
        # Mock scenario data
        ballista_data = Mock()
        ballista_data.type_id = "BALLISTA_REGULAR"
        ballista_data.position = (5, 5)
        ballista_data.initial_occupant_id = None
        
        # Act
        result = ballista_system.initialize_ballista_instance(ballista_data)
        
        # Assert
        assert result.current_durability == regular_ballista_weapon.durability, "Initial durability should match weapon durability"

    def test_ballista_disabled_when_operator_defeated(self, setup_game_components, setup_test_data):
        """Test that ballista is disabled when its operator is defeated."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Set up ballista with operator
        regular_ballista_instance.occupying_unit_id = archer_unit.id
        regular_ballista_instance.is_enabled = True
        
        # Mock event for unit removal
        unit_removed_event = Mock()
        unit_removed_event.unit_id = archer_unit.id
        
        # Mock map system to return the ballista when queried
        map_system.get_all_objects_of_type.return_value = [regular_ballista_instance]
        
        # Act
        ballista_system.on_unit_removed_from_map(unit_removed_event)
        
        # Assert
        assert regular_ballista_instance.occupying_unit_id is None, "Operator reference should be cleared"
        assert regular_ballista_instance.is_enabled is False, "Ballista should be disabled"
        map_system.get_all_objects_of_type.assert_called_once()

    # Test Action Cost
    def test_ballista_attack_consumes_unit_action(self, setup_game_components, setup_test_data):
        """Test that firing a ballista consumes the unit's action."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        action_system = setup_game_components["action_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Mock combat preview
        mock_preview = {
            "attacker_unit_id": archer_unit.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": regular_ballista_instance.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 0,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview.return_value = mock_preview
        
        # Act
        ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        action_system.mark_unit_action_complete.assert_called_once_with(archer_unit)
    def test_check_unit_can_use_ballista_disallowed_class(self, setup_game_components, setup_test_data):
        """Test that units with disallowed class cannot use ballistae."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        data_provider = setup_game_components["data_provider"]
        knight_unit = setup_test_data["units"]["knight_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        
        # Configure mocks
        data_provider.get_ballista_type.return_value = regular_ballista_type
        
        # Act
        result = ballista_system.check_unit_can_use_ballista(knight_unit, regular_ballista_instance)
        
        # Assert
        assert result is False, "Knight should not be able to use ballista"
        data_provider.get_ballista_type.assert_called_once_with(regular_ballista_instance.ballista_type_id)
