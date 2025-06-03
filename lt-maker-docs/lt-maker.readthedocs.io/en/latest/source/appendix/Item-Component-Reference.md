<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

<a href="../../index.html" class="icon icon-home">lt-maker</a>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" spy="affix" role="navigation"
aria-label="Navigation menu">

<span class="caption-text">Contents:</span>

- <a href="../home.html" class="reference internal">Lex Talionis Wiki</a>

<span class="caption-text">Getting Started:</span>

- <a href="../getting_started/index.html"
  class="reference internal">Getting Started</a>

<span class="caption-text">Editor Guides:</span>

- <a href="../editors/Editors-Overview.html"
  class="reference internal">Editors Overview</a>
- <a href="../editors/index.html" class="reference internal">Editors</a>

<span class="caption-text">Events:</span>

- <a href="../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../guides/Guides-Overview.html"
  class="reference internal">Guides Overview</a>
- <a href="../guides/index.html" class="reference internal">Guides</a>

<span class="caption-text">appendix:</span>

- <a href="Text-Formatting-Commands.html" class="reference internal">Text
  Formatting Commands</a>
- <a href="Item-Component-Reference.html#"
  class="current reference internal">Item Component Dictionary</a>
  - <a href="Item-Component-Reference.html#essential-aspects"
    class="reference internal">Essential Aspects:</a>
  - <a href="Item-Component-Reference.html#targeting"
    class="reference internal">Targeting:</a>
  - <a href="Item-Component-Reference.html#weapon-components"
    class="reference internal">Weapon Components:</a>
  - <a href="Item-Component-Reference.html#restrictions"
    class="reference internal">Restrictions:</a>
  - <a href="Item-Component-Reference.html#exp"
    class="reference internal">EXP:</a>
  - <a href="Item-Component-Reference.html#promotion"
    class="reference internal">Promotion:</a>
  - <a href="Item-Component-Reference.html#extra-components"
    class="reference internal">Extra Components:</a>
  - <a href="Item-Component-Reference.html#staff-components"
    class="reference internal">Staff Components:</a>
  - <a href="Item-Component-Reference.html#special-components"
    class="reference internal">Special Components:</a>
  - <a href="Item-Component-Reference.html#alternate-formulas"
    class="reference internal">Alternate Formulas</a>
  - <a href="Item-Component-Reference.html#aoe"
    class="reference internal">AOE:</a>
  - <a href="Item-Component-Reference.html#aesthetic-components"
    class="reference internal">Aesthetic Components:</a>
  - <a href="Item-Component-Reference.html#advanced-components"
    class="reference internal">Advanced Components:</a>
- <a href="Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="Special-Variables.html" class="reference internal">Special
  Variables</a>
- <a href="Special-Tags.html" class="reference internal">Special Tags</a>
- <a href="trigger-reference.html" class="reference internal">Event
  Triggers</a>
- <a href="Random-Seed-Mechanics.html" class="reference internal">Random
  Seed Mechanics</a>
- <a href="FAQ.html" class="reference internal">Frequently Asked
  Questions</a>
- <a href="Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="index.html" class="reference internal">Code Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- Item Component Dictionary
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/Item-Component-Reference.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="item-component-dictionary" class="section">

<span id="id1"></span>

# Item Component Dictionary<a href="Item-Component-Reference.html#item-component-dictionary"
class="headerlink" title="Link to this heading"></a>

The item components in this dictionary are broken down by icon going
from left to right, with each icon’s aspects being explained top to
bottom.

<div id="essential-aspects" class="section">

## Essential Aspects:<a href="Item-Component-Reference.html#essential-aspects"
class="headerlink" title="Link to this heading"></a>

| Component          | Description                                                                                                                                                                                                                           |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **No AI**          | Adding this component prevents the AI from trying to use the item. This is important for sequence items, which the AI is unable to handle.                                                                                            |
| **Spell**          | This item will be included under the Spells menu instead of the Attack menu. A useful way to separate weapons from utility items like staves or non-damaging tomes.                                                                   |
| **Weapon**         | Item is a weapon that can be used to attack and initiate combat. Important to add to anything that’s being used for that purpose.                                                                                                     |
| **Siege Weapon**   | The weapon cannot counterattack or be counterattacked, but can be equipped and double. Used instead of the weapon component.                                                                                                          |
| **Usable**         | Item can be used from the items menu. Must be paired with the Targets Allies component.                                                                                                                                               |
| **Usable in Base** | Item is usable in base. Must be paired with the Targets Allies component.                                                                                                                                                             |
| **Unrepairable**   | An item with the repair component cannot repair an item with this component.                                                                                                                                                          |
| **Value**          | The value that the item can be bought and sold for in shops.                                                                                                                                                                          |
| **Accessory**      | The item is considered an accessory and takes up an accessory slot in a unit’s inventory. Make sure to increase the number of accessory slots to more than zero and have a total number of inventory + accessory slots less than six. |
| **Item Prefab**    | The item inherits all the components of the selected item.                                                                                                                                                                            |
| **Item Tags**      | The item gains all of the associated tags. Note: the tags are associated to the item instead of any unit.                                                                                                                             |

