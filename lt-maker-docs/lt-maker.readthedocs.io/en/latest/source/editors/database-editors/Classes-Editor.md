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

- <a href="../Editors-Overview.html" class="reference internal">Editors
  Overview</a>
- <a href="../index.html" class="reference internal">Editors</a>
  - <a href="../Editors-Overview.html" class="reference internal">Editors
    Overview</a>
  - <a href="../Level-Editor.html" class="reference internal">Level
    Editor</a>
  - <a href="../Overworld-Editor.html" class="reference internal">Overworld
    Editor</a>
  - <a href="../Event-Editor.html" class="reference internal">Event
    Editor</a>
  - <a href="index.html" class="reference internal">Database Editors</a>
    - <a href="Units-Editor.html" class="reference internal">Units Editor</a>
    - <a href="Teams-Editor.html" class="reference internal">Teams Editor</a>
    - <a href="Factions-Editor.html" class="reference internal">Factions
      Editor</a>
    - <a href="Party-Editor.html" class="reference internal">Party Editor</a>
    - <a href="Classes-Editor.html#"
      class="current reference internal">Classes Editor</a>
      - <a href="Classes-Editor.html#class-tags"
        class="reference internal">Class Tags</a>
      - <a href="Classes-Editor.html#special-promotion-gain-values"
        class="reference internal">Special Promotion Gain Values</a>
      - <a href="Classes-Editor.html#combat-animation"
        class="reference internal">Combat Animation</a>
    - <a href="Tags-Editor.html" class="reference internal">Tags Editor</a>
    - <a href="Game-Vars-Editor.html" class="reference internal">Game Vars
      Editor</a>
    - <a href="Weapon-Types-Editor.html" class="reference internal">Weapon
      Types Editor</a>
    - <a href="Items-And-Skills-Editors.html" class="reference internal">Items
      And Skills Editors</a>
    - <a href="AI-Editor.html" class="reference internal">AI Editor</a>
    - <a href="Terrain-And-Movement-Costs-Editors.html"
      class="reference internal">Terrain and Movement Costs Editors</a>
    - <a href="Stats-Editor.html" class="reference internal">Stats Editor</a>
    - <a href="Equations-Editor.html" class="reference internal">Equations
      Editor</a>
    - <a href="Constants-Editor.html" class="reference internal">Constants
      Editor</a>
    - <a href="Difficulty-Modes-Editor.html"
      class="reference internal">Difficulty Modes Editor</a>
    - <a href="Supports-Editor.html" class="reference internal">Supports
      Editor</a>
    - <a href="Lore-Editor.html" class="reference internal">Lore Editor</a>
    - <a href="Raw-Data-Editor.html" class="reference internal">Raw Data
      Editor</a>
    - <a href="Translations-Editor.html"
      class="reference internal">Translations Editor</a>
  - <a href="../resource-editors/index.html"
    class="reference internal">Resource Editors</a>

<span class="caption-text">Events:</span>

- <a href="../../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../../guides/Guides-Overview.html"
  class="reference internal">Guides Overview</a>
- <a href="../../guides/index.html" class="reference internal">Guides</a>

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
- [Editors](../index.html)
- [Database Editors](index.html)
- Classes Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/database-editors/Classes-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="classes-editor" class="section">

# Classes Editor<a href="Classes-Editor.html#classes-editor" class="headerlink"
title="Link to this heading"></a>

*last updated 2024-11-13*

<div id="class-tags" class="section">

## Class Tags<a href="Classes-Editor.html#class-tags" class="headerlink"
title="Link to this heading"></a>

Unlike tags attached to a unit or those granted via events, tags
conferred by classes cannot be removed, even via event. However, if you
change a class’s tags in the project, all existing save files will have
units of that class updated as well. This is in contrast to units,
items, and skills, where existing instances of those objects in a save
file will not be automatically updated when you update the editor.

</div>

<div id="special-promotion-gain-values" class="section">

## Special Promotion Gain Values<a href="Classes-Editor.html#special-promotion-gain-values"
class="headerlink" title="Link to this heading"></a>

There are three special values that can be entered for a class’s
Promotion Gains: -99, -98, and -97.

| Promotion Gain Value | Explanation                                                                                                                                                                                   |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **-99**              | Automatically sets a unit’s stat to the class’s base stat upon promotion.                                                                                                                     |
| **-98**              | Sets a unit’s stat to the class’s base stat upon promotion if the class’s base stat is higher than the unit’s current stat. Best used for Gaiden/Echoes-style promotions.                     |
| **-97**              | Changes a unit’s stat by the difference between their current class’s base stat and their new class’s base stat. Useful for differentiating gains when two classes promote to the same class. |

Note that, in order to preserve movement booster gains when promoting,
either -97 or specifying the movement gain directly (e.g. a +1 bonus for
a 6 MOV unit that promotes from a 5 MOV unit) must be used, as -99 and
-98 can both erase the gains of the movement booster under some
circumstances.

</div>

<div id="combat-animation" class="section">

## Combat Animation<a href="Classes-Editor.html#combat-animation" class="headerlink"
title="Link to this heading"></a>

If you ‘Cancel’ while in the Choose Combat Animation window in the class
editor, it will unassign whatever the current combat animation is for
that class. This is the only way to unassign combat animations from a
class.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Party-Editor.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Party Editor"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Tags-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Tags Editor">Next <span
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
