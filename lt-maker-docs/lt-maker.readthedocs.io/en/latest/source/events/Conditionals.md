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

- <a href="index.html" class="reference internal">Events</a>
  - <a href="Event-Overview.html" class="reference internal">Event
    Overview</a>
  - <a href="Conditionals.html#"
    class="current reference internal">Conditionals</a>
    - <a href="Conditionals.html#event-objects"
      class="reference internal">Event Objects</a>
    - <a href="Conditionals.html#boolean-operators"
      class="reference internal">Boolean Operators</a>
    - <a href="Conditionals.html#list-comprehensions"
      class="reference internal">List comprehensions</a>
    - <a href="Conditionals.html#common-tasks"
      class="reference internal">Common Tasks</a>
    - <a href="Conditionals.html#full-useful-attributes-of-global-game-object"
      class="reference internal">Full Useful Attributes of Global Game
      Object</a>
  - <a href="Region-Events.html" class="reference internal">Region
    Events</a>
  - <a href="Miscellaneous-Events.html"
    class="reference internal">Miscellaneous Events</a>
  - <a href="Test-Events.html" class="reference internal">Test Events</a>
  - <a href="Python-Eventing.html" class="reference internal">Python
    Eventing</a>
  - <a href="Event-Debugger.html" class="reference internal">Debugger</a>

<span class="caption-text">Guides:</span>

- <a href="../guides/Guides-Overview.html"
  class="reference internal">Guides Overview</a>
- <a href="../guides/index.html" class="reference internal">Guides</a>

<span class="caption-text">appendix:</span>

- <a href="../appendix/Text-Formatting-Commands.html"
  class="reference internal">Text Formatting Commands</a>
- <a href="../appendix/Item-Component-Reference.html"
  class="reference internal">Item Component Dictionary</a>
- <a href="../appendix/Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="../appendix/Special-Variables.html"
  class="reference internal">Special Variables</a>
- <a href="../appendix/Special-Tags.html"
  class="reference internal">Special Tags</a>
- <a href="../appendix/trigger-reference.html"
  class="reference internal">Event Triggers</a>
- <a href="../appendix/Random-Seed-Mechanics.html"
  class="reference internal">Random Seed Mechanics</a>
- <a href="../appendix/FAQ.html" class="reference internal">Frequently
  Asked Questions</a>
- <a href="../appendix/Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="../appendix/index.html" class="reference internal">Code
  Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- [Events](index.html)
- Conditionals
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/events/Conditionals.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="conditionals" class="section">

# Conditionals<a href="Conditionals.html#conditionals" class="headerlink"
title="Link to this heading"></a>

*last updated v0.1*

Conditionals are perhaps the most powerful tool in the game designer’s
arsenal. They allow you to further refine how and when certain events
will occur, abilities can be activated, or items will behave, and much
more.

![ExampleConditionalInSkillEditor](./media/cc18a7af910c15cc948484817960014199f3a0cf.png)

All conditionals in the **Lex Talionis** engine are evaluated at runtime
by a Python evaluation engine. As such, this means that all conditionals
must be written in valid Python. At first this may seem to have a strict
learning curve, but the minimal Python needed to write conditionals can
be learned easily. Having the conditionals evaluated by a real
programming language like Python enables them to be much more powerful
and expressive than would otherwise be possible.

<div id="event-objects" class="section">

## Event Objects<a href="Conditionals.html#event-objects" class="headerlink"
title="Link to this heading"></a>

![ExampleConditionalInEventEditor](./media/2ca9a613deceab3022a29109429acc7b895ee7c8.png)

While checking the conditionals for an event (whether that be through
the Condition box in the left pane of the Event Editor or through an if
statement), the event may expose certain variables with extra
information.

For instance, in a <span class="pre">`unit_wait`</span> event, the
<span class="pre">`unit`</span> variable is set to the unit that just
waited. You could use the <span class="pre">`unit`</span> variable now
to figure out which unit just waited, their team, their class, etc.

