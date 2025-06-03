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
- <a href="Item-Component-Reference.html" class="reference internal">Item
  Component Dictionary</a>
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
  - <a href="game-state-reference.html" class="reference internal">GameState
    class</a>
  - <a href="level-reference.html" class="reference internal">Level
    Object</a>
  - <a href="unit-reference.html" class="reference internal">UnitObject
    class</a>
  - <a href="region-reference.html" class="reference internal">RegionObject
    class</a>
  - <a href="region-reference.html#regionprefab-class"
    class="reference internal">RegionPrefab class</a>
  - <a href="party-reference.html" class="reference internal">Party
    Object</a>
  - <a href="unit_funcs-reference.html" class="reference internal">Unit
    Helper Functions</a>
  - <a href="item_funcs-reference.html" class="reference internal">Item
    Helper Functions</a>
  - <a href="query_funcs-reference.html" class="reference internal">Useful
    Functions</a>
  - <a href="constants-reference.html#"
    class="current reference internal">Constants</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- [Code Documentation](index.html)
- Constants
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/constants-reference.rst"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="constants" class="section">

# Constants<a href="constants-reference.html#constants" class="headerlink"
title="Link to this heading"></a>

<div class="docutils container">

**Inventory**

|                 |                                        |          |                   |
|-----------------|----------------------------------------|----------|-------------------|
| **Name**        | **Description**                        | **Type** | **Default Value** |
| Num Items       | Max number of Items in inventory       | Int      | 5                 |
| Num Accessories | Max number of Accessories in inventory | Int      | 0                 |
| Sell Modifier   | Value multiplier when selling an item  | Float    | 0.5               |

**Major Features**

|                 |                                                    |          |                   |
|-----------------|----------------------------------------------------|----------|-------------------|
| **Name**        | **Description**                                    | **Type** | **Default Value** |
| Turnwheel       | Turnwheel                                          | Bool     | False             |
| Initiative      | Per Unit Initiative Order                          | Bool     | False             |
| Fatigue         | Fatigue                                            | Bool     | False             |
| Reset Fatigue   | Automatically reset fatigue to 0 for benched units | Bool     | False             |
| Minimap         | Enable Minimap                                     | Bool     | True              |
| Lead            | Global Leadership Stars                            | Bool     | False             |
| Bexp            | Bonus Experience                                   | Bool     | False             |
| Rd Bexp Lvl     | Always gain 3 stat-ups when using Bonus Exp.       | Bool     | False             |
| Support         | Supports                                           | Bool     | False             |
| Overworld       | Overworld                                          | Bool     | False             |
| Overworld Start | Start in Overworld                                 | Bool     | False             |
| Unit Notes      | Unit Notes                                         | Bool     | False             |
| Crit            | Allow Criticals                                    | Bool     | True              |
| Glancing Hit    | Chance (%) to score a glancing hit                 | Int      | 0                 |

**Pair Up**

|                     |                                          |          |                   |
|---------------------|------------------------------------------|----------|-------------------|
| **Name**            | **Description**                          | **Type** | **Default Value** |
| Pairup              | Pair Up                                  | Bool     | False             |
| Limit Attack Stance | Limit Attack Stance to first attack only | Bool     | False             |
| Attack Stance Only  | Only attack stance allowed               | Bool     | False             |
| Player Pairup Only  | Only player units can pairup             | Bool     | False             |

**Other**

