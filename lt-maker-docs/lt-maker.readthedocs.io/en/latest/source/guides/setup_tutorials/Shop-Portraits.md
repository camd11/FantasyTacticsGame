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
    - <a href="Shop-Portraits.html#" class="current reference internal">Shop
      Portraits</a>
    - <a href="Fonts-And-Languages.html" class="reference internal">Working
      with Fonts and Languages</a>
    - <a href="Custom-Components-And-Sprites.html"
      class="reference internal">Custom Components and Sprites</a>
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
- Shop Portraits
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/setup_tutorials/Shop-Portraits.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="shop-portraits" class="section">

# Shop Portraits<a href="Shop-Portraits.html#shop-portraits" class="headerlink"
title="Link to this heading"></a>

This guide will very swiftly illustrate how to update the three special
shop portraits in LT maker: armory, vendor, and arena.

These portraits are not stored in the same way as standard unit
portraits. Instead, to update these portraits, you must use the
**resources/custom_sprites** directory in your project. If a
**custom_sprites** directory does not already exist for your project,
create one (make sure it’s named exactly **custom_sprites**).

![CustomSpritesFileExplorer](./media/709994f41212425c1ef88c3348929ffdf3f80c93.png)

Then, place the portrait you wish to use in this directory and name it
one of the following file names to replace its respective default
portrait:

**arena_portrait.png**  
**armory_portrait.png**  
**vendor_portrait.png**

![PlaceImageLikeSo](./media/504d8365a5a8ed5e1fb7fe16c9963417f4011902.png)

Now when you set up a shop of that type in a shop event, you should see
your replaced portrait.

![HiAnna](./media/06afd0af448c0279f599fd55ad106bc004f72912.png)

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Title-Screen.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Title Screen"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Fonts-And-Languages.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Working with Fonts and Languages">Next
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
