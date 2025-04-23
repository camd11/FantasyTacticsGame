# Changelog

## 2023-07-27: Refactoring and Feature Implementation

### Removed
- Deprecated scenario loader system
- Obsolete backup file `src/gameplay_systems/ai_system_fixed.py.bak`

### Added
- CLI command handling for:
  - Item usage (`_handle_item_action`)
  - Trading between units (`_handle_trade_action`)
  - Visiting locations (`_handle_visit_action`)
  - Seizing objectives (`_handle_seize_action`)
- GUI mode support:
  - Added `--gui` flag to command line arguments
  - Implemented Pygame initialization when GUI mode is enabled
  - Created separate game loops for CLI and GUI modes

### Changed
- Updated `src/main.py` to use chapter-based loading with `--chapter` flag
- Improved code consistency and error handling in CLI input handler
- Separated GUI initialization from CLI mode to avoid conflicts

### Fixed
- Various function calls in CLI handlers were corrected to use `_handle_command_input()` instead of non-existent `_handle_unit_actions()`
- Added proper inventory size validation during item trading
- Added unit deselection after actions to prevent unintended behavior

## Next Steps
- Complete GUI implementation with unit sprites and action controls
- Add support for more advanced scenario events
- Improve battle animations and visual feedback 