</div>

<div id="targeting" class="section">

## Targeting:<a href="Item-Component-Reference.html#targeting" class="headerlink"
title="Link to this heading"></a>

| Component                      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Targets Anything**           | Any tile can be targeted by this item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **Targets Units**              | Any unit within range, regardless of team, can be targeted.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Targets Enemies**            | Can only target enemy units.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Targets Allies**             | Can only target allied units, including green units (assuming a player is using the item).                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **EvalSpecialRange**           | Takes a condition accepting <span class="pre">`x`</span>, <span class="pre">`y`</span> that will limit what positions relative to the unit can be targeted within range. For example, the condition <span class="pre">`x`</span>` `<span class="pre">`==`</span>` `<span class="pre">`0`</span>` `<span class="pre">`or`</span>` `<span class="pre">`y`</span>` `<span class="pre">`==`</span>` `<span class="pre">`0`</span> will lock the range to a “cross” shape, allowing the unit to shoot directly vertically or horizontally. |
| **Eval Target Restrict**       | This component takes a string that will be evaluated in python. If the string evaluates to false for a targeted unit they cannot be targeted by this weapon. See an upcoming guide for options when creating these strings.                                                                                                                                                                                                                                                                                                           |
| **Empty Tile Target Restrict** | Used in conjunction with Targets Anything to restrict the target to empty tiles.                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **Minimum Range**              | A fixed integer that sets the minimum range of an item. Zero means that it can target the user. Unneeded for usable items. Don’t go into the negatives.                                                                                                                                                                                                                                                                                                                                                                               |
| **Maximum Range**              | A fixed integer that sets the maximum range of an item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Maximum Equation Range**     | Refers to an equation defined in the equations editor. The maximum range is set to the evaluated value of that equation. Useful for staves like Warp or Physic that are based on the user’s magic.                                                                                                                                                                                                                                                                                                                                    |
| **Global Range**               | Anywhere on the map can be a potential target for this item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

</div>

<div id="weapon-components" class="section">

## Weapon Components:<a href="Item-Component-Reference.html#weapon-components"
class="headerlink" title="Link to this heading"></a>

| Component          | Description                                                                                                                                           |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Weapon Type**    | The type of weapon that the wielder must be able to use in order to attack with this item.                                                            |
| **Weapon Rank**    | The rank of the desired weapon type needed to use this item.                                                                                          |
| **Magic**          | Item uses magic formulas for calculating damage.                                                                                                      |
| **Magic at Range** | Item uses magic formulas only at range (Levin or Wind Sword)                                                                                          |
| **Hit**            | The base hit value of the item. Factored into the overall hit equation.                                                                               |
| **Damage**         | The base might of the item.                                                                                                                           |
| **Crit**           | The base crit of the item.                                                                                                                            |
| **Weight**         | Lowers effective speed. At first, subtracted from the CONSTITUTION equation. If negative, subtracts from speed resulting in a unit’s effective speed. |
| **Unwieldy**       | When equipped, defense is reduced by the specified integer.                                                                                           |
| **Stat Change**    | A list of stats that correspond to integers. When equipped, stats are changed by that amount.                                                         |

</div>

<div id="restrictions" class="section">

## Restrictions:<a href="Item-Component-Reference.html#restrictions" class="headerlink"
title="Link to this heading"></a>

| Component        | Description                                                                                                                                                                                 |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Uses**         | The item’s total uses. The item will be destroyed when uses reach zero.                                                                                                                     |
| **Chapter Uses** | The item’s uses per chapter. The uses recharge to full at chapter end, even if all are used. Do not combine with the uses component.                                                        |
| **HPCost**       | Item subtracts the specified amount of HP upon use. If the subtraction would kill the unit the item becomes unusable.                                                                       |
| **Mana Cost**    | Item subtracts the specified amount of Mana upon use. MANA must be defined in the equations editor. If unit does not have enough mana the item will not be usable.                          |
| **Cooldown**     | The item cannot be used for the specified number of turns. Since timers tick down at the start of the turn, setting cooldown to one will allow the unit to use the item on their next turn. |
| **Prf Unit**     | Only the chosen units can use this weapon.                                                                                                                                                  |
| **Prf Class**    | Only the chosen classes can use this weapon.                                                                                                                                                |
| **Prf Tag**      | Only units with the chosen tags can use this weapon.                                                                                                                                        |
| **Prf Affinity** | Only units that have one of the chosen affinities can use this weapon.                                                                                                                      |
| **Locked**       | Item cannot be taken or dropped from a unit’s inventory. However, the trade command can be used to rearrange its position, and event commands can remove the item.                          |

