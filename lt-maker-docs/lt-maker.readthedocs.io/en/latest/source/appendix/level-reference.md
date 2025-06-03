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

- <a href="../editors/Editors-Overview.html"
  class="reference internal">Editors Overview</a>
- <a href="../editors/index.html" class="reference internal">Editors</a>

<span class="caption-text">Events:</span>

- <a href="../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../guides/Guides-Overview.html"
  class="reference internal">Guides Overview</a>
- <a href="../guides/index.html" class="reference internal">Guides</a>

<span class="caption-text">appendix:</span>

- <a href="Text-Formatting-Commands.html" class="reference internal">Text
  Formatting Commands</a>
- <a href="Item-Component-Reference.html" class="reference internal">Item
  Component Dictionary</a>
- <a href="Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="Special-Variables.html" class="reference internal">Special
  Variables</a>
- <a href="Special-Tags.html" class="reference internal">Special Tags</a>
- <a href="trigger-reference.html" class="reference internal">Event
  Triggers</a>
- <a href="Random-Seed-Mechanics.html" class="reference internal">Random
  Seed Mechanics</a>
- <a href="FAQ.html" class="reference internal">Frequently Asked
  Questions</a>
- <a href="Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="index.html" class="reference internal">Code Documentation</a>
  - <a href="game-state-reference.html" class="reference internal">GameState
    class</a>
  - <a href="level-reference.html#" class="current reference internal">Level
    Object</a>
    - <a href="level-reference.html#app.engine.objects.level.LevelObject"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject</code></span></a>
      - <a href="level-reference.html#app.engine.objects.level.LevelObject.nid"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.nid</code></span></a>
      - <a href="level-reference.html#app.engine.objects.level.LevelObject.name"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.name</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.tilemap"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.tilemap</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.bg_tilemap"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.bg_tilemap</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.party"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.party</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.music"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.music</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.objective"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.objective</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.units"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.units</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.regions"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.regions</code></span></a>
      - <a
        href="level-reference.html#app.engine.objects.level.LevelObject.ai_groups"
        class="reference internal"><span class="pre"><code
        class="docutils literal notranslate">LevelObject.ai_groups</code></span></a>
  - <a href="unit-reference.html" class="reference internal">UnitObject
    class</a>
  - <a href="region-reference.html" class="reference internal">RegionObject
    class</a>
  - <a href="region-reference.html#regionprefab-class"
    class="reference internal">RegionPrefab class</a>
  - <a href="party-reference.html" class="reference internal">Party
    Object</a>
  - <a href="unit_funcs-reference.html" class="reference internal">Unit
    Helper Functions</a>
  - <a href="item_funcs-reference.html" class="reference internal">Item
    Helper Functions</a>
  - <a href="query_funcs-reference.html" class="reference internal">Useful
    Functions</a>
  - <a href="constants-reference.html"
    class="reference internal">Constants</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- [Code Documentation](index.html)
- Level Object
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/level-reference.rst"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="level-object" class="section">

# Level Object<a href="level-reference.html#level-object" class="headerlink"
title="Link to this heading"></a>

*<span class="pre">class</span><span class="w"> </span>*<span class="sig-prename descclassname"><span class="pre">app.engine.objects.level.</span></span><span class="sig-name descname"><span class="pre">LevelObject</span></span><a href="level-reference.html#app.engine.objects.level.LevelObject"
class="headerlink" title="Link to this definition"></a>  
Representation of a Level or Chapter in the engine. Contains information
about the tilemap of the level, which is the chapter’s main party, what
music should exist for each phase, etc.

<span class="sig-name descname"><span class="pre">nid</span></span><a href="level-reference.html#app.engine.objects.level.LevelObject.nid"
class="headerlink" title="Link to this definition"></a>  
The unique ID for the level

Type<span class="colon">:</span>  
NID

<span class="sig-name descname"><span class="pre">name</span></span><a href="level-reference.html#app.engine.objects.level.LevelObject.name"
class="headerlink" title="Link to this definition"></a>  
The name of the level (displayed in the Chapter Title card)

Type<span class="colon">:</span>  
str

<span class="sig-name descname"><span class="pre">tilemap</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.tilemap"
class="headerlink" title="Link to this definition"></a>  
The current tilemap for the level

Type<span class="colon">:</span>  
TileMapObject

<span class="sig-name descname"><span class="pre">bg_tilemap</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.bg_tilemap"
class="headerlink" title="Link to this definition"></a>  
The current background tilemap for the level

Type<span class="colon">:</span>  
TileMapObject

<span class="sig-name descname"><span class="pre">party</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.party"
class="headerlink" title="Link to this definition"></a>  
The chapter’s main party

Type<span class="colon">:</span>  
NID

<span class="sig-name descname"><span class="pre">music</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.music"
class="headerlink" title="Link to this definition"></a>  
Keys are the phase, value is the song name

Type<span class="colon">:</span>  
dict

<span class="sig-name descname"><span class="pre">objective</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.objective"
class="headerlink" title="Link to this definition"></a>  
The objective text

Type<span class="colon">:</span>  
dict

<span class="sig-name descname"><span class="pre">units</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.units"
class="headerlink" title="Link to this definition"></a>  
(Data\[UnitObject\]): Database of the units in the level

<span class="sig-name descname"><span class="pre">regions</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.regions"
class="headerlink" title="Link to this definition"></a>  
(Data\[RegionObject\]): Database of regions in the level

<span class="sig-name descname"><span class="pre">ai_groups</span></span><a
href="level-reference.html#app.engine.objects.level.LevelObject.ai_groups"
class="headerlink" title="Link to this definition"></a>  
Database of AI Groups in the level

Type<span class="colon">:</span>  
Data\[AIGroupObject\]

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="game-state-reference.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="GameState class"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="unit-reference.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="UnitObject class">Next <span
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
