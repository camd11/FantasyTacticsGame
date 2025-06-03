# Implementation Notes

## Mechanics Implementation: Capture and Carrier Penalties

### 1. Capture Command

**Event Scripts & Skills:**

*   **`CaptureCommand` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:40)
    *   Type: Combat Art.
    *   Effect: Initiates the capture attempt by calling the `CaptureArtEffect` skill.
    *   Description: "Halves Str/Mag/Skl/Spd/Def for this attack. If foe is defeated & user's CON > foe's CON (or foe unarmed), capture foe."
*   **`CaptureArtEffect` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:7)
    *   Type: Hidden, No Animation.
    *   Components:
        *   `stat_multiplier`: Halves STR, MAG, SKL, SPD, DEF of the attacker *during this specific combat instance*.
        *   `event_after_initiated_combat`: Calls `Global_Capture_Event` after the combat initiated by `CaptureCommand` concludes.
*   **`Global_Capture_Event` (Event Script):** [`game/events/capture_events.yaml`](game/events/capture_events.yaml:40)
    *   Triggered by: `CaptureArtEffect` skill.
    *   Context: `unit` is attacker, `unit2` is defender.
    *   Logic:
        1.  Checks if defender's HP <= 0.
        2.  Checks if attacker is not already carrying a unit (`not unit.traveler`).
        3.  Checks success conditions:
            *   Attacker's CON (`unit.stats['CON']`) > Defender's CON (`unit2.stats['CON']`), OR
            *   Defender is unarmed (`not game.get_unit(unit2.nid).get_weapon()`) OR defender's weapon has `cannot_counter` tag.
        4.  If successful:
            *   `resurrect;{e:unit2.nid}`: Ensures the unit is 'alive' for pair_up.
            *   `change_team;{e:unit2.nid};player`: Temporarily changes defender's team to player. This facilitates item trading and ensures `pair_up` works as expected for an enemy.
            *   `pair_up;{e:unit2.nid};{e:unit.nid}`: Attacker (`unit`) "rescues" the defender (`unit2`).
            *   `set_current_hp;{e:unit2.nid};0`: Sets captive's HP to 0. They will die if dropped (handled by `Kill_Empty_HP_Unit` event).
            *   `give_skill;{e:unit.nid};CarryingPenalty`: Applies the general stat-halving penalty to the captor.

**Item Trading with Captive:**
*   Achieved by temporarily changing the captive's team to "player" within the `Global_Capture_Event`. Standard trade commands should then work. The captive remains at 0 HP.

**Dropping/Killing Captive:**
*   The `Kill_Empty_HP_Unit` event (triggered by `Search_For_Empty_HP` on `unit_wait`) handles killing any unit on the map with 0 HP that isn't being carried.
*   The `Kill_0_HP_Travelers_End_Chapter` event handles killing any 0 HP captives still being carried at chapter end.

### 2. Stat Halving for Carrying (Capture & Allied Rescue)

**Core Penalty Skill:**

*   **`CarryingPenalty` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:1)
    *   Type: Hidden.
    *   Component: `stat_multiplier` halves STR, MAG, SKL, SPD, DEF by 0.5.
    *   Application:
        *   Given to the captor by `Global_Capture_Event` upon successful capture.
        *   Given to an ally rescuer by `Global_Allied_Rescue_Event` upon successful rescue.

**Movement Penalty Skill (Conditional):**

*   **`CarryingMovementPenalty` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:68)
    *   Type: Hidden.
    *   Component: `stat_multiplier` halves MOV by 0.5.
    *   Application:
        *   Given by `Global_Allied_Rescue_Event` if the rescued ally's CON > (rescuer's CON / 2).
        *   *Note: This specific MOV penalty is not currently applied during enemy capture in `Global_Capture_Event` but could be added if desired.*

**Allied Rescue Implementation:**

*   **`RescueAllyCommand` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:101)
    *   Type: Combat Art (Non-Combat), Target Ally.
    *   Effect: Initiates allied rescue by calling `RescueAllyArtEffect`.
*   **`RescueAllyArtEffect` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:84)
    *   Type: Hidden, No Animation.
    *   Component: `event_after_initiated_combat` (placeholder, ideally `event_after_action` or similar for non-combat skills) calls `Global_Allied_Rescue_Event`.
*   **`Global_Allied_Rescue_Event` (Event Script):** [`game/events/capture_events.yaml`](game/events/capture_events.yaml:54)
    *   Triggered by: `RescueAllyArtEffect`.
    *   Context: `unit` is rescuer, `unit2` is target ally.
    *   Logic:
        1.  Checks if rescuer is not already carrying (`not unit.traveler`).
        2.  Checks if target is an ally (`game.get_unit(unit.nid).team == game.get_unit(unit2.nid).team`).
        3.  Checks if target is not mounted (`'Mounted' not in game.get_unit(unit2.nid).tags`).
        4.  Checks rescue condition: `(rescuer.CON + (5 if rescuer_is_mounted else 0)) > target.CON`.
        5.  If successful:
            *   `pair_up;{e:unit2.nid};{e:unit.nid}`.
            *   `give_skill;{e:unit.nid};CarryingPenalty`.
            *   Conditionally `give_skill;{e:unit.nid};CarryingMovementPenalty` if `unit2.CON > (unit.CON / 2)`.

**Removing Penalties:**

*   **`Handle_Unit_Stop_Carrying` (Event Script):** [`game/events/capture_events.yaml`](game/events/capture_events.yaml:89)
    *   Trigger: Intended to be called when a unit drops or transfers a carried unit (e.g., by modifying the "Drop" / "Transfer" commands or via a `UnitWait` check).
    *   Effect: Removes `CarryingPenalty` and `CarryingMovementPenalty` from the unit that was carrying.

### Lex Talionis Functions/Components Used:

*   **Skills:** `combat_art`, `stat_multiplier`, `event_after_initiated_combat`, `hidden`, `no_animation`, `target_enemy`, `target_ally`, `no_combat`.
*   **Event Commands:** `if`, `resurrect`, `change_team`, `pair_up`, `set_current_hp`, `give_skill`, `remove_skill`, `loop_units`, `kill_unit`.
*   **Event Variables/Functions:** `unit`, `unit2`, `game.get_unit()`, `unit.get_hp()`, `unit.stats['CON']`, `unit.traveler`, `unit.team`, `unit.tags`, `game.get_skill()`, `game.get_unit(unit.traveler)`.

### Deviations from Thracia 776:

*   **Rescue Command Implementation:** Implemented as a Combat Art skill (`RescueAllyCommand`) rather than a default map command. This was done to easily hook into the event system for applying penalties. The standard "Rescue" command might exist in LT with different behavior; this custom skill ensures Thracia-like penalties.
*   **Movement Penalty on Capture:** The specific movement penalty (`carried_CON > carrier_CON / 2`) is currently only implemented for allied rescue, not enemy capture. It could be added to `Global_Capture_Event` if needed.
*   **Trigger for Removing Penalties:** The `Handle_Unit_Stop_Carrying` event currently relies on being called by other actions (Drop/Transfer). A more automatic trigger (e.g., "OnPairUpEnd") would be ideal if available in LT, or a more complex `UnitWait` check would be needed to detect when `unit.traveler` becomes null.

### Initial Testing Setup:

*   [`game/maps/sandbox_capture_test.tmx`](game/maps/sandbox_capture_test.tmx:1) updated with:
    *   `Leif` (Player, Lord_Leif, CON 5, has CaptureCommand, RescueAllyCommand).
    *   `Enemy_Brigand_CON3` (Enemy, Thief_FE5, CON 3, IronSword).
    *   `EnemyUnit_Unarmed` (Enemy, Archer_FE5, CON 7, no items).
    *   `AllyUnit_ToRescue` (Player, PegasusKnight, CON 5, IronLance).
*   [`game/game_data/units.json`](game/game_data/units.json:1) and [`game/game_data/classes.json`](game/game_data/classes.json:1) confirmed to have CON values. `Enemy_Brigand_CON3` added for specific CON testing.

## Initial Engine Study: Capture & Constants (2025-06-02)

### Capture Mechanic Tutorial Insights:
- The Capture mechanic, as implemented in the Lex Talionis tutorial, involves creating two skills:
    1.  A "Capture" command skill (Combat Art) that the player selects. This skill primarily serves to trigger an "effect" skill and potentially display the command.
    2.  An "effect" skill (e.g., "CaptureArt") that is hidden. This skill:
        -   Halves the user's STR, MAG, SKL, LCK, SPD for the combat.
        -   Calls a global event script *after* combat is initiated.
- The core logic resides in a global event script (e.g., "Global_Capture_Event"):
    -   **Trigger**: None (called by the "CaptureArt" skill).
    -   **Conditions**:
        -   Defender's HP <= 0.
        -   Attacker's CON > Defender's CON.
        -   Attacker is not already rescuing/paired up.
        -   (Alternative for Fates-style: remove CON check).
    -   **Actions if conditions met**:
        -   Resurrect the defender.
        -   Change defender's team to player.
        -   Use the `pair_up` command to make the attacker "rescue" the defender (requires `pairup` to be disabled in constants for this behavior).
        -   Set the captured unit's HP to 0. This is a specific way to handle them so they "die" if dropped, as 0 HP units don't immediately die until their next combat or a specific event handles it.
    -   **Edge Case (Unarmed/Non-damaging weapon)**: An `elif` condition handles capturing enemies who are unarmed or have a non-damaging weapon (like a staff) equipped, bypassing some checks.