</div>

<div id="exp" class="section">

## EXP:<a href="Item-Component-Reference.html#exp" class="headerlink"
title="Link to this heading"></a>

| Component     | Description                                                                                                                                                    |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **EXP**       | Item gives a fixed integer of EXP each use. Useful for staves like Warp or Rescue.                                                                             |
| **Level EXP** | Gives EXP based on the level difference between attacker and defender. How EXP is normally calculated for weapons, with higher level enemies granting more EXP |
| **Heal EXP**  | Gives EXP based on the amount healed.                                                                                                                          |
| **WEXP**      | Gives a fixed integer of weapon EXP.                                                                                                                           |
| **Fatigue**   | If fatigue is enabled, increases the amount of fatigue a user suffers while using this item. Can be negative in order to remove fatigue.                       |

</div>

<div id="promotion" class="section">

## Promotion:<a href="Item-Component-Reference.html#promotion" class="headerlink"
title="Link to this heading"></a>

| Component              | Description                                                                                                  |
|------------------------|--------------------------------------------------------------------------------------------------------------|
| **Promote**            | Promotes the targeted unit (most often the user) into whatever promotions their class has available to them. |
| **Force Promote**      | Promotes the targeted unit into the class specified in the component.                                        |
| **Class Change**       | Reclasses the unit to whatever reclass options they have available.                                          |
| **Force Class Change** | Reclasses the unit to the specified class.                                                                   |

</div>

<div id="extra-components" class="section">

## Extra Components:<a href="Item-Component-Reference.html#extra-components"
class="headerlink" title="Link to this heading"></a>

| Component                   | Description                                                                                                                                                                                                                                                                 |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Effective**               | If this item is effective against an enemy its damage value will be increased by the integer chosen here instead. This is **not** a multiplier, but an addition.                                                                                                            |
| **Effective Tag**           | Item will be considered effective if the targeted enemy has any of the tags listed in this component.                                                                                                                                                                       |
| **Brave**                   | Weapon has the brave property, doubling its attacks.                                                                                                                                                                                                                        |
| **Brave On Attack**         | The weapon is only brave when making an attack, and acts as a normal weapon when being attacked.                                                                                                                                                                            |
| **Lifelink**                | The unit heals this percentage of damage dealt to an enemy on hit. Chosen value should be between 0 and 1.                                                                                                                                                                  |
| **Damage on Miss**          | Item deals a percentage of it’s normal damage on a miss.                                                                                                                                                                                                                    |
| **Eclipse**                 | On hit, target loses half of their current HP.                                                                                                                                                                                                                              |
| **No Double**               | Item cannot double the enemy.                                                                                                                                                                                                                                               |
| **Cannot Counter**          | Even when equipped as a weapon, the item cannot make a counterattack when its wielder is attacked.                                                                                                                                                                          |
| **Cannot be Countered**     | Targets cannot make a counterattack with their weapon when attacked.                                                                                                                                                                                                        |
| **Ignore Weapon Advantage** | Any weapon advantage relationships defined in the weapon types editor are ignored by this item.                                                                                                                                                                             |
| **Reaver**                  | Weapon advantage relationships defined in the weapon types editor are doubled and reversed against this weapon. If two reaver weapons are in combat with each other weapon advantage works as normal.                                                                       |
| **Double Triangle**         | The effects of weapon advantage relationships are doubled by this item.                                                                                                                                                                                                     |
| **Status On Equip**         | A unit with this item equipped will receive the specified status.                                                                                                                                                                                                           |
| **Status On Hold**          | A unit with this item in their inventory will receive the specified status.                                                                                                                                                                                                 |
| **Gain Mana After Combat**  | Takes a string that will be evaluated by python. At the end of combat the string is evaluated if the item was used and the result is translated into mana gained by the unit. If you want a flat gain of X mana, enter <span class="pre">`X`</span>, where X is an integer. |

</div>

<div id="staff-components" class="section">

## Staff Components:<a href="Item-Component-Reference.html#staff-components"
class="headerlink" title="Link to this heading"></a>

