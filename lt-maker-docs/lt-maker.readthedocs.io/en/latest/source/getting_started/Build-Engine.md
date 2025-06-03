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

- <a href="index.html" class="reference internal">Getting Started</a>
  - <a href="Getting-Started.html" class="reference internal">Getting
    Started</a>
  - <a href="Python-Installation.html" class="reference internal">Necessary
    Installs (for Windows)</a>
  - <a href="making-a-basic-map.html" class="reference internal">The
    Basics</a>
  - <a href="Build-Engine.html#" class="current reference internal">Build
    Engine</a>
    - <a href="Build-Engine.html#non-python-process"
      class="reference internal">Non-Python Process</a>
    - <a href="Build-Engine.html#python-process"
      class="reference internal">Python Process</a>
    - <a href="Build-Engine.html#complete"
      class="reference internal">Complete!</a>

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
- [Getting Started](index.html)
- Build Engine
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/getting_started/Build-Engine.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="build-engine" class="section">

# Build Engine<a href="Build-Engine.html#build-engine" class="headerlink"
title="Link to this heading"></a>

If you want to be able to distribute an executable to others for release
and playtesting, this document will tell you how.

<div id="non-python-process" class="section">

## Non-Python Process<a href="Build-Engine.html#non-python-process" class="headerlink"
title="Link to this heading"></a>

If you are working with an executable version of the editor, follow this
process.

You can download the current version of the standalone engine from here:
https://gitlab.com/rainlash/lt-maker/-/jobs/artifacts/release/download?job=build_engine
(Download will start automatically!)

![GenericEngineProject](./media/2e9bf6173ec2cdea59c59b5a208f1f6c4c198298.png)

Unzip the download, stick your <span class="pre">`.ltproj`</span> file
in the folder <span class="pre">`lt_engine/lt_engine`</span> (should be
at the same level as <span class="pre">`app`</span>,
<span class="pre">`Include`</span>, etc.), and then you should be good
to go. Test that the engine works with your project, and then re-zip it
all up for distribution to others!

</div>

<div id="python-process" class="section">

## Python Process<a href="Build-Engine.html#python-process" class="headerlink"
title="Link to this heading"></a>

If are working with the Python version of the **Lex Talionis** engine,
the process is much simpler.

Open your project in the editor. Under the
<span class="pre">`File`</span> menu, click
<span class="pre">`Build`</span>` `<span class="pre">`Project`</span>.
This will ask you where to place the build, and will then build the
project in that location.

Afterwards, it will open the build folder.

</div>

<div id="complete" class="section">

## Complete\!<a href="Build-Engine.html#complete" class="headerlink"
title="Link to this heading"></a>

Your engine, ready for distribution, should be one directory above the
<span class="pre">`lt-maker`</span> directory, and named the same as
your project. Make sure to test it out first before delivering it to
others!

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="making-a-basic-map.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="The Basics"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="../editors/Editors-Overview.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Editors Overview">Next <span class="fa fa-arrow-circle-right"
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