|                                  |                                                              |          |                   |
|----------------------------------|--------------------------------------------------------------|----------|-------------------|
| **Name**                         | **Description**                                              | **Type** | **Default Value** |
| Reset Uses                       | Reset uses on droppable items when acquired                  | Bool     | True              |
| Long Range Storage               | Allow use of storage even when not near convoy               | Bool     | True              |
| Allow Negative As                | Allow Attack Speed to be negative                            | Bool     | False             |
| Trade                            | Can trade items on map                                       | Bool     | True              |
| Growth Info                      | Can view unit growths in Info Menu                           | Bool     | True              |
| Alt Growth Format                | Base growths include class growths in Info Menu              | Bool     | False             |
| Backpropagate Difficulty Growths | Apply difficulty bonus growths to past levels                | Bool     | True              |
| Traveler Time Decrement          | Timed skills applied to traveler units will decrease.        | Bool     | False             |
| Def Double                       | Defender can double counterattack                            | Bool     | True              |
| Min Damage                       | Min damage dealt by an attack                                | Int      | 0                 |
| Convoy On Death                  | Items held by dead player units are sent to convoy           | Bool     | ConstantTag.OTHER |
| Repair Shop                      | Access the Repair Shop in prep and base                      | Bool     | False             |
| Sound Room In Codex              | Can access sound room from Codex menu in base                | Bool     | True              |
| Give And Take                    | Units can give a unit after taking a unit                    | Bool     | ConstantTag.OTHER |
| Combat Art Category              | Combat Arts get put in their own category in the menu        | Bool     | False             |
| Reset Mana                       | Mana resets to full for units upon completion of the chapter | Bool     | ConstantTag.OTHER |
| Double Splash                    | When doubling, splash/aoe applied on second strike           | Bool     | ConstantTag.OTHER |

**Line Of Sight**

|               |                                                       |          |                   |
|---------------|-------------------------------------------------------|----------|-------------------|
| **Name**      | **Description**                                       | **Type** | **Default Value** |
| Line Of Sight | Force items and abilities to obey line of sight rules | Bool     | False             |
| Aura Los      | Force auras to obey line of sight rules               | Bool     | False             |
| Fog Los       | Fog of War will also be affected by line of sight     | Bool     | False             |

**Ai**

|                 |                                        |          |                   |
|-----------------|----------------------------------------|----------|-------------------|
| **Name**        | **Description**                        | **Type** | **Default Value** |
| Ai Fog Of War   | AI will also be affected by Fog of War | Bool     | False             |
| Attack Zero Hit | Enemy AI attacks even if Hit is 0      | Bool     | True              |
| Attack Zero Dam | Enemy AI attacks even if Damage is 0   | Bool     | True              |
| Zero Move       | Show Movement as 0 if AI does not move | Bool     | False             |

**Leveling**

|                           |                                                               |                               |                   |
|---------------------------|---------------------------------------------------------------|-------------------------------|-------------------|
| **Name**                  | **Description**                                               | **Type**                      | **Default Value** |
| Unit Stats As Bonus       | Add class stats to non-generic base stats                     | Bool                          | False             |
| Enemy Leveling            | Method for autoleveling generic units                         | Random, Fixed, Dynamic, Match | Match             |
| Auto Promote              | Units will promote automatically upon reaching max level      | Bool                          | False             |
| Promote Skill Inheritance | Promoted units will have the skills of their previous classes | Bool                          | True              |
| Promote Level Reset       | Promotion resets level back to 1                              | Bool                          | True              |
| Class Change Level Reset  | Class Change resets level back to 1                           | Bool                          | False             |
| Learn Skills On Reclass   | Learn the skills of your new class when you reclass           | Bool                          | True              |
| Learn Skills On Promote   | Learn the skills of your new class when you promote           | Bool                          | True              |
| Negative Growths          | Negative growth rates will reduce stats                       | Bool                          | True              |
| Class Change Same Tier    | Class Change only between classes of the same tier            | Bool                          | False             |
| Generic Feats             | Generic units will be given random feats when appropriate     | Bool                          | False             |

**Aesthetic**

