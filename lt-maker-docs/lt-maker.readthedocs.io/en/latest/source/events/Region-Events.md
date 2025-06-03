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
  - <a href="Region-Events.html#" class="current reference internal">Region
    Events</a>
    - <a href="Region-Events.html#villages-houses"
      class="reference internal">Villages / Houses</a>
    - <a href="Region-Events.html#shops-armories"
      class="reference internal">Shops / Armories</a>
    - <a href="Region-Events.html#seize" class="reference internal">Seize</a>
    - <a href="Region-Events.html#escape"
      class="reference internal">Escape</a>
    - <a href="Region-Events.html#switch"
      class="reference internal">Switch</a>
    - <a href="Region-Events.html#chest-door" class="reference internal">Chest
      / Door</a>
  - <a href="Miscellaneous-Events.html"
    class="reference internal">Miscellaneous Events</a>
  - <a href="Test-Events.html" class="reference internal">Test Events</a>
  - <a href="Python-Eventing.html" class="reference internal">Python
    Eventing</a>
  - <a href="Event-Debugger.html" class="reference internal">Debugger</a>

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
- Region Events
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/events/Region-Events.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="region-events" class="section">

# Region Events<a href="Region-Events.html#region-events" class="headerlink"
title="Link to this heading"></a>

*last update v0.1*

![RegionEventPane](./media/1f3be7bdb27d0d68535a07bd384ac40886c521a5.png)

Event regions are a flexible way for the game designer to give the
player additional actions their characters can perform while on specific
regions of the map. With event regions, you can implement visiting
villages, visiting shops, seizing thrones, escaping the map, flicking
switches, and unlocking chests or doors, and much more.

The condition box in the Region pane allows you to specify which units
will be able to access that region’s action. For instance, if you only
want Eirika to be able to Seize, you can set the condition to
<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Eirika'`</span>.

<div id="villages-houses" class="section">

## Villages / Houses<a href="Region-Events.html#villages-houses" class="headerlink"
title="Link to this heading"></a>

![VillageRegion](./media/29129a844ec2dff4a350d8488331132e5c483822.png)

![VillageRegionEvent](./media/0ced857ea01e2d9a9fe2ba907ddfe3011e58a3dc.png)

The condition in the Event Editor specifies *which* region this event
corresponds to.

A normal visit event looks something like this

<div class="highlight-default notranslate">

<div class="highlight">

    transition;Close
    change_background;House
    transition;Open
    add_portrait;{unit};Left;no_block
    add_portrait;Man;Right
    speak;Man;You'll never defeat Gharnef!
    remove_portrait;{unit};no_block
    remove_portrait;Man
    transition;Close
    change_background
    transition;Open
    give_item;{unit};Red Gem
    has_attacked;{unit}

</div>

</div>

The <span class="pre">`has_attacked`</span> command at the end is
important if you don’t want the unit to be able to move or attack after
visiting the village

</div>

<div id="shops-armories" class="section">

## Shops / Armories<a href="Region-Events.html#shops-armories" class="headerlink"
title="Link to this heading"></a>

![ShopRegion](./media/ef50abbca650e1d58f6ec7aa686a6846cb6eff5e.png)

![ShopRegionEvent](./media/e77ea36f83f0e34312d72e04e4d1c5cdfdc49bc5.png)

A normal shop event looks something like this

<div class="highlight-default notranslate">

<div class="highlight">

    transition;Close
    music;Armory Music
    shop;{unit};Iron Sword,Iron Lance,Iron Axe
    transition;Open

</div>

</div>

The <span class="pre">`shop`</span> command handles all the intricacies
of shopping for you, including making sure the unit can’t move back
after making a transaction.

</div>

<div id="seize" class="section">

## Seize<a href="Region-Events.html#seize" class="headerlink"
title="Link to this heading"></a>

A normal seize event looks something like this

<div class="highlight-default notranslate">

<div class="highlight">

    win_game

</div>

</div>

</div>

<div id="escape" class="section">

## Escape<a href="Region-Events.html#escape" class="headerlink"
title="Link to this heading"></a>

![EscapeRegion](./media/928f0b80b7ef78b2eb3c838831ce54462a245293.png)

![EscapeRegionEvent](./media/49ec3a60cd800fa9274703493afb35c77e925c1c.png)

A normal escape event looks something like this

<div class="highlight-default notranslate">

<div class="highlight">

    remove_unit;{unit}
    wait;400
    if;not any(unit.team == 'player' for unit in game.units if unit.position)
        win_game
    end

</div>

</div>

</div>

<div id="switch" class="section">

## Switch<a href="Region-Events.html#switch" class="headerlink"
title="Link to this heading"></a>

![SwitchRegion](./media/ac9b89eba34689bac7599fbfb897987adaeb135d.png)

![SwitchRegionEvent](./media/89d925f819a2a38be319c863289efb371cf7f2cc.png)

You can increment a counter every time a switch event is processed if
you want to keep track

</div>

<div id="chest-door" class="section">

## Chest / Door<a href="Region-Events.html#chest-door" class="headerlink"
title="Link to this heading"></a>

![ChestRegion](./media/50c5148b4c7491f76a103a81327a8c3c3c1a4b66.png)

![ChestRegionEvent](./media/511a3efaed0e512edee99f5e36bd5ffb4ec6b813.png)

A normal chest event looks something like this

<div class="highlight-default notranslate">

<div class="highlight">

    show_layer;Chest1
    unlock;{unit}
    give_money;2000
    has_attacked;{unit}

</div>

</div>

The unlock command handles spending the unlockable you used to unlock
the chest (whether that be by a key, lockpick, or with locktouch)

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Conditionals.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Conditionals"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Miscellaneous-Events.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Miscellaneous Events">Next <span
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
