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
- <a href="Special-Tags.html#" class="current reference internal">Special
  Tags</a>
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
- Special Tags
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/Special-Tags.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="special-tags" class="section">

<span id="id1"></span>

# Special Tags<a href="Special-Tags.html#special-tags" class="headerlink"
title="Link to this heading"></a>

*last updated v0.1*

This appendix details every tag that the **Lex Talionis** engine handles
uniquely. You can of course assign other tags to units and classes and
check for them in your own event scripts or item/skill components.

Both units and classes can be assigned tags. A unit in game has it’s own
tags as well as the tags of it’s class.

**Lord** - If ‘Autocursor’ is **ON**, will be hovered over by the cursor
when the player phase starts.

**Boss** - The unit will be designated as a boss. They will have a boss
icon on their sprite, and give more EXP when defeated if the *Boss
Bonus* constant is set.

**Required** - Unit must be chosen from among the list of available
units to deploy in the Prep Screen.

**Blacklist** - Unit cannot be deployed for the chapter in the Prep
Screen.

**Armor** - Denotes a unit as Armor. Affects movement SFX when the unit
walks.

**Mounted** - Denotes a unit as Mounted. Affects movement SFX, as well
as the Aid icon.

**Flying** - Denotes a unit as Flying. Affects movement SFX, as well as
the Aid icon.

**Dragon** - Denotes a unit as a Dragon. Used for the Aid icon.

**AutoPromote** - This unit/class will automatically promote if they
level past their class’s maximum level.

**NoAutoPromote** - This unit/class cannot promote via leveling up past
their class’s maximum level.

**Convoy** - Allows the unit/class to access the convoy during their
turn.

**AdjConvoy** - Allows allies adjacent to the unit/class to access the
convoy during their turn.

**Tile** - Denotes a unit should behave as a destructible tile. Unit
cannot be selected, and will not show up in the Info Menu. Unit will
also not be contained in most lists of units throughout the engine.

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Special-Variables.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Special Variables"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="trigger-reference.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Event Triggers">Next <span
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
