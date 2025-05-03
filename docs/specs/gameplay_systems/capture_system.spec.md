# Specification: Capture System

**Based on:** `research.md` (Section 5.5)

## 1. Overview

This system handles the 'Capture' mechanic, allowing units to subdue enemies instead of killing them, primarily to take their items. It involves specific conditions, combat penalties, post-capture state management, item trading, and AI considerations.

## 2. Modules and Data Structures

*   **Unit:**
    *   `current_hp`: Integer
    *   `max_hp`: Integer
    *   `stats`: Dictionary (Str, Mag, Skl, Spd, Def, Con, Mov, Luk)
    *   `inventory`: List of Items
    *   `is_mounted`: Boolean
    *   `cls_name`: String (Class Name)
    *   `status`: String (e.g., "Normal", "Captured", "Carrying")
    *   `carried_unit`: Reference to another Unit (or None)
    *   `can_capture`: Boolean (Derived property or flag)
*   **Item:**
    *   `name`: String
    *   `weight`: Integer
    *   `type`: String (e.g., "Weapon", "Consumable")
*   **CombatSystem:** (Assumed dependency for handling capture battles)
*   **InventorySystem:** (Assumed dependency for item transfers)
*   **AISystem:** (Assumed dependency for AI decision making)

## 3. Core Logic

### 3.1. Initiating Capture

**Function:** `can_initiate_capture(attacker: Unit, defender: Unit) -> Boolean`

*   **Purpose:** Determines if the `attacker` can attempt to capture the `defender`.
*   **Logic:**
    1.  Check if `defender` is capturable:
        *   Return `False` if `defender.stats['Con'] >= 20`.
        *   Return `False` if `defender.is_mounted`.
            *   *Exception:* If `defender` is asleep, they might dismount automatically, making them capturable. This interaction needs clarification/handling in the Status Effects system. (`research.md`, line 265)
    2.  Check `attacker`'s ability to capture:
        *   Condition 1: `attacker.stats['Con'] > defender.stats['Con']`.
        *   Condition 2: `attacker.is_mounted`.
        *   Return `True` if Condition 1 OR Condition 2 is met.
    3.  Return `False` otherwise.
*   **TDD Anchor:** `# TEST: test_can_initiate_capture_con_check()`
*   **TDD Anchor:** `# TEST: test_can_initiate_capture_mounted_attacker()`
*   **TDD Anchor:** `# TEST: test_cannot_capture_high_con_defender()`
*   **TDD Anchor:** `# TEST: test_cannot_capture_mounted_defender()`

**Function:** `attempt_capture(attacker: Unit, defender: Unit)`

*   **Purpose:** Initiates the capture attempt, potentially leading to combat.
*   **Logic:**
    1.  Verify `can_initiate_capture(attacker, defender)`. If `False`, abort.
    2.  Check if `defender` is unarmed or incapacitated (e.g., "Sleep" status):
        *   If `True`, proceed directly to `_apply_successful_capture(attacker, defender)` without combat. (`research.md`, line 270)
        *   **TDD Anchor:** `# TEST: test_capture_succeeds_without_combat_on_unarmed_target()`
        *   **TDD Anchor:** `# TEST: test_capture_succeeds_without_combat_on_sleeping_target()`
    3.  If `defender` can fight back:
        *   Apply temporary capture penalties to `attacker`: Halve Str, Mag, Skl, Spd, Def (round down). (`research.md`, line 268)
        *   **TDD Anchor:** `# TEST: test_capture_applies_stat_penalties_to_attacker()`
        *   Initiate combat via `CombatSystem.resolve_combat(attacker, defender, is_capture_attempt=True)`.
        *   Remove temporary penalties from `attacker` after combat resolution.
        *   Check combat outcome:
            *   If `defender.current_hp <= 0`: Call `_apply_successful_capture(attacker, defender)`.
            *   Else (defender survived): Capture failed.

### 3.2. Capture Outcome (Successful Capture)

**Function:** `_apply_successful_capture(capturer: Unit, captured_unit: Unit)`

