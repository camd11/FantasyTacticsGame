# Specification: Prf Weapon Effects System

**Status: Implemented**

## 1. Overview

This document outlines the design for a system to handle unique effects associated with specific weapons, often referred to as "Prf" (preferred/personal) weapons. The goal is to create a flexible and extensible system that allows defining and applying special behaviors beyond standard weapon statistics (Might, Hit, Crit, Weight, Range, Weapon Type).

## 2. Data Representation

Prf weapon effects will be defined directly within the `data/items.yaml` file, associated with specific weapon item IDs. Each weapon entry can optionally include a `prf_effects` list. Each element in this list represents a single effect and contains a `type` identifier and any necessary parameters for that effect type.

**Example (`data/items.yaml`):**

```yaml
# ... other items ...

I001_IronSword:
  name: Iron Sword
  type: Sword
  mt: 5
  hit: 90
  crit: 0
  wt: 5
  range: [1]
  cost: 460
  wexp: 1

I050_LegendarySword:
  name: Legendary Sword
  type: Sword
  mt: 12
  hit: 85
  crit: 10
  wt: 8
  range: [1]
  cost: 0 # Unbuyable
  wexp: 1
  prf_effects:
    - type: STAT_BOOST
      stat: skl # Skill
      value: 5
    - type: EFFECTIVE_VS
      category: ['armor', 'cavalry'] # Can be unit tags, class types, etc.
    - type: GRANT_SKILL
      skill_id: S010_Vantage # Assumes S010_Vantage is defined in skills.yaml

I051_BraveLance:
  name: Brave Lance
  type: Lance
  mt: 10
  hit: 70
  crit: 0
  wt: 12
  range: [1]
  cost: 7600
  wexp: 1
  prf_effects:
    - type: BRAVE_EFFECT # Allows consecutive attacks if AS allows

I052_VenomDagger:
  name: Venom Dagger
  type: Dagger
  mt: 3
  hit: 95
  crit: 5
  wt: 2
  range: [1]
  cost: 1000
  wexp: 1
  prf_effects:
    - type: STATUS_ON_HIT
      status_id: ST005_Poison # Assumes ST005_Poison is defined
      chance: 100 # Percentage chance

# ... other items ...
```

## 3. Prf Effect Types

The system will initially support the following effect types. Each type will have a corresponding handler function or logic within the relevant game system.

*   **`STAT_BOOST`**: Passively increases a unit's stat while the weapon is equipped.
    *   `stat`: The abbreviation of the stat to boost (e.g., `hp`, `str`, `mag`, `skl`, `spd`, `lck`, `def`, `res`, `mov`).
    *   `value`: The integer amount to increase the stat by.
    *   **Integration:** `UnitSystem` (Stat Calculation)
    *   **TDD Anchor:** `[TDD: Test stat boost effect]`

*   **`EFFECTIVE_VS`**: Grants bonus effective damage against specific targets. The bonus damage calculation (e.g., 2x or 3x weapon might) will follow standard effectiveness rules, potentially defined globally or overridden here.
    *   `category`: A list of strings representing target categories (e.g., class types like `'armor'`, `'cavalry'`, `'flier'`, attributes like `'dragon'`, `'monster'`, specific unit IDs).
    *   *(Optional)* `multiplier`: Override the default effectiveness multiplier (e.g., `3`). Defaults to game's standard multiplier if omitted.
    *   **Integration:** `CombatCalculator` / `CombatSystem` (Damage Calculation)
    *   **TDD Anchor:** `[TDD: Test effective damage effect]`

*   **`GRANT_SKILL`**: Passively grants the unit a skill while the weapon is equipped.
    *   `skill_id`: The ID of the skill to grant (must exist in `data/skills.yaml`).
    *   **Integration:** `UnitSystem` (Skill List Retrieval), any system checking for skills.
    *   **TDD Anchor:** `[TDD: Test grant skill effect]`

