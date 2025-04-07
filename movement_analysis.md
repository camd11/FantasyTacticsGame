Debugging the Unit Movement Issue in V7SparcTry2
Problem Summary

In the V7SparcTry2 branch of FantasyTacticsGame, units are not moving as expected – either they don’t move at all or they only move a single tile. This behavior points to a flaw in how movement commands are being processed. After tracing the code, the issue appears to stem from input handling and action processing, rather than the pathfinding algorithm itself. Specifically, the game’s engine is not executing the full movement path because combined move actions (like “move + wait”) are not being handled correctly.
Likely Cause: Combined Move Actions Not Processed

When a player issues a move command via the CLI, the input handler bundles the move with a follow-up action (usually “wait”) into a combined action of type "MOVE_AND_WAIT". For example, after the player selects a destination, the CLI returns a dictionary like:

{  
  'type': 'MOVE_AND_WAIT',  
  'unit_id': <unit_id>,  
  'move_data': {'type': 'MOVE', 'unit_id': <unit_id>, 'path': [(x0,y0), ..., (xt,yt)]},  
  'action_data': {'type': 'WAIT'}  
}

We see this in the CLI input handler code, where after choosing a target tile, the code constructs a combined action with type "MOVE_AND_WAIT"​
github.com
​
github.com
. This combined action includes the movement path and an immediate “wait” action after moving:

move_action = {
    'type': 'MOVE',
    'unit_id': unit_id,
    'path': path
}
# ...
return {
    'type': 'MOVE_AND_WAIT',
    'unit_id': unit_id,
    'move_data': move_action,
    'action_data': {'type': 'WAIT'}
}

The bug is that the game’s main engine loop does not recognize or handle the "MOVE_AND_WAIT" action type. In the engine’s player-phase loop, the code only checks for single action types like "MOVE", "WAIT", "ATTACK", etc., and delegates those to the action handler​
github.com
. Combined types such as "MOVE_AND_WAIT" (and similarly, if any, "MOVE_AND_ATTACK", etc.) are not included in this check. As a result, when a combined move command is returned, the engine’s if/elif logic skips it, meaning the action handler is never invoked to carry out the move:

player_input = self.input_handler.get_input()
if player_input['type'] == "END_TURN":
    break
elif player_input['type'] in ["MOVE", "WAIT", "ATTACK", ...]:
    # Process single actions
    self.action_handler.process_action(player_input['unit_id'], player_input)
# (No branch here catches 'MOVE_AND_WAIT', so nothing happens)

Because "MOVE_AND_WAIT" doesn’t enter the processing pipeline, the movement never executes, and the unit remains in its original place. This explains why the unit appears not to move at all in those cases. Essentially, the move path that was calculated is never fed into the movement system’s execution function.
Why Sometimes “One Square” Movement?

Reports that units move “only one square” could indicate a related logic issue that partially executed a move. One possibility is that earlier in development (or for AI-controlled units), a move might have been attempted as a simple "MOVE" action with a path, but perhaps only the first step was applied due to a misprocessed outcome. For example, if the engine had processed a "MOVE" without the follow-up action (or if the AI tried moving separately), it might have moved the unit one tile and then stopped. However, given the current branch code, the more direct interpretation is that no multi-step movement is completing, leading to either zero movement or the appearance of moving a single tile if an intermediate step was mistakenly applied. The core issue remains the same: the path intended for movement isn’t being fully executed by the game loop.
Key Scripts to Examine

    src/input/cli_input_handler.py: Manages player commands. It constructs combined move actions. The relevant code shows that after selecting a move destination, the input handler returns a combined "MOVE_AND_WAIT" action​
    github.com
    ​
    github.com
    .

    src/core_engine/engine.py: The game loop that reads player_input and decides what to do. Here, the code fails to handle the combined action type, as shown above​
    github.com
    .

    src/core_engine/action_handler.py: Performs the actual move execution. Notably, it has logic to handle combined actions if called. For instance, process_action explicitly checks for "MOVE_AND_WAIT" and then calls handle_move followed by handle_wait​
    github.com
    ​
    github.com
    . The handle_move function uses movementSystem.execute_move(unit_id, path) to move the unit along the full path​
    github.com
    . In other words, the move logic itself (pathfinding and movementSystem) is implemented to move the unit to the target tile – the unit would teleport to the final position (there’s no step-by-step animation in CLI, it just updates the coordinates in one go). This suggests that if handle_move were called correctly, the unit should jump to the chosen tile (not just one square).

Because the action handler’s combined-action branch isn’t reached in the current loop, none of this movement code runs for player moves, which perfectly aligns with the observed issue.
Additional Factors to Check

