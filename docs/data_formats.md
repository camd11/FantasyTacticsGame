# Fantasy Tactics Game Data Formats

This document defines the data formats used in the Fantasy Tactics Game project. It specifies how game data is structured in external files, making it easy to modify and extend the game without changing the code.

## Overview

The game uses JSON as the primary format for data files. This provides a good balance of human readability, ease of editing, and parsing performance. The data is organized into several categories:

1. Units
2. Classes
3. Weapons and Items
4. Maps
5. Chapters
6. Skills
7. Terrain

## Directory Structure

```
/data
  /units
    player_units.json
    enemy_units.json
    npc_units.json
  /classes
    classes.json
    promotion_data.json
  /weapons
    weapons.json
    staves.json
    items.json
  /maps
    /chapter1
      map.json
      events.json
      units.json
    /chapter2
      ...
  /chapters
    chapters.json
    objectives.json
  /skills
    skills.json
  /terrain
    terrain_types.json
    movement_costs.json
    terrain_bonuses.json
```

## Unit Data Format

Units are defined in JSON files with the following structure:

```json
{
  "units": [
    {
      "id": "leif",
      "name": "Leif",
      "class": "lord",
      "level": 1,
      "base_stats": {
        "hp": 22,
        "strength": 6,
        "magic": 2,
        "skill": 6,
        "speed": 8,
        "luck": 6,
        "defense": 4,
        "constitution": 6,
        "movement": 6
      },
      "growth_rates": {
        "hp": 70,
        "strength": 35,
        "magic": 10,
        "skill": 40,
        "speed": 50,
        "luck": 40,
        "defense": 25,
        "constitution": 5,
        "movement": 3
      },
      "weapon_ranks": {
        "sword": "C",
        "lance": null,
        "axe": null,
        "bow": null,
        "fire": null,
        "thunder": null,
        "wind": null,
        "light": null,
        "dark": null,
        "staff": null
      },
      "skills": ["leadership"],
      "pcc": 1,
      "movement_stars": 0,
      "leadership_stars": 1,
      "starting_items": [
        "light_brand",
        "iron_sword",
        "vulnerary"
      ],
      "supports": [
        {"unit_id": "finn", "bonus": 10},
        {"unit_id": "nanna", "bonus": 10}
      ]
    }
  ]
}
```

### Unit Properties

- `id`: Unique identifier for the unit
- `name`: Display name of the unit
- `class`: ID of the unit's class
- `level`: Starting level
- `base_stats`: Base statistics
- `growth_rates`: Percentage chance to increase each stat on level up
- `weapon_ranks`: Proficiency in each weapon type (E, D, C, B, A, S, or null)
- `skills`: List of skill IDs
- `pcc`: Pursuit Critical Coefficient
- `movement_stars`: Number of movement stars
- `leadership_stars`: Number of leadership stars
- `starting_items`: List of item IDs
- `supports`: List of support relationships

## Class Data Format

Classes are defined in JSON files with the following structure:

```json
{
  "classes": [
    {
      "id": "lord",
      "name": "Lord",
      "base_stats": {
        "hp": 20,
        "strength": 5,
        "magic": 0,
        "skill": 5,
        "speed": 6,
        "luck": 5,
        "defense": 3,
        "constitution": 5,
        "movement": 6
      },
      "max_stats": {
        "hp": 60,
        "strength": 20,
        "magic": 20,
        "skill": 20,
        "speed": 20,
        "luck": 20,
        "defense": 20,
        "constitution": 20,
        "movement": 10
      },
      "usable_weapons": ["sword"],
      "class_skills": [],
      "movement_type": "cavalry",
      "can_dismount": true,
      "dismounted_stats": {
        "movement": 5
      },
      "dismounted_weapons": ["sword"],
      "promotes_to": "master_knight"
    }
  ]
}
```

### Class Properties

- `id`: Unique identifier for the class
- `name`: Display name of the class
- `base_stats`: Base statistics for the class
- `max_stats`: Maximum statistics for the class
- `usable_weapons`: List of weapon types the class can use
- `class_skills`: List of skill IDs granted by the class
- `movement_type`: Type of movement (infantry, cavalry, armor, flying, etc.)
- `can_dismount`: Whether the class can dismount
- `dismounted_stats`: Stat changes when dismounted
- `dismounted_weapons`: Usable weapons when dismounted
- `promotes_to`: ID of the class this promotes to

## Promotion Data Format

Promotion data is defined in JSON files with the following structure:

