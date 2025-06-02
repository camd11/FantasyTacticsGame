from enum import Enum, auto

class SkillID(Enum):
    """Unique identifiers for skills."""
    VANTAGE = auto()
    WRATH = auto()
    ADEPT = auto()
    CRITICAL = auto()
    NIHIL = auto()
    PAVISE = auto()
    LUNA = auto()
    SOL = auto()
    ASTRA = auto()
    AWARENESS = auto() # FE5 specific - negates enemy criticals
    CHARGE = auto()
    PRAYER = auto()
    STEAL = auto()
    DANCE = auto()
    CONTINUE = auto() # Pursuit in other FEs
    AMBUSH = auto()
    MIRACLE = auto()
    ELITE = auto() # Paragon in other FEs
    BARGAIN = auto()
    # Add other skills as identified from game data

    # Placeholder for weapon-specific skills if needed, e.g.
    # WRATH_SWORD = auto()

    # Placeholder for leadership stars if they are treated as skills
    # LEADERSHIP_STAR_1 = auto()

class Skill:
    """
    Represents a skill that a character or class can possess.
    Skills provide passive bonuses, active commands, or modify combat/unit behavior.

    Attributes:
        id (SkillID): The unique identifier for the skill.
        name (str): The display name of the skill.
        description (str): A textual description of the skill's effects.
        effects (dict): A dictionary defining the skill's impact (currently a placeholder).
    """
    def __init__(self, id: SkillID, name: str, description: str, effects: dict = None):
        """
        Initializes a new Skill instance.

        Args:
            id: The unique SkillID for this skill.
            name: The display name of the skill. Must not be empty.
            description: A description of the skill's effects. Must not be empty.
            effects: A dictionary defining the skill's impact.
                     (Implementation details TBD, placeholder for now)

        Raises:
            ValueError: If name or description is empty.
        """
        if not isinstance(id, SkillID):
            raise TypeError("ID must be a SkillID enum member.")
        if not name:
            raise ValueError("Skill name cannot be empty.")
        if not description:
            raise ValueError("Skill description cannot be empty.")

        self._id: SkillID = id
        self._name: str = name
        self._description: str = description
        self._effects: dict = effects if effects is not None else {}
        # ActivationCondition and other complex properties TBD

    @property
    def id(self) -> SkillID:
        """Gets the unique SkillID of the skill."""
        return self._id

    @property
    def name(self) -> str:
        """Gets the display name of the skill."""
        return self._name

    @property
    def description(self) -> str:
        """Gets the description of the skill."""
        return self._description

    @property
    def effects(self) -> dict:
        """Gets the effects definition of the skill (placeholder)."""
        return self._effects

    def apply_effect(self, target_unit, context) -> None:
        """
        Applies the skill's effect to the target unit within a given context.
        This is a placeholder and will need specific implementation per skill.

        Args:
            target_unit: The UnitInstance the skill is affecting.
            context: The current game context (e.g., combat phase, map state).
        """
        # Specific skill logic would go here, potentially calling out to
        # a registry of effect handlers based on self._effects.
        # For now, this method does nothing or raises NotImplementedError
        # if called directly without a specific skill's override.
        # print(f"Applying effect for skill {self.name} on {target_unit} in context {context}")
        pass # Or raise NotImplementedError("Skill effect application not yet implemented.")

    def __repr__(self) -> str:
        return f"Skill(ID={self.id}, Name='{self.name}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Skill):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

# Example of how SkillTriggerType might look if needed later, based on spec:
# class SkillTriggerType(Enum):
#     PASSIVE = auto()
#     ON_COMBAT_START = auto()
#     ON_HIT = auto()
#     ON_TAKE_DAMAGE = auto()
#     COMMAND = auto()
#     ON_LEVEL_UP = auto()