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

- <a href="Editors-Overview.html" class="reference internal">Editors
  Overview</a>
- <a href="index.html" class="reference internal">Editors</a>
  - <a href="Editors-Overview.html" class="reference internal">Editors
    Overview</a>
  - <a href="Level-Editor.html#" class="current reference internal">Level
    Editor</a>
    - <a href="Level-Editor.html#level-music" class="reference internal">Level
      Music</a>
    - <a href="Level-Editor.html#display-formatting"
      class="reference internal">Display Formatting</a>
    - <a href="Level-Editor.html#formations-and-deployment"
      class="reference internal">Formations and Deployment</a>
    - <a href="Level-Editor.html#ai-groups" class="reference internal">AI
      Groups</a>
  - <a href="Overworld-Editor.html" class="reference internal">Overworld
    Editor</a>
  - <a href="Event-Editor.html" class="reference internal">Event Editor</a>
  - <a href="database-editors/index.html"
    class="reference internal">Database Editors</a>
  - <a href="resource-editors/index.html"
    class="reference internal">Resource Editors</a>

<span class="caption-text">Events:</span>

- <a href="../events/index.html" class="reference internal">Events</a>

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
- [Editors](index.html)
- Level Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/Level-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="level-editor" class="section">

# Level Editor<a href="Level-Editor.html#level-editor" class="headerlink"
title="Link to this heading"></a>

*last updated 2024-11-11*

<div id="level-music" class="section">

## Level Music<a href="Level-Editor.html#level-music" class="headerlink"
title="Link to this heading"></a>

A lesser known behavior of the LT music system is that “battle”
variations of music will only play if the music is set to the battle
slot as well as the phase slot. If you set music to only the phase slot
but not the battle slot, the non-battle variant will continue playing.

![YesMusic](./media/8db392735c4a28a7c293d474985abaff814f5aac.png)
![NoMusic](./media/c4ecf44e45b6e0df1d2737efe3d0532742bced34.png)

The setup on the left will play the battle variation in combat, while
the one on the left will not. You can take advantage of this behavior
and set/unset battle music via an event midway through a chapter for
additional musical effect.

</div>

<div id="display-formatting" class="section">

## Display Formatting<a href="Level-Editor.html#display-formatting" class="headerlink"
title="Link to this heading"></a>

Unlike the text in many other editors/eventing, the objective displays
use commas to break lines, like so.

![Comma0](./media/b650ba2ccc747b6858bd5e97c94a4b743c7d6bee.png)
![Comma1](./media/46628f8283473914eee911129bfc787f1584c2de.png)
![Comma2](./media/a0fe4d7ab160a194d22d6fd69226cdef5aca0862.png)

</div>

<div id="formations-and-deployment" class="section">

## Formations and Deployment<a href="Level-Editor.html#formations-and-deployment" class="headerlink"
title="Link to this heading"></a>

Formation regions set your default deployment count for a chapter. For
those that want a greater control over deploy count, the
<span class="pre">`_prep_slots`</span> and
<span class="pre">`_minimum_deployment`</span> level variables can be
used to set upper and lower bounds for deployment count. More
information can be found in the
<a href="../appendix/Special-Variables.html#level-variables"
class="reference internal"><span class="std std-ref">Level
Variables</span></a> appendix entry.

</div>

<div id="ai-groups" class="section">

## AI Groups<a href="Level-Editor.html#ai-groups" class="headerlink"
title="Link to this heading"></a>

AI Groups can be set in the units editor for both generics and normal
units, allowing units in the same group to all charge at once if a
number of units equal to the threshold could attack your army.

![AIGroups](./media/216b7f746a36dc8b951f8562549e4e1e13a6e3cb.png)

However, as seen below, enemies with the ‘Guard’ type AI will still have
a stationary range display. This is a lie; they will charge.

![ItLies](./media/5fa9eea43359bd2496a6887d1063953d905edb18.png)

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="index.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="Editors"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Overworld-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Overworld Editor">Next <span
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