```json
{
  "promotions": [
    {
      "from_class": "social_knight",
      "to_class": "paladin",
      "stat_bonuses": {
        "strength": 1,
        "skill": 3,
        "speed": 2,
        "defense": 2,
        "constitution": 1,
        "movement": 1
      },
      "weapon_rank_bonuses": {
        "sword": 1
      },
      "promotion_item": "knights_proof"
    }
  ]
}
```

### Promotion Properties

- `from_class`: ID of the base class
- `to_class`: ID of the promoted class
- `stat_bonuses`: Stat increases upon promotion
- `weapon_rank_bonuses`: Weapon rank increases upon promotion
- `promotion_item`: ID of the item required for promotion

## Weapon and Item Data Format

Weapons and items are defined in JSON files with the following structure:

```json
{
  "weapons": [
    {
      "id": "iron_sword",
      "name": "Iron Sword",
      "type": "sword",
      "might": 5,
      "hit": 80,
      "critical": 0,
      "weight": 5,
      "range": "1",
      "uses": 46,
      "rank": "E",
      "effective_against": [],
      "special_effects": []
    },
    {
      "id": "light_brand",
      "name": "Light Brand",
      "type": "sword",
      "might": 9,
      "hit": 70,
      "critical": 0,
      "weight": 9,
      "range": "1-2",
      "uses": 60,
      "rank": "C",
      "effective_against": [],
      "special_effects": ["magic_damage_at_range"]
    }
  ],
  "staves": [
    {
      "id": "heal",
      "name": "Heal",
      "type": "staff",
      "might": 10,
      "hit": 100,
      "weight": 2,
      "range": "1",
      "uses": 30,
      "rank": "E",
      "effect": "heal",
      "effect_value": 10
    }
  ],
  "items": [
    {
      "id": "vulnerary",
      "name": "Vulnerary",
      "type": "consumable",
      "uses": 3,
      "effect": "heal",
      "effect_value": 20
    },
    {
      "id": "knights_proof",
      "name": "Knight's Proof",
      "type": "promotion",
      "uses": 1,
      "effect": "promote",
      "eligible_classes": ["social_knight", "lance_knight", "arch_knight", "axe_knight", "free_knight", "troubadour", "pegasus_knight", "dragon_knight", "bow_fighter", "sword_fighter", "axe_fighter", "mage", "priest", "thief"]
    }
  ]
}
```

### Weapon Properties

- `id`: Unique identifier for the weapon
- `name`: Display name of the weapon
- `type`: Type of weapon (sword, lance, axe, bow, fire, thunder, wind, light, dark)
- `might`: Base damage
- `hit`: Base hit rate
- `critical`: Base critical rate
- `weight`: Weight (affects Attack Speed)
- `range`: Attack range (1, 2, or 1-2)
- `uses`: Number of uses before breaking
- `rank`: Required weapon rank to use
- `effective_against`: List of unit types the weapon is effective against
- `special_effects`: List of special effects

### Staff Properties

- `id`: Unique identifier for the staff
- `name`: Display name of the staff
- `type`: Always "staff"
- `might`: Healing power or effect strength
- `hit`: Base hit rate
- `weight`: Weight (affects Attack Speed)
- `range`: Effect range
- `uses`: Number of uses before breaking
- `rank`: Required weapon rank to use
- `effect`: Type of effect (heal, restore, warp, etc.)
- `effect_value`: Numeric value for the effect

### Item Properties

- `id`: Unique identifier for the item
- `name`: Display name of the item
- `type`: Type of item (consumable, promotion, key, etc.)
- `uses`: Number of uses
- `effect`: Type of effect
- `effect_value`: Numeric value for the effect
- `eligible_classes`: For promotion items, list of classes that can use it

## Map Data Format

Maps are defined in JSON files with the following structure:

```json
{
  "id": "chapter1",
  "name": "Chapter 1: The Warrior of Fiana",
  "width": 20,
  "height": 15,
  "terrain": [
    ["plain", "plain", "plain", "forest", "forest", "mountain", "mountain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
    ["plain", "plain", "plain", "forest", "forest", "mountain", "mountain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
    // ... more rows
  ],
  "spawn_points": {
    "player_start": [5, 5],
    "enemy_start": [15, 5],
    "reinforcement_1": [0, 0],
    "reinforcement_2": [19, 14]
  },
  "objective_points": {
    "seize": [15, 7],
    "escape": [0, 0]
  },
  "objects": [
    {
      "type": "door",
      "position": [10, 5],
      "properties": {
        "locked": true
      }
    },
    {
      "type": "chest",
      "position": [12, 8],
      "properties": {
        "item": "knights_proof",
        "locked": true
      }
    },
    {
      "type": "village",
      "position": [3, 10],
      "properties": {
        "item": "iron_sword",
        "dialogue": "village_1_dialogue"
      }
    }
  ],
  "fog_of_war": false
}
```

