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

- <a href="index.html" class="reference internal">Events</a>
  - <a href="Event-Overview.html" class="reference internal">Event
    Overview</a>
  - <a href="Conditionals.html" class="reference internal">Conditionals</a>
  - <a href="Region-Events.html" class="reference internal">Region
    Events</a>
  - <a href="Miscellaneous-Events.html"
    class="reference internal">Miscellaneous Events</a>
  - <a href="Test-Events.html" class="reference internal">Test Events</a>
  - <a href="Python-Eventing.html" class="reference internal">Python
    Eventing</a>
  - <a href="Event-Debugger.html#"
    class="current reference internal">Debugger</a>

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
- [Events](index.html)
- Debugger
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/events/Event-Debugger.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="debugger" class="section">

# Debugger<a href="Event-Debugger.html#debugger" class="headerlink"
title="Link to this heading"></a>

The debug screen is accessible via the <span class="pre">`debug`</span>
menu item (in the on-map option menu - the one which normally contains
<span class="pre">`UNITS`</span>, <span class="pre">`OPTIONS`</span>,
<span class="pre">`END`</span>` `<span class="pre">`TURN`</span>, etc.),
if launching the game in debug mode.

If not, the debug screen is still accessible via the same menu, but the
player must enter the following code, using directional input keys, to
open it:
<span class="pre">`UP,`</span>` `<span class="pre">`UP,`</span>` `<span class="pre">`DOWN,`</span>` `<span class="pre">`DOWN,`</span>` `<span class="pre">`LEFT,`</span>` `<span class="pre">`RIGHT,`</span>` `<span class="pre">`LEFT,`</span>` `<span class="pre">`RIGHT`</span>.

![DebugOption](./media/5a4757d3221c4d804af4b8cea27896cacd243285.png)
![DebugMenu](./media/927b68f5f8aa349b13d09873c79d1e9d674a4087.png)

The debug screen calls a miniature event when you enter a command. That
event has access to:

> <div>
>
> - **unit**: the unit under the cursor
>
> - **position**: the position under the cursor
>
> </div>

You can see these values displayed on the top right corner of your
screen, as seen in the above screenshot. No unit will be displayed when
not hovering over a unit.

While in this menu, you may type in any event command and hit
<span class="pre">`Enter`</span> to have that event command be
immediately executed. Try out
<span class="pre">`give_item;Eirika;Vulnerary`</span> as an example.

To exit the Debug menu, press <span class="pre">`Enter`</span> while
there is no text in the debug command line. Do not press
<span class="pre">`Escape`</span> or your game window will close
entirely.

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Python-Eventing.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Python Eventing"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="../guides/Guides-Overview.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Guides Overview">Next <span class="fa fa-arrow-circle-right"
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
