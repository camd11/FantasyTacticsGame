"""
Fantasy Tactics Game - Main Entry Point

This script serves as the main entry point for the game. It parses command-line
arguments and delegates to the GameApplication class to run the game.
"""

import argparse
import logging
from src.app import GameApplication


def main():
    """
    Main entry point for the game.
    
    Parses command-line arguments and initializes the GameApplication.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Fantasy Tactics Game')
    parser.add_argument('--ai-vs-ai', action='store_true', 
                        help='Enable AI vs AI mode (AI controls player units)')
    parser.add_argument('--ascii-display', action='store_true', 
                        help='Enable ASCII map display in the console')
    parser.add_argument('--chapter', type=str, default='1',
                        help='Chapter ID to load (default: 1)')
    parser.add_argument('--gui', action='store_true',
                        help='Enable GUI mode with Pygame')
    args = parser.parse_args()
    
    # Create and run the game application
    app = GameApplication(
        ai_vs_ai=args.ai_vs_ai,
        ascii_display=args.ascii_display,
        chapter_id=args.chapter,
        use_gui=args.gui
    )
    
    # Run the application
    app.run()


if __name__ == "__main__":
    main()