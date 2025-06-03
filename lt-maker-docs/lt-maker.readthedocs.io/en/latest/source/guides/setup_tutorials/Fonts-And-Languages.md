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
    - <a href="Fonts-And-Languages.html#"
      class="current reference internal">Working with Fonts and Languages</a>
      - <a href="Fonts-And-Languages.html#where-to-find-fonts"
        class="reference internal">Where to find fonts</a>
      - <a href="Fonts-And-Languages.html#what-are-png-and-idx-files"
        class="reference internal">What are PNG and IDX files?</a>
      - <a href="Fonts-And-Languages.html#anatomy-of-a-png-file"
        class="reference internal">Anatomy of a PNG file</a>
      - <a href="Fonts-And-Languages.html#anatomy-of-a-idx-file"
        class="reference internal">Anatomy of a IDX file</a>
      - <a href="Fonts-And-Languages.html#a-worked-example"
        class="reference internal">A worked example</a>
      - <a href="Fonts-And-Languages.html#modifying-existing-characters"
        class="reference internal">Modifying existing characters</a>
      - <a href="Fonts-And-Languages.html#adding-new-characters"
        class="reference internal">Adding new characters</a>
      - <a href="Fonts-And-Languages.html#adding-new-fonts"
        class="reference internal">Adding new fonts</a>
      - <a href="Fonts-And-Languages.html#adding-language-support"
        class="reference internal">Adding Language Support</a>
      - <a href="Fonts-And-Languages.html#special-notes"
        class="reference internal">Special Notes</a>
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
- Working with Fonts and Languages
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/setup_tutorials/Fonts-And-Languages.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="working-with-fonts-and-languages" class="section">

<span id="fonts-guide"></span>

# Working with Fonts and Languages<a href="Fonts-And-Languages.html#working-with-fonts-and-languages"
class="headerlink" title="Link to this heading"></a>

If you wish to add a new font or modify existing fonts, you can do so by
directly modifying the font files in your project. Adding language
support for non-alphabetical systems works the same way.

<div id="where-to-find-fonts" class="section">

## Where to find fonts<a href="Fonts-And-Languages.html#where-to-find-fonts"
class="headerlink" title="Link to this heading"></a>

Under <span class="pre">`<your_project.ltproj>/resources/fonts/`</span>
you will find two types of files: <span class="pre">`.png`</span> files
and <span class="pre">`.idx`</span> files. These files are loaded into
the engine at startup and are responsible for the text fonts that are
available for you to use.

</div>

<div id="what-are-png-and-idx-files" class="section">

## What are PNG and IDX files?<a href="Fonts-And-Languages.html#what-are-png-and-idx-files"
class="headerlink" title="Link to this heading"></a>

PNG files are font character maps. These are essentially files that
contain the character images that will be directly drawn onto the game
screen. The characters in the file are lined up in a grid. When you
create text in your game, the engine will open this file and fetch the
corresponding character image in the PNG based on its location in the
grid, also called its index. The text that it fetches corresponds to the
text you have put in your game. The engine knows where each character is
by looking at the IDX file. The IDX file contains information on the
pixel width and height of each box in the PNG grid, a mapping of each
character available for use to a grid index, as well as the width of
specific characters so you can adjust your kerning.

</div>

<div id="anatomy-of-a-png-file" class="section">

## Anatomy of a PNG file<a href="Fonts-And-Languages.html#anatomy-of-a-png-file"
class="headerlink" title="Link to this heading"></a>

![FontPng](./media/501869d00de72507310b5bd1a71984ee513e2eae.png)

</div>

<div id="anatomy-of-a-idx-file" class="section">

## Anatomy of a IDX file<a href="Fonts-And-Languages.html#anatomy-of-a-idx-file"
class="headerlink" title="Link to this heading"></a>

![FontIdx](./media/6133260764db05e6802befe53d963341be087ace.png)

</div>

<div id="a-worked-example" class="section">

## A worked example<a href="Fonts-And-Languages.html#a-worked-example" class="headerlink"
title="Link to this heading"></a>

In the default project, you will find convo as one of the available
fonts. This font has its corresponding
<span class="pre">`convo.png`</span> and
<span class="pre">`convo.idx`</span> files, already shown in the above
sections. When you have a line of text (called a string) such as “Hi”
displayed in your game, the engine will look at each character in the
string and then look in <span class="pre">`convo.idx`</span> to tell at
which <span class="pre">`x,`</span>` `<span class="pre">`y`</span>
indices it will find the character image in
<span class="pre">`convo.png`</span>. It will then multiply these
indices by the <span class="pre">`width`</span> and
<span class="pre">`height`</span> found in
<span class="pre">`convo.idx`</span> to get the exact top-left pixel
location in <span class="pre">`convo.png`</span>. It will use the
character image it finds at that location by directly drawing what it
finds in a
<span class="pre">`height`</span>` `<span class="pre">`x`</span>` `<span class="pre">`cwidth`</span>
box.

![FontHIdxExample](./media/a29ce90cc7c2c76ff06f30f6d20574b48d028bc8.png)
![FontHPngExample](./media/ae1ed77112d6c6cd07de7e97328a4c8c00d7619c.png)

