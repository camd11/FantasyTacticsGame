# Assuming Character and UnitInstance might be needed for apply_autolevel context later
# from .character import Character
# from .unit_instance import UnitInstance

class AutolevelScheme:
    """
    Represents an autolevel scheme, defining a set of growth rates.
    These schemes can be used for generic units or as a base for specific characters.

    Attributes:
        scheme_id (str): The unique identifier for the scheme.
        name (str): The display name of the scheme.
        description (str): A textual description of the scheme.
        growth_hp (int): HP growth rate (0-100+).
        growth_strength (int): Strength growth rate.
        growth_magic (int): Magic growth rate.
        growth_skill (int): Skill growth rate.
        growth_speed (int): Speed growth rate.
        growth_luck (int): Luck growth rate.
        growth_defense (int): Defense growth rate.
        growth_constitution (int): Constitution growth rate.
        growth_movement (int): Movement growth rate.
    """
    # Expected keys in the input growths_dict
    STAT_INPUT_KEYS = ["HP", "Strength", "Magic", "Skill", "Speed", "Luck", "Defense", "Constitution", "Movement"]
    # Corresponding internal lowercase attribute suffixes
    INTERNAL_STAT_SUFFIXES = [key.lower() for key in STAT_INPUT_KEYS]


    def __init__(self, scheme_id: str, growths_dict: dict, name: str = "", description: str = ""):
        """
        Initializes an AutolevelScheme.

        Args:
            scheme_id: The unique identifier for the scheme.
            growths_dict: A dictionary containing growth rates for stats.
                          Expected keys match STAT_INPUT_KEYS (e.g., "HP", "Strength").
                          Values must be non-negative integers.
            name: The display name of the scheme (optional).
            description: A description of the scheme (optional).
        
        Raises:
            ValueError: If scheme_id is invalid, or if growths_dict is missing keys
                        or contains invalid (e.g., negative or non-integer) growth rates.
            TypeError: If scheme_id, name, or description are not strings.
        """
        if not isinstance(scheme_id, str) or not scheme_id:
            raise ValueError("scheme_id must be a non-empty string.")
        self.scheme_id: str = scheme_id

        if not isinstance(name, str):
            raise TypeError("name must be a string.")
        self.name: str = name

        if not isinstance(description, str):
            raise TypeError("description must be a string.")
        self.description: str = description

        # Validate and assign growths
        for input_key, internal_suffix in zip(self.STAT_INPUT_KEYS, self.INTERNAL_STAT_SUFFIXES):
            if input_key not in growths_dict:
                raise ValueError(f"Missing growth key in growths_dict: {input_key}")
            
            value = growths_dict[input_key]
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"Growth rate for {input_key} ('{value}') in scheme '{scheme_id}' "
                    "must be a non-negative integer."
                )
            
            setattr(self, f"growth_{internal_suffix}", value)

    def apply_autolevel(self, character_instance: any, levels_to_gain: int) -> None: # 'any' for now
        """
        Applies autoleveling to a character instance for a number of levels.

        This method is a placeholder. Its detailed logic for how autoleveling
        affects a character (e.g., direct stat application vs. influencing
        level-up chances) is not fully specified for this component in isolation
        and would typically involve interaction with the Character/UnitInstance class,
        including random number generation and respecting stat caps.

        Args:
            character_instance: The character instance (e.g., Character or UnitInstance)
                                to apply autoleveling to. Type hint is 'any' for now.
            levels_to_gain: The number of levels to gain.

        Raises:
            ValueError: If levels_to_gain is negative.
            TypeError: If levels_to_gain is not an integer.
        """
        if not isinstance(levels_to_gain, int):
            raise TypeError("levels_to_gain must be an integer.")
        if levels_to_gain < 0:
            raise ValueError("levels_to_gain must be a non-negative integer.")
        
        # Placeholder: Actual logic would involve iterating `levels_to_gain` times.
        # For each level, "roll" for stat increases based on the scheme's
        # growth rates (e.g., self.growth_hp, self.growth_strength) and apply them
        # to the character_instance, likely via methods on Character or UnitInstance
        # that handle stat caps and other level-up mechanics.
        #
        # import random
        # for _ in range(levels_to_gain):
        #     for stat_suffix in self.INTERNAL_STAT_SUFFIXES:
        #         growth_rate = getattr(self, f"growth_{stat_suffix}")
        #         if random.randint(1, 100) <= growth_rate:
        #             # character_instance.increase_stat(stat_suffix, 1) # Hypothetical method
        #             pass
        pass