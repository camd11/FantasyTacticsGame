"""
InputHandler module for handling user input in the game.

This module contains the InputHandler class which is responsible for
processing user input events and translating them into game actions.
"""

import pygame


class InputHandler:
    """
    A class for handling user input events and translating them into game actions.
    
    The InputHandler is responsible for processing keyboard, mouse, and other input
    events from Pygame and translating them into appropriate game actions.
    """
    
    def __init__(self, game_engine_api=None):
        """
        Initialize the InputHandler with a game engine API.
        
        Args:
            game_engine_api: An interface to interact with the game engine.
        """
        self.game_engine_api = game_engine_api
        self.event_callbacks = {}
        
    def register_callback(self, event_type, callback):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: The type of event to register for (e.g., pygame.KEYDOWN).
            callback: The function to call when the event occurs.
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
        
    def process_event(self, event):
        """
        Process a Pygame event and trigger appropriate callbacks.
        
        Args:
            event: The Pygame event to process.
        """
        if event.type in self.event_callbacks:
            for callback in self.event_callbacks[event.type]:
                callback(event)
                
    def process_events(self, events):
        """
        Process a list of Pygame events.
        
        Args:
            events: A list of Pygame events to process.
        """
        for event in events:
            self.process_event(event)