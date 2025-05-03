# Gameplay Mechanic Test Scenario Initiative

## Purpose

This document tracks the creation of dedicated, isolated gameplay test scenarios for each major implemented mechanic in the Thracia 776 recreation project. These scenarios aim to verify the correct functionality of each mechanic in a controlled gameplay environment.

## Naming Convention

Scenario directories will follow the pattern: `data/scenarios/test_mechanic_<category>_<mechanic_or_action>/`

*   `<category>`: Broad category (e.g., `unit_action`, `combat`, `skill`, `status`, `map`, `resource`, `staff`).
*   `<mechanic_or_action>`: Specific mechanic or action being tested (e.g., `capture_execute`, `skill_astra`, `status_poison_apply`, `map_ballista_fire`).

## Tracking

| Category                     | Mechanic/Action Tested                     | Proposed Scenario Directory Name                 | Status   | Notes                                                                 |
| :--------------------------- | :----------------------------------------- | :----------------------------------------------- | :------- | :-------------------------------------------------------------------- |
| **I. Unit Actions**          |                                            |                                                  |          |                                                                       |
|                              | Capture: Execute Command                   | `test_mechanic_unit_action_capture_execute`      | Ready for Testing | Need units with appropriate CON/HP.                                   |
|                              | Capture: Stat Penalties (Capturer)         | `test_mechanic_unit_action_capture_penalties`    | To Do    | Verify capturer stats after capture.                                  |
|                              | Capture: Status Effects (Captured)         | `test_mechanic_unit_action_capture_status`       | To Do    | Verify captured unit stats/status.                                    |
|                              | Capture: Steal Items                       | `test_mechanic_unit_action_capture_steal`        | To Do    | Capturer needs Thief skill/class. Captured unit needs items.          |
|                              | Capture: Release Command                   | `test_mechanic_unit_action_capture_release`      | To Do    | Capturer needs to use 'Release'.                                      |
|                              | Capture: Rescue by Ally                    | `test_mechanic_unit_action_capture_rescue`       | To Do    | Need ally adjacent to capturer.                                       |
|                              | Steal: Execute Command                     | `test_mechanic_unit_action_steal_execute`        | To Do    | Thief vs target with stealable item. Test SPD/CON checks.             |
|                              | Steal: Fatigue Cost                        | `test_mechanic_unit_action_steal_fatigue`        | To Do    | Verify fatigue increase on steal attempt.                             |
|                              | Rescue: Execute Command                    | `test_mechanic_unit_action_rescue_execute`       | To Do    | Need units with appropriate CON.                                      |
|                              | Rescue: Stat Penalties (Rescuer)           | `test_mechanic_unit_action_rescue_penalties`     | To Do    | Verify rescuer stats after rescue.                                    |
|                              | Rescue: Drop Command                       | `test_mechanic_unit_action_rescue_drop`          | To Do    | Rescuer drops rescued unit.                                           |
|                              | Rescue: Take Command                       | `test_mechanic_unit_action_rescue_take`          | To Do    | Ally takes rescued unit from rescuer.                                 |
|                              | Dismount: Execute Command                  | `test_mechanic_unit_action_dismount_execute`     | To Do    | Mounted unit uses 'Dismount'.                                         |
|                              | Dismount: Stat/Movement Changes            | `test_mechanic_unit_action_dismount_stats`       | To Do    | Verify stats/move type change on dismount/remount.                    |
|                              | Trading: Item Exchange                     | `test_mechanic_unit_action_trade_items`          | To Do    | Two adjacent allies trade items.                                      |
|                              | Trading: Give Item                         | `test_mechanic_unit_action_trade_give`           | To Do    | Test giving when recipient inventory is full/not full.                |
|                              | Talk: Initiate Conversation                | `test_mechanic_unit_action_talk_initiate`        | To Do    | Use predefined talk pair from data. Verify event trigger.             |
|                              | Move Again (Dance/Play): Refresh Unit      | `test_mechanic_skill_move_again_refresh`         | To Do    | Dancer/Bard refreshes adjacent ally who has acted.                    |
|                              | Move Again (Dance/Play): Single Use        | `test_mechanic_skill_move_again_single_use`      | To Do    | Verify unit cannot be refreshed twice in one turn.                    |
| **II. Combat Mechanics**     |                                            |                                                  |          |                                                                       |
|                              | PCC: Initial Attack Crit Cap               | `test_mechanic_combat_pcc_initial_cap`           | To Do    | Setup combat where crit > 25%, verify cap.                            |
|                              | PCC: Follow-up Attack Crit                 | `test_mechanic_combat_pcc_followup`              | To Do    | Setup combat with follow-up, verify PCC multiplier (and 100% cap).    |
|                              | Skill: Astra Activation                    | `test_mechanic_skill_astra_activate`             | To Do    | Unit with Astra attacks. Verify multiple hits, reduced damage.        |
|                              | Skill: Sol Activation                      | `test_mechanic_skill_sol_activate`               | To Do    | Unit with Sol attacks & hits. Verify HP recovery.                     |
|                              | Skill: Luna Activation                     | `test_mechanic_skill_luna_activate`              | To Do    | Unit with Luna attacks high DEF/RES enemy. Verify damage calculation. |
|                              | Skill: Pavise Activation                   | `test_mechanic_skill_pavise_activate`            | To Do    | Unit with Pavise attacked physically. Verify damage negation.         |
|                              | Skill: Nihil Activation                    | `test_mechanic_skill_nihil_activate`             | To Do    | Unit with Nihil vs enemy with combat skill (e.g., Luna). Verify skill negation. |
|                              | Skill: Charge Activation                   | `test_mechanic_skill_charge_activate`            | To Do    | Unit with Charge initiates combat. Verify post-combat move conditions. |
|                              | Prf Weapon: Stat Boost                     | `test_mechanic_prf_stat_boost`                   | To Do    | Requires defining/using a Prf weapon with this effect. Verify stats.  |
|                              | Prf Weapon: Effective Vs                   | `test_mechanic_prf_effective_vs`                 | To Do    | Requires Prf weapon vs specific unit type. Verify effective damage.   |
|                              | Prf Weapon: Grant Skill                    | `test_mechanic_prf_grant_skill`                  | To Do    | Requires Prf weapon granting a skill. Verify skill effect in combat.  |
|                              | Prf Weapon: Brave Effect                   | `test_mechanic_prf_brave_effect`                 | To Do    | Requires Prf weapon with brave effect. Verify multiple attacks.       |
|                              | Prf Weapon: Status on Hit                  | `test_mechanic_prf_status_on_hit`                | To Do    | Requires Prf weapon inflicting status. Verify status application.     |
|                              | Support/Leadership: Adjacent Support       | `test_mechanic_support_adjacent`                 | To Do    | Place supported units adjacent. Verify combat stat bonuses.           |
|                              | Support/Leadership: Leadership Stars       | `test_mechanic_support_leadership`               | To Do    | Place units within range of leader. Verify combat stat bonuses.       |
| **III. Status Effects**      |                                            |                                                  |          |                                                                       |
|                              | Poison: Application & Damage               | `test_mechanic_status_poison_apply_dmg`          | To Do    | Apply poison, end turn, verify HP loss.                               |
|                              | Poison: Cure                               | `test_mechanic_status_poison_cure`               | To Do    | Apply poison, use Restore/Antitoxin, verify removal.                  |
|                              | Sleep: Application & Effect                | `test_mechanic_status_sleep_apply_effect`        | To Do    | Apply sleep, verify unit cannot act.                                  |
|                              | Sleep: Cure/Duration                       | `test_mechanic_status_sleep_cure`                | To Do    | Apply sleep, wait turns or use Restore, verify wake up.               |
|                              | Petrify: Application & Effect              | `test_mechanic_status_petrify_apply_effect`      | To Do    | Apply petrify, verify unit cannot act & high DEF.                     |
|                              | Petrify: Cure/Duration                     | `test_mechanic_status_petrify_cure`              | To Do    | Apply petrify, wait turns or use Restore, verify cure.                |
|                              | Paralysis: Application & Effect            | `test_mechanic_status_paralysis_apply_effect`    | To Do    | Apply paralysis, verify unit cannot act.                              |
|                              | Paralysis: Cure/Duration                   | `test_mechanic_status_paralysis_cure`            | To Do    | Apply paralysis, wait turns or use Restore, verify cure.              |
|                              | Berserk: Application & Effect              | `test_mechanic_status_berserk_apply_effect`      | To Do    | Apply berserk, verify unit attacks nearest unit.                      |
|                              | Berserk: Cure/Duration                     | `test_mechanic_status_berserk_cure`              | To Do    | Apply berserk, wait turns or use Restore, verify cure.                |
|                              | Silence: Application & Effect              | `test_mechanic_status_silence_apply_effect`      | To Do    | Apply silence to mage/staff user, verify inability to use magic.      |
|                              | Silence: Cure/Duration                     | `test_mechanic_status_silence_cure`              | To Do    | Apply silence, wait turns or use Restore, verify cure.                |
| **IV. Map Interactions**     |                                            |                                                  |          |                                                                       |
|                              | Ballista: Mount                            | `test_mechanic_map_ballista_mount`               | To Do    | Unit with correct rank mounts ballista.                               |
|                              | Ballista: Fire                             | `test_mechanic_map_ballista_fire`                | To Do    | Mounted unit fires ballista at target in range. Verify combat.        |
|                              | Ballista: Durability                       | `test_mechanic_map_ballista_durability`          | To Do    | Fire ballista multiple times, verify durability decrease.             |
|                              | Door/Chest: Key Use                        | `test_mechanic_map_door_chest_key`               | To Do    | Unit uses correct key on door/chest. Verify open/item & key consumed. |
|                              | Door/Chest: Locktouch Skill                | `test_mechanic_map_door_chest_locktouch`         | To Do    | Thief uses Locktouch on door/chest. Verify open/item.                 |
|                              | Terrain: Combat Bonuses                    | `test_mechanic_map_terrain_bonus`                | To Do    | Initiate combat on terrain providing bonuses (Fort). Verify stats.    |
|                              | Terrain: Turn Effects (Heal/Damage)        | `test_mechanic_map_terrain_turn_effect`          | To Do    | End turn on Fort/Lava. Verify HP change.                              |
|                              | Fog of War: Vision Range                   | `test_mechanic_map_fog_vision`                   | To Do    | Enable Fog, move unit, verify revealed area.                          |
|                              | Fog of War: Torch/Light                    | `test_mechanic_map_fog_torch`                    | To Do    | Enable Fog, use Torch/Light, verify increased vision.                 |
|                              | Shop/Armory: Purchase                      | `test_mechanic_map_shop_buy`                     | To Do    | Unit visits shop, buys item. Verify gold decrease & item receipt.     |
|                              | Shop/Armory: Sell                          | `test_mechanic_map_shop_sell`                    | To Do    | Unit visits shop, sells item. Verify gold increase & item removal.    |
|                              | Convoy/Supply: Deposit                     | `test_mechanic_map_convoy_deposit`               | To Do    | Unit deposits item into convoy. Verify inventory & convoy state.      |
|                              | Convoy/Supply: Withdraw                    | `test_mechanic_map_convoy_withdraw`              | To Do    | Unit withdraws item from convoy. Verify inventory & convoy state.     |
| **V. Resource Management**   |                                            |                                                  |          |                                                                       |
|                              | Fatigue: Accumulation                      | `test_mechanic_resource_fatigue_accumulate`      | To Do    | Perform actions (combat, staff), verify fatigue increase.             |
|                              | Fatigue: High Fatigue Effect               | `test_mechanic_resource_fatigue_effect`          | To Do    | Test deploying unit with fatigue > max HP (if implemented).           |
| **VI. Staff Usage**          |                                            |                                                  |          |                                                                       |
|                              | Staff: Status Infliction (e.g., Sleep)     | `test_mechanic_staff_status_inflict`             | To Do    | Use Sleep staff on target. Verify status application.                 |
|                              | Staff: Status Cure (Restore)               | `test_mechanic_staff_status_cure`                | To Do    | Use Restore staff on unit with status. Verify removal.                |
|                              | Staff: Warp                                | `test_mechanic_staff_warp`                       | To Do    | Use Warp staff on ally. Verify movement to target location.           |