While the major culprit is the input/engine mismatch, it’s also wise to verify that the pathfinding and movement calculations themselves are working as intended:

    Movement Range Calculation: The movement range for a unit is calculated via MovementSystem.calculate_movement_range(), which delegates to MapSystem.get_reachable_tiles()​
    github.com
    . If units always had a very limited range (like 1), that could cause “only one square” movement. But typically, base movement (MOV) is higher, and the code doesn’t obviously cap it incorrectly. The pathfinder uses Dijkstra’s algorithm to find all reachable tiles within movement_points​
    github.com
    ​
    github.com
    , and reconstructs the optimal path to the destination​
    github.com
    ​
    github.com
    . These routines seem logically sound. A quick check confirms that if a unit has, say, MOV=5, the reachable tiles set and the computed path should cover the full distance, not just one step, provided the engine calls them. So the pathfinding logic is likely fine – the unit’s movement stat (MOV) and terrain costs should be loaded from data, and the algorithm will return a full path. Indeed, when the CLI prints the path (print(f"Moving to {target_pos} along path: {path}")), it shows all intermediate coordinates​
    github.com
    ​
    github.com
    , indicating the correct path was found. The lack of movement is not due to a faulty path, but because execution never happens.

    Validity Checks: The movement system ensures a destination is reachable and not occupied by an enemy. The is_valid_destination() method checks if the target tile is in the reachable set and not currently occupied​
    github.com
    ​
    github.com
    . If a tile were incorrectly deemed invalid, it could prevent movement. However, in practice the user would be prompted “Invalid destination” and asked again, so this likely isn’t the silent failure we’re seeing. It’s more about the action not firing at all.

    Unit State Flags: After moving, the code sets unit.has_moved = True​
    github.com
    and later unit.has_acted = True after the follow-up action​
    github.com
    . If a unit was mistakenly flagged as having moved (or if has_moved was never reset at turn start), it might refuse to move again. The TurnManager resets these at the start of a new turn​
    github.com
    . There’s no indication that these flags are interfering with the first move action of a turn, so they are likely not the direct cause.

Solution Suggestions

1. Fix the Engine’s Action Handling for Combined Moves:
Ensure the game loop recognizes combined actions and passes them to the action handler. This could be done by extending the condition to include combined types or by handling them in a separate branch. For example, modify the engine’s player-phase logic to catch "MOVE_AND_WAIT" (and any similar combined types) and call action_handler.process_action on them. Since the ActionHandler is already equipped to split and execute the combined move+wait sequence​
github.com
​
github.com
, invoking it properly will move the unit along the full path and then perform the waiting action.

Example Fix:

elif player_input['type'] in ["MOVE", "WAIT", "ATTACK", ... , "SEIZE", "MOVE_AND_WAIT", "MOVE_AND_ATTACK"]:
    self.action_handler.process_action(player_input['unit_id'], player_input)

By doing this, a "MOVE_AND_WAIT" input will trigger handle_move -> execute_move (teleporting the unit to the target) and then handle_wait to end the unit’s turn. This should make the unit visibly jump to the intended tile instead of staying put.

2. Adjust Input Handling (Alternative):
Alternatively, one could change the CLI input handler to not require a combined action. For instance, it could return a simple 'MOVE' action with the path, and then immediately process a 'WAIT' in sequence. However, since the infrastructure for combined actions is already in place (and needed for AI combos like move+attack), it’s cleaner to fix the engine loop to support it.

3. Verify Movement Stats & Pathfinding:
After code fixes, double-check that units have appropriate movement points (MOV) loaded from the data and that the pathfinder isn’t constrained unnecessarily. The commit history notes a fix for “AI movement range” which suggests there were some tweaks to reachable tile calculation or usage【35†L179-188】. For example, maybe AI was using an incorrect movement value or the ASCII map wasn’t updating positions (as hinted by a comment in Engine​
github.com
). These should be revisited to ensure the path length used is correct. Given the current logic in find_reachable and reconstruct_path, the unit should traverse the entire path list if executed. If you still observe “one-square” movement after enabling proper execution, then investigate if the path list being passed into execute_move is complete. (As of now, it should be – map_system.get_path() calls the pathfinder’s reconstruct_path which reconstructs the full route from start to end​
github.com
.)

4. Testing After Fix:
Once the engine processes the move, test a scenario: select a unit with a movement greater than 1, choose a destination a few tiles away, and confirm the unit’s position updates correctly to that tile. Also test moving just one tile to ensure that still works (it should). Verify that the unit’s state flags (has_moved/has_acted) prevent additional moves until the next turn, which is the intended behavior.
Conclusion

The movement issue in the V7SparcTry2 branch is primarily caused by a logic oversight in handling combined move actions. The pathfinding and movement execution code exists and is capable of moving units across multiple tiles, but the command never reaches that execution step due to the input/engine mismatch. By correcting the engine’s handling of movement inputs (ensuring combined actions are processed or splitting them appropriately), the unit movement will function properly – units will move along the full calculated path rather than not moving or appearing to inch forward one square at a time. This fix aligns the input flow with the movement system, resolving the observed bug.