Each event exposes a different set of variables. Check out the Trigger
List section in the <a href="Event-Overview.html#eventoverview"
class="reference internal"><span
class="std std-ref">Event-Overview</span></a> for more information.

</div>

<div id="boolean-operators" class="section">

## Boolean Operators<a href="Conditionals.html#boolean-operators" class="headerlink"
title="Link to this heading"></a>

You can use <span class="pre">`and`</span>,
<span class="pre">`or`</span>, and <span class="pre">`not`</span> to
combine or invert conditionals as necessary.
<span class="pre">`A`</span>` `<span class="pre">`and`</span>` `<span class="pre">`B`</span>
returns true if both A and B return true individually, otherwise it will
return false.
<span class="pre">`A`</span>` `<span class="pre">`or`</span>` `<span class="pre">`B`</span>
returns true if either A or B return true individually, otherwise it
will return false.
<span class="pre">`not`</span>` `<span class="pre">`A`</span> will
return true if A is false, and vice versa.

You can do this more than once in a chain. For instance
<span class="pre">`(A`</span>` `<span class="pre">`and`</span>` `<span class="pre">`B)`</span>` `<span class="pre">`or`</span>` `<span class="pre">`C`</span>
will check whether A and B are both true, or C is true. If C is false
and it is not the case that both A and B are true, then it will return
false.

Example Use Case:
<span class="pre">`game.check_alive('Joel')`</span>` `<span class="pre">`and`</span>` `<span class="pre">`game.check_alive('Nia')`</span>
to check that both characters are alive before giving them a post-battle
conversation.

</div>

<div id="list-comprehensions" class="section">

## List comprehensions<a href="Conditionals.html#list-comprehensions" class="headerlink"
title="Link to this heading"></a>

Sometimes you need to check the values for several objects at once. You
can do this using Python *list comprehensions*.

Python list comprehensions follow a simple syntax:

<div class="highlight-python notranslate">

<div class="highlight">

    [obj for obj in list_of_objects if obj is good]

</div>

</div>

This python statement will return a list of the objects in
<span class="pre">`list_of_objects`</span>, filtered by the if statement
at the end, so it will only return the *good* objects. The if statement
at the end is optional and can be left off if you don’t want to filter
the object list by any property.

Example (Checks if a unit has a skill with nid
<span class="pre">`Vantage`</span>)

<div class="highlight-default notranslate">

<div class="highlight">

    if;'Vantage' in [skill.nid for skill in unit.skills]
        s;{unit};I have vantage!
    end

</div>

</div>

You can use the python functions <span class="pre">`len`</span>,
<span class="pre">`sum`</span>, <span class="pre">`any`</span>, and
<span class="pre">`all`</span> on list comprehensions.

Example (Checks if any player unit’s y position on the map is less than
13)

<div class="highlight-default notranslate">

<div class="highlight">

    any(unit.position[1] < 13 for unit in game.units if unit.position and unit.team == 'player')

</div>

</div>

1.  <span class="pre">`len`</span> returns the number of objects in the
    list

2.  <span class="pre">`sum`</span> adds up the objects in the list

3.  <span class="pre">`any`</span> returns **True** if at least one
    object in the list is true

4.  <span class="pre">`all`</span> returns **True** if *all* objects in
    the list are true

> <div>
>
> If you are new to Python, you can always find out more information by
> just googling it. These days, Python is a common first-time coders
> language, so there is lots of information out there for beginners.
>
> </div>

</div>

<div id="common-tasks" class="section">

## Common Tasks<a href="Conditionals.html#common-tasks" class="headerlink"
title="Link to this heading"></a>

Check if the unit referenced by the event is a specific unit
<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Eirika'`</span>

Check if the region referenced by the event is a specific region
<span class="pre">`region.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'House1'`</span>

Check if a unit is alive
<span class="pre">`game.check_alive(unit.nid)`</span> or
<span class="pre">`game.check_alive('Eirika')`</span>

Check if a unit is dead
<span class="pre">`game.check_dead(unit.nid)`</span> or
<span class="pre">`game.check_dead('Eirika')`</span>

