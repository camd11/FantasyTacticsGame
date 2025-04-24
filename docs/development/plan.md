# Development Plan: Core Game Mechanics and Visual Tests

This document outlines the next steps for implementing and improving core game mechanics in the Fantasy Tactics Game, based on research into Fire Emblem: Thracia 776.

## Testing Vision

All implemented features should follow our three-component testing approach:

1. **Standard Logging:** Console output and error logs for basic verification of logic and functionality.
2. **Visual Logs:** Text-based and HTML visual logs documenting turn-by-turn game state changes for detailed analysis.
3. **Pygame Visuals:** Interactive graphical display allowing direct observation of gameplay mechanics and animations.

This approach ensures comprehensive validation of functionality, behavior, and visual presentation for each feature implemented.

## Phase 1: Foundational Systems & Corrections (Based on New Research)

### Objective: Implement core Thracia 776 mechanics accurately and correct existing implementations based on detailed research.

**Tasks:**

1.  **Stats System Refinement:**
    *   Verify universal stat caps (HP 80, others 20).
    *   Implement Build (Bld) stat and its effect on Attack Speed (AS = Spd - MAX(0, Wpn Wt - Bld)). **Custom mechanic:** Unlike Thracia, Bld mitigates weight for ALL weapons, including tomes.
    *   Implement Pursuit Critical Coefficient (PCC) mechanic for follow-up critical hits. Crit cap on first hit (25% unless Wrath).
    *   Implement Leadership Stars (LS) global bonus (+3 Hit/Avo per star).
    *   Implement Movement Stars (MS) re-action chance (5 * MS %).
    *   **(Doc Ref:** `docs/game_mechanics/Unit_Stats.md`)**
    *   **Testing:** Create tests with all three components to validate stat calculations and their effects.

2.  **Combat System Core:**
    *   Implement accurate Hit Rate formula: `(Wpn Hit + (Skl*2) + Lck + Supports + LS + Charisma + Triangle) - Target Avoid`. Cap 1-99%.
    *   Implement accurate Avoid formula: `(AS*2) + Lck + Supports + LS + Charisma + Terrain Bonus`.
    *   Implement Weapon Triangle (+/- 5 Hit for Phys/Anima, Light/Dark vs Anima).
    *   Implement Staff Accuracy formula: `Base (60/100) + (Skl*4)`. Cap 1-99%.
    *   Implement Status Staff Condition: `User Mag > Target Mag`. Fails on Thrones/Gates.
    *   Implement Staff Double-Casting chance: `(Spd + Skl + Lck) / 2 %`.
    *   **(Doc Ref:** `docs/game_mechanics/Combat_System.md`)**
    *   **Testing:** Create tests with all three components showcasing hit calculation, combat resolution, and staff usage.

3.  **Rescue Mechanics Correction:**
    *   Implement Bld check: `Rescuer Bld >= Target Bld / 2` (adjust +5 Bld for mounted rescuer).
    *   Implement Rule: Cannot rescue a unit already rescuing someone else.
    *   Implement Stat Penalty: Rescuer stats (Str/Mag/Skl/Spd/Def) halved.
    *   Implement Movement Penalty: Rescuer Mov halved if `Carried Bld > Carrier Bld / 2` (adjust Bld for mount).
    *   Ensure Drop/Take/Give actions function correctly.
    *   **(Doc Ref:** `docs/game_mechanics/Unique_Systems.md`)**
    *   **Testing:** Create tests demonstrating rescue mechanics with proper visualization of stat changes and movement penalties.

4.  **Dismounting System:**
    *   Implement automatic dismounting indoors / voluntary outdoors.
    *   Apply stat penalties (loss of Mounting Gains from `docs/research/New_Stats.md`).
    *   Change movement type and restrict weapon access (usually Sword only).
    *   Remove Canto ability when dismounted.
    *   Allow remounting outdoors.
    *   **(Doc Ref:** `docs/game_mechanics/Unique_Systems.md`, `docs/research/New_Stats.md`)**
    *   **Testing:** Create tests showing the dismounting process, stat changes, and behavior differences with visual feedback.

5.  **Basic Skills Implementation:**
    *   Implement Canto (for mounted units, post-action movement, blocked by Capture/Rescue actions).
    *   Implement Wrath (guaranteed crit on counter).
    *   Implement Ambush (Vantage - attack first on enemy phase).
    *   Implement Elite (Paragon - double EXP gain).
    *   **(Doc Ref:** `docs/game_mechanics/Skills.md`)**
    *   **Testing:** Create tests for each skill with visual indicators when skills activate.