- **Handling Dropped/0 HP Units**:
    -   A separate global event (e.g., "Search_For_Empty_HP") with a `unit_wait` trigger loops through all units.
    -   This loop calls another global event (e.g., "Kill_Empty_HP_Unit") for each unit.
    -   "Kill_Empty_HP_Unit" (trigger: None) checks if the current unit's HP is 0 and, if so, uses the `kill_unit` command.
    -   This ensures units set to 0 HP by Capture (or other means) are properly removed if they are on the map and their turn comes or they are interacted with in a way that triggers `unit_wait`.
- **End of Chapter**:
    -   To prevent captured units from being "recruited" if held at chapter end, another event (e.g., "Kill_0_HP_Travelers") is created.
    -   This event is called via `loop_units` *before* the `win_game` command. It checks player units for travelers (rescued units) with 0 HP and kills them.
- **Checking for Captured Status**:
    -   To check if a specific unit (e.g., "Lifis") is captured at chapter end, a `game_var` can be used.
    -   A `loop_units` command iterates through player units checking `unit.traveler`.
    -   An event called by this loop checks if `game.get_unit(unit.traveler).nid == 'Lifis_NID'` and sets the `game_var` if true.

### Engine Constants Management:
- Global game constants and feature toggles appear to be managed in a `constants.json` file.
- This file is typically located at `project_directory/game_data/constants.json`.
- It contains a list of arrays, where each inner array is a `["constant_name", value]` pair.
- Examples found: `["fatigue", false]`, `["lead", false]`, `["pairup", false]`.
- The Capture tutorial specifically mentions that the `pairup` constant needs to be `false` for the `pair_up` event command to function as a "rescue" mechanic for capturing.

## Data Extraction: Items and Initial Constants (2025-06-02)

### 1. Directory Creation
- The directory `game/game_data/` was created to store game data files.

### 2. Initial `constants.json`
- An initial [`game/game_data/constants.json`](../game/game_data/constants.json) file was created with the following content, based on findings in [`docs/thracia_mechanics_specification_summary.md`](thracia_mechanics_specification_summary.md) and inferred Lex Talionis constant names:
```json
{
  "FATIGUE_SYSTEM": true,
  "FATIGUE_MODE": 1,
  "GLOBAL_LEADERSHIP_STARS": true,
  "LEADERSHIP_HIT_BONUS_PER_STAR": 3,
  "LEADERSHIP_AVOID_BONUS_PER_STAR": 3,
  "ENABLE_PAIR_UP": false,
  "RNG_MODE": "1RN",
  "PCC_CRIT_MULTIPLIER": true,
  "STAVES_CAN_MISS": true
}
```

### 3. Item Data Extraction & Formatting

#### a. Investigation of Data Sources
- **`FE5Tools/`**: This directory was explored. While it contains Python scripts like [`FE5Tools/rip_battle_weapons.py`](../FE5Tools/rip_battle_weapons.py) and [`FE5Tools/format_battle_weapon.py`](../FE5Tools/format_battle_weapon.py), these appear to be for processing graphical assets (battle animations, icons) rather than extracting statistical item data (might, hit, weight, uses, etc.). No pre-extracted item data files (e.g., CSV, JSON) were found.
- **`FireEmblem5/TABLES/`**: This directory was investigated for raw data files.
    - [`FireEmblem5/TABLES/WeaponEffectTable.csv`](../FireEmblem5/TABLES/WeaponEffectTable.csv) and [`FireEmblem5/TABLES/WeaponEffectOffsets.csv`](../FireEmblem5/TABLES/WeaponEffectOffsets.csv) were found to define pointers to weapon *effects* (Poison, Lifesteal) and their offsets, not core item stats.
    - Other CSV files in this directory did not appear to contain comprehensive item statistical data.
- **`FireEmblem5/TEXT/`**: This directory was explored and found to primarily contain dialogue text files, organized by chapter. While item names or descriptions might be embedded within these, structured statistical data was not apparent.

#### b. Lex Talionis Item Schema
- The Lex Talionis `items.json` schema was provided by the user. Key aspects include:
    - Each item is a JSON object with `nid` (unique ID), `name`, `desc`, `icon_nid`, and `icon_index`.
    - A `components` list defines all other properties (stats, effects, usability).
    - Examples of components: `["Weapon"]`, `["Weapon Type", "Sword"]`, `["Damage", 5]`, `["Weight", 5]`, `["Uses", 46]`, `["Value", 460]`, `["Heal", 10]`, `["Spell"]`, `["Targets Allies"]`.

#### c. Sample Item Data Extraction
- Due to the difficulty in locating and parsing easily accessible raw item statistical data from the provided `FireEmblem5/` directory structure, a pragmatic approach was taken for the initial sample:
    - Stats for a representative set of 10 Thracia 776 items were "looked up" using simulated external knowledge (akin to consulting a Fire Emblem wiki like Serenes Forest).
    - The selected items: Iron Sword, Iron Lance, Iron Axe, Iron Bow, Fire tome, Heal staff, Vulnerary, Stamina Drink, Lockpick, Torch staff.

