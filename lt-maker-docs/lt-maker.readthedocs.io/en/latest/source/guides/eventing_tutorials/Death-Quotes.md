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
    - <a href="Death-Quotes.html#"
      class="current reference internal">Universal Death Quotes Tutorial</a>
      - <a href="Death-Quotes.html#problem-description"
        class="reference internal">Problem Description</a>
      - <a href="Death-Quotes.html#solution"
        class="reference internal">Solution</a>
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
- Universal Death Quotes Tutorial
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/eventing_tutorials/Death-Quotes.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="universal-death-quotes-tutorial" class="section">

# Universal Death Quotes Tutorial<a href="Death-Quotes.html#universal-death-quotes-tutorial"
class="headerlink" title="Link to this heading"></a>

<div id="problem-description" class="section">

## Problem Description<a href="Death-Quotes.html#problem-description" class="headerlink"
title="Link to this heading"></a>

I want to introduce death quotes into my game.

</div>

<div id="solution" class="section">

## Solution<a href="Death-Quotes.html#solution" class="headerlink"
title="Link to this heading"></a>

There are two ways of going about this, both using events. One is on an
individual level. The second is on a general level. Which solution you
choose depends on how you wish to implement the death sequences in your
game.

<div id="individual-solution" class="section">

### Individual Solution<a href="Death-Quotes.html#individual-solution" class="headerlink"
title="Link to this heading"></a>

This solution already exists implemented in
<span class="pre">`default.ltproj`</span>. This solution involves using
an event that is triggered on the death of each unit. The event is as
follows:

![Screenshot_20210916_194901](./media/e07cc1fc332165e39cd1f7854d815db644d9cec9.png)

This event is fairly basic.

- It is a <span class="pre">`global`</span> event, meaning it can
  potentially trigger in any level.

- It triggers on <span class="pre">`unit_death`</span>, with a condition
  of
  <span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Vanessa'`</span>,
  meaning that when the unit with NID “Vanessa” dies, this event will
  play.

- Technically, this event is not bound to trigger once, based on the
  <span class="pre">`Trigger`</span>` `<span class="pre">`only`</span>` `<span class="pre">`once?`</span>
  checkbox. But since units should only be dying once, it doesn’t
  matter.

To sum, at any point in the game, if Vanessa dies, this event will play.
The event is a very straightforward talk event. It will display
Vanessa’s portrait, play a dialogue, and then remove her portrait. But
as they say, the sky’s the limit. If you want extremely elaborate death
sequences, that might involve multiple characters, giving items,
whatever crazy thing you come up with, this is the solution for you. One
drawback of this solution is that this requires a separate event for
every single unit.

</div>

<div id="general-solution" class="section">

### General solution<a href="Death-Quotes.html#general-solution" class="headerlink"
title="Link to this heading"></a>

The vast majority of the death quotes in the game will be much simpler,
following the above format - the portrait flashes, the character says
their dying line, and finally, the portrait disappears. The following
event makes use of Unit Fields to reduce event count and simplify the
process. It is as follows:

![Screenshot_20210916_195754](./media/44379b4a92b6aa665bd091dae6a0f0458a084175.png)

It’s pretty much the same, except that there is no condition attached.
This will trigger every single time a unit dies.

The meat of its functionality is in the eventing:

<div class="highlight-default notranslate">

<div class="highlight">

    if;unit.get_field('DeathQuote')
        add_portrait;{eval:unit.nid};FarRight
        speak;{eval:unit.nid};{eval:unit.get_field('DeathQuote')}
        expression;{eval:unit.nid};CloseEyes
        remove_portrait;{eval:unit.nid}
    end

</div>

</div>

For those who are unfamiliar with Unit Fields, I would recommend reading
both the other tutorials and the
<a href="../../events/Conditionals.html"
class="reference internal"><span class="doc std std-doc">eval
documentation</span></a>. To put it simply, however, this will check if
the unit that died possesses a field called
<span class="pre">`DeathQuote`</span>, and if so, it will play a scene
of the unit appearing, speaking the exact contents of their DeathQuote,
and then disappearing - exactly the same as the above scene.

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Breakable-Walls.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Breakable Walls"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Choices-and-Battle-Saves.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Choices and Battle Saves">Next <span
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
