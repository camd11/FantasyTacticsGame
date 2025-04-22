# Repository Cleanup Plan

This document outlines the steps taken to refactor and clean up the `FantasyTacticsGame` repository on the `FirstCursorTry` branch. The goal is to improve organization, remove obsolete files, and ensure consistency.

## Cleanup Steps

1.  **Document the Plan:**
    *   Create this `CLEANUP_PLAN.md` file.
    *   Commit as "docs: add cleanup plan outlining repository refactor".

2.  **Set Up Test Running:**
    *   Identify and confirm the command to run the test suite (`pytest`).
    *   Run tests after each major step to catch regressions.

3.  **Remove Ignored/Generated Files:**
    *   Delete all `__pycache__/` directories from the repository.
    *   Delete any tracked `.pyc` or `.coverage` files.
    *   Update `.gitignore` to include patterns for `__pycache__/`, `*.pyc`, `*.log`, and `.coverage`.
    *   Commit as "chore: remove pycache, logs, and coverage files; update .gitignore".

4.  **Clean Up Root Directory:**
    *   Delete log files (`*.log`) from the root directory.
    *   Move relevant test scripts (`test_ai_vs_ai.py`) from root to `tests/ai/`.
    *   Remove redundant test scripts (`test_ai_vs_ai_debug.py`, etc.) from root.
    *   Relocate utility scripts (`run_ai_vs_ai_test.py`, `convert_yaml_to_json.py`) from root to a new `tools/` directory.
    *   Remove AI assistant configuration files (`.cursorrules`, `.roomodes`) from root.
    *   Commit as "chore: remove or move miscellaneous root files (logs, AI test scripts, config)".

5.  **Reorganize Documentation:**
    *   Move all standalone `.md` files (except `README.md`, `CLEANUP_PLAN.md`) from root into the `docs/` directory.
    *   Merge `PROJECT_STATUS.md` and `Progress.md` into `docs/status.md`.
    *   Consolidate AI research notes (`AI_*.MD`) into `docs/research/ai_research_summary.md`.
    *   Delete the original merged markdown files from root.
    *   Ensure `README.md` links to relevant documentation within `docs/`.
    *   Commit as "docs: consolidate documentation in docs/ folder, merge duplicate files".

6.  **Simplify Data Directories:**
    *   Assume `data/chapters/` is the canonical source for level data.
    *   Remove the deprecated `data/scenarios/` directory.
    *   Remove the potentially duplicate `data/maps/test_chapter` directory.
    *   Update any code references pointing to the removed data paths.
    *   Commit as "refactor(data): remove deprecated scenario files and unify chapter data".

7.  **Remove Deprecated Code Paths:**
    *   Remove the `ScenarioLoader` module (`src/core_engine/scenario_loader.py`) and its associated tests (`tests/core_engine/test_scenario_loader.py`).
    *   Remove any code that imports or utilizes the `ScenarioLoader`.
    *   Clean up any identified `# TODO remove` or dead code blocks.
    *   Commit as "refactor: remove deprecated code (scenario loader, old systems)".

8.  **Verify and Refine:**
    *   Run the full test suite (`pytest`) and fix any failures.
    *   Ensure the game's CLI entry point still functions.
    *   Commit any necessary fixes as "test: fix tests and references after cleanup".

9.  **Archiving (Optional):**
    *   (Skipped for this plan - focus is on removal)

10. **Final Cleanup & Documentation:**
    *   Update `README.md` and other documentation to reflect the new structure and remove references to deleted components.
    *   Update this `CLEANUP_PLAN.md` if necessary.
    *   Commit as "docs: update README and cleanup plan after refactor completion".

11. **Conclusion:**
    *   Ensure all tests pass.
    *   Push all commits to the remote repository. 