For example, for the character “H” the exact pixel location of the
character will can be found by taking the
<span class="pre">`x,`</span>` `<span class="pre">`y`</span> index in
<span class="pre">`convo.idx`</span>
(<span class="pre">`9,`</span>` `<span class="pre">`1`</span>). The
width and height of grid boxes in <span class="pre">`convo.idx`</span>
is <span class="pre">`16`</span> and <span class="pre">`10`</span>
respectively. By multiplying the
<span class="pre">`x,`</span>` `<span class="pre">`y`</span> and the
<span class="pre">`width,`</span>` `<span class="pre">`height`</span>,
the exact top-left pixel location of “H” can be found at
<span class="pre">`144,`</span>` `<span class="pre">`10`</span>. When
the engine goes and draws the “H”, it will check
<span class="pre">`cwidth`</span> and find it is
<span class="pre">`6`</span>. It will then draw every pixel in a
<span class="pre">`height`</span>` `<span class="pre">`x`</span>` `<span class="pre">`cwidth`</span>
at the pixel location, which is a
<span class="pre">`16`</span>` `<span class="pre">`x`</span>` `<span class="pre">`6`</span>
box at <span class="pre">`144,`</span>` `<span class="pre">`10`</span>.

</div>

<div id="modifying-existing-characters" class="section">

## Modifying existing characters<a href="Fonts-And-Languages.html#modifying-existing-characters"
class="headerlink" title="Link to this heading"></a>

You can modify existing characters by redrawing them in the PNG file in
your favorite art software. You can also swap mappings of characters
however you see fit in the IDX file.

</div>

<div id="adding-new-characters" class="section">

## Adding new characters<a href="Fonts-And-Languages.html#adding-new-characters"
class="headerlink" title="Link to this heading"></a>

You can add new characters by adding them to an empty location the PNG
file and then setting up the correct mapping in the IDX file.

</div>

<div id="adding-new-fonts" class="section">

## Adding new fonts<a href="Fonts-And-Languages.html#adding-new-fonts" class="headerlink"
title="Link to this heading"></a>

You can add new fonts by creating new PNG and IDX files and then
correctly setting them up based on the scheme described in previous
sections.

</div>

<div id="adding-language-support" class="section">

## Adding Language Support<a href="Fonts-And-Languages.html#adding-language-support"
class="headerlink" title="Link to this heading"></a>

Some LT games are made for languages using non-Latin alphabets. While LT
does not have native support for these alphabets, it’s straightforward
to add them.

> <div>
>
> NOTA BENE: You **must** have your editor **closed** while doing this,
> otherwise there is risk of data corruption.
>
> </div>

First, download a font which supports the alphabet of your choice. Below
are a few recommendations - some of the developers have personally
tested these and confirmed them to be suitable for use in LT.

| Language             | Font                                                                            |
|----------------------|---------------------------------------------------------------------------------|
| **Mandarin Chinese** | <a                                                                              
                        href="https://github.com/rougier/freetype-gl/blob/master/fonts/fireflysung.ttf"  
                        class="reference external">Firefly Sung</a>                                      |
| **Japanese**         | <a href="https://itouhiro.hatenablog.com/entry/20130602/font"                   
                        class="reference external">PixelMPlus</a>                                        |

Next, move the font into your project’s fonts folder, located at
<span class="pre">`MyProject.ltproj/resources/fonts`</span>.

Finally, open up the <span class="pre">`fonts.json`</span> file in that
directory. You will see a list of entries like this:

<div class="highlight-json notranslate">

<div class="highlight">

    {
            "nid": "bconvo",
            "fallback_ttf": null,
            "fallback_size": 16,
            "default_color": "black",
            "outline_font": false,
            "palettes": {
                "black": [
                    [
                        40,
                        40,
                        40,
                        255
                    ],
                    [
                        184,
                        184,
                        184,
                        255
                    ]
                ]
            }
    }

</div>

</div>

In order to add your new font (let’s say you decided to download
<span class="pre">`fireflysung.ttf`</span>), you will change the
<span class="pre">`fallback_ttf`</span> field to
<span class="pre">`fireflysung.ttf`</span>. You may also need to play
with the <span class="pre">`fallback_size`</span> field in order to
ensure your font renders correctly: for example, the
<span class="pre">`PixelMPlus`</span> font comes in a 10-pixel and
12-pixel version, and will render very badly if you do not set the size
accordingly.

Once you change those two fields, you’re done!

</div>

<div id="special-notes" class="section">

## Special Notes<a href="Fonts-And-Languages.html#special-notes" class="headerlink"
title="Link to this heading"></a>

Some fonts in the game render with outlines. We support these as well!
However, it requires additional work for certain font-styles. You must
set the <span class="pre">`outline_font`</span> to
<span class="pre">`true`</span> for these fonts (although this has
already been set for the most common outlined fonts), and you must order
each color in the palette such that the primary text color is the first
RGBA value (in the example above, <span class="pre">`black`</span> has a
primary color of
<span class="pre">`40,`</span>` `<span class="pre">`40,`</span>` `<span class="pre">`40,`</span>` `<span class="pre">`255`</span>),
and the secondary text color is the second RGBA value (again, in the
example above, the secondary color is
<span class="pre">`184,`</span>` `<span class="pre">`184,`</span>` `<span class="pre">`184,`</span>` `<span class="pre">`255`</span>).
The primary will be used for the main text body, while the secondary
will be used as the outline.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Shop-Portraits.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Shop Portraits"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Custom-Components-And-Sprites.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Custom Components and Sprites">Next <span
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