#### d. `items.json` Creation
- The sample item data was formatted according to the Lex Talionis schema and saved into [`game/game_data/items.json`](../game/game_data/items.json).
- Example entry (Iron Sword):
```json
{
  "nid": "IronSword",
  "name": "Iron Sword",
  "desc": "A standard iron sword.",
  "icon_nid": "ItemIcons",
  "icon_index": 0,
  "components": [
    ["Weapon"],
    ["Weapon Type", "Sword"],
    ["Weapon Rank", "E"],
    ["Damage", 5],
100|     ["Hit", 90],
101|     ["Crit", 0],
102|     ["Weight", 5],
103|     ["Minimum Range", 1],
104|     ["Maximum Range", 1],
105|     ["Uses", 46],
106|     ["WEXP", 1],
107|     ["Value", 460]
108|   ]
109| }
110| ```
111| - Item weights were included as specified, being critical for mechanics like Steal and Capture.
112|
113| ### 4. Challenges and Recommendations
114| - **Challenge**: The primary challenge was the inability to easily locate and parse structured raw item statistical data (might, hit, weight, uses, price, weapon type, rank, etc.) directly from the `FireEmblem5/` ROM data files provided. The data is likely embedded in assembly files (`.asm`) or other compiled formats within `FireEmblem5/SRC/` or requires specialized tools beyond the scope of initial investigation.
115| - **Recommendation**: For comprehensive and accurate data for all Thracia 776 items, a more robust data extraction pipeline should be developed. This might involve:
116|     - Utilizing or adapting more advanced scripts from `FE5Tools/` if available for stat extraction.
117|     - Developing new scripts to parse the specific ROM data structures where item stats are stored.
118|     - Consulting community resources or tools specifically designed for Thracia 776 ROM hacking and data extraction.
119| - The current sample in `items.json` serves as a placeholder and proof-of-concept for the data structure.
120 |
121 | ## Data Extraction: Classes and Units (2025-06-03)
122 |
123 | ### 1. Investigation of Data Sources & Lex Talionis Schemas
124 | - **`FE5Tools/` and `FireEmblem5/`**: Similar to item data, direct extraction of structured class and unit base/growth data from these directories proved challenging for this stage. The data is likely in assembly or other compiled formats requiring specialized parsing.
125 | - **Lex Talionis Schemas**:
126 |     - **Classes (`classes.json`)**:
127 |         - Examined [`lt-maker/default.ltproj/game_data/classes/Archer.json`](../lt-maker/default.ltproj/game_data/classes/Archer.json) as a reference.
128 |         - Key fields include: `nid`, `name`, `desc`, `tier`, `movement_group`, `promotes_from`, `turns_into`, `tags`, `max_level`, `bases` (object), `growths` (object), `growth_bonus` (object), `promotion` (object for stat gains), `max_stats` (object), `learned_skills` (list), `wexp_gain` (object mapping weapon types to `[usable_flag, base_wexp, max_wexp]`), `icon_nid`, `map_sprite_nid`, `combat_anim_nid`.
129 |     - **Units (`units.json`)**:
130 |         - Examined [`lt-maker/default.ltproj/game_data/units/Eirika.json`](../lt-maker/default.ltproj/game_data/units/Eirika.json) as a reference.
131 |         - Key fields include: `nid`, `name`, `desc`, `level`, `klass` (links to class `nid`), `tags`, `bases` (object, overrides class bases), `growths` (object, overrides class growths), `stat_cap_modifiers` (object), `starting_items` (list of `[item_nid, droppable_flag]`), `learned_skills` (list for personal skills), `wexp_gain` (object, overrides class wexp), `alternate_classes`, `portrait_nid`, `affinity`.
132 |
133 | ### 2. Class Data Extraction & Formatting (`classes.json`)
134 | - A new file, [`game/game_data/classes.json`](../game/game_data/classes.json), was created.
135 | - Data for a sample of 7 Thracia 776 classes was extracted, primarily using Serenes Forest as the data source due to parsing difficulties: Lord (Leif-specific), Cavalier, Pegasus Knight, Mage, Thief, Archer, Armor Knight.
136 | - **Assumptions & Mapping**:
137 |     - **Build (Bld) -> Constitution (CON)**.
138 |     - **Magic (Mag) & Resistance (Res)**: Handled as separate stats. Physical classes generally have 0 base MAG unless specified.
139 |     - **Class Growths**: Since Thracia 776 primarily uses unit-specific growths, the growths of a representative unit for that class (e.g., Leif for Lord, Finn for Cavalier - using average growths where multiple generics exist) were used as placeholders for class growths. This is an approximation.
140 |     - **Promotion Gains**: The `promotion` block in unpromoted classes is filled with zeros. Promoted classes would have their own full base stat definitions.
141 |     - **Weapon Experience (WEXP)**: Mapped ranks E-A to WEXP values: E=1, D=31, C=71, B=121, A=181. Max WEXP is 251. The `wexp_gain` array is `[can_use_flag, starting_wexp, max_wexp_cap]`.
142 |     - **Leadership (LEAD)**: Set to 0 for class bases/growths as it's a unit-specific attribute (Leadership Stars) in Thracia 776.
143 |     - **NIDs**: Placeholder NIDs (e.g., `Lord_Leif_Icon`) were used for icons and sprites.
144 |     - **Max Stats**: Generic FE max stats (20 for most, 60 HP, relevant MOV) were used as placeholders, as Thracia 776 class caps are generally 20 for all stats.
145 |     - **`growth_bonus` and `promotion` objects**: Kept empty or zeroed for base classes as per the `Archer.json` example, as these seem to apply to the class itself rather than what a unit *receives* on promotion (which would be handled by the new class's bases).
146 |
147 | ### 3. Unit Data Extraction & Formatting (`units.json`)
148 | - A new file, [`game/game_data/units.json`](../game/game_data/units.json), was created.
149 | - Data for a sample of 5 Thracia 776 units was extracted using Serenes Forest: Leif, Finn, Eyvel, Asbel, Lifis.
150 | - **Mapping & Considerations**:
151 |     - Unit `bases` and `growths` directly reflect their personal stats.
152 |     - `klass` links to the `nid` in `classes.json`. For Eyvel (Swordmaster), a "Swordmaster_FE5" klass nid was used, with a note that this class definition would need to be added.
153 |     - **Personal Skills**:
154 |         - **PCC (Pursuit Critical Coefficient)**: Represented as skills like "PCC_1", "PCC_2", etc., in the `learned_skills` list. The number indicates the PCC value.
155 |         - **Leadership Stars**: Represented as skills like "LeadershipStar_1", "LeadershipStar_2".
156 |         - **Movement Stars**: Would be "MovementStar_X". (Not present in the current small sample but noted for future).
157 |         - These will require corresponding skill definitions in a `skills.json` file later.
158 |     - `starting_items` list includes item NIDs and a boolean for whether they are droppable (assumed `false` for player starting gear unless specified).
159 |     - `affinity` was set to `null` as Thracia 776 does not have GBA-style affinities.
160 |     - `wexp_gain` for units reflects their personal starting weapon ranks.
161 |
162 | ### 4. Challenges and Next Steps
163 | - **Raw Data Parsing**: The primary challenge remains the difficulty of parsing class/unit stats directly from the `FireEmblem5/` directory. Using external sources (Serenes Forest) was a necessary workaround for this stage.
164 | - **Skill Definitions**: Personal skills like PCC and Leadership Stars, added to `units.json`, will require corresponding definitions in a `skills.json` file to be functional.
165 | - **Class Definitions for Pre-promotes**: Classes for units like Eyvel (Swordmaster) need to be added to `classes.json`.
166 | - **Completeness**: The current data is a small sample. A full data extraction effort will be substantial.
167 | - **Movement Costs & Other Class Attributes**: Fields like `movement_group` in `classes.json` imply further data definition (e.g., in `terrain.json` or `movement_costs.json`) to define how different movement types interact with terrain.
168 | - **Weapon Locks/Effectiveness**: The current schema doesn't explicitly show weapon locks (e.g., "Prf" or specific character locks on items) or class-based weapon effectiveness beyond basic weapon types. This might be handled via item components (`usable_by_nid`, `effective_against_tag`) or skill components.
## Mechanics Implementation: Initial Engine Settings & Constants (2025-06-03)

This section details the investigation into configuring core Thracia 776 mechanics using built-in Lex Talionis engine settings, primarily through `game/game_data/constants.json`.

### 1. Review of `constants.json` and Lex Talionis Documentation

- The existing [`game/game_data/constants.json`](../game/game_data/constants.json) was reviewed:
  ```json
  {
    "FATIGUE_SYSTEM": true,
    "FATIGUE_MODE": 1,
    "GLOBAL_LEADERSHIP_STARS": true,
    "LEADERSHIP_HIT_BONUS_PER_STAR": 3,
    "LEADERSHIP_AVOID_BONUS_PER_STAR": 3,
    "ENABLE_PAIR_UP": false,
    "RNG_MODE": "1RN",
    "PCC_CRIT_MULTIPLIER": true,
    "STAVES_CAN_MISS": true
  }
  ```
- Lex Talionis documentation (specifically `constants-reference.html` and `Constants-Editor.html` from `lt-maker-docs/`) was consulted to understand these constants.

### 2. Findings for Specific Mechanics:

#### a. Fatigue
- **Configurable via Constants**: Yes, partially.
    - The `FATIGUE_SYSTEM` constant (documented as "Fatigue" which "Causes units to accumulate fatigue each time they are deployed on a map") enables the core fatigue system. This is correctly set to `true`.
    - The `FATIGUE_MODE: 1` entry in `constants.json` is believed to correspond to setting the internal `_fatigue` game variable to `1`. According to [`docs/thracia_mechanics_specification_summary.md`](thracia_mechanics_specification_summary.md), this value (`_fatigue = 1`) correctly implements the Thracia-style deployment restriction (unit cannot deploy if Fatigue > Max HP).
- **Changes Made**: No changes to `constants.json` were necessary as the existing values align with the initial requirements.
- **Further Action**: Thracia's per-action fatigue accumulation (e.g., +1 for most actions, more for staves) is not covered by these constants and will require custom event scripting as per [`docs/thracia_mechanics_specification_summary.md:28`](docs/thracia_mechanics_specification_summary.md:28).

#### b. Leadership Stars
- **Configurable via Constants**: Yes.
    - The `GLOBAL_LEADERSHIP_STARS` constant (documented as "Global Leadership Stars" or "Lead") enables the system where leader units grant passive bonuses. This is correctly set to `true`.
    - The actual bonus per star (`+3 Hit/+3 Avoid`) is handled via custom equations (`LEAD_HIT = 3 * unit.LEAD`, `LEAD_AVOID = 3 * unit.LEAD`) and a `LEAD` stat on units, as specified in the LT docs and [`docs/thracia_mechanics_specification_summary.md:53-54`](docs/thracia_mechanics_specification_summary.md:53-54). The constants `LEADERSHIP_HIT_BONUS_PER_STAR: 3` and `LEADERSHIP_AVOID_BONUS_PER_STAR: 3` in `constants.json` appear to be descriptive placeholders for these equation values rather than direct engine constants themselves, but serve as good documentation.
- **Changes Made**: No changes to `constants.json` were necessary.
- **Further Action**: Define the `LEAD` stat and the `LEAD_HIT`/`LEAD_AVOID` equations in the respective LT editors.

#### c. Pursuit Critical Coefficient (PCC)
- **Configurable via Constants**: Partially, or requires clarification.
    - The Lex Talionis documentation does not explicitly list a constant named `PCC_CRIT_MULTIPLIER` or a direct toggle for PCC/FE5-style follow-up criticals.
    - The existing `"PCC_CRIT_MULTIPLIER": true` in `constants.json` is likely a placeholder or a custom engine flag.
    - The general "Allow Criticals" constant enables criticals, but PCC is more specific.
- **Changes Made**: No changes to `constants.json` at this stage.
- **Further Action**: The core PCC logic (multiplying base critical chance by the unit's PCC stat on their follow-up attack, and PCC=0 resulting in 0% crit on follow-up) will almost certainly need to be implemented by modifying the critical hit formula in the Lex Talionis Equations Editor, as suggested by [`docs/thracia_mechanics_specification_summary.md:125`](docs/thracia_mechanics_specification_summary.md:125). A hidden "PCC" stat will also need to be added to units.

#### d. Random Number (RN) System (1RN vs 2RN)
- **Configurable via Constants**: Potentially, but needs verification.
    - The Lex Talionis documentation consulted (`constants-reference.html`, `Constants-Editor.html`, `Random-Seed-Mechanics.html`) does not explicitly define an `RNG_MODE` constant or a clear toggle for 1RN vs 2RN systems.
    - The entry `"RNG_MODE": "1RN"` in `constants.json` is the current best approach to enforce a single-RN system.
    - Thracia 776 requires a single RN (0-99 roll) for both combat and staff accuracy. It's crucial to confirm if `RNG_MODE: "1RN"` achieves this globally.
- **Changes Made**: No changes to `constants.json` at this stage.
- **Further Action**: Extensive testing will be required to confirm that `"RNG_MODE": "1RN"` correctly implements a true single-RN system for all relevant calculations (combat hit/crit/skill activation, staff accuracy). If it doesn't, or if it's not a recognized engine constant, this will become a significant custom scripting task or may require engine source investigation. The constant `"STAVES_CAN_MISS": true` is also present and likely interacts with this.

### 3. Summary of Mechanics Status:

- **Preliminarily Addressed by Configuration (pending testing/equation setup)**:
    - **Fatigue (Deployment Penalty)**: `FATIGUE_SYSTEM: true`, `FATIGUE_MODE: 1`.
    - **Leadership Stars (Global Bonus Enable)**: `GLOBAL_LEADERSHIP_STARS: true`. (Requires stat and equation setup).
    - **Random Number System (1RN for Combat/Staves)**: `RNG_MODE: "1RN"`, `STAVES_CAN_MISS: true`. (Requires thorough testing to confirm global 1RN behavior).

- **Definitely Requires Custom Scripting / Equation Editing**:
    - **Fatigue (Per-Action Accumulation)**: Needs event scripting.
    - **Leadership Stars (Bonus Calculation)**: Requires `LEAD` stat and `LEAD_HIT`/`LEAD_AVOID` equations.
    - **Pursuit Critical Coefficient (PCC) (Core Logic)**: Requires "PCC" stat and modification of the critical hit formula in the Equations Editor. The existing `PCC_CRIT_MULTIPLIER` constant's function needs to be clarified; it may just be a flag for scripts.

This initial review suggests that while `constants.json` provides a good starting point for several mechanics, deeper engine features (like the Equations Editor) and custom scripting will be essential for achieving full Thracia 776 accuracy.

## Mechanics Implementation: Fatigue
This section details the implementation of the Fatigue mechanic.

### 1. Fatigue Storage and Configuration

*   **Storage**: Fatigue is stored as a custom unit attribute `fatigue` directly on the unit object.
    *   Added to all unit definitions in [`game/game_data/units.json`](../game/game_data/units.json) with an initial value of `0`.
    *   Example: `"fatigue": 0` within each unit's JSON entry.
*   **Configuration**:
    *   A constant `FATIGUE_PER_ACTION` is defined in [`game/game_data/constants.json`](../game/game_data/constants.json). This determines how much fatigue is gained per action.
        *   Currently set to `1`: `"FATIGUE_PER_ACTION": 1`.
    *   The existing `FATIGUE_SYSTEM: true` and `FATIGUE_MODE: 1` in `constants.json` are utilized. `FATIGUE_MODE: 1` is crucial as it enables the Thracia-style deployment lockout (Fatigue >= MaxHP).

### 2. Per-Action Fatigue Accumulation

*   **Skill**: `FatigueAccumulator` ([`game/game_data/skills.json`](../game/game_data/skills.json))
    *   **Type**: Hidden.
    *   **Component**: `event_after_action` which triggers the `Global_Gain_Fatigue_Event`.
    *   **Application**: This skill is added to the `learned_skills` of all relevant player classes in [`game/game_data/classes.json`](../game/game_data/classes.json) (e.g., `[0, "FatigueAccumulator"]`), ensuring units of these classes automatically accumulate fatigue.
*   **Event Script**: `Global_Gain_Fatigue_Event` ([`game/events/fatigue_events.py`](../game/events/fatigue_events.py))
    *   **Triggered by**: `FatigueAccumulator` skill after a unit performs an action.
    *   **Logic**:
        1.  Retrieves `FATIGUE_PER_ACTION` from `game.game_vars`.
        2.  Increments the acting unit's `fatigue` attribute by this amount.
        3.  Includes commented-out alerts/speak lines for debugging.

### 3. Chapter-End Fatigue Check & Deployment Lockout

*   **Status Effect**: `Fatigued_Out` ([`game/game_data/skills.json`](../game/game_data/skills.json))
    *   **Type**: Status effect.
    *   **Components**:
        *   `prevent_deployment`: Prevents the unit from being deployed.
        *   `status`: Marks it as a status.
        *   `time: 1`: Indicates a duration, though its primary management is via the chapter-end event.
    *   **Icon**: Placeholder `GenericSkill` icon.
*   **Event Script**: `Chapter_End_Fatigue_Processing` ([`game/events/fatigue_events.py`](../game/events/fatigue_events.py))
    *   **Trigger**: `level_end` (or equivalent chapter end hook).
    *   **Logic**:
        1.  Iterates through all units in the player's party.
        2.  For each unit, compares their current `unit.fatigue` with their maximum HP (`unit.stats.get('HP')`).
        3.  If `fatigue >= MaxHP`:
            *   If the unit does not already have the `Fatigued_Out` status, it is applied using `game.add_skill(unit, "Fatigued_Out")`.
        4.  If `fatigue < MaxHP`:
            *   If the unit has the `Fatigued_Out` status, it is removed using `game.remove_skill(unit, "Fatigued_Out")`.
        5.  Includes commented-out alerts/speak lines for debugging.

### 4. "Stamina Drink" Item Functionality

*   **Item**: "Stamina Drink" ([`game/game_data/items.json`](../game/game_data/items.json))
    *   **Components**:
        *   `Usable`, `Usable in Base`, `Targets Allies`.
        *   `event_on_use`: Triggers the `Use_Stamina_Drink_Event`.
        *   `Uses: 1`, `Value: 1000`.
*   **Event Script**: `Use_Stamina_Drink_Event` ([`game/events/fatigue_events.py`](../game/events/fatigue_events.py))
    *   **Triggered by**: Using the "Stamina Drink" item.
    *   **Context**: `unit` (user), `target_unit` (recipient of the drink).
    *   **Logic**:
        1.  Sets `target_unit.fatigue` to `0`.
        2.  Checks if the `target_unit` has the `Fatigued_Out` status. If so, removes it.
        3.  Includes commented-out alerts/speak lines for debugging.

### 5. Files Created/Modified:

*   **Modified**:
    *   [`game/game_data/constants.json`](../game/game_data/constants.json): Added `FATIGUE_PER_ACTION`.
    *   [`game/game_data/units.json`](../game/game_data/units.json): Added `fatigue: 0` to all unit definitions.
    *   [`game/game_data/skills.json`](../game/game_data/skills.json): Added `FatigueAccumulator` skill and `Fatigued_Out` status effect.
    *   [`game/game_data/classes.json`](../game/game_data/classes.json): Added `FatigueAccumulator` to `learned_skills` for player classes.
    *   [`game/game_data/items.json`](../game/game_data/items.json): Modified "Stamina Drink" to use `event_on_use`.
*   **Created**:
    *   [`game/events/fatigue_events.py`](../game/events/fatigue_events.py): Contains `Global_Gain_Fatigue_Event`, `Chapter_End_Fatigue_Processing`, and `Use_Stamina_Drink_Event`.

### 6. Important Notes & Assumptions:

*   **Event Registration**: The Python event classes in `fatigue_events.py` will need to be registered with the Lex Talionis engine to be discoverable. This usually involves an `__init__.py` in the `game/events/` directory or a similar mechanism in the project's main setup.
*   **Accessing Unit Stats**: The code assumes `unit.fatigue` is the correct way to access/modify the custom fatigue stat and `unit.stats.get('HP')` retrieves maximum HP.
*   **Skill/Event Component NIDs**: The NIDs used for components like `event_after_action`, `prevent_deployment`, `event_on_use` are based on common Lex Talionis patterns. If these exact NIDs are incorrect for the specific LT version/fork, they may need adjustment.
*   **Debugging Lines**: Commented-out `game.alerts.append` and `game.speak` lines are included in the event scripts for easier debugging during testing.
*   **MaxHP Access**: Assumed `unit.stats.get('HP')` or `unit.stats['HP']` correctly refers to the unit's maximum HP, not current HP, for the fatigue check.

### Mechanics Implementation: Leadership Stars

**Data Storage:**

*   Leadership Stars are stored as skills with NIDs like `LeadershipStar_1`, `LeadershipStar_2`, etc.
    *   Units are assigned these skills in their `learned_skills` array in [`game/game_data/units.json`](../game/game_data/units.json). (e.g., Leif has [`"LeadershipStar_1"`](game/game_data/units.json:42)).
    *   These skills are defined in [`game/game_data/skills.json`](../game/game_data/skills.json). Currently, they are simple marker skills with a "hidden" component.

**Effect Implementation (Global Bonus):**

*   The global bonus (+Hit, +Avoid) is calculated and applied by the `apply_leadership_bonuses` function within [`game/events/leadership_star_events.py`](../game/events/leadership_star_events.py).
*   **Trigger**: This function is intended to be triggered at the start of each phase (e.g., Player Phase, Enemy Phase). The exact event hook (e.g., `on_phase_start`) depends on the engine's event system.
*   **Calculation Logic**:
    1.  The script iterates through all deployed units.
    2.  It sums the number of leadership stars for each team (`player`, `enemy`, `other`) by checking for `LeadershipStar_X` skills on units and extracting the star count from the skill NID.
    3.  For each unit on a team, a bonus is calculated:
        *   Hit Bonus = `total_team_stars * LEADERSHIP_HIT_BONUS_PER_STAR`
        *   Avoid Bonus = `total_team_stars * LEADERSHIP_AVOID_BONUS_PER_STAR`
*   **Bonus Application**:
    *   The script attempts to use a conceptual `game.set_unit_turn_stat_bonus(unit, stat_name, value, source_tag)` function to apply these bonuses temporarily for the current turn/phase.
    *   A corresponding `clear_leadership_bonuses_on_turn_end` function is provided to remove these bonuses, intended to be triggered at phase or turn end.
    *   The actual mechanism for applying and removing temporary stat bonuses is dependent on specific Lex Talionis engine capabilities. If direct temporary stat modifiers are not available, this would require creating and managing temporary status effects.
*   **Constants Used**:
    *   [`LEADERSHIP_HIT_BONUS_PER_STAR`](../game/game_data/constants.json): Value `3`. Found in [`game/game_data/constants.json`](game/game_data/constants.json:6).
    *   [`LEADERSHIP_AVOID_BONUS_PER_STAR`](../game/game_data/constants.json): Value `3`. Found in [`game/game_data/constants.json`](game/game_data/constants.json:7).

**Files Created/Modified:**

*   **Modified**:
    *   [`game/game_data/units.json`](../game/game_data/units.json): Ensured units like Leif have `LeadershipStar_X` skills.
    *   [`game/game_data/skills.json`](../game/game_data/skills.json): Added definitions for `LeadershipStar_1` through `LeadershipStar_5`.
    *   [`game/game_data/constants.json`](../game/game_data/constants.json): Constants `LEADERSHIP_HIT_BONUS_PER_STAR` and `LEADERSHIP_AVOID_BONUS_PER_STAR` were already present.
*   **Created**:
    *   [`game/events/leadership_star_events.py`](../game/events/leadership_star_events.py): Contains `apply_leadership_bonuses` and `clear_leadership_bonuses_on_turn_end`.

### Mechanics Implementation: Movement Stars

**Data Storage:**

*   Movement Stars are stored as skills with NIDs like `MovementStar_1`, `MovementStar_2`, etc.
    *   Units are assigned these skills in their `learned_skills` array in [`game/game_data/units.json`](../game/game_data/units.json) (e.g., Leif modified to have [`"MovementStar_1"`](game/game_data/units.json:43), Finn with [`"MovementStar_2"`](game/game_data/units.json:102)).
    *   These skills are defined in [`game/game_data/skills.json`](../game/game_data/skills.json).

**Refresh Logic (After "Wait" Action):**

*   **Skill Component**:
    *   Each `MovementStar_X` skill in [`game/game_data/skills.json`](../game/game_data/skills.json) has an `event_after_wait_action` component.
    *   This component is configured to trigger a global event named `Global_Movement_Star_Refresh_Event`.
*   **Event Script**: The logic for this event is handled by the `handle_movement_star_refresh` function in [`game/events/movement_star_events.py`](../game/events/movement_star_events.py).
*   **Refresh Calculation & Check**:
    1.  The script first checks if the unit has already refreshed this turn using a flag: `unit.custom_data['movement_star_refreshed_this_turn']`. If true, no action is taken.
    2.  It calculates the unit's total movement stars by checking for `MovementStar_X` skills and extracting the star count from the skill NID.
    3.  The refresh chance is calculated: `total_movement_stars * MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR`.
    4.  A random number is rolled. If the roll is less than the calculated chance, the refresh is successful.
*   **Action Refresh & Flagging**:
    *   If successful, the unit's action state is refreshed (e.g., `unit.has_acted = False`, `unit.has_moved = False`). The exact method depends on the engine's API for refreshing units.
    *   The flag `unit.custom_data['movement_star_refreshed_this_turn']` is set to `True` to prevent further refreshes in the same turn.
*   **Resetting the Flag**:
    *   The `reset_movement_star_refresh_flags` function in the same event script is designed to set `unit.custom_data['movement_star_refreshed_this_turn'] = False` for all units.
    *   This reset function is intended to be triggered at the start of each global turn or phase (e.g., Player Phase start, Enemy Phase start).
*   **Constant Used**:
    *   [`MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR`](../game/game_data/constants.json): Value `0.05` (5%). Added to [`game/game_data/constants.json`](game/game_data/constants.json:12).

**Files Created/Modified:**

*   **Modified**:
    *   [`game/game_data/units.json`](../game/game_data/units.json): Added `MovementStar_X` skills to sample units.
    *   [`game/game_data/skills.json`](../game/game_data/skills.json): Added definitions for `MovementStar_1` through `MovementStar_5` and included the `event_after_wait_action` component.
    *   [`game/game_data/constants.json`](../game/game_data/constants.json): Added `MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR`.
*   **Created**:
    *   [`game/events/movement_star_events.py`](../game/events/movement_star_events.py): Contains `handle_movement_star_refresh` and `reset_movement_star_refresh_flags`.

## Pursuit Critical Coefficient (PCC)

**Data Storage & Configuration:**

*   **PCC Value Storage**:
    *   Units are assigned skills like `PCC_0`, `PCC_1`, ..., `PCC_5` in their `learned_skills` array in [`game/game_data/units.json`](game/game_data/units.json:0) (e.g., Leif has [`"PCC_2"`](game/game_data/units.json:41)).
    *   These skills are defined in [`game/game_data/skills.json`](game/game_data/skills.json:304) and utilize the `pcc_static` item component.
    *   The `pcc_static` component (defined in [`lt-maker/app/engine/skill_components/combat_components.py`](lt-maker/app/engine/skill_components/combat_components.py:290)) takes a `value` which corresponds to the PCC multiplier (0-5).
*   **Engine Constant**:
    *   The constant `PCC_CRIT_MULTIPLIER` is set to `true` in [`game/game_data/constants.json`](game/game_data/constants.json:10). This likely enables the engine's PCC logic.

**Combat Equation Modification (Critical Hit Calculation):**

*   The core logic for PCC is handled by the engine's skill system and combat calculations.
*   The `pcc_static` skill component has a `crit_multiplier` method: `unit.get_stat(self.value) if attack_info[0] > 0 else 1` for the `pcc` component or `self.value if attack_info[0] > 0 else 1` for the `pcc_static` component (see [`lt-maker/app/engine/skill_components/combat_components.py`](lt-maker/app/engine/skill_components/combat_components.py:285-286) and [`lt-maker/app/engine/skill_components/combat_components.py:298-299)). The `attack_info[0] > 0` condition checks if the current attack is a follow-up (second strike or later in a brave attack sequence).
*   This multiplier is then used in [`lt-maker/app/engine/combat_calcs.py`](lt-maker/app/engine/combat_calcs.py:0) within the `compute_crit` function (specifically line 456: `crit *= skill_system.crit_multiplier(...)` ) or potentially within the "Thracia Crit" section of `compute_damage` (lines 527-531: `might += total_might * thracia_crit`) if `thracia_critical_multiplier_formula` is configured to use the PCC value. Given the `pcc_static` component directly provides a `crit_multiplier`, it's more likely the former.
*   The final critical chance is capped at 100% by `utils.clamp(crit, 0, 100)` in [`compute_crit`](lt-maker/app/engine/combat_calcs.py:459).
*   **No direct modification to `combat_calcs.py` was needed for PCC itself**, as the engine appears to support it through the `pcc_static` skill component and the existing `PCC_CRIT_MULTIPLIER` constant. The primary implementation step was correctly defining the `PCC_X` skills in `skills.json`.

## Staff Hit/Miss Logic

**Staff Hit Calculation:**

*   **Configuration**:
    *   The constant `STAVES_CAN_MISS` is set to `true` in [`game/game_data/constants.json`](game/game_data/constants.json:11).
    *   The game's `RNG_MODE` is set to `"1RN"` in [`game/game_data/constants.json`](game/game_data/constants.json:9), aligning with Thracia's single Roll Number system for hit checks.
*   **Formula Implementation**:
    *   The staff accuracy formula `Hit% = BaseStaffHit + (4 * User's Skill_stat)`, capped at 99, is implemented by modifying the `accuracy` function in [`lt-maker/app/engine/combat_calcs.py`](lt-maker/app/engine/combat_calcs.py:133).
    *   The modification checks if the item is a 'Staff' and if `STAVES_CAN_MISS` is true.
    *   If so, it calculates: `accuracy = min(99, base_staff_hit + (4 * user_skill))`.
        *   `base_staff_hit` is taken from `item_system.hit(unit, item)`, which should be the staff's defined base hit (e.g., 60 for Heal, 100 for Torch).
        *   `user_skill` is `unit.stats.get('SKL', 0)`.
    *   If not a staff or staves cannot miss, the standard accuracy calculation proceeds.

**Staff Miss Effect (No Use Consumed, Act Again):**

*   **No Use Consumed**:
    *   This is handled by the default behavior of the `Uses` and `ChapterUses` components in [`lt-maker/app/engine/item_components/usable_components.py`](lt-maker/app/engine/item_components/usable_components.py:0).
    *   The `UsesOptions` component (paired with `Uses` and `ChapterUses`) has a `lose_uses_on_miss` option which defaults to `False` (see lines 147 and 160).
    *   Since staff items in [`game/game_data/items.json`](game/game_data/items.json:0) (e.g., [`HealStaff`](game/game_data/items.json:109)) do not explicitly override `UsesOptions` to set `lose_uses_on_miss` to `true`, they will not consume a use on miss by default.
*   **Act Again on Miss**:
    *   This is implemented by modifying the `on_miss` methods within the `Uses` and `ChapterUses` classes in [`lt-maker/app/engine/item_components/usable_components.py`](lt-maker/app/engine/item_components/usable_components.py:37) and (line 102 respectively).
    *   Inside `on_miss`:
        1.  It checks if the item is a 'Staff' (using `item_system.weapon_type`) and if `STAVES_CAN_MISS` is true.
        2.  It further checks if `item.uses_options.lose_uses_on_miss()` is `False` (confirming a use was not and should not be consumed for this miss).
        3.  If all conditions are met, the unit's action is refreshed by setting `unit.has_acted = False` and `unit.has_moved = False`. This logic is adapted from how Movement Stars refresh units (see [`game/events/movement_star_events.py`](game/events/movement_star_events.py:70-73)).
    *   Necessary imports (`DB`, `item_system`, `game`) were added to [`lt-maker/app/engine/item_components/usable_components.py`](lt-maker/app/engine/item_components/usable_components.py:0).

**Core Engine Scripts Modified:**

*   [`lt-maker/app/engine/combat_calcs.py`](lt-maker/app/engine/combat_calcs.py:0): Modified the `accuracy` function to implement the custom staff hit formula.
*   [`lt-maker/app/engine/item_components/usable_components.py`](lt-maker/app/engine/item_components/usable_components.py:0): Modified the `on_miss` methods in `Uses` and `ChapterUses` classes to refresh the unit if a staff misses and no use is consumed.

**Note on Maintainability:** Modifications to core engine scripts (`combat_calcs.py`, `usable_components.py`) are significant. These changes might conflict with future updates to the Lex Talionis engine. It's crucial to document these changes clearly and consider isolating them further if possible (e.g., through custom skill components or more targeted hooks if the engine supports them) to improve long-term maintainability. For now, direct modification was the most straightforward approach based on the investigation.
## Steal Mechanic

**Skills & Events:**

*   **`StealCommand` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:393)
    *   Type: Combat Art (Non-Combat), Target Enemy, Range 1.
    *   Effect: Initiates the steal attempt by calling `StealArtEffect`.
    *   Description: "Attempt to steal an item from an adjacent enemy. Requires Thief's CON >= Enemy's CON and Thief's CON >= Item's Weight."
    *   Assigned to: `Thief_FE5` class in [`game/game_data/classes.json`](game/game_data/classes.json:331).
*   **`StealArtEffect` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:370)
    *   Type: Hidden, No Animation.
    *   Component: `event_after_initiated_combat` (should be `event_after_action` for non-combat) calls `Global_Steal_Event`.
*   **`Global_Steal_Event` (Event Script):** [`game/events/steal_events.py`](game/events/steal_events.py:0)
    *   Triggered by: `StealArtEffect`.
    *   Context: `unit` (thief), `target` (enemy).
    *   Logic:
        1.  Checks `thief.CON >= enemy.CON`. If fails, displays message and ends.
        2.  Filters `enemy.items` to find `stealable_items` where `thief.CON >= item.weight`.
        3.  If no stealable items, displays message and ends.
        4.  Presents a `choice_menu` (UI assumed) listing `stealable_items` (name and weight).
        5.  If player selects an item:
            *   `game.remove_item(enemy, selected_item_object)`
            *   `game.add_item(thief, selected_item_object.nid)`
            *   Displays success message.
        6.  If player cancels, displays message.

**Data Requirements:**

*   Units need a `CON` stat (e.g., `unit.stats.get('CON', 0)`).
*   Items in [`game/game_data/items.json`](game/game_data/items.json:0) need a `weight` attribute accessible via `game.get_item_data(item.nid).weight`.
*   Lex Talionis needs `choice_menu.display`, `game.remove_item`, `game.add_item` functions.

## Dismount Mechanic

**Class Definitions:**

*   Dismounted versions of mounted classes are defined in [`game/game_data/classes.json`](game/game_data/classes.json:0).
    *   Example: `Cavalier_Dismounted` ([`game/game_data/classes.json`](game/game_data/classes.json:478)), `PegasusKnight_Dismounted` ([`game/game_data/classes.json`](game/game_data/classes.json:519)).
    *   These classes have:
        *   `movement_group`: "Light Foot".
        *   Lower `MOV` in their `bases`.
        *   `wexp_gain` restricted (e.g., only Swords).
        *   A `fields` entry like `["dismount_pair:OriginalMountedClassNid"]` to link back to their mounted version (e.g., `Cavalier_Dismounted` has `dismount_pair:Cavalier`).
    *   Map sprites and combat animations are placeholders (e.g., `SwordKnight_MapSprite`).

**Skills & Events (Optional Mount/Dismount Commands):**

*   **`DismountCommand` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:433)
    *   Type: Combat Art (Non-Combat), Target Self.
    *   Effect: Calls `DismountArtEffect`.
    *   Condition: `unit.is_mounted() and game.map.properties.get('terrain_type') == 'outdoor'` (placeholders).
    *   Assigned to: Mounted classes (e.g., `Cavalier`, `PegasusKnight`) in [`game/game_data/classes.json`](game/game_data/classes.json:142).
*   **`DismountArtEffect` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:433)
    *   Type: Hidden, No Animation.
    *   Component: `event_after_action` calls `Global_Dismount_Event`.
*   **`Global_Dismount_Event` (Event Script):** [`game/events/mount_events.py`](game/events/mount_events.py:0)
    *   Triggered by: `DismountArtEffect`.
    *   Context: `unit` (mounted unit).
    *   Logic:
        1.  Iterates through all class definitions to find a class `c_data` where `c_data.fields` contains `dismount_pair:{unit.klass}`. This identifies the dismounted version.
        2.  If found, `game.change_class(unit, dismounted_class_nid)`.
        3.  Displays success/failure message.
*   **`MountCommand` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:474)
    *   Type: Combat Art (Non-Combat), Target Self.
    *   Effect: Calls `MountArtEffect`.
    *   Condition: `not unit.is_mounted() and unit.can_mount() and game.map.properties.get('terrain_type') == 'outdoor'` (placeholders).
    *   Assigned to: Dismounted classes (e.g., `Cavalier_Dismounted`, `PegasusKnight_Dismounted`) in [`game/game_data/classes.json`](game/game_data/classes.json:499).