Check the team of a unit
<span class="pre">`unit.team`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'player'`</span>
or
<span class="pre">`game.get_unit('Eirika').team`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'player'`</span>

Check the current turn number
<span class="pre">`game.turncount`</span>` `<span class="pre">`==`</span>` `<span class="pre">`5`</span>
or
<span class="pre">`game.turncount`</span>` `<span class="pre">`<`</span>` `<span class="pre">`10`</span>

Check nid of terrain at a position
<span class="pre">`game.tilemap.get_terrain(position)`</span>

Check name of terrain at a position
<span class="pre">`DB.terrain.get(game.tilemap.get_terrain(position)).name`</span>

Check the current mode
<span class="pre">`game.mode.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Lunatic'`</span>

Check the current level
<span class="pre">`game.level.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Chapter`</span>` `<span class="pre">`2'`</span>

Access a level variable
<span class="pre">`game.level_vars['num_switches']`</span>

Access a game variable
<span class="pre">`game.game_vars['villages_saved']`</span>

Example:

<div class="highlight-default notranslate">

<div class="highlight">

    if;game.game_vars['villages_saved'] >= 3
        give_item;Protagonist;Reward
    end

</div>

</div>

Variables can also be accessed in the following manner in the event
editor: <span class="pre">`{v:num_switches}`</span> or
<span class="pre">`{v:villages_saved}`</span>

Example:

<div class="highlight-default notranslate">

<div class="highlight">

    if;{v:villages_saved} >= 3
        give_item;Protagonist;Reward
    end

</div>

</div>

Check if a boss unit has already given their fight quote for the
challenger
<span class="pre">`check_pair('Lyon',`</span>` `<span class="pre">`'Eirika')`</span>

Check if a boss unit has already given their default fight quote.
<span class="pre">`Eirika`</span> and <span class="pre">`Ephraim`</span>
are the units with non-default fight quotes
<span class="pre">`check_default('Lyon',`</span>` `<span class="pre">`['Eirika',`</span>` `<span class="pre">`'Ephraim'])`</span>
or
<span class="pre">`check_default('Batta',`</span>` `<span class="pre">`[])`</span>

Check size of party
<span class="pre">`len(game.get_units_in_party())`</span>

Example:

<div class="highlight-default notranslate">

<div class="highlight">

    if;len(game.get_units_in_party()) < 5
        alert;You have lost too many members of your party
        lose_game
    end

</div>

</div>

</div>

<div id="full-useful-attributes-of-global-game-object" class="section">

## Full Useful Attributes of Global Game Object<a href="Conditionals.html#full-useful-attributes-of-global-game-object"
class="headerlink" title="Link to this heading"></a>

The game object is a very powerful source of information about the state
of the game. It keeps track of all units in the current level as well as
all non-generic units ever loaded into the game (whether alive or dead).

<div class="highlight-default notranslate">

<div class="highlight">

    game_vars: dict[str: ??]
    level_vars: dict[str: ??]
    playtime: float  # How long has the player been playing on this save file
    turncount: int
    units: list  # List of all units the game is tracking
    mode: DifficultyModeObject  # the current mode
    level: LevelObject  # the current level object
    tilemap: TileMapObject  # The current tilemap
    party: PartyObject  # the current party

    get_unit(str) -> UnitObject  # Returns a Unit with the given nid
    get_region(str) -> RegionObject  # Returns a Region with the given nid
    get_party(str) -> PartyObject # Returns the party with the given nid
    get_all_units() -> list  # Returns all alive units on the map
    get_player_units() -> list  # All alive player units on the map
    get_enemy_units() -> list  # All alive enemy units on the map
    get_all_units_in_party(str?) -> list  # All non-generic player units in the given party (defaults to current party)
    get_units_in_party(str?) -> list  # All alive non-generic player units in the given party (defaults to current party)
    check_dead(str) -> bool
    check_alive(str) -> bool
    get_money() -> int  # money of current party

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Event-Overview.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Event Overview"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Region-Events.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Region Events">Next <span
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
