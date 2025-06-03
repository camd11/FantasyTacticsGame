<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

<a href="../../../index.html" class="icon icon-home">lt-maker</a>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" spy="affix" role="navigation"
aria-label="Navigation menu">

<span class="caption-text">Contents:</span>

- <a href="../../home.html" class="reference internal">Lex Talionis
  Wiki</a>

<span class="caption-text">Getting Started:</span>

- <a href="../../getting_started/index.html"
  class="reference internal">Getting Started</a>

<span class="caption-text">Editor Guides:</span>

- <a href="../../editors/Editors-Overview.html"
  class="reference internal">Editors Overview</a>
- <a href="../../editors/index.html"
  class="reference internal">Editors</a>

<span class="caption-text">Events:</span>

- <a href="../../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../Guides-Overview.html" class="reference internal">Guides
  Overview</a>
- <a href="../index.html" class="reference internal">Guides</a>
  - <a href="../setup_tutorials/index.html"
    class="reference internal">Project Setup Tutorials</a>
  - <a href="index.html" class="reference internal">Eventing Tutorials</a>
    - <a href="Arena.html" class="reference internal">GBA-style Arena</a>
    - <a href="Breakable-Walls.html" class="reference internal">Breakable
      Walls</a>
    - <a href="Death-Quotes.html" class="reference internal">Universal Death
      Quotes Tutorial</a>
    - <a href="Choices-and-Battle-Saves.html"
      class="reference internal">Choices and Battle Saves</a>
    - <a href="Unit-Groups.html#" class="current reference internal">Unit
      Groups</a>
      - <a href="Unit-Groups.html#unit-group-commands"
        class="reference internal">Unit Group Commands</a>
    - <a href="Achievements.html" class="reference internal">Achievements</a>
    - <a href="A-Simple-Mercenary-Shop.html" class="reference internal">A
      Simple Mercenary Shop Tutorial</a>
    - <a href="Promotion-Personal-Skills.html"
      class="reference internal">Promotion Personal Skills Tutorial</a>
  - <a href="../skill_item_tutorials/index.html"
    class="reference internal">Skill and Item Tutorials</a>

<span class="caption-text">appendix:</span>

- <a href="../../appendix/Text-Formatting-Commands.html"
  class="reference internal">Text Formatting Commands</a>
- <a href="../../appendix/Item-Component-Reference.html"
  class="reference internal">Item Component Dictionary</a>
- <a href="../../appendix/Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="../../appendix/Special-Variables.html"
  class="reference internal">Special Variables</a>
- <a href="../../appendix/Special-Tags.html"
  class="reference internal">Special Tags</a>
- <a href="../../appendix/trigger-reference.html"
  class="reference internal">Event Triggers</a>
- <a href="../../appendix/Random-Seed-Mechanics.html"
  class="reference internal">Random Seed Mechanics</a>
- <a href="../../appendix/FAQ.html" class="reference internal">Frequently
  Asked Questions</a>
- <a href="../../appendix/Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="../../appendix/index.html" class="reference internal">Code
  Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../../index.html" class="icon icon-home"
  aria-label="Home"></a>
- [Guides](../index.html)
- [Eventing Tutorials](index.html)
- Unit Groups
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/eventing_tutorials/Unit-Groups.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="unit-groups" class="section">

# Unit Groups<a href="Unit-Groups.html#unit-groups" class="headerlink"
title="Link to this heading"></a>

Suppose that you’re working on a map, and you want to have a part where
a bunch of units spawn together and move together at the same time
during some part in a cutscene.

If you were to do this one-by-one, only dealing with individual units,
you would have to write several lines of event commands for each one.
It’s not long before this gets out of hand.

<div class="highlight-python notranslate">

<div class="highlight">

    # Spawns our gang of enemies
    add_unit;Enemy1;x,y
    add_unit;Enemy2;x,y
    add_unit;Enemy3;x,y
    # Moves them to their starting positions simultaneously
    move_unit;Enemy1;x,y;no_block
    move_unit;Enemy2;x,y;no_block
    move_unit;Enemy3;x,y

</div>

</div>

You have to use a command to add each unit, then you need to use a move
command on each one to get the effect of them all moving together.

There has to be a better way, right?

The solution is to use Unit Groups.

![ExampleUnitGroupMenu](./media/101704a4d9f4e924e72904a961e3d348141fa2d4.png)

When viewing a single Chapter’s tilemap and units, you’ll see four tabs
on the bottom left corner of the editor. As the name suggests, the
Groups tab deals with user-defined groups of units.

A unit group can consist of any units loaded on the map, no matter what
team they are on. To create a group, click the Create New Group button
at the bottom of the Groups list.

![ExampleNewUnitGroup](./media/678f6715812fa75da374940d01fb5611a50a52e2.png)

A blank group should appear on the list. You can rename the group by
clicking on the New Group text.

You can add a unit by clicking the + button next to the text box.
Pressing it will give you this prompt. You can select any unit you have
loaded on the map to add them to the group.

![ExampleLoadUnitInGroup](./media/469bc7d6792ef63fbcf5d834e02b92a6eae1927c.png)

Placing each unit works much like the Unit field in the Level Editor.
Unit positions are allowed to overlap, making them useful for
reinforcements and cutscenes.

Using events, we can move each group with only one command.

Before, we had to use a bunch of individual lines to handle multiple
units:

<div class="highlight-python notranslate">

<div class="highlight">

    # Spawns our gang of enemies
    add_unit;Enemy1;x,y
    add_unit;Enemy2;x,y
    add_unit;Enemy3;x,y
    # Moves them to their starting positions simultaneously
    move_unit;Enemy1;x,y;no_block
    move_unit;Enemy2;x,y;no_block
    move_unit;Enemy3;x,y

</div>

</div>

But now, this statement becomes much simpler:

<div class="highlight-python notranslate">

<div class="highlight">

    # Spawns the enemies
    spawn_group;Thug n Friends;south;Thug n Friends;fade
    # Moves them to their starting positions
    move_group;Thug n Friends;Starting

</div>

</div>

<div id="unit-group-commands" class="section">

## Unit Group Commands<a href="Unit-Groups.html#unit-group-commands" class="headerlink"
title="Link to this heading"></a>

All unit group related event commands:

<div class="highlight-python notranslate">

<div class="highlight">

    # Adds a group of units to the map. StartingGroup determines the spawn positions of each unit
    # in Group.
    add_group;Group;StartingGroup;EntryType;Placement;flags

    # This command also adds a group, but causes them to spawn at one of the edges of the 
    # screen specified by the CardinalDirection argument. Group specifies which units to spawn. 
    # StartingGroup specifies where to spawn those units.
    spawn_group;Group;CardinalDirection;StartingGroup;EntryType;Placement;flags

    # Moves each unit in Group to their corresponding position in StartingGroup
    move_group;Group;StartingGroup

    # Removes the specified group from the map
    remove_group;Group

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Choices-and-Battle-Saves.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Choices and Battle Saves"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Achievements.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Achievements">Next <span
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