*   **Purpose:** Handles the state changes when a capture is successful.
*   **Logic:**
    1.  Set `captured_unit.status = "Captured"`.
    2.  Set `captured_unit.current_hp = 1` (or confirm if it stays at 0 but is treated as captured). *Needs clarification - research suggests HP reduced to 0 triggers capture, but state might imply 1 HP.* Let's assume it stays 0 but status prevents death.
    3.  Set `capturer.status = "Carrying"`.
    4.  Set `capturer.carried_unit = captured_unit`.
    5.  Apply carrying penalties to `capturer`: Halve Str, Mag, Skl, Spd, Def. (`research.md`, line 272, 284)
        *   **TDD Anchor:** `# TEST: test_carrying_unit_has_halved_stats()`
    6.  Apply movement penalty to `capturer` if applicable (based on `captured_unit.stats['Con']` vs `capturer.stats['Con']`). (`research.md`, line 284)
        *   Formula: `if captured_unit.Con > (capturer.Con / 2 + (5 if capturer.is_mounted else 0)) then halve capturer.Mov`.
        *   **TDD Anchor:** `# TEST: test_carrying_unit_movement_penalty_applied()`
        *   **TDD Anchor:** `# TEST: test_carrying_unit_no_movement_penalty_if_light_enough()`
    7.  Visually represent the `capturer` carrying the `captured_unit` (e.g., change sprite).

### 3.3. Stealing Items from Captured Unit

**Function:** `access_captured_inventory(trading_unit: Unit, capturer_unit: Unit) -> List[Item]`

*   **Purpose:** Allows a unit adjacent to the `capturer_unit` to access the inventory of the `carried_unit`.
*   **Logic:**
    1.  Verify `capturer_unit.status == "Carrying"` and `capturer_unit.carried_unit` is not None.
    2.  Verify `trading_unit` is adjacent to `capturer_unit`.
    3.  Return `capturer_unit.carried_unit.inventory`.
*   **TDD Anchor:** `# TEST: test_can_access_captured_unit_inventory_via_trade()`

**Integration with `InventorySystem.trade_item`:**

*   The `trade_item` function needs modification or an overload to handle trading between a `trading_unit` and a `captured_unit` (accessed via the `capturer_unit`).
*   It should allow `trading_unit` to take items from `captured_unit.inventory`.
*   It should prevent giving items *to* the `captured_unit`.
*   Handle inventory limits for the `trading_unit`.
*   **TDD Anchor:** `# TEST: test_trade_takes_item_from_captured_unit()`
*   **TDD Anchor:** `# TEST: test_trade_fails_if_trader_inventory_full()`
*   **TDD Anchor:** `# TEST: test_cannot_trade_item_to_captured_unit()`

### 3.4. Releasing/Dropping Captured Unit

**Function:** `release_captured_unit(capturer: Unit)`

*   **Purpose:** Releases the captured enemy, removing them from the map.
*   **Logic:**
    1.  Verify `capturer.status == "Carrying"` and `capturer.carried_unit` is not None.
    2.  Get reference to `captured_unit = capturer.carried_unit`.
    3.  Remove `captured_unit` from the game map/active units list. (Effectively defeated/retreated).
    4.  Reset `capturer.status = "Normal"`.
    5.  Set `capturer.carried_unit = None`.
    6.  Remove carrying penalties (stats, movement) from `capturer`.
    7.  Grant no EXP for releasing. (`research.md`, line 272, 288)
*   **TDD Anchor:** `# TEST: test_release_removes_captured_unit_from_map()`
*   **TDD Anchor:** `# TEST: test_release_resets_capturer_status_and_penalties()`

**Function:** `drop_captured_unit(capturer: Unit, target_tile: Tile)`

*   **Purpose:** Drops the captured unit onto an adjacent tile (similar to dropping a rescued ally). *Note: Research primarily mentions "Release". Dropping might not apply to captured enemies, only rescued allies. Assuming "Release" is the primary action.* If dropping *is* possible, it would likely make the captured unit an independent (but likely inactive/vulnerable) unit on the map again. This needs clarification. For now, focusing on "Release".

**Function:** `take_captured_unit(taker: Unit, giver: Unit)`