### Map Properties

- `id`: Unique identifier for the map
- `name`: Display name of the map
- `width`: Width of the map in tiles
- `height`: Height of the map in tiles
- `terrain`: 2D array of terrain types
- `spawn_points`: Dictionary of named spawn points
- `objective_points`: Dictionary of named objective points
- `objects`: List of map objects
- `fog_of_war`: Whether fog of war is enabled

### Map Object Properties

- `type`: Type of object (door, chest, village, shop, arena, bridge, ballista, throne, gate)
- `position`: [x, y] coordinates
- `properties`: Object-specific properties

## Event Data Format

Events are defined in JSON files with the following structure:

```json
{
  "events": [
    {
      "id": "chapter_start",
      "type": "turn",
      "trigger": {
        "turn": 1,
        "phase": "player"
      },
      "actions": [
        {
          "type": "dialogue",
          "dialogue_id": "chapter1_intro"
        },
        {
          "type": "camera_move",
          "position": [5, 5]
        }
      ]
    },
    {
      "id": "reinforcements_1",
      "type": "turn",
      "trigger": {
        "turn": 3,
        "phase": "enemy"
      },
      "actions": [
        {
          "type": "spawn_unit",
          "unit_id": "enemy_soldier",
          "position": [0, 0],
          "count": 3
        },
        {
          "type": "dialogue",
          "dialogue_id": "reinforcements_arrive"
        }
      ]
    },
    {
      "id": "village_visit",
      "type": "interaction",
      "trigger": {
        "object_type": "village",
        "position": [3, 10]
      },
      "actions": [
        {
          "type": "dialogue",
          "dialogue_id": "village_1_dialogue"
        },
        {
          "type": "give_item",
          "item_id": "iron_sword",
          "to_unit": "acting_unit"
        },
        {
          "type": "change_object",
          "position": [3, 10],
          "new_state": "visited"
        }
      ]
    }
  ]
}
```

### Event Properties

- `id`: Unique identifier for the event
- `type`: Type of event (turn, interaction, unit_death, etc.)
- `trigger`: Conditions that trigger the event
- `actions`: List of actions to perform when triggered

### Trigger Properties

- `turn`: Turn number (for turn events)
- `phase`: Phase (player, enemy, npc)
- `object_type`: Type of object (for interaction events)
- `position`: [x, y] coordinates (for position-based events)
- `unit_id`: ID of the unit (for unit-based events)

### Action Properties

- `type`: Type of action (dialogue, spawn_unit, give_item, etc.)
- `dialogue_id`: ID of the dialogue (for dialogue actions)
- `position`: [x, y] coordinates (for position-based actions)
- `unit_id`: ID of the unit (for unit-based actions)
- `item_id`: ID of the item (for item-based actions)
- `count`: Number of units to spawn (for spawn actions)
- `new_state`: New state for objects (for change_object actions)

## Chapter Data Format

Chapters are defined in JSON files with the following structure:

```json
{
  "chapters": [
    {
      "id": "chapter1",
      "name": "Chapter 1: The Warrior of Fiana",
      "map_id": "chapter1",
      "objective": {
        "type": "seize",
        "target": "seize",
        "description": "Seize the gate"
      },
      "deployment": {
        "max_units": 8,
        "forced_units": ["leif"],
        "starting_positions": {
          "leif": [5, 5],
          "finn": [6, 5],
          "eyvel": [5, 6]
        }
      },
      "rewards": {
        "items": ["knights_proof"],
        "gold": 1000,
        "experience": 100
      },
      "next_chapter": "chapter2",
      "gaiden_requirements": {
        "chapter": "chapter1x",
        "conditions": [
          {
            "type": "visit",
            "object_position": [3, 10]
          }
        ]
      }
    }
  ]
}
```

### Chapter Properties

- `id`: Unique identifier for the chapter
- `name`: Display name of the chapter
- `map_id`: ID of the map used for the chapter
- `objective`: Chapter objective
- `deployment`: Deployment information
- `rewards`: Rewards for completing the chapter
- `next_chapter`: ID of the next chapter
- `gaiden_requirements`: Requirements for unlocking a gaiden chapter

