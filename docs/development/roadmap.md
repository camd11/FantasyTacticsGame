# Development Roadmap

This document provides an overview of the current state of the Fantasy Tactics Game project and outlines the priorities for future development.

## Current Status

### Recently Completed Work

- **AI System Refinement**: Completed the Two-Phase Goal-Oriented Utility AI system, fixing issues with the TacticalExecutor and improving goal handling
- **Documentation Reorganization**: Consolidated documentation into a structured hierarchy with centralized index and comprehensive guides
- **Visual Testing Framework**: Established multiple approaches for visual testing with both interactive and automated options
- **Tools Directory**: Moved utility scripts to a dedicated tools directory for better organization

### Core Systems Status

| System | Status | Notes |
|--------|--------|-------|
| Core Engine | ✅ Stable | Core game loop and state management functioning |
| Movement | ✅ Stable | Pathfinding and unit movement implemented |
| Combat | ✅ Stable | Basic attack and damage calculations working |
| AI | 🔄 Active Development | Goals and tactical execution implemented, ongoing refinement |
| UI | 🔄 Active Development | Basic UI working, needs more polish |
| Renderer | ✅ Stable | Core rendering pipeline functioning |
| Items/Inventory | 🔄 Active Development | Basic functionality working, needs expansion |
| Skills | 🔄 Active Development | Basic skill system implemented, needs more skills |
| Events | 🛑 Needs Work | Event system needs refinement |

## Development Priorities

### Short-Term (Next 2-4 Weeks)

1. **AI System Robustness**
   - Add comprehensive tests for all goal types
   - Improve AI personas with more specialized behaviors
   - Enhance AI logging for better debugging

2. **Visual Test Stability**
   - Consolidate visual testing approaches
   - Fix renderer errors in visual_test_runner.py
   - Add more visual test scenarios for core mechanics

3. **UI Improvements**
   - Enhance the unit info display
   - Add tooltips for actions and skills
   - Improve feedback for player actions

4. **Core Mechanics Polish**
   - Refine combat calculations for better balance
   - Add status effect visualizations
   - Improve turn flow and action feedback

### Medium-Term (Next 2-3 Months)

1. **Content Expansion**
   - Add more unit classes with varied abilities
   - Create additional map types with unique terrain features
   - Develop more complex scenario objectives

2. **AI Strategic Depth**
   - Implement advanced goals like flanking and coordinated attacks
   - Add situation awareness to AI for better group tactics
   - Create difficulty levels for AI personas

3. **Campaign Development**
   - Design chapter progression system
   - Implement story event triggers
   - Create narrative integration with gameplay

4. **Technical Improvements**
   - Optimize rendering for better performance
   - Refactor core systems for better maintainability
   - Improve save/load system for campaign progress

### Long-Term Vision

1. **Complete Campaign**
   - Full story-driven campaign with multiple chapters
   - Character progression and customization
   - Branching storylines based on player choices

2. **Advanced Battle Mechanics**
   - Weather and time-of-day effects
   - Complex terrain interactions
   - Morale and psychology systems

3. **Rich Content**
   - Diverse unit roster with unique abilities
   - Extensive item and equipment variety
   - Multiple faction aesthetics and mechanics

4. **Enhanced AI**
   - Personality-driven AI behaviors
   - Learning component for adaptive difficulty
   - Campaign-level strategic AI

## Current Technical Debt

Areas that need attention to prevent future development issues:

1. **Test Coverage Gaps**
   - Several gameplay systems lack comprehensive tests
   - Edge case handling in the AI system needs more tests
   - Integration tests between systems need expansion

2. **Code Structure**
   - Some circular dependencies need resolution
   - Better separation of concerns in UI and renderer
   - Event system needs clearer architecture

3. **Performance Concerns**
   - AI path calculation can be slow with many units
   - Renderer has inefficiencies with many sprites
   - Memory usage grows over long sessions

4. **Documentation Gaps**
   - API documentation is inconsistent
   - Some newer systems lack detailed documentation
   - Architecture diagrams need updates for recent changes

## Next Immediate Tasks

For a new developer joining the project, these tasks would be good starting points:

1. **Low Complexity**
   - Add missing unit tests for the MovementSystem
   - Create additional visual test scenarios
   - Improve error messages in the AI logger

2. **Medium Complexity**
   - Implement a new skill type with visual effects
   - Add a specialized AI persona for a specific unit type
   - Enhance the terrain effect system

3. **Higher Complexity**
   - Refactor the event system for better decoupling
   - Implement a new AI goal type with tactical actions
   - Create a more sophisticated UI for unit management

## Conclusion

The Fantasy Tactics Game has a strong foundation with functioning core systems. The focus now is on stabilizing the AI system, expanding content, and polishing the user experience while addressing technical debt to ensure maintainable future development. 