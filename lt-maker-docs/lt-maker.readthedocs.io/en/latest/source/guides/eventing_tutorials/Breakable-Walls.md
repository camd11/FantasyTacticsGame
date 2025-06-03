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
    - <a href="Breakable-Walls.html#"
      class="current reference internal">Breakable Walls</a>
      - <a href="Breakable-Walls.html#creating-a-breakable-wall"
        class="reference internal">Creating a breakable wall</a>
    - <a href="Death-Quotes.html" class="reference internal">Universal Death
      Quotes Tutorial</a>
    - <a href="Choices-and-Battle-Saves.html"
      class="reference internal">Choices and Battle Saves</a>
    - <a href="Unit-Groups.html" class="reference internal">Unit Groups</a>
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
- Breakable Walls
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/eventing_tutorials/Breakable-Walls.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="breakable-walls" class="section">

# Breakable Walls<a href="Breakable-Walls.html#breakable-walls" class="headerlink"
title="Link to this heading"></a>

*last updated v0.1*

Weirdly enough, breakable walls in the **Lex Talionis** are not created
using tiles or regions, but rather are invisible units you place on the
map on top of the wall tile.

Since the breakable wall is a unit, it can interact in interesting ways
with all the items and skills you have in your game.

<div id="creating-a-breakable-wall" class="section">

## Creating a breakable wall<a href="Breakable-Walls.html#creating-a-breakable-wall"
class="headerlink" title="Link to this heading"></a>

![WallClass](./media/adc20e70b1baa9d1e58019272f57c64469c6358c.png)

1.  Create a “Wall” class. The wall class should use an invisible map
    sprite. The HP of the “Wall” class determines the HP of the
    resulting breakable wall.

![NoAvoidSkill](./media/864a55e82c85285bbdd065df1e808b8d1af7707a.png)

2.  If you want the “Wall” to behave like a GBA wall where it can’t be
    doubled, can’t be crit, and cannot avoid attacks, you’ll need to
    give it a skill that gives it a lot of defense speed, a lot of crit
    avoid and a negative amount of regular avoid.

3.  For the chapter you want the wall to be present in, create a generic
    unit of the “Wall” class for each wall.

![BreakableWallEvent](./media/9bc0a6293a97e5e5b93c68997353b4a82c55ae53.png)

4.  Now, you just need to catch the wall’s death event and do something
    when the wall dies.

<div class="highlight-default notranslate">

<div class="highlight">

    # Show destruction anim
    map_anim;Snag;{position}
    # Show the new layer
    show_layer;Breakable1

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Arena.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="GBA-style Arena"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Death-Quotes.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Universal Death Quotes Tutorial">Next
<span class="fa fa-arrow-circle-right" aria-hidden="true"></span></a>

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
