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
    - <a href="Title-Screen.html#" class="current reference internal">Title
      Screen</a>
      - <a href="Title-Screen.html#logo" class="reference internal">Logo</a>
      - <a href="Title-Screen.html#press-start" class="reference internal">Press
        Start</a>
      - <a href="Title-Screen.html#background"
        class="reference internal">Background</a>
      - <a href="Title-Screen.html#attribution"
        class="reference internal">Attribution</a>
      - <a href="Title-Screen.html#complete"
        class="reference internal">Complete!</a>
    - <a href="Shop-Portraits.html" class="reference internal">Shop
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
- Title Screen
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/setup_tutorials/Title-Screen.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="title-screen" class="section">

# Title Screen<a href="Title-Screen.html#title-screen" class="headerlink"
title="Link to this heading"></a>

In this section, we will change the default *The Lion Throne* title
screen to the one used by the *The Sacred Stones*. Once you understand
how to do that, changing the title menu to use your own custom images
should be easy.

![TitleScreen](./media/22c11b5a37ddba2fa1ece4d858ec79a0dfd03792.png)
![SacredStonesTitleScreen](./media/3bc276fab56369f16774af1b05df06bc56d9b50f.png)

There are four main components to the title screen that you can change.

1.  Logo

2.  Press Start Icon

3.  Background

4.  Attribution

<div id="logo" class="section">

## Logo<a href="Title-Screen.html#logo" class="headerlink"
title="Link to this heading"></a>

Download the new Sacred Stones logo:

![SacredStonesLogo](./media/8f81b2a483d4684f4a9b1d2ca3fbcb3d7c42ef99.png)

To do these changes, we will have to delve into your project’s
**resources/custom_sprites** directory. If a **custom_sprites**
directory does not already exist for your project, create one (make sure
it’s named exactly **custom_sprites**). Then, put the Sacred Stones logo
PNG file into that directory with the exact name **logo.png**.

![CustomSpritesFileExplorer](./media/0fb103c231ac08c322b2776992bdb36fd4a363c9.png)

</div>

<div id="press-start" class="section">

## Press Start<a href="Title-Screen.html#press-start" class="headerlink"
title="Link to this heading"></a>

![PressStartSprite](./media/cf7239b14dd59648f953eb94331a196c4a2172cf.png)

This works similarly. If you have a new Press Start animation you want
to show, you can add the PNG file to the **custom_sprites** directory in
your project’s **resources**. Make sure it’s named exactly
**press_start.png**.

![DifferentLogoTitleScreen](./media/b5e7ba11f1f76ad7965c7da593442b20979406c2.png)

</div>

<div id="background" class="section">

## Background<a href="Title-Screen.html#background" class="headerlink"
title="Link to this heading"></a>

![SacredStonesBackground](./media/7e2b73510d810aae597dbf2e00b15a50d5b9d8bc.png)

Switching out the background is also a simple affair. Open up the
Panoramas editor and locate the **title_background** panorama. Delete
it. Now you can import your own background. It can be a static
background like Sacred Stones uses, or you can import several png files
at the same time as long as they have numbers at the end of their
filenames (like **title_background0.png**, **title_background1.png**,
etc.)

</div>

<div id="attribution" class="section">

## Attribution<a href="Title-Screen.html#attribution" class="headerlink"
title="Link to this heading"></a>

On the bottom left hand corner of the title screen is the attribution.
You can change what it says in the Translations editor. Find the key
<span class="pre">`_attribution`</span> and change the value to whatever
you’d like the title screen to say, such as
<span class="pre">`created`</span>` `<span class="pre">`by`</span>` `<span class="pre">`you`</span>.
If the key does not exist in the translations editor, create a new
Translation with the key first.

![TranslationsEditor](./media/3d3be66a8ce42f507e62b627b1139ad6ef288c27.png)

</div>

<div id="complete" class="section">

## Complete\!<a href="Title-Screen.html#complete" class="headerlink"
title="Link to this heading"></a>

Now you can pull up the game and check out the new and improved title
screen!

![FinishedTitleMenu](./media/3bc276fab56369f16774af1b05df06bc56d9b50f.png)

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="index.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="Project Setup Tutorials"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Shop-Portraits.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Shop Portraits">Next <span
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