|                               |                                                             |          |                   |
|-------------------------------|-------------------------------------------------------------|----------|-------------------|
| **Name**                      | **Description**                                             | **Type** | **Default Value** |
| Boss Crit                     | Final blow on boss will use critical animation              | Bool     | False             |
| Battle Platforms              | Use battle platforms when battle backgrounds are on         | Bool     | True              |
| Roam Hide Hp                  | Hide hp bars during free roam                               | Bool     | False             |
| Roam Dir Pose                 | Keep direction after moving in free roam.                   | Bool     | False             |
| Roam Dir Anim                 | If “Keep Direction” enabled, stop pose will animate.        | Bool     | False             |
| Autogenerate Grey Map Sprites | Automatically generate grey “wait” map sprites              | Bool     | True              |
| Translucent Unit Sprite       | A phantom of current unit will appear at cursor’s position  | Bool     | False             |
| Talk Display                  | If enough room, display who a unit can talk to in info menu | Bool     | False             |
| Show Abilities                | Display range of extra abilities                            | Bool     | False             |
| Info Menu Blink               | Portraits will blink in info menu                           | Bool     | False             |

**Title**

|                 |                                             |              |                   |
|-----------------|---------------------------------------------|--------------|-------------------|
| **Name**        | **Description**                             | **Type**     | **Default Value** |
| Num Save Slots  | Number of save slots                        | Positive Int | 3                 |
| Game Nid        | Game Unique Identifier                      | Nid          | LT                |
| Title           | Game Title                                  | Str          | Lex Talionis Game |
| Title Particles | Display particle effect on title screen     | Bool         | True              |
| Title Sound     | Access sound room in Extras on title screen | Bool         | True              |

**Music**

|                      |                                                  |          |                   |
|----------------------|--------------------------------------------------|----------|-------------------|
| **Name**             | **Description**                                  | **Type** | **Default Value** |
| Music Main           | Music to play on title screen                    | Music    | None              |
| Music Promotion      | Music to play on promotion                       | Music    | None              |
| Music Class Change   | Music to play on class change                    | Music    | None              |
| Music Game Over      | Music to play on game over                       | Music    | Game Over         |
| Restart Phase Music  | Restart phase music at beginning of new phase    | Bool     | True              |
| Restart Battle Music | Restart battle music at beginning of each combat | Bool     | True              |

**Wexp**

|             |                                          |          |                   |
|-------------|------------------------------------------|----------|-------------------|
| **Name**    | **Description**                          | **Type** | **Default Value** |
| Kill Wexp   | Kills give double weapon exp             | Bool     | True              |
| Double Wexp | Each hit when doubling grants weapon exp | Bool     | True              |
| Miss Wexp   | Gain weapon exp even on miss             | Bool     | True              |

**Exp**

|                 |                                                                        |                    |                   |
|-----------------|------------------------------------------------------------------------|--------------------|-------------------|
| **Name**        | **Description**                                                        | **Type**           | **Default Value** |
| Exp Curve       | How linear the exp curve is; Higher = less linear                      | Float              | 0.035             |
| Exp Magnitude   | How much base exp is received for each interaction                     | Float              | 10                |
| Exp Offset      | Tries to keep player character this many levels above enemies          | Int                | 0                 |
| Gexp Max        | Maximum exp that can be earned from a hit                              | Float              | 30                |
| Gexp Min        | Minimum exp that can be earned from a hit                              | Float              | 1                 |
| Gexp Slope      | How sharply exp drops off                                              | Float              | 0.25              |
| Gexp Intercept  | Exp earned by two equal-level units fighting                           | Float              | 10                |
| Exp Formula     | Which exp formula to use                                               | standard, gompertz | standard          |
| Kill Multiplier | Exp multiplier on kill                                                 | Float              | 3                 |
| Boss Bonus      | Extra exp for killing a boss                                           | Int                | 40                |
| Min Exp         | Min exp gained in combat                                               | Int                | 1                 |
| Default Exp     | Default exp gain                                                       | Int                | 11                |
| Heal Curve      | How much to multiply the amount healed by to determine experience gain | Float              | 0                 |
| Heal Magnitude  | Added to total exp for healing                                         | Int                | 0                 |
| Heal Offset     | Modifies expected healing                                              | Int                | 11                |
| Heal Min        | Min exp gained for healing                                             | Int                | 11                |

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="query_funcs-reference.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Useful Functions"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>

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
