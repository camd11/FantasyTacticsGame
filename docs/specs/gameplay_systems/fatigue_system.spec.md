# Specification: Fatigue System (`fatigue_system.spec.md`)

## 1. Overview

The Fatigue System simulates unit stamina across chapters, forcing players to rotate their army members. Units accumulate fatigue points based on their actions during a chapter. If a unit's fatigue meets or exceeds their maximum HP, they become fatigued and cannot be deployed in the subsequent chapter unless a special item is used. This system encourages broader roster usage and adds a strategic layer to unit management.

**Reference:** Thracia 776 Mechanics (Section 7 in `research.md`)

## 2. Goals

*   Track fatigue accumulation for each player unit based on actions performed.
*   Determine unit fatigue status at the end of each chapter.
*   Prevent fatigued units (except the Lord) from being deployed in the next chapter.
*   Provide mechanisms for fatigue recovery (sitting out, using S-Drink).
*   Integrate fatigue tracking with combat, staff usage, and other relevant actions.
*   Display fatigue information to the player.

## 3. Non-Goals

*   Applying in-chapter stat penalties due to fatigue (Thracia 776 fatigue only affects deployment).
*   Complex fatigue interactions beyond the defined rules (e.g., fatigue affecting skill activation).

## 4. Data Structures

*   **`Unit` Object:**
    *   `current_fatigue`: Integer, tracks fatigue points accumulated *during* the current chapter. Initialized to 0 at the start of each chapter deployment.
    *   `is_fatigued`: Boolean, flag indicating if the unit is fatigued *for the next deployment*. Set at the end of a chapter based on `current_fatigue` vs `max_hp`. Reset when fatigue is cleared.
    *   `max_hp`: Integer, the unit's maximum Hit Points (used as the fatigue threshold).

*   **`Game State`:**
    *   Needs to persist the `is_fatigued` status for each unit between chapters.
    *   Needs to track the current chapter number to know when to start enforcing fatigue (Chapter 8 onwards).

*   **`Item` Data:**
    *   Define `S-Drink` (Stamina Drink) item with an effect to reset `current_fatigue` and `is_fatigued`.

## 5. Core Logic & Pseudocode

### 5.1. `FatigueManager` Module/Class

