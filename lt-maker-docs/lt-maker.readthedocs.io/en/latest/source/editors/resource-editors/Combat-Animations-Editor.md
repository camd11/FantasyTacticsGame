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
  - <a href="../database-editors/index.html"
    class="reference internal">Database Editors</a>
  - <a href="index.html" class="reference internal">Resource Editors</a>
    - <a href="Icons-Editor.html" class="reference internal">Icons Editor</a>
    - <a href="Portraits-Editor.html" class="reference internal">Portraits
      Editor</a>
    - <a href="Map-Animations-Editor.html" class="reference internal">Map
      Animations Editor</a>
    - <a href="Backgrounds-Editor.html" class="reference internal">Backgrounds
      Editor</a>
    - <a href="Map-Sprites-Editor.html" class="reference internal">Map Sprites
      Editor</a>
    - <a href="Combat-Animations-Editor.html#"
      class="current reference internal">Combat Animations Editor</a>
      - <a href="Combat-Animations-Editor.html#common-issues"
        class="reference internal">Common Issues</a>
    - <a href="Tilemaps-Editor.html" class="reference internal">Tilemaps
      Editor</a>
    - <a href="Sounds-Editor.html" class="reference internal">Sounds
      Editor</a>

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
- [Resource Editors](index.html)
- Combat Animations Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/resource-editors/Combat-Animations-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="combat-animations-editor" class="section">

# Combat Animations Editor<a href="Combat-Animations-Editor.html#combat-animations-editor"
class="headerlink" title="Link to this heading"></a>

*last updated 2024-11-13*

<div id="common-issues" class="section">

## Common Issues<a href="Combat-Animations-Editor.html#common-issues" class="headerlink"
title="Link to this heading"></a>

<div id="attack-miss-import-issue" class="section">

### Attack/Miss Import Issue<a href="Combat-Animations-Editor.html#attack-miss-import-issue"
class="headerlink" title="Link to this heading"></a>

Occasionally, a battle animation will cause your game to crash right
before hitting. Check to make sure that the animation’s
<span class="pre">`Attack`</span> and
<span class="pre">`Critical`</span> poses both start and stop the hit
routine, as below.

![CheckHits](./media/cf5830dbeb5a9d45b86c5aa9c89aae6b382a02c8.png)

Alternatively, the <span class="pre">`Miss`</span> pose will either be
missing the miss routine, or erroneously have the start and/or stop hit
routine. Ensure it *only* has the miss routine, as seen below.

![CheckMiss](./media/d90ab2e030e35c13705d8e60154c65c05649765a.png)

If hit/miss instructions are incorrect or missing, add them in at the
appropriate locations through the below dropdown.

![DIY](./media/4df91b10df6ce18d4ff853ad38ae704e9fce173a.png)

</div>

<div id="missing-spell" class="section">

### Missing Spell<a href="Combat-Animations-Editor.html#missing-spell" class="headerlink"
title="Link to this heading"></a>

If a battle animation is not playing (it defaults to map animation
despite a battle animation being set for the unit/class), it is
generally an issue fetching the spell effect for that animation.

If the battle animation is *not supposed* to use a battle cast animation
(such as for a melee weapon), ensure that the animation does *not* have
the <span class="pre">`Cast`</span>` `<span class="pre">`Spell`</span>
instruction.

If the battle animation *is* supposed to use a specific battle cast
animation, as in the case of magic tomes, check to make sure that the
item the unit is using has a valid
<span class="pre">`Battle`</span>` `<span class="pre">`Cast`</span>` `<span class="pre">`Anim`</span>
component.

If the battle animation is supposed to use a generic battle cast
animation, such as all bows using arrows, ensure that the effect
referenced in the
<span class="pre">`Cast`</span>` `<span class="pre">`Spell`</span>
instruction of the animation is present in the Combat Effect tab and is
not set to <span class="pre">`None`</span>.

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Map-Sprites-Editor.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Map Sprites Editor"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Tilemaps-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Tilemaps Editor">Next <span
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
