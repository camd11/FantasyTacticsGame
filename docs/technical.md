## Logging

### Visual Scenario Logger (`src.utils.visual_logger`)

**Purpose:** Provides a human-readable text log of a game scenario, primarily designed for debugging and reviewing AI behavior or specific game sequences. When enabled, it outputs key events and ASCII representations of the map state throughout the simulation.

**Activation:** The logger is activated by passing the `--ascii` command-line flag when running `src/app.py`.

**Output Format (`logs/visual_log_*.txt`):**
- **Initial State:** Records the starting map layout and unit positions.
- **Turn Start:** Marks the beginning of each turn (`----- TURN X START -----`).
- **Phase Start:** Indicates the start of each phase (`--- PHASE ---`).
- **Actions:** Logs actions performed by units, including the unit name, ID, action type, and relevant details (e.g., target position for movement).
- **End-of-Turn State:** Records the map state after the final active phase of each turn (`===== END OF TURN X STATE =====`).

**Integration:**
- An instance of `VisualScenarioLogger` is created in `src/app.py` if the `--ascii` flag is present.
- It's passed to the `EngineCore` instance via the `set_visual_logger()` method after the engine is initialized.
- The `EngineCore` calls the logger's methods (`log_initial_state`, `log_turn_start`, `log_phase_start`, `log_action`, `log_end_of_turn_state`) at appropriate points in the game loop execution.

The logger uses the `CLIDisplay`'s `render_ascii_map` method to generate the map snapshots. 