6.  **Weather System (Initial Pass):**
    *   Create `WeatherSystem` class.
    *   Implement basic weather types (Clear, Rain, Snow, Fog).
    *   **Correction:** Based on research, Thracia 776 weather seems primarily *cosmetic* with *no* significant gameplay effects (unlike GBA games). Focus on visual implementation (rain/snow particles, fog overlay) without stat penalties for now, pending further confirmation if desired.
    *   **(Doc Ref:** `docs/game_mechanics/Map_Environment.md`, `tests/.../test_weather_effects.py` - Note: Tests may need adjustment if penalties are removed).
    *   **Testing:** Create tests demonstrating weather visuals in Pygame with appropriate particle effects.

**Testing Required:** Create/update tests demonstrating Bld/AS, PCC, LS/MS effects, Staff Accuracy/Conditions, corrected Rescue/Dismount, basic skills (Canto, Wrath, Ambush, Elite), and cosmetic weather visuals. Ensure all tests include standard logging, visual logs, and Pygame visualization.

## Phase 2: Advanced Systems & Unique Mechanics

### Objective: Implement Thracia-specific systems like Capture and Fatigue, and expand core systems.

**Tasks:**

1.  **Capture System:**
    *   Implement Capture command & Bld check (`Player Bld > Enemy Bld` or player mounted).
    *   Implement combat with halved initiator stats.
    *   Implement carrying mechanic (halved captor stats, potential halved Mov).
    *   Implement Item Seizure (Trade with captive) and Release command.
    *   Implement AI logic for capturing player units.
    *   **(Doc Ref:** `docs/game_mechanics/Unique_Systems.md`)**
    *   **Testing:** Create tests showing the capture process with visual indicators for stat penalties and unit status.

2.  **Fatigue System:**
    *   Implement hidden Fatigue counter per unit (except Leif).
    *   Track Fatigue gain from actions (Combat +1, Staff +1-5, Dance +1, Steal +1).
    *   Implement end-of-chapter check (Fatigue > Max HP).
    *   Implement deployment restriction for fatigued units.
    *   Implement S Drink functionality.
    *   **(Doc Ref:** `docs/game_mechanics/Unique_Systems.md`)**
    *   **Testing:** Create tests demonstrating fatigue accumulation and its effects with visual feedback.

3.  **Progression Systems:**
    *   Implement EXP formulas (consider relative levels/class).
    *   Implement WExp gain (including staff ranks).
    *   Implement Promotion via Knight Proof (apply fixed stat gains, WExp boosts).
    *   **(Doc Ref:** `docs/game_mechanics/Progression.md`)**
    *   **Testing:** Create tests showing EXP gain, WExp increases, and the promotion process with animations.

4.  **Advanced Skills:**
    *   Implement Adept (Continue - (AS)% chance).
    *   Implement Luna ((Skl)% chance, ignore defense, guarantee hit).
    *   Implement Sol ((Skl)% chance, absorb HP, guarantee hit).
    *   Implement Pavise ((Level)% chance, negate damage).
    *   Implement Miracle ((Luck*3)% chance or low HP dodge).
    *   Implement Awareness (Nihil - negate skills/crits).
    *   Implement Charge (Accost - repeat combat rounds).
    *   Implement Charisma (passive aura).
    *   **(Doc Ref:** `docs/game_mechanics/Skills.md`)**
    *   **Testing:** Create tests for each skill with appropriate visual effects and animations when they activate.

5.  **Support & Leadership:**
    *   Implement fixed support relationships (bonus within 3 tiles).
    *   Ensure Leadership Star bonus stacks correctly.
    *   **(Doc Ref:** `docs/game_mechanics/Unique_Systems.md`, `Unit_Stats.md`)**
    *   **Testing:** Create tests showing support bonuses with visual indicators for affected units.

6.  **Item System:**
    *   Implement consumable effects (Vulnerary, Holy Water, Keys, Stat Rings, Skill Manuals).
    *   Implement Crusader Scroll effects (growth modification, crit negation).
    *   Implement Convoy access/management.
    *   **(Doc Ref:** `docs/game_mechanics/Items_Equipment.md`)**
    *   **Testing:** Create tests demonstrating item usage with appropriate animations and visual feedback.

**Testing Required:** Demonstrate Capture/Fatigue, Promotion, advanced skills, support bonuses, item effects (especially scrolls), Convoy usage. All tests should implement the three-component approach with standard logging, visual logs, and Pygame visualization.

## Phase 3: AI, Environment & Polish

### Objective: Refine enemy AI, implement map environment features, and polish systems.

