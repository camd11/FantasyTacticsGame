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
    - <a href="Combat-Animations-Editor.html"
      class="reference internal">Combat Animations Editor</a>
    - <a href="Tilemaps-Editor.html#"
      class="current reference internal">Tilemaps Editor</a>
      - <a href="Tilemaps-Editor.html#importing"
        class="reference internal">Importing</a>
      - <a href="Tilemaps-Editor.html#layers"
        class="reference internal">Layers</a>
      - <a href="Tilemaps-Editor.html#foreground-layers"
        class="reference internal">Foreground Layers</a>
      - <a href="Tilemaps-Editor.html#autotiles"
        class="reference internal">Autotiles</a>
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
- Tilemaps Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/resource-editors/Tilemaps-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="tilemaps-editor" class="section">

# Tilemaps Editor<a href="Tilemaps-Editor.html#tilemaps-editor" class="headerlink"
title="Link to this heading"></a>

*last updated 2024-11-13*

<div id="importing" class="section">

## Importing<a href="Tilemaps-Editor.html#importing" class="headerlink"
title="Link to this heading"></a>

**Tilesets** can be imported from any .png image that is some multiple
of 16x16 in size. It is not possible to import **tilemaps** in this way,
but it is possible to import a .png of a tilemap as a tileset and then
use that tileset to create a map by selecting the entire tileset and
applying it to the map.

![Tilesetting](./media/4336d793cee9b77da6c392cd70cb518674eb9eb9.png)

</div>

<div id="layers" class="section">

## Layers<a href="Tilemaps-Editor.html#layers" class="headerlink"
title="Link to this heading"></a>

Layers in the LT tilemap editor function as both image editing layers
and FEGBA tile changes.

Layers are displayed in *inverse* order of priority; the base layer is
at the top, while the top-most layer is at the bottom, as below.

![Layers](./media/3be86df146eaca4e3213b24a3e546388ca540d79.png)
![LayersAgain](./media/8f0436e8d1d9208faacf23922d2ac191811e0c61.png)

Note that checking/unchecking layers in the tilemap editor does not do
anything in-game, and is solely meant for visual aid while editing
tilemaps. Only the base layer is visible by default in-game; use the
<span class="pre">`show_layer`</span> and
<span class="pre">`hide_layer`</span> event commands to toggle layers as
needed.

If terrain is missing for a layer, it will default to using the top-most
non-empty terrain data. A complete lack of terrain will default to the
top terrain type in the Terrain editor, NID 0, name ‘–’ in
default.ltproj.

</div>

<div id="foreground-layers" class="section">

## Foreground Layers<a href="Tilemaps-Editor.html#foreground-layers" class="headerlink"
title="Link to this heading"></a>

Pressing the foreground button pictured below while a layer is selected
will make that layer a foreground layer. You can tell which layers are
already foreground layers by their blue text.

![Foreground](./media/cf68e7adb651725a330fa90b43661acf7621e2d1.png)

Foreground layers are displayed above units on the map.

</div>

<div id="autotiles" class="section">

## Autotiles<a href="Tilemaps-Editor.html#autotiles" class="headerlink"
title="Link to this heading"></a>

<div id="autotiles-how-do-they-work" class="section">

### Autotiles, how do they work???<a href="Tilemaps-Editor.html#autotiles-how-do-they-work"
class="headerlink" title="Link to this heading"></a>

In the GBA games, water features such as rivers, streams, and seas all
have moving sprites to effect the illusion that there really is running
water in those pixel streams.

![AutotileExample](./media/5966988f99fd34ed69607650dc5d0ebac01153d5.gif)

Every 29 frames, the sprite for the tile of water is replaced by a
slightly different predetermined tile. This is done 16 times and then
loops back around to the start. This technique is called Autotiles.

Some autotiles are included in the engine by default for your use. All
autotiles are stored in the
<span class="pre">`resources/autotile_templates`</span> directory. Not
every autotile used by the GBA Fire Emblem games is available by
default. LT-maker welcomes additional autotile template contributions if
you have them or can generate them.

![AutotileTemplateExample](./media/616241ba216b6863627c89361109fb1a028c40cb.png)

Each tile in the autotile template must be duplicated 15 more times as
you go horizontally. The engine will take these templates and generate
an autotile tilemap for your own tilemaps, and then render that autotile
tilemap every 29 frames.

</div>

<div id="using-autotiles" class="section">

### Using Autotiles<a href="Tilemaps-Editor.html#using-autotiles" class="headerlink"
title="Link to this heading"></a>

You can add autotiles to your own maps by entering the Tilemap editor.
There are two buttons on the bottom right that will automatically
generate autotile tilemaps for your tilemaps.

![AutotileTilemapEditor](./media/dda61ecb466a4433f55c1072a06d578db8c726a0.png)

In general, you should use the left button of the two. When pressed, the
editor will analyze your existing tilemap and then search through every
tile in the autotile templates to determine if any of them match the
tiles you are using in the tilemap.

The tiles do not need to match in color, but they need to match in
pattern. Once matched, the autotile template tile will be palette
shifted to match your existing tiles.

![ExampleAutotileMatch](./media/2061ef97fa116cbc81315d908d32f0ead48c5acf.png)

If you instead click the right button of the two, the same occurs,
except the final step where the autotile template tile is palette
shifted to match existing tiles does not occur. The autotile template
tile will keep its original color palette.

</div>

<div id="adding-your-own-autotile-templates" class="section">

### Adding your own Autotile Templates<a href="Tilemaps-Editor.html#adding-your-own-autotile-templates"
class="headerlink" title="Link to this heading"></a>

You can use autotiles for more than just water. They can be used for
things like fire flickering on torches, or trees moving in the wind, or
whatever your heart desires.

You can add your own autotile templates easily.

1.  Make sure the editor is off.

2.  Create an image with your autotiles in the same format as existing
    autotile templates (each tile’s changes in a row horizontally).

3.  Place that image in the
    <span class="pre">`resources/autotile_templates`</span> directory of
    your engine.

Now your autotiles will be ready for use once you start the editor up.

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Combat-Animations-Editor.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Combat Animations Editor"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Sounds-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Sounds Editor">Next <span
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
