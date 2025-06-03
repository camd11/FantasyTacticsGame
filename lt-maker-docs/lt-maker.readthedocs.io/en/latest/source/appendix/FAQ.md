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
- <a href="FAQ.html#" class="current reference internal">Frequently Asked
  Questions</a>
  - <a href="FAQ.html#audio" class="reference internal">Audio</a>
    - <a href="FAQ.html#my-music-is-playing-at-a-different-pitch"
      class="reference internal">My music is playing at a different pitch?</a>
    - <a href="FAQ.html#does-lt-support-tmx-map-files"
      class="reference internal">Does LT support <span class="pre"><code
      class="docutils literal notranslate">.tmx</code></span> map files?</a>
    - <a href="FAQ.html#how-do-i-soft-reset-the-game"
      class="reference internal">How do I soft reset the game?</a>
    - <a
      href="FAQ.html#can-i-stop-certain-tracks-songs-from-showing-up-in-the-sound-room"
      class="reference internal">Can I stop certain tracks/songs from showing
      up in the Sound Room?</a>
- <a href="Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="index.html" class="reference internal">Code Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- Frequently Asked Questions
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/FAQ.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="frequently-asked-questions" class="section">

# Frequently Asked Questions<a href="FAQ.html#frequently-asked-questions" class="headerlink"
title="Link to this heading"></a>

<div id="audio" class="section">

## Audio<a href="FAQ.html#audio" class="headerlink"
title="Link to this heading"></a>

<div id="my-music-is-playing-at-a-different-pitch" class="section">

### My music is playing at a different pitch?<a href="FAQ.html#my-music-is-playing-at-a-different-pitch"
class="headerlink" title="Link to this heading"></a>

LT is configured at 44100 Hz. Most likely, your music was sampled at
48000 Hz. You can use
<a href="https://superuser.com/questions/420531/audacity-resampling"
class="reference external">Audacity</a> to resample your track to the
appropriate frequency.

</div>

<div id="does-lt-support-tmx-map-files" class="section">

### Does LT support <span class="pre">`.tmx`</span> map files?<a href="FAQ.html#does-lt-support-tmx-map-files" class="headerlink"
title="Link to this heading"></a>

No. LT uses <span class="pre">`.png`</span> files for the graphical
component of its maps, and uses internal data for terrain data.

</div>

<div id="how-do-i-soft-reset-the-game" class="section">

### How do I soft reset the game?<a href="FAQ.html#how-do-i-soft-reset-the-game" class="headerlink"
title="Link to this heading"></a>

Press whatever keys/buttons are mapped to your SELECT, BACK, and START
actions at the same time. By default, this is “X” + “Z” + “S” on the
keyboard.

</div>

<div id="can-i-stop-certain-tracks-songs-from-showing-up-in-the-sound-room"
class="section">

### Can I stop certain tracks/songs from showing up in the Sound Room?<a
href="FAQ.html#can-i-stop-certain-tracks-songs-from-showing-up-in-the-sound-room"
class="headerlink" title="Link to this heading"></a>

Any <span class="pre">`SongPrefab`</span> in the editor with a title
that starts with an underscore (<span class="pre">`_`</span>) will be
ignored in the Sound Room. This makes it useful for things like the
prolonged Chapter Sound, ambience tracks, etc. to be excluded from the
Sound Room.

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Random-Seed-Mechanics.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Random Seed Mechanics"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Contributing_to_the_LTWiki.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Contributing to the LTWiki">Next <span
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