**Tasks:**

1.  **AI Behavior:**
    *   Implement varied AI routines (Aggressive, Guard, Flee, etc.).
    *   Refine AI targeting priorities.
    *   Implement AI use of Capture, Steal, Staves effectively.
    *   **Crucially:** Ensure AI *ignores* player Fog of War for targeting/movement as per Thracia 776 behavior.
    *   **(Doc Ref:** `docs/game_mechanics/AI_Behavior.md`)**
    *   **Testing:** Create tests demonstrating different AI behaviors with clear visual indication of decision-making and actions.

2.  **Fog of War System:**
    *   Implement FoW visual obscuring.
    *   Implement vision ranges (base, Thief bonus).
    *   Implement Torch item/staff effects (temporary increased vision, decay).
    *   Implement "bumping" into unseen enemies.
    *   **(Doc Ref:** `docs/game_mechanics/Map_Environment.md`)**
    *   **Testing:** Create tests showing fog of war mechanics with appropriate visual effects for revealing/concealing areas.

3.  **Terrain System:**
    *   Implement all terrain types with correct Mov costs per unit type.
    *   Implement terrain combat bonuses (Avo/Def) and healing effects.
    *   Ensure flier interaction is correct (ignore costs, no bonuses).
    *   **(Doc Ref:** `docs/game_mechanics/Map_Environment.md`)**
    *   **Testing:** Create tests demonstrating movement costs and combat effects with visual feedback.

4.  **Map Objectives:**
    *   Implement Seize, Escape (including Leif rule), Defend conditions.
    *   Implement Reinforcement triggers (turn, location). Consider Ambush Spawns.
    *   **Testing:** Create tests for different objective types with appropriate visual indicators and feedback.

5.  **Final Polish & Integration:**
    *   Develop integrated scenario tests combining multiple mechanics.
    *   Address any remaining bugs or inconsistencies.
    *   Ensure smooth UI/UX for all implemented features.
    *   **Testing:** Create comprehensive scenarios demonstrating multiple systems working together.

**Testing Required:** Showcase AI decision-making (capture, steal, staff use), FoW revealing/concealing, terrain effects on movement/combat, objective completion/failure, reinforcement spawns. All tests should follow the three-component approach.

## Phase 4: Testing Infrastructure Improvements

### Objective: Enhance the testing framework to fully support the three-component testing vision.

**Tasks:**

1.  **Standard Logging Enhancements:**
    *   Standardize log formats across all systems.
    *   Implement log level filtering (DEBUG, INFO, WARNING, ERROR).
    *   Create helpers for consistent logging of game state changes.
    *   Ensure all tests produce meaningful console output.

2.  **Visual Logger Improvements:**
    *   Extend the VisualScenarioLogger to capture more detailed game state information.
    *   Enhance HTML output with better formatting and navigation.
    *   Add support for additional logging points in the game loop.
    *   Implement automatic generation of visual logs for all test types.

3.  **Pygame Visualization Integration:**
    *   Create a standardized testing harness for Pygame visualization.
    *   Implement a common interface for test modules to control rendering.
    *   Develop additional animations and visual effects for all game mechanics.
    *   Ensure all tests have a visual representation option.

4.  **Test Runner Enhancements:**
    *   Modify test runners to support all three components simultaneously.
    *   Implement command-line flags to toggle specific component activation.
    *   Create a unified test selector that works across all test types.
    *   Support batch running of tests with all components enabled.

5.  **Documentation and Guidelines:**
    *   Update testing documentation with detailed examples of three-component tests.
    *   Create templates for new test development.
    *   Document best practices for each testing component.
    *   Provide guidelines for writing tests that work well visually.

6.  **Continuous Integration:**
    *   Set up automated test runs for standard and visual log tests.
    *   Implement screenshot comparison for visual regression testing.
    *   Create reporting mechanisms to track test coverage across all components.

## Development Guidelines

- Prioritize accuracy to Thracia 776 mechanics based on the new documentation.
- Each mechanic should have corresponding tests that implement all three components: standard logging, visual logs, and Pygame visualization.
- All visual elements should have appropriate animations and feedback.
- Maintain clear code documentation.
- Preserve the core tactical feel of Fire Emblem.

## Metrics for Success

- All core Thracia 776 mechanics implemented accurately as per `docs/game_mechanics/`.
- Every feature has comprehensive test coverage with all three testing components.
- Visual tests provide clear, informative feedback about system behavior.
- Robust AI exhibiting Thracia-like behaviors (including ignoring FoW).
- Stable and well-integrated system. 