| Component             | Description                                                                                                                                                                                                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Heal**              | Heals the target for the specified integer.                                                                                                                                                                                                                                           |
| **Magic Heal**        | Heals the target for the specified integer + the HEAL equation defined in the equations editor. Will act oddly if no HEAL equation is defined.                                                                                                                                        |
| **Refresh**           | Has an effect identical to dancing in normal FE. A dance skill makes use of this component in an attached item.                                                                                                                                                                       |
| **Restore**           | Removes all statuses with the negative component from the target.                                                                                                                                                                                                                     |
| **Restore Specific**  | Removes the specified status from the target.                                                                                                                                                                                                                                         |
| **Unlock Staff**      | Map regions that are considered Locked can be unlocked with this item. Should not be used in conjunction with other major components.                                                                                                                                                 |
| **Can Unlock**        | Allows the item to unlock specific types of locks. In GBA games, the unlock staff can only unlock doors. This component would allow for that limited functionality. In particular, <span class="pre">`region.nid.startswith('Door')`</span> would limit the staff to unlocking doors. |
| **Repair**            | Repairs a selected item in the target’s inventory. Used in the Hammerne staff.                                                                                                                                                                                                        |
| **Trade**             | Opens a trade menu with a hit target. Can be used for a thief staff.                                                                                                                                                                                                                  |
| **Menu After Combat** | Using this item returns the user to the menu state. However, user cannot attack again. Menu activates after any use of the item that involves targeting a unit (including targeting the user).                                                                                        |

</div>

<div id="special-components" class="section">

## Special Components:<a href="Item-Component-Reference.html#special-components"
class="headerlink" title="Link to this heading"></a>

| Component                      | Description                                                                                                                                                                                                                                                                                                                                                       |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Permanent Stat Change**      | Using this item permanently changes the stats of the target in the specified ways. The target and user are often the same unit (think of normal FE stat boosters).                                                                                                                                                                                                |
| **Permanent Growth Change**    | Using this item permanently changes the growth values of the target in the specified ways.                                                                                                                                                                                                                                                                        |
| **Wexp Change**                | Using this item permanently changes the WEXP of the target. Can specify individual amounts for different weapon types. Useful for Arms Scroll.                                                                                                                                                                                                                    |
| **Fatigue on Hit**             | If fatigue is enabled, increases the amount of fatigue a target suffers when hit by this item. Can be negative in order to remove fatigue.                                                                                                                                                                                                                        |
| **Status on Hit**              | Target gains the specified status on hit. Applies instantly, potentially causing values to change mid-combat.                                                                                                                                                                                                                                                     |
| **Status After Combat on Hit** | If the target is hit they gain the specified status at the end of combat. Prevents changes being applied mid-combat.                                                                                                                                                                                                                                              |
| **Shove**                      | Unit is shoved the specified number of tiles.                                                                                                                                                                                                                                                                                                                     |
| **Shove Target Restrict**      | Works the same as shove but will not allow the item to be selected if the action cannot be performed.                                                                                                                                                                                                                                                             |
| **Swap**                       | The user and adjacent target’s positions are swapped.                                                                                                                                                                                                                                                                                                             |
| **Pivot**                      | On hit, the user moves the specified number of tiles past the target.                                                                                                                                                                                                                                                                                             |
| **Pivot Target Restrict**      | Works the same as pivot but will not allow the item to be selected if the action cannot be performed.                                                                                                                                                                                                                                                             |
| **Draw Back**                  | The user and target both move the specified number of tiles backwards.                                                                                                                                                                                                                                                                                            |
| **Draw Back Target Restrict**  | Works the same as draw back but will not allow the item to be selected if the action cannot be performed.                                                                                                                                                                                                                                                         |
| **Steal**                      | On hit the user may steal any non-equipped item from the target.                                                                                                                                                                                                                                                                                                  |
| **GBASteal**                   | On hit the user may steal non-weapon and non-spell item from the target.                                                                                                                                                                                                                                                                                          |
| **Event On Hit**               | The selected event plays before a hit, if the unit will hit with this item. The event is triggered with args (<span class="pre">`unit1`</span>=attacking unit, <span class="pre">`unit2`</span>=target, <span class="pre">`item`</span>=item, <span class="pre">`position`</span>=attacking unit’s position, <span class="pre">`region`</span>=targeted position) |
| **Event After Combat**         | The selected event plays at the end of combat so long as an attack in combat hit.                                                                                                                                                                                                                                                                                 |

</div>

<div id="alternate-formulas" class="section">

## Alternate Formulas<a href="Item-Component-Reference.html#alternate-formulas"
class="headerlink" title="Link to this heading"></a>