```pseudocode
MODULE FatigueManager

  // --- Constants ---
  CONSTANT FATIGUE_START_CHAPTER = 8
  CONSTANT FATIGUE_PER_COMBAT = 1
  CONSTANT FATIGUE_PER_STEAL = 1
  CONSTANT FATIGUE_PER_DANCE = 1
  CONSTANT FATIGUE_STAFF_COST = {
    'E': 1,
    'D': 2,
    'C': 3,
    'B': 4,
    'A': 5,
    '*': 5 // Assuming '*' rank staves cost the same as A
  }
  CONSTANT LORD_UNIT_ID = "Leif" // Example ID for the Lord

  // --- Functions ---

  FUNCTION increment_fatigue(unit, action_type, staff_rank=NULL)
    // TDD_ANCHOR: test_increment_fatigue_combat
    // TDD_ANCHOR: test_increment_fatigue_staff_various_ranks
    // TDD_ANCHOR: test_increment_fatigue_steal
    // TDD_ANCHOR: test_increment_fatigue_dance
    // TDD_ANCHOR: test_increment_fatigue_lord_accumulates
    // TDD_ANCHOR: test_increment_fatigue_only_after_chapter_7

    IF GameState.current_chapter < FATIGUE_START_CHAPTER THEN
      RETURN // Fatigue system not active yet
    ENDIF

    VAR fatigue_increase = 0

    SWITCH action_type:
      CASE "COMBAT":
        fatigue_increase = FATIGUE_PER_COMBAT
      CASE "STAFF":
        IF staff_rank IS NOT NULL AND staff_rank IN FATIGUE_STAFF_COST THEN
          fatigue_increase = FATIGUE_STAFF_COST[staff_rank]
        ELSE
          // Log error: Invalid staff rank or rank not provided
          fatigue_increase = 1 // Default to 1 if rank is missing/invalid? Or 0? TBD. Let's assume 1 for now.
        ENDIF
      CASE "STEAL":
        fatigue_increase = FATIGUE_PER_STEAL
      CASE "DANCE":
        fatigue_increase = FATIGUE_PER_DANCE
      // Add other fatigue-inducing actions if any
    ENDSWITCH

    unit.current_fatigue += fatigue_increase

    // Optional: Update UI to show fatigue change or warning if near threshold
    // display_fatigue_update(unit)

  ENDFUNCTION

  FUNCTION check_and_set_fatigue_status_post_chapter(all_player_units)
    // Called at the very end of a chapter, before moving to the next prep screen.
    // TDD_ANCHOR: test_set_fatigue_status_below_threshold
    // TDD_ANCHOR: test_set_fatigue_status_at_threshold
    // TDD_ANCHOR: test_set_fatigue_status_above_threshold
    // TDD_ANCHOR: test_set_fatigue_status_lord_never_fatigued_for_deployment
    // TDD_ANCHOR: test_set_fatigue_status_only_after_chapter_7

    IF GameState.current_chapter < FATIGUE_START_CHAPTER THEN
      // Ensure all units are marked as not fatigued if before Chapter 8
      FOR unit IN all_player_units:
        unit.is_fatigued = FALSE
      ENDFOR
      RETURN
    ENDIF

    FOR unit IN all_player_units:
      // Lord exemption: Leif never becomes 'is_fatigued' for deployment purposes
      IF unit.id == LORD_UNIT_ID THEN
        unit.is_fatigued = FALSE
      ELSE
        // Check if fatigue meets or exceeds max HP
        IF unit.current_fatigue >= unit.max_hp THEN
          unit.is_fatigued = TRUE
        ELSE
          unit.is_fatigued = FALSE
        ENDIF
      ENDIF

      // Reset the *current chapter* fatigue counter for the next map/prep screen
      // The 'is_fatigued' flag persists until cleared.
      unit.current_fatigue = 0

    ENDFOR

  ENDFUNCTION

  FUNCTION reset_fatigue_for_unit(unit)
    // Called when a unit sits out a chapter or uses an S-Drink.
    // TDD_ANCHOR: test_reset_fatigue_clears_flag_and_counter

    unit.current_fatigue = 0 // Should already be 0 unless S-Drink used mid-prep?
    unit.is_fatigued = FALSE
    // Optional: Update UI

  ENDFUNCTION

  FUNCTION handle_deployment_fatigue(deployed_units, benched_units)
    // Called at the start of a new chapter deployment (after prep screen confirms deployment).
    // TDD_ANCHOR: test_handle_deployment_resets_benched_unit_fatigue
    // TDD_ANCHOR: test_handle_deployment_keeps_deployed_unit_fatigue_status

    // Reset fatigue for units who were benched (sat out)
    FOR unit IN benched_units:
      reset_fatigue_for_unit(unit)
    ENDFOR

    // Deployed units retain their 'is_fatigued' status (which should be FALSE if they were allowed deployment)
    // Their 'current_fatigue' is already 0, ready for the new chapter.

  ENDFUNCTION

  FUNCTION can_deploy_unit(unit)
    // Used by the Deployment/Prep Screen UI to determine availability.
    // TDD_ANCHOR: test_can_deploy_not_fatigued
    // TDD_ANCHOR: test_can_deploy_fatigued_non_lord
    // TDD_ANCHOR: test_can_deploy_fatigued_lord
    // TDD_ANCHOR: test_can_deploy_before_chapter_8

    IF GameState.current_chapter < FATIGUE_START_CHAPTER THEN
      RETURN TRUE // Fatigue not enforced yet
    ENDIF

    IF unit.id == LORD_UNIT_ID THEN
      RETURN TRUE // Lord can always deploy
    ELSE
      RETURN NOT unit.is_fatigued
    ENDIF

  ENDFUNCTION

  FUNCTION use_stamina_drink(unit)
    // Called when the S-Drink item is used from the prep screen inventory.
    // TDD_ANCHOR: test_use_stamina_drink_resets_fatigue

    reset_fatigue_for_unit(unit)
    // Consume the S-Drink item from inventory
    InventoryManager.remove_item(unit, "S-Drink", 1) // Example call

  ENDFUNCTION

ENDMODULE
```