*   **Purpose:** Allows an adjacent ally (`taker`) to take the captured unit from the current `giver`.
*   **Logic:**
    1.  Verify `giver.status == "Carrying"` and `giver.carried_unit` is not None.
    2.  Verify `taker` is adjacent to `giver`.
    3.  Verify `taker` is not already carrying someone (`taker.status == "Normal"`).
    4.  Check if `taker` can carry the `captured_unit` (Con check might apply here too, similar to Rescue). *Needs clarification if Con check applies to taking.* Assume yes for now: `taker.stats['Con'] > giver.carried_unit.stats['Con']`.
    5.  If checks pass:
        *   `captured_unit = giver.carried_unit`
        *   Reset `giver.status = "Normal"`, `giver.carried_unit = None`, remove penalties from `giver`.
        *   Set `taker.status = "Carrying"`, `taker.carried_unit = captured_unit`, apply penalties to `taker`.
*   **TDD Anchor:** `# TEST: test_take_transfers_captured_unit_and_penalties()`
*   **TDD Anchor:** `# TEST: test_take_fails_if_taker_cannot_carry()`

### 3.5. AI Considerations

**Integration with `AISystem.evaluate_actions`:**

*   When an AI unit evaluates potential actions against a target:
    1.  Check if `can_initiate_capture(ai_unit, target_unit)` is `True`.
    2.  If `True`, evaluate "Capture" as a potential action alongside "Attack".
    3.  **Target Selection Priority:**
        *   AI might prioritize capture if the target is unarmed or incapacitated (Sleep). (`research.md`, line 307)
        *   AI might prioritize capture if it can succeed without taking lethal damage (factoring in the halved stats during the capture attempt).
        *   AI might prefer capture over a kill if capture is possible, especially for certain AI personalities (e.g., bandits). (`research.md`, line 307)
        *   **TDD Anchor:** `# TEST: test_ai_prioritizes_capture_on_unarmed_player()`
        *   **TDD Anchor:** `# TEST: test_ai_evaluates_capture_risk_with_halved_stats()`
    4.  **Post-Capture AI:**
        *   If an AI unit successfully captures a player unit:
            *   Its primary goal may become escaping the map with the captive. (`research.md`, line 277)
            *   It may immediately attempt to trade the captive's items to nearby allies. (`research.md`, line 280, 315)
            *   **TDD Anchor:** `# TEST: test_ai_tries_to_escape_after_capturing_player()`
            *   **TDD Anchor:** `# TEST: test_ai_trades_captured_player_items_to_allies()`

## 4. Interactions with Other Systems

*   **Combat System:** Needs to handle the `is_capture_attempt` flag to apply attacker penalties and determine capture success (HP <= 0) instead of death.
*   **Status System:** Sleep status makes units automatically capturable without combat. Needs to handle the state transition (e.g., sleeping mounted unit dismounts). Captured status itself needs definition (prevents action, makes vulnerable).
*   **Inventory System:** Needs to handle trading with captured units.
*   **Unit System:** Needs to track `status` ("Normal", "Carrying", "Captured") and `carried_unit`. Needs to apply/remove stat/movement penalties based on status.
*   **AI System:** Needs to incorporate capture evaluation into action selection and define post-capture behavior (escape, trade items).
*   **Turn System:** Penalties for carrying persist across turns until the carried unit is released/taken.

## 5. Edge Cases & Constraints

*   **Inventory Full:** Cannot take items from captured unit if the trading unit's inventory is full.
*   **Multiple Capturers:** A unit cannot capture if already carrying someone.
*   **Capture Immunity:** Units with Con >= 20 or mounted units cannot be captured.
*   **Releasing:** Releasing removes the unit permanently from the current map.
*   **Player Unit Captured:** Triggers specific AI behavior (escape, item trading) and potential recovery in later chapters (e.g., Chapter 21x). (`research.md`, line 279, 420)
*   **Mounted Capturers:** Can capture regardless of Con difference (vs. non-mounted, non-20-Con targets).
*   **Terrain:** Defensive terrain bonuses apply to the defender during a capture attempt, making it harder. (`research.md`, line 294)