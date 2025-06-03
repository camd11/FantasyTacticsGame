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
    - <a href="Icons-Editor.html#" class="current reference internal">Icons
      Editor</a>
      - <a href="Icons-Editor.html#removing-icon-sheets"
        class="reference internal">Removing Icon Sheets</a>
      - <a href="Icons-Editor.html#icons-in-text"
        class="reference internal">Icons In Text</a>
    - <a href="Portraits-Editor.html" class="reference internal">Portraits
      Editor</a>
    - <a href="Map-Animations-Editor.html" class="reference internal">Map
      Animations Editor</a>
    - <a href="Backgrounds-Editor.html" class="reference internal">Backgrounds
      Editor</a>
    - <a href="Map-Sprites-Editor.html" class="reference internal">Map Sprites
      Editor</a>
    - <a href="Combat-Animations-Editor.html"
      class="reference internal">Combat Animations Editor</a>
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
- Icons Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/resource-editors/Icons-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="icons-editor" class="section">

# Icons Editor<a href="Icons-Editor.html#icons-editor" class="headerlink"
title="Link to this heading"></a>

*last updated 2024-11-13*

<div id="removing-icon-sheets" class="section">

## Removing Icon Sheets<a href="Icons-Editor.html#removing-icon-sheets" class="headerlink"
title="Link to this heading"></a>

Icon sheets cannot be removed via the editor. Instead, you must go to
the appropriate icons folder in the <span class="pre">`resources`</span>
folder of your project and delete the icon sheet image there, as well as
altering the <span class="pre">`.json`</span> file to no longer
reference that sheet.

It is generally **not** recommended to alter files in this manner unless
you are sufficiently experienced with the engine. Do this only if you
absolutely must remove the icon sheet for whatever reason.

</div>

<div id="icons-in-text" class="section">

## Icons In Text<a href="Icons-Editor.html#icons-in-text" class="headerlink"
title="Link to this heading"></a>

Any 16x16 icon can be displayed in text by using
<span class="pre">`<icon>ICONNAME</>`</span>. As such, it is recommended
to replace the name of any icon you may wish to reference, such as icons
used to represent weapon effectiveness.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="index.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="Resource Editors"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Portraits-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Portraits Editor">Next <span
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