### 5.2. Integration Points

*   **Combat System:** After any combat round concludes (attack or counter-attack), call `FatigueManager.increment_fatigue(unit, "COMBAT")` for each participating player unit.
*   **Staff System:** After a staff is successfully used, call `FatigueManager.increment_fatigue(unit, "STAFF", staff_rank=used_staff.rank)` for the staff user.
*   **Skill System (Steal/Dance):** After a successful Steal or Dance action, call `FatigueManager.increment_fatigue(unit, "STEAL")` or `FatigueManager.increment_fatigue(unit, "DANCE")` respectively for the acting unit.
*   **Chapter End:** Before transitioning to the next chapter's preparations, call `FatigueManager.check_and_set_fatigue_status_post_chapter(GameState.get_all_player_units())`.
*   **Deployment/Prep Screen:**
    *   Use `FatigueManager.can_deploy_unit(unit)` to determine if a unit is selectable for deployment. Grey out or mark units where this returns `FALSE`.
    *   Provide an option to use `S-Drink` from the inventory/prep menu, which calls `FatigueManager.use_stamina_drink(unit)`. Using the drink should immediately update the unit's deployability status in the UI.
    *   After the player confirms the deployment list, call `FatigueManager.handle_deployment_fatigue(deployed_units, benched_units)`.
*   **Game State:** Ensure `is_fatigued` status is saved and loaded correctly between sessions and chapters.
*   **UI:**
    *   Display `unit.current_fatigue` and `unit.max_hp` on the unit status screen.
    *   Visually indicate fatigue status (e.g., yellow numbers near threshold, greyed out unit) on the prep screen roster.

## 6. Edge Cases & Considerations

*   **Fatigue Start:** Ensure the system only becomes active from Chapter 8 onwards. No fatigue should accumulate or be enforced before then.
*   **Lord Exemption:** Double-check that the Lord (Leif) can always be deployed, even if their theoretical fatigue exceeds Max HP. They should still *accumulate* fatigue points, however.
*   **S-Drink Usage:** Can S-Drinks be used mid-chapter? (Likely no, only prep screen). Ensure the timing and effect are correct. What happens if an S-Drink is used on a non-fatigued unit? (Should still reset `current_fatigue` to 0, harmlessly).
*   **Multi-Part Chapters:** How does fatigue carry over between parts of a multi-part chapter (e.g., Chapter 16A/16B)? (Assumed fatigue accumulates across parts and is checked only at the very end of the entire chapter sequence before the *next* chapter's prep).
*   **Staff Rank Missing:** How to handle fatigue if staff rank data is missing or invalid? (Defaulted to 1, but needs confirmation).
*   **Max HP Changes:** If a unit's Max HP changes during a chapter (e.g., level up, HP booster), which value is used for the fatigue check at the end? (Likely the Max HP value *at the time of the check*).
*   **Saving/Loading:** Ensure fatigue state (`is_fatigued`) is correctly persisted.

## 7. TDD Anchors Summary

*   `test_increment_fatigue_combat`
*   `test_increment_fatigue_staff_various_ranks`
*   `test_increment_fatigue_steal`
*   `test_increment_fatigue_dance`
*   `test_increment_fatigue_lord_accumulates`
*   `test_increment_fatigue_only_after_chapter_7`
*   `test_set_fatigue_status_below_threshold`
*   `test_set_fatigue_status_at_threshold`
*   `test_set_fatigue_status_above_threshold`
*   `test_set_fatigue_status_lord_never_fatigued_for_deployment`
*   `test_set_fatigue_status_only_after_chapter_7`
*   `test_reset_fatigue_clears_flag_and_counter`
*   `test_handle_deployment_resets_benched_unit_fatigue`
*   `test_handle_deployment_keeps_deployed_unit_fatigue_status`
*   `test_can_deploy_not_fatigued`
*   `test_can_deploy_fatigued_non_lord`
*   `test_can_deploy_fatigued_lord`
*   `test_can_deploy_before_chapter_8`
*   `test_use_stamina_drink_resets_fatigue`