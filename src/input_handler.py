def get_player_input(prompt="Enter command: "):
    """
    Gets input from the player via the console.
    Returns the raw input string.
    """
    try:
        command = input(prompt)
        return command.strip().lower()
    except EOFError:
        # Handle cases where input stream is closed (e.g., testing)
        return "quit" # Or raise a specific exception

def parse_command(command_string):
    """
    Parses a raw command string into an action and arguments.
    Examples:
        "move 5 10" -> ('move', (5, 10))
        "select"      -> ('select', None)
        "wait"        -> ('wait', None)
        "quit"        -> ('quit', None)
        "w"           -> ('cursor_up', None) # Example cursor movement
        "a"           -> ('cursor_left', None)
        "s"           -> ('cursor_down', None)
        "d"           -> ('cursor_right', None)
    Returns a tuple (action_type, args) or (None, None) if invalid.
    """
    parts = command_string.split()
    if not parts:
        return None, None

    action = parts[0]

    # Simple cursor movement aliases (WASD)
    if action == 'w': return 'cursor_up', None
    if action == 'a': return 'cursor_left', None
    if action == 's': return 'cursor_down', None
    if action == 'd': return 'cursor_right', None
    if action == 'e': return 'select', None # Add 'e' for examine/select

    # Other commands
    if action == "move" and len(parts) == 3:
        try:
            x = int(parts[1])
            y = int(parts[2])
            return 'move', (x, y)
        except ValueError:
            return None, None # Invalid coordinates
    elif action in ["select", "wait", "quit", "attack", "item", "capture", "endturn"]: # Add more actions as needed
         # Commands that might take more args later, but basic form is just the action word
         # For now, we only handle the action type
         # TODO: Add argument parsing for actions like 'attack', 'item' etc.
        return action, None
    else:
        # Unknown command
        return None, None

# Example usage (can be run standalone for testing)
if __name__ == "__main__":
    while True:
        cmd_str = get_player_input()
        action_type, args = parse_command(cmd_str)
        if action_type == 'quit':
            break
        if action_type:
            print(f"Parsed: Action='{action_type}', Args={args}")
        else:
            print(f"Invalid command: '{cmd_str}'")