Each of the alternate formulas here replace the specified stat with a
selected equation from the equations editor. Most are self explanatory.

Resist - Resist refers to both defense and resistance. Increasing a
unit’s resist will decrease the damage they take, regardless of
magic/physical damage. Magic items essentially use this component, by
swapping the enemy’s normal DEFENSE equation for the alternate resist
formula of MAGIC_DEFENSE.

Attack vs Defense Speed - Lex Talionis can calculate speed when being
attacked differently than speed when attacking. These two components are
part of this distinction.

</div>

<div id="aoe" class="section">

## AOE:<a href="Item-Component-Reference.html#aoe" class="headerlink"
title="Link to this heading"></a>

| Component                      | Description                                                                                                             |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| **Blast AOE**                  | Blast extends outwards the specified number of tiles.                                                                   |
| **Enemy Blast AOE**            | Similar to Blast AOE, except only effects enemies.                                                                      |
| **Ally Blast AOE**             | Similar to Blast AOE, except only effects allies.                                                                       |
| **Equation Blast AOE**         | Works similar to Blast AOE, except instead of a fixed integer the range of the blast is chosen by a specified equation. |
| **Enemy Cleave AOE**           | All enemies within one tile (or diagonal from the user) are affected by this attack’s AOE.                              |
| **All Allies AOE**             | All allies on the map are targeted by this item’s AOE.                                                                  |
| **All Allies Except Self AOE** | All allies on the map other than the user are targeted by this item’s AOE.                                              |
| **All Enemies AOE**            | All enemies on the map are targeted by this item’s AOE.                                                                 |
| **Line AOE**                   | A line is drawn from the user to the target, affecting each unit within it. Never extends past the target.              |

</div>

<div id="aesthetic-components" class="section">

## Aesthetic Components:<a href="Item-Component-Reference.html#aesthetic-components"
class="headerlink" title="Link to this heading"></a>

| Component                  | Description                                                                                                                                                 |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Map Hit Add Blend**      | On hit, the target is made brighter using the specified color.                                                                                              |
| **Map Hit Sub Blend**      | On hit, the target is made darker using the specified color.                                                                                                |
| **Map Hit SFX**            | When the target is hit by this item the selected sfx is played.                                                                                             |
| **Map Cast SFX**           | When item is used the selected sfx is played.                                                                                                               |
| **Map Cast Anim**          | Adds a specific animation effect when the item is used. Relevant in map combat situations.                                                                  |
| **Battle Cast Anim**       | Adds a specific animation effect when the item is used. This does not change the battle animation used, think instead of the effects spells cast when used. |
| **Battle Animation Music** | When entering a battle with this item the chapter’s normal battle music is substituted for the selected music.                                              |
| **Warning**                | A yellow exclamation mark appears above the wielder’s head. Often used for killing weapons.                                                                 |
| **Eval Warning**           | A red exclamation mark appears above the wielder’s head if the selected unit matches the evaluated string. Often used for effective weapons.                |
| **Text Color**             | Item’s text is recolored to the chosen color.                                                                                                               |

</div>

<div id="advanced-components" class="section">

## Advanced Components:<a href="Item-Component-Reference.html#advanced-components"
class="headerlink" title="Link to this heading"></a>

| Component             | Description                                                                                                                                                                                                |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Multi Item**        | Stores a list of other items to be included as part of this multi item. When using the item the sub-items stored within the list can each be accessed and used. Useful for Three Houses-like magic system. |
| **Sequence Item**     | Item requires various sub-items to be work properly. Useful for complex items like Warp or Rescue. Items are used from list’s top to bottom.                                                               |
| **Multi Target**      | Can target a specified number of units when used.                                                                                                                                                          |
| **Allow Same Target** | If the item is multi target this component allows it to select the same target multiple times.                                                                                                             |
| **Store Unit**        | The targeted unit is stored in the game’s memory when hit. The next time the unload unit component is called the unit is placed on the targeted tile.                                                      |
| **Unload Unit**       | Places the unit stored through the store unit component on the specified target (most often a tile).                                                                                                       |

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Text-Formatting-Commands.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Text Formatting Commands"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Skill-Component-Reference.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Skill Component Dictionary">Next <span
class="fa fa-arrow-circle-right" aria-hidden="true"></span></a>

</div>

------------------------------------------------------------------------

<div role="contentinfo">

© Copyright 2024, rainlash.

</div>

Built with [Sphinx](https://www.sphinx-doc.org/) using a
[theme](https://github.com/readthedocs/sphinx_rtd_theme) provided by
[Read the Docs](https://readthedocs.org).

</div>

</div>

</div>

</div>
