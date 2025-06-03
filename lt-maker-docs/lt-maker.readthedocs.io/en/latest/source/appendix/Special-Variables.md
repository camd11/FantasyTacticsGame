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
- <a href="Special-Variables.html#"
  class="current reference internal">Special Variables</a>
  - <a href="Special-Variables.html#format"
    class="reference internal">Format:</a>
  - <a href="Special-Variables.html#game-variables"
    class="reference internal">Game Variables</a>
  - <a href="Special-Variables.html#level-variables"
    class="reference internal">Level Variables</a>
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
- Special Variables
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/Special-Variables.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="special-variables" class="section">

<span id="id1"></span>

# Special Variables<a href="Special-Variables.html#special-variables" class="headerlink"
title="Link to this heading"></a>

*Last updated v0.1*

This appendix details every special game or level variable used by the
**Lex Talionis** engine. Normally, game and level variables are utilized
by the game designer in events, but a special set of names are reserved
by the engine for specific uses.

<div id="format" class="section">

## Format:<a href="Special-Variables.html#format" class="headerlink"
title="Link to this heading"></a>

<span class="pre">`command`</span> **type** description

</div>

<div id="game-variables" class="section">

## Game Variables<a href="Special-Variables.html#game-variables" class="headerlink"
title="Link to this heading"></a>

These variables are saved for the entirety of a given game.

<span class="pre">`_random_seed`</span> **int** The random seed used by
the engine for combat RNG and random level ups. Automatically set to a
number between 0 and 1023 upon creation of a “New Game”.

<span class="pre">`_next_level_nid`</span> **Level (str)** Internal to
the engine; Do not modify yourself.

<span class="pre">`_goto_level`</span> **Level (str)** Set to the nid of
the level you want to go to next. If not set, the engine will just move
to the following level like normal. Reset upon the start of the next
level. If set to <span class="pre">`_force_quit`</span>, game will end
(and return to title screen) instead of moving to the following level.

<span class="pre">`_go_to_overworld_nid`</span> **Overworld (str)** Set
to the nid of the overworld to go to next.

<span class="pre">`_current_turnwheel_uses`</span> **int** The number of
uses of the turnwheel left in this level. Defaults to -1, which
represents infinite uses. Automatically reset to
<span class="pre">`_max_turnwheel_uses`</span> upon winning the a level.

<span class="pre">`_max_turnwheel_uses`</span> **int** The maximum
number of uses of the turnwheel the player has access to. Defaults to
-1, which represents infinite uses.

<span class="pre">`_convoy`</span> **bool** Set to True to give the
player access to the convoy.

<span class="pre">`_turnwheel`</span> **bool** Set to True to give the
player access to the turnwheel.

<span class="pre">`_supports`</span> **bool** Set to True to give the
player access to support conversations and have characters gain support
points.

<span class="pre">`_minimap`</span> **bool** Set to True to give the
player access to the minimap. Set to False to remove player access of
the minimap. Defaults to True.

<span class="pre">`_fatigue`</span> **int** Set to 0 to turn off
fatigue. Set to 1 to have fatigue prevent unit from participating in a
chapter. Set to 2 to have fatigue apply a Fatigued status when fatigue
\>= max fatigue and Rested when fatigue \< max fatigue. Set to 3 to have
the engine track fatigue but not do anything with it by default.

<span class="pre">`_repair_shop`</span> **bool** Set to True to give the
player access to the repair shop in the prep and base menus.

<span class="pre">`_prep_market`</span> **bool** Set to True to give the
player access to the market in the prep screen.

<span class="pre">`_prep_music`</span> **Music (str)** Set this music as
the background music in the prep screen. You don’t normally need to set
this manually, since it is set by the <span class="pre">`prep`</span>
event command.

<span class="pre">`_base_market`</span> **bool** Set to True to give the
player access to the market in the base screen.

<span class="pre">`_base_bg_name`</span> **Panorama (str)** Load this
panorama as the background in the base screen. You don’t normally need
to set this manually, since it is set by the
<span class="pre">`base`</span> event command.

<span class="pre">`_base_music`</span> **Music (str)** Set this music as
the background music in the base screen. You don’t normally need to set
this manually, since it is set by the <span class="pre">`base`</span>
event command.

<span class="pre">`_bexp_menu_music`</span> **Music (str)** Set this
music as the background music in the bonus experience menu. You don’t
normally need to set this manually, since it is set by the
<span class="pre">`open_bexp_menu`</span> event command.

<span class="pre">`_phase_music_fade_ms`</span> **int** Number of
milliseconds the phase music will take to fade in. Defaults to 400 ms.

<span class="pre">`_last_choice`</span> **str** Always holds the most
recent choice made by the player from using the
<span class="pre">`choice`</span> event command.

</div>

<div id="level-variables" class="section">

## Level Variables<a href="Special-Variables.html#level-variables" class="headerlink"
title="Link to this heading"></a>

These variables are cleared after winning or losing the current level

<span class="pre">`_win_game`</span> **bool** Set to True to force the
player to win the current level. Best practice is to just call the
<span class="pre">`win_game`</span> event command, which does the same
thing.

<span class="pre">`_lose_game`</span> **bool** Set to True to force the
player to lose the current level. Best practice is to just call the
<span class="pre">`lose_game`</span> event command, which does the same
things.

<span class="pre">`_level_end_triggered`</span> **bool** Internal to the
engine; Do not modify yourself.

<span class="pre">`_fog_of_war`</span> **bool** Determines whether there
is a base fog of war

<span class="pre">`_fog_of_war_type`</span> **int** Defaults to 0 0 -
Entire map is revealed, but enemy positions are masked (like in the GBA)
1 - Entire map is revealed, but enemy positions are masked (like in the
GBA) (yes, these are identical for past compatibility reasons) 2 - Both
map and enemy positions are masked (like in Thracia) 3 - Both map and
enemy positions are masked at the start, but the map stays revealed
after exploring it

<span class="pre">`_fog_of_war_radius`</span> **int** The distance that
player units will be able to see in the fog. Defaults to 0.

<span class="pre">`_ai_fog_of_war_radius`</span> **int** The distance
that ai units will be able to see in the fog. If not set, defaults to
<span class="pre">`_fog_of_war_radius`</span>

<span class="pre">`_other_fog_of_war_radius`</span> **int** The distance
that other team units will be able to see in the fog. If not set,
defaults to <span class="pre">`_ai_fog_of_war_radius`</span>

<span class="pre">`_prep_pick`</span> **bool** Set to True to enable
“Pick Units” in the prep screen. You don’t normally need to set this
manually, since it is set by the <span class="pre">`prep`</span> event
command.

<span class="pre">`_prep_slots`</span> **int** Limits the number of
units that can be brought to the level. Used only when you want to limit
the number of player units to a number lower than the number of
Formation tiles. Defaults to None.

<span class="pre">`_minimum_deployment`</span> **int** Must deploy at
least this many units during the Prep Screen. If you have less units
that this, must deploy all units.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Skill-Component-Reference.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Skill Component Dictionary"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Special-Tags.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Special Tags">Next <span
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