*   **`MountArtEffect` (Skill):** [`game/game_data/skills.json`](game/game_data/skills.json:474)
    *   Type: Hidden, No Animation.
    *   Component: `event_after_action` calls `Global_Mount_Event`.
*   **`Global_Mount_Event` (Event Script):** [`game/events/mount_events.py`](game/events/mount_events.py:47)
    *   Triggered by: `MountArtEffect`.
    *   Context: `unit` (dismounted unit).
    *   Logic:
        1.  Retrieves `mounted_class_nid` from the current (dismounted) class's `dismount_pair` field.
        2.  If found, `game.change_class(unit, mounted_class_nid)`.
        3.  Displays success/failure message.

**Indoor Auto-Swap:**

*   **Event Script**: `Indoor_Map_Auto_Dismount` ([`game/events/mount_events.py`](game/events/mount_events.py:74))
    *   Trigger: `level_start`.
    *   Logic:
        1.  Checks if `game.map_registry.get_current_map_data().properties.get('is_indoor', False)` is true.
        2.  If indoor, iterates through all units on map (`game.get_all_units_on_map()`).
        3.  For each unit, if their class `movement_group` is 'Mounted' or 'Flying':
            *   Searches all class definitions for the corresponding dismounted class (where `dismount_pair` matches the unit's current class).
            *   If found, `game.change_class(unit_obj, dismounted_class_nid_target)`.
*   **Map Property**: Requires maps to have an `is_indoor: true` property in their TMX file or equivalent map data for the auto-dismount to trigger.

**Placeholder Conditions/Functions:**

*   `unit.is_mounted()`: Needs implementation or engine equivalent. Could check `unit.klass` against a list of mounted class NIDs or check `game.get_class_data(unit.klass).movement_group`.
*   `unit.can_mount()`: Needs implementation. Could check if `unit.klass` is a dismounted version of an originally mounted class (e.g., by checking its `dismount_pair` field).
*   `game.map.properties.get('terrain_type') == 'outdoor'`: Assumes map property for terrain type.
*   `game.map_registry.get_current_map_data().properties.get('is_indoor', False)`: Assumes map property for indoor status.

## Escape Objective Mechanic

### 1. Escape Tile Identification

*   **Method**: Escape Tiles are identified by a specific region `nid` in the TMX map file.
*   **Region NID**: `EscapePoint`
*   **TMX Setup**:
    *   In a TMX map editor (like Tiled), create an object layer (e.g., "Region Layer").
    *   Add a rectangle object over the desired tile(s).
    *   Set the `type` of this object to `region`.
    *   Add a custom property to this region object:
        *   `name`: `nid`
        *   `type`: `string` (or default)
        *   `value`: `EscapePoint`
    *   Example in [`game/maps/sandbox_escape_test.tmx`](game/maps/sandbox_escape_test.tmx:59):
        ```xml
        <objectgroup id="3" name="Region Layer">
         <object id="4" name="EscapePoint_1" type="region" x="144" y="144" width="16" height="16"> <!-- (9,9) -->
          <properties>
           <property name="nid" value="EscapePoint"/>
           <property name="region_type" value="event"/>
           <property name="sub_type" value="EscapePoint"/>
          </properties>
         </object>
        </objectgroup>
        ```

### 2. Event Triggering and Logic

*   **Global Event Trigger**: A global event is set up to monitor all unit movements.
    *   File: [`game/events/global_triggers.yaml`](game/events/global_triggers.yaml:0)
    *   Event NID: `Global_Escape_Objective_Check_On_Move`
    *   Trigger: `unit_move` (fires after any unit completes its movement).
    *   Script: Calls the Python function `game.events.escape_events.on_unit_move`.
*   **Core Logic Script**: [`game/events/escape_events.py`](game/events/escape_events.py:0)
    *   Function: `on_unit_move(event_name: str, unit: UnitObject, new_position: tuple)`
    *   Constants:
        *   `ESCAPE_REGION_NID = "EscapePoint"`
        *   `LORD_SKILL_NID = "Lord"`
        *   `CAPTURED_SKILL_NID = "Captured"`

### 3. Non-Lord Unit Escape

*   **Condition**: A player unit (not having the `Lord` skill) moves onto a tile with a region `nid` of `EscapePoint`.
*   **Action**:
    *   The unit is removed from the current map using `action.do(action.RemoveUnit(unit))`.
    *   The unit remains in the player's party roster for future chapters (they are not added to `game.killed_units` or similar).
    *   An alert message is displayed: `"{unit.name} has escaped!"`.

### 4. Lord Unit Escape & Chapter End

*   **Lord Identification**: The "Lord" unit is identified by possessing a specific skill.
    *   Skill NID: `Lord`
    *   Defined in: [`game/game_data/skills.json`](game/game_data/skills.json:543)
        ```json
        {
          "nid": "Lord",
          "name": "Lord",
          "desc": "Identifies this unit as a Lord. If this unit escapes, the chapter ends.",
          "icon_nid": "GenericSkill",
          "icon_index": [0, 2], // Example icon
          "components": [ { "nid": "hidden", "name": "Hidden" } ]
        }
        ```
    *   Assigned to: Leif in [`game/game_data/units.json`](game/game_data/units.json:46).
*   **Condition**: A player unit with the `Lord` skill moves onto a tile with a region `nid` of `EscapePoint`.
*   **Actions**:
    1.  **Lord Escapes**: The Lord unit is removed from the map (`action.do(action.RemoveUnit(unit))`).
    2.  **Alert**: Message `"{Lord_unit.name} has escaped! The chapter ends."` is displayed.
    3.  **Flag Remaining Units as Captured**:
        *   The script iterates through all other player units still on the map (`other_unit.position` is not None).
        *   It checks that the unit is not already on an `EscapePoint` and does not already have the `Captured` skill.
        *   If these conditions are met, the `Captured` skill is assigned to them: `skill_system.assign_skill(other_unit, CAPTURED_SKILL_NID)`.
        *   An alert message is displayed: `"{other_unit.name} has been captured!"`.
    4.  **"Captured" Skill**:
        *   Skill NID: `Captured`
        *   Defined in: [`game/game_data/skills.json`](game/game_data/skills.json:556)
            ```json
            {
              "nid": "Captured",
              "name": "Captured",
              "desc": "Unit has been captured and cannot be deployed.",
              "icon_nid": "GenericSkill",
              "icon_index": [2, 2], // Example icon
              "components": [
                { "nid": "prevent_deployment", "name": "Prevent Deployment" },
                { "nid": "status", "name": "Status" }
              ]
            }
            ```
        *   Effect: Units with this skill cannot be deployed in subsequent chapters.
    5.  **End Chapter**:
        *   `game.level_vars['next_level']` is set (e.g., to `"NEXT_CHAPTER_NID"` or a game over screen identifier).
        *   `game.game_vars['_win_game'] = True` is set.
        *   `action.do(action.EndPhase())` and `action.do(action.WinGame())` are called to formally end the chapter.

### 5. Data/Skill Setup Summary

*   **Skills Added/Used**:
    *   `Lord` ([`game/game_data/skills.json`](game/game_data/skills.json:543)): Identifies the main lord.
    *   `Captured` ([`game/game_data/skills.json`](game/game_data/skills.json:556)): Prevents deployment of units left behind.
*   **Unit Modifications**:
    *   Leif ([`game/game_data/units.json`](game/game_data/units.json:46)) assigned the `Lord` skill.
*   **Event Scripts**:
    *   [`game/events/escape_events.py`](game/events/escape_events.py:0): Contains the core `on_unit_move` logic.
    *   [`game/events/global_triggers.yaml`](game/events/global_triggers.yaml:0): Sets up the `unit_move` trigger to call the escape logic.
*   **Map Region**:
    *   Region NID: `EscapePoint` used in TMX files.
    *   Example map: [`game/maps/sandbox_escape_test.tmx`](game/maps/sandbox_escape_test.tmx:0).
## Demonstration Maps

### Map 1 - Supply Raid (`ch1_supply_raid.tmx`)

**Objective:** Defeat all enemies (or seize a specific tile, as per event script).

**Showcased Mechanics:**

This map is designed to provide a practical demonstration of the Capture, Steal, and Staff Miss mechanics.

*   **Capture:**
    *   **Player Unit:** `P001_Leif_Like` (Class: `Lord_Capture`) is designed with the `CaptureCommand` skill and a CON of 7.
    *   **Enemy Target:** `E001_WeakBrigand` (Class: `Brigand`) has a lower CON (6), making them a viable capture target for `P001_Leif_Like`. The player is encouraged to weaken this enemy and then use the Capture command.
    *   The map layout might include chokepoints or terrain to help isolate this enemy for a capture attempt.

*   **Steal:**
    *   **Player Unit:** `P002_Thief` (Class: `Thief_FE5`) possesses the `StealCommand` skill. Their CON is 5.
    *   **Enemy Target:** `E002_ItemHolder` (Class: `Archer_FE5`, CON 5) carries `Vulnerary_Stealable`.
    *   **Item:** `Vulnerary_Stealable` is defined in [`game/game_data/items.json`](game/game_data/items.json:235) with a `Weight` of 1. This ensures `P002_Thief` (CON 5) can steal it from `E002_ItemHolder` (CON 5), as Thief's CON >= Item Weight and Thief's CON >= Enemy's CON (or meets other steal criteria if implemented, like Speed).
    *   The placement of this enemy should allow the thief to approach and attempt to steal.

*   **Staff Miss & Act Again:**
    *   **Player Unit:** `P003_StaffUser` (Class: `Priest`) is equipped with `OffensiveStaff_LowHit`.
    *   **Item:** `OffensiveStaff_LowHit` (defined in [`game/game_data/items.json`](game/game_data/items.json:213)) has a base `Hit` of 40. Combined with the staff hit formula (`BaseHit + 4*SKL`), this creates a significant chance of missing.
    *   **Enemy Target:** `E003_StaffTarget` (Class: `Soldier`) or any other enemy can be targeted by this staff.
    *   **Mechanic Showcase:** When `P003_StaffUser` uses `OffensiveStaff_LowHit` and misses:
        1.  The staff use should not be consumed (as per `lose_uses_on_miss: false` default for `UsesOptions` in `usable_components.py`).
        2.  The staff user (`P003_StaffUser`) should be able to act again (due to the modifications in `on_miss` methods in `usable_components.py`).
    *   The map design should provide opportunities for the staff user to engage enemies with this staff.

### Map 2 — Escape the Fortress (`ch2_escape_fortress.tmx`)

**Objective:** The primary objective is for the Lord unit (e.g., Leif) to escape the fortress by reaching an "EscapePoint" region. Other player units can also escape via these points to be saved for future chapters. If the Lord escapes, any remaining player units on the map who have not escaped are considered "Captured".

**Showcased Mechanics:**

This map is designed to demonstrate several key Thracia 776 mechanics in an indoor setting:

*   **Indoor Dismount:**
    *   **Map Property:** The map `ch2_escape_fortress.tmx` has the custom property `is_indoor: true`.
    *   **Event:** The `Indoor_Map_Auto_Dismount` event (from [`game/events/mount_events.py`](game/events/mount_events.py:74)) is expected to trigger at the start of the level (typically via `global_triggers.yaml` or the level's own event script like [`game/events/ch2_escape_fortress_events.yaml`](game/events/ch2_escape_fortress_events.yaml:19)).
    *   **Demonstration:** Any player units deployed that are of a mounted class (e.g., Cavalier, Pegasus Knight) will automatically be changed to their corresponding dismounted class (e.g., `Cavalier_Dismounted`) at the start of the chapter.
    *   **Optional Commands:** If `DismountCommand` and `MountCommand` skills are assigned, players might attempt to use them. `MountCommand` should ideally fail indoors or be unavailable.

*   **Escape Objective:**
    *   **Map Regions:** The map includes one or more regions with the `nid` "EscapePoint" (e.g., `EscapePoint_1` defined in [`game/maps/ch2_escape_fortress.tmx`](game/maps/ch2_escape_fortress.tmx:37)).
    *   **Event:** The `Global_Escape_Event` (logic in [`game/events/escape_events.py`](game/events/escape_events.py:0), triggered by `unit_move` via [`game/events/global_triggers.yaml`](game/events/global_triggers.yaml:0)) handles the escape.
    *   **Demonstration:**
        *   Non-Lord player units moving onto an `EscapePoint` will be removed from the map and saved.
        *   When the Lord unit (identified by the `Lord` skill, e.g., Leif) moves onto an `EscapePoint`, the chapter ends. Remaining player units are marked with the "Captured" status.

*   **Movement Stars:**
    *   **Units:** Player units should be deployed with `MovementStar_X` skills (e.g., a unit with `MovementStar_1`). These skills are defined in [`game/game_data/skills.json`](game/game_data/skills.json:465) and assigned in [`game/game_data/units.json`](game/game_data/units.json:0).
    *   **Event:** The `Global_Movement_Star_Event` (logic in [`game/events/movement_star_events.py`](game/events/movement_star_events.py:0), triggered by `event_after_wait_action` on the Movement Star skills and a reset event on phase start) should be active.
    *   **Demonstration:** After a unit with Movement Stars performs a "Wait" action, they will have a chance (5% per star) to refresh their actions for that turn. The map design should allow for situations where this could be tactically advantageous.

*   **Leadership Stars:**
    *   **Units:** The Lord unit (e.g., Leif) and potentially other player units should be deployed with `LeadershipStar_X` skills. These skills are defined in [`game/game_data/skills.json`](game/game_data/skills.json:428) and assigned in [`game/game_data/units.json`](game/game_data/units.json:0).
    *   **Event:** The `Global_Leadership_Star_Event` (logic in [`game/events/leadership_star_events.py`](game/events/leadership_star_events.py:0), typically triggered on phase start) should be active to apply bonuses.
    *   **Demonstration:** Allied units within the aura of leaders (the entire map, as per current global implementation) will receive Hit and Avoid bonuses during combat, showcasing the passive benefits of leadership.

*   **Allied Rescue:**
    *   **Units & Scenario:** The map should include:
        *   A relatively frail player unit (low HP/Def).
        *   A stronger player unit with good CON and the `RescueAllyCommand` skill (defined in [`game/game_data/skills.json`](game/game_data/skills.json:101)).
    *   **Mechanic:** The `Global_Allied_Rescue_Event` (from [`game/events/capture_events.yaml`](game/events/capture_events.yaml:54)) handles the rescue.
    *   **Demonstration:** The map design should present a situation where the frail unit is in danger, making it beneficial for the stronger unit to use the `RescueAllyCommand`. This will also demonstrate the `CarryingPenalty` and potentially `CarryingMovementPenalty` applied to the rescuer.

**Crucial Setups:**

*   **Map Properties:** `is_indoor: true` in [`ch2_escape_fortress.tmx`](game/maps/ch2_escape_fortress.tmx:0).
*   **Regions:** At least one `EscapePoint` region in the TMX file.
*   **Unit Skills:**
    *   Mounted units for auto-dismount.
    *   Lord unit with the `Lord` skill.
    *   Units with `MovementStar_X` and `LeadershipStar_X` skills.
    *   Units suitable for demonstrating Rescue (one frail, one strong with `RescueAllyCommand`).
*   **Event Scripts:**
    *   [`game/events/ch2_escape_fortress_events.yaml`](game/events/ch2_escape_fortress_events.yaml:0) should correctly set up the chapter.
    *   Ensure `Indoor_Map_Auto_Dismount`, `Global_Leadership_Star_Event`, `Global_Movement_Star_Event`, and `Global_Escape_Event` are active, likely through `global_triggers.yaml` or explicit calls in the chapter event script.

### Map 3 — Fatigue Trials (`ch3a_fatigue_trial.tmx` & `ch3b_fatigue_results.tmx`)

**Objective (3a):** Survive for a set number of turns or defeat a specific enemy. The primary goal is for the player to engage in actions that accumulate fatigue on their units.
**Objective (3b):** Observe the deployment list, noting units unavailable due to fatigue. Optionally, a very minor encounter or simply ending the chapter after observation.

**Showcased Mechanics:**

These two linked maps are designed to clearly demonstrate:

1.  **Fatigue Lock-out Across a Chapter Transition:**
    *   **`ch3a_fatigue_trial.tmx`**:
        *   **Purpose:** This map serves as the "fatigue accumulation" phase.
        *   **Design:** It should feature scenarios encouraging repeated actions. Examples:
            *   Player staff users healing each other or healing durable, non-threatening units.
            *   Player combat units attacking durable enemies that don't pose a significant threat, allowing for many rounds of combat.
            *   A longer turn limit or a "Defeat Commander" objective that requires sustained engagement.
        *   **Eventing:** The [`game/events/ch3a_fatigue_trial_events.yaml`](game/events/ch3a_fatigue_trial_events.yaml:0) script will manage unit deployment, basic AI, and the win condition. Crucially, upon chapter completion, it transitions to `ch3b_fatigue_results.tmx`. The engine's standard end-of-chapter sequence should trigger the `Chapter_End_Fatigue_Processing` event from [`game/events/fatigue_events.py`](game/events/fatigue_events.py:0) to assess and apply the `Fatigued_Out` status to units whose fatigue exceeds their Max HP.
    *   **`ch3b_fatigue_results.tmx`**:
        *   **Purpose:** This map serves as the "results" phase, directly showing the consequences of fatigue accumulated in `ch3a`.
        *   **Design:** This can be a very simple map, potentially just a deployment screen leading into an immediate chapter end, or a small, non-challenging encounter.
        *   **Demonstration:** The key element is the **deployment list** presented to the player at the start of this chapter. Units that received the `Fatigued_Out` status at the end of `ch3a` should be greyed out, unselectable, or otherwise clearly indicated as unavailable for deployment due to fatigue.
        *   **Eventing:** The [`game/events/ch3b_fatigue_results_events.yaml`](game/events/ch3b_fatigue_results_events.yaml:0) script will handle the display of the objective. The core demonstration relies on the engine's deployment screen correctly interpreting the `Fatigued_Out` status.

2.  **Pursuit Critical Coefficient (PCC) in Action:**
    *   **`ch3a_fatigue_trial.tmx`**:
        *   **Unit Setup:**
            *   Include player units with varying PCC values. This is achieved by assigning them `PCC_X` skills (e.g., `PCC_0`, `PCC_2`, `PCC_5`) in [`game/game_data/units.json`](game/game_data/units.json:0). These skills are defined in [`game/game_data/skills.json`](game/game_data/skills.json:0) and use the `pcc_static` component.
            *   Place enemy units that player units can reliably double (i.e., have significantly lower AS than the player's PCC units). These enemies should also be durable enough to survive the first hit.
        *   **Demonstration:** During combat initiated by a player unit with a PCC skill against an enemy they can double:
            *   The first attack's critical chance should be calculated normally.
            *   The **follow-up attack's** critical chance should be `BaseCrit * PCC_Value`. For example, a unit with `PCC_2` and a base 10% crit on their weapon would have a 20% crit chance on their follow-up. A unit with `PCC_0` would have a 0% crit chance on their follow-up, regardless of weapon crit.
        *   The map design should facilitate these combat scenarios.

**Crucial Setups:**

*   **Fatigue System:**
    *   Ensure `FATIGUE_SYSTEM: true` and `FATIGUE_MODE: 1` are set in [`game/game_data/constants.json`](game/game_data/constants.json:0).
    *   The `FatigueAccumulator` skill must be assigned to player classes in [`game/game_data/classes.json`](game/game_data/classes.json:0).
    *   The `Chapter_End_Fatigue_Processing` event in [`game/events/fatigue_events.py`](game/events/fatigue_events.py:0) must be correctly triggered by the engine at the end of `ch3a`.
    *   The `Fatigued_Out` status skill in [`game/game_data/skills.json`](game/game_data/skills.json:0) must have the `prevent_deployment` component.
*   **PCC System:**
    *   Ensure `PCC_CRIT_MULTIPLIER: true` (or equivalent engine toggle) is active in [`game/game_data/constants.json`](game/game_data/constants.json:0).
    *   `PCC_X` skills must be correctly defined with the `pcc_static` component in [`game/game_data/skills.json`](game/game_data/skills.json:0).
    *   Player units intended to demonstrate PCC must be assigned these skills.
    *   The combat calculation engine must correctly use the `crit_multiplier` provided by the `pcc_static` skill component for follow-up attacks.
*   **Event Files:**
    *   [`game/events/ch3a_fatigue_trial_events.yaml`](game/events/ch3a_fatigue_trial_events.yaml:0) must correctly transition to `ch3b_fatigue_results.tmx` and allow for fatigue accumulation.
    *   [`game/events/ch3b_fatigue_results_events.yaml`](game/events/ch3b_fatigue_results_events.yaml:0) must correctly load and allow the player to observe the deployment list.