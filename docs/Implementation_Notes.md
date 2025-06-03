# Implementation Notes

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