*   **`BRAVE_EFFECT`**: Allows the unit to attack twice consecutively if their Attack Speed (AS) is sufficiently higher than the opponent's (or potentially unconditionally, depending on game rules).
    *   *(No parameters needed for basic version)*
    *   **Integration:** `CombatSystem` (Attack Sequence Logic)
    *   **TDD Anchor:** `[TDD: Test brave effect integration]`

*   **`STATUS_ON_HIT`**: Inflicts a status effect on the target upon a successful hit during combat.
    *   `status_id`: The ID of the status effect to inflict.
    *   `chance`: The percentage chance (0-100) of inflicting the status on hit.
    *   **Integration:** `CombatSystem` (Post-Hit Application)
    *   **TDD Anchor:** `[TDD: Test status on hit effect]`

## 4. Integration Points

The application of Prf effects needs to be integrated into various parts of the game logic:

1.  **`UnitSystem` / Stat Calculation:**
    *   When calculating a unit's current stats (e.g., `unit.get_current_stats()`), iterate through the equipped weapon's `prf_effects`.
    *   Apply any `STAT_BOOST` effects.
    *   When retrieving a unit's list of active skills (e.g., `unit.get_active_skills()`), include skills granted by `GRANT_SKILL` effects from the equipped weapon.

2.  **`CombatCalculator` / `CombatSystem` (Damage Calculation):**
    *   During the damage calculation phase, check the attacker's equipped weapon for `EFFECTIVE_VS` effects.
    *   Compare the `category` list against the defender's properties (class type, tags, etc.).
    *   If a match occurs, apply the effective damage multiplier to the weapon's might as per standard rules.

3.  **`CombatSystem` (Combat Flow / Attack Sequence):**
    *   Before initiating attacks, check for `BRAVE_EFFECT` on the attacker's weapon. Modify the attack sequence logic to allow for consecutive hits based on this effect and potentially AS checks.
    *   After a hit connects (damage is dealt), check the attacker's weapon for `STATUS_ON_HIT` effects. Roll for the `chance` and apply the specified `status_id` to the defender if successful.

## 5. Extensibility

The system is designed for extensibility:

*   **Adding New Effect Types:**
    1.  Define a new unique `type` string (e.g., `LIFE_STEAL`).
    2.  Define the required parameters for this new type (e.g., `percentage`).
    3.  Implement the logic for this effect in the relevant system module(s) (`CombatSystem`, `UnitSystem`, etc.). This typically involves adding a new conditional check for the `type` string and executing the corresponding logic.
    4.  Update data files (`data/items.yaml`) to use the new effect type.
    5.  Add corresponding tests.

*   **Effect Handlers:** Consider implementing a dispatcher pattern or a dictionary mapping effect types to handler functions within each relevant system. This can make the integration points cleaner and easier to modify.

    ```python
    # Example in CombatSystem (Conceptual)
    PRF_EFFECT_HANDLERS_ON_HIT = {
        'STATUS_ON_HIT': _apply_status_on_hit,
        # 'LIFE_STEAL': _apply_life_steal, # Future effect
    }

    def _apply_post_hit_prf_effects(attacker, defender, weapon):
        if not weapon or not weapon.prf_effects:
            return
        for effect in weapon.prf_effects:
            handler = PRF_EFFECT_HANDLERS_ON_HIT.get(effect['type'])
            if handler:
                handler(attacker, defender, weapon, effect) # Pass effect data
    ```

## 6. TDD Anchors Summary

*   `[TDD: Test stat boost effect]` - Verify stats are correctly boosted when equipping/unequipping.
*   `[TDD: Test effective damage effect]` - Verify correct damage multiplier against specified categories.
*   `[TDD: Test grant skill effect]` - Verify skill appears in unit's active skills and functions correctly.
*   `[TDD: Test brave effect integration]` - Verify consecutive attacks occur under appropriate conditions.
*   `[TDD: Test status on hit effect]` - Verify status is applied correctly based on chance after a hit.
*   `[TDD: Test multiple effects interaction]` - Verify a weapon with multiple Prf effects applies all correctly.
*   `[TDD: Test effect removal on unequip]` - Verify passive effects (stats, skills) are removed when the weapon is unequipped.