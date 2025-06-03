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
  - <a href="index.html" class="reference internal">Project Setup
    Tutorials</a>
    - <a href="Title-Screen.html" class="reference internal">Title Screen</a>
    - <a href="Shop-Portraits.html" class="reference internal">Shop
      Portraits</a>
    - <a href="Fonts-And-Languages.html" class="reference internal">Working
      with Fonts and Languages</a>
    - <a href="Custom-Components-And-Sprites.html#"
      class="current reference internal">Custom Components and Sprites</a>
      - <a
        href="Custom-Components-And-Sprites.html#project-specific-custom-components"
        class="reference internal">Project Specific Custom Components</a>
      - <a
        href="Custom-Components-And-Sprites.html#project-specific-custom-sprites"
        class="reference internal">Project Specific Custom Sprites</a>
  - <a href="../eventing_tutorials/index.html"
    class="reference internal">Eventing Tutorials</a>
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
- [Project Setup Tutorials](index.html)
- Custom Components and Sprites
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/setup_tutorials/Custom-Components-And-Sprites.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="custom-components-and-sprites" class="section">

# Custom Components and Sprites<a
href="Custom-Components-And-Sprites.html#custom-components-and-sprites"
class="headerlink" title="Link to this heading"></a>

*last updated 2024-11-13*

If you’ve developed your own custom components or engine sprites, those
custom assets will be necessary to run your game/project. However, up
until now your only option to distribute these custom assets was:

1.  Petition rainlash to add your custom components to the master branch
    of the engine, so that others using your custom assets would have
    access to them.

2.  Distribute your own bespoke version of the engine to your players
    that includes the custom assets.

Well, now there’s a third option. **Project Specific Custom Components
and Sprites**

<div id="project-specific-custom-components" class="section">

## Project Specific Custom Components<a
href="Custom-Components-And-Sprites.html#project-specific-custom-components"
class="headerlink" title="Link to this heading"></a>

In your project’s *resources* directory, there should be a directory
called <span class="pre">`custom_components`</span>. Within that
directory, there’ll be two files:
<span class="pre">`custom_item_components.py`</span> and
<span class="pre">`custom_skill_components.py`</span>.

These will be loaded at runtime when you start the editor or the engine
and load up your project, so players of your game can use the canonical
Lex Talionis engine with your .ltproj project and its bespoke custom
components without any friction.

To learn how to write components, you should reference the other
component tutorials in this section, as well as the existing component
code within the engine, located in
<span class="pre">`app/engine/item_components/`</span> and
<span class="pre">`app/engine/skill_components`</span>

</div>

<div id="project-specific-custom-sprites" class="section">

## Project Specific Custom Sprites<a
href="Custom-Components-And-Sprites.html#project-specific-custom-sprites"
class="headerlink" title="Link to this heading"></a>

As with custom components, your project’s *resources* directory should
contain a directory called <span class="pre">`custom_sprites`</span>.
This directory will contain nothing at all by default.

Any image placed within this directory will take precedence over an
image with the same name in the *sprites* directory of the engine. You
can do this to overwrite various engine graphics without touching the
engine directory directly, such as the title screen image.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Fonts-And-Languages.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Working with Fonts and Languages"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="../eventing_tutorials/index.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Eventing Tutorials">Next <span class="fa fa-arrow-circle-right"
aria-hidden="true"></span></a>

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
