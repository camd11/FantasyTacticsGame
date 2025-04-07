# Project Status

## Completed Work

- **Core Gameplay Systems:**
    - AI System
    - Combat System
    - Fatigue System
    - Event System
    - Status Effects System
    - Dismounting System
    - Support/Leadership System
    - Capture System
        - Allows units to capture enemies if they have higher Constitution (CON) and the target has low HP.
        - Capturer suffers stat penalties (e.g., reduced Speed, Skill).
        - Captured unit is immobilized, cannot act, and has stats reduced to 0.
        - Capturer can steal items from the captured unit.
        - Captured units can be released by the capturer or rescued by allies.
    - Stealing System
        - Allows units with the 'Thief' skill to steal non-equipped items from adjacent enemies.
        - Success depends on the thief's Speed vs. the target's Speed and the thief's CON vs. the item's weight.
        - Stealing incurs a fatigue cost for the thief.
        - Stolen items are transferred to the thief's inventory.
    - Rescue/Drop/Take System
        - Allows units to rescue adjacent allies if their CON is sufficient.
        - Rescuer suffers stat penalties (e.g., reduced Speed, Skill).
        - Rescued unit is removed from the map and cannot act ('Rescued' state).
        - Rescuer can drop the rescued unit onto an adjacent empty tile.
        - Allies can take the rescued unit from the rescuer.
- **Initial Data Population:**
    - Units (`units.yaml`): Added Mareeta, Nanna, Saias.
    - Items (`items.yaml`): Added Short Lance, Rapier, Physic, Killer Lance, Hand Axe.
    - Classes (`classes.yaml`): Added Myrmidon, Troubadour, Bishop.
    - Skills (`skills.yaml`): Added Astra, Sol, Luna, Pavise, Canto+.
    - Promotions (`promotions.yaml`): Added Myrmidon->Swordmaster, Troubadour->Valkyrie/Paladin.
    - Supports (`supports.yaml`): Added initial support pairs (e.g., Leif/Nanna, Othin/Tanya).
    - Terrain (`terrain.yaml`)
- **CLI Enhancements:**
    - Basic command-line interface implemented.
- **Bug Fixes:**
    - Resolved module import issues.
    - Corrected `class_id` attribute handling.
- **AI & Testing Features:**
    - Implemented AI vs AI testing mode via `--ai-vs-ai` flag.
    - Implemented optional ASCII map display via `--ascii-display` flag.
    - Adjusted AI vs AI turn limit to 10 for testing.
    - Enhanced AI action logging for better simulation visibility.
    - Fixed runtime errors related to ASCII display (`get_map_dimensions`, `turn_manager` access).
    - Fixed persistent AI movement range bug (corrected terrain cost lookup in `DataProvider`).
    - Fixed `AttributeError` by adding `get_units_in_range` method to `UnitSystem`.
    - Fixed phase/faction mismatch warnings and processing logic in `EngineCore`.
    - Fixed `AttributeError` by adding `get_unit` method to `UnitSystem`.
- **AI Refinement:**
    - Improved AI target prioritization logic.
    - Implemented basic AI archetypes (Aggressive/CHARGE, Defensive/GUARD).
- **Testing & Integration:**
    - Resolved 6 integration test failures related to `DataProvider`, `Engine`, `EventHandler`, and `GameState`. All unit tests are now passing.
    - Created new test scenarios for:
        - Weapon Triangle (`test_weapon_triangle.py`)
        - Poison Status (`test_poison_status.py`)
        - Fatigue Accumulation (`test_fatigue_accumulation.py`)
        - Vantage Skill (`test_vantage_skill.py`)
        - Wrath Skill (`test_wrath_skill.py`)
- **Configuration:**
    - Created placeholder map files (`layouts.yaml`, `placements.yaml`, `events.yaml`) in `data/maps/test_chapter/` to resolve startup warnings related to missing default chapter data.

## Remaining Tasks

- **Data Population:**
    - Add more units, items, classes, skills, promotions, and supports.
    - Create chapter-specific data (layouts, placements, events).
- **CLI Development:**
    - Implement fully interactive turn-by-turn gameplay via CLI.
- **Testing:**
    - Develop more comprehensive testing scenarios covering edge cases and complex interactions.
- **Future Enhancements:**
    - Potential GUI implementation.
- **Bug Fixing:**
    - Address any remaining warnings or bugs as they arise.

## Known Issues

- (Add any known issues here)
