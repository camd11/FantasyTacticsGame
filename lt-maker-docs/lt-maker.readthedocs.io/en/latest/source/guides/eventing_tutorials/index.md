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
  - <a href="index.html#" class="current reference internal">Eventing
    Tutorials</a>
    - <a href="Arena.html" class="reference internal">GBA-style Arena</a>
    - <a href="Breakable-Walls.html" class="reference internal">Breakable
      Walls</a>
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
- Eventing Tutorials
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/eventing_tutorials/index.rst"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="eventing-tutorials" class="section">

# Eventing Tutorials<a href="index.html#eventing-tutorials" class="headerlink"
title="Link to this heading"></a>

These are guides on various useful applications of events.

<div class="toctree-wrapper compound">

<span class="caption-text">Contents</span>

- <a href="Arena.html" class="reference internal">GBA-style Arena</a>
  - <a href="Arena.html#prerequisites"
    class="reference internal">Prerequisites</a>
  - <a href="Arena.html#setting-up-the-event"
    class="reference internal">Setting up the event</a>
  - <a href="Arena.html#reference" class="reference internal">Reference</a>
- <a href="Breakable-Walls.html" class="reference internal">Breakable
  Walls</a>
  - <a href="Breakable-Walls.html#creating-a-breakable-wall"
    class="reference internal">Creating a breakable wall</a>
- <a href="Death-Quotes.html" class="reference internal">Universal Death
  Quotes Tutorial</a>
  - <a href="Death-Quotes.html#problem-description"
    class="reference internal">Problem Description</a>
  - <a href="Death-Quotes.html#solution"
    class="reference internal">Solution</a>
- <a href="Choices-and-Battle-Saves.html"
  class="reference internal">Choices and Battle Saves</a>
  - <a href="Choices-and-Battle-Saves.html#choices"
    class="reference internal">Choices</a>
  - <a href="Choices-and-Battle-Saves.html#battle-saves"
    class="reference internal">Battle Saves</a>
- <a href="Unit-Groups.html" class="reference internal">Unit Groups</a>
  - <a href="Unit-Groups.html#unit-group-commands"
    class="reference internal">Unit Group Commands</a>
- <a href="Achievements.html" class="reference internal">Achievements</a>
  - <a href="Achievements.html#basic-functionality"
    class="reference internal">Basic Functionality</a>
  - <a href="Achievements.html#secret-achievements"
    class="reference internal">Secret Achievements</a>
  - <a href="Achievements.html#player-record-storage"
    class="reference internal">Player record storage</a>
- <a href="A-Simple-Mercenary-Shop.html" class="reference internal">A
  Simple Mercenary Shop Tutorial</a>
  - <a href="A-Simple-Mercenary-Shop.html#problem-description"
    class="reference internal">Problem Description</a>
  - <a href="A-Simple-Mercenary-Shop.html#solution"
    class="reference internal">Solution</a>
  - <a href="A-Simple-Mercenary-Shop.html#raw-data"
    class="reference internal">Raw Data</a>
  - <a href="A-Simple-Mercenary-Shop.html#choice-eventing"
    class="reference internal">Choice Eventing</a>
  - <a href="A-Simple-Mercenary-Shop.html#textboxes-for-fun-and-profit"
    class="reference internal">Textboxes for fun and profit</a>
  - <a href="A-Simple-Mercenary-Shop.html#events-from-choices"
    class="reference internal">Events from Choices</a>
  - <a href="A-Simple-Mercenary-Shop.html#reference"
    class="reference internal">Reference</a>
- <a href="Promotion-Personal-Skills.html"
  class="reference internal">Promotion Personal Skills Tutorial</a>
  - <a href="Promotion-Personal-Skills.html#problem-description"
    class="reference internal">Problem Description</a>
  - <a href="Promotion-Personal-Skills.html#solution"
    class="reference internal">Solution</a>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="../setup_tutorials/Custom-Components-And-Sprites.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Custom Components and Sprites"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Arena.html" class="btn btn-neutral float-right" accesskey="n"
rel="next" title="GBA-style Arena">Next <span
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