### Objective Properties

- `type`: Type of objective (seize, escape, defeat, defend)
- `target`: Target for the objective (e.g., position to seize)
- `description`: Description of the objective

### Deployment Properties

- `max_units`: Maximum number of units that can be deployed
- `forced_units`: List of unit IDs that must be deployed
- `starting_positions`: Dictionary mapping unit IDs to starting positions

### Gaiden Requirements Properties

- `chapter`: ID of the gaiden chapter
- `conditions`: List of conditions for unlocking the gaiden chapter

## Skill Data Format

Skills are defined in JSON files with the following structure:

```json
{
  "skills": [
    {
      "id": "wrath",
      "name": "Wrath",
      "description": "Guarantees a critical hit when counterattacking",
      "activation_type": "combat",
      "activation_condition": "is_counterattacking",
      "effect": {
        "type": "set_critical",
        "value": 100
      }
    },
    {
      "id": "adept",
      "name": "Adept",
      "description": "Skill% chance to perform an extra attack",
      "activation_type": "combat",
      "activation_condition": "random",
      "activation_rate": "skill",
      "effect": {
        "type": "extra_attack",
        "count": 1
      }
    },
    {
      "id": "leadership",
      "name": "Leadership",
      "description": "Grants +3 Hit and Avoid to all allies for each leadership star",
      "activation_type": "passive",
      "effect": {
        "type": "leadership_bonus",
        "hit": 3,
        "avoid": 3
      }
    }
  ]
}
```

### Skill Properties

- `id`: Unique identifier for the skill
- `name`: Display name of the skill
- `description`: Description of the skill
- `activation_type`: When the skill activates (combat, passive, etc.)
- `activation_condition`: Condition for activation
- `activation_rate`: Rate of activation (for random activation)
- `effect`: Effect of the skill

## Terrain Data Format

Terrain types are defined in JSON files with the following structure:

```json
{
  "terrain_types": [
    {
      "id": "plain",
      "name": "Plain",
      "description": "Basic terrain with no special effects",
      "avoid_bonus": 5,
      "defense_bonus": 0,
      "healing": false
    },
    {
      "id": "forest",
      "name": "Forest",
      "description": "Provides defensive bonuses but slows movement",
      "avoid_bonus": 20,
      "defense_bonus": 2,
      "healing": false
    },
    {
      "id": "mountain",
      "name": "Mountain",
      "description": "Difficult terrain with high defensive bonuses",
      "avoid_bonus": 30,
      "defense_bonus": 5,
      "healing": false
    },
    {
      "id": "fort",
      "name": "Fort",
      "description": "Provides defensive bonuses and heals units each turn",
      "avoid_bonus": 20,
      "defense_bonus": 10,
      "healing": true,
      "healing_amount": 5
    }
  ]
}
```

### Terrain Type Properties

- `id`: Unique identifier for the terrain type
- `name`: Display name of the terrain type
- `description`: Description of the terrain type
- `avoid_bonus`: Avoid bonus provided by the terrain
- `defense_bonus`: Defense bonus provided by the terrain
- `healing`: Whether the terrain has a healing effect
- `healing_amount`: Amount of HP healed each turn (if healing is true)

## Movement Cost Data Format

Movement costs are defined in JSON files with the following structure:

```json
{
  "movement_costs": {
    "plain": {
      "infantry": 1,
      "armor": 1,
      "cavalry": 1,
      "flying": 1,
      "pirate": 1,
      "brigand": 1
    },
    "forest": {
      "infantry": 2,
      "armor": 2,
      "cavalry": 3,
      "flying": 1,
      "pirate": 2,
      "brigand": 2
    },
    "mountain": {
      "infantry": 2,
      "armor": 1,
      "cavalry": null,
      "flying": 1,
      "pirate": 2,
      "brigand": 2
    },
    "river": {
      "infantry": null,
      "armor": null,
      "cavalry": null,
      "flying": 1,
      "pirate": 4,
      "brigand": null
    }
  }
}
```

### Movement Cost Properties

- Each terrain type has a dictionary of movement costs for each movement type
- `null` indicates impassable terrain

## Conclusion

These data formats provide a flexible and extensible way to define game data. By separating data from code, it becomes easier to modify and extend the game without changing the core logic. This approach also makes it easier to create tools for editing game data.