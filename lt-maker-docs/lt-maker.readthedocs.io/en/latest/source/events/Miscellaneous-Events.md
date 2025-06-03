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
  - <a href="Miscellaneous-Events.html#"
    class="current reference internal">Miscellaneous Events</a>
    - <a href="Miscellaneous-Events.html#death-events"
      class="reference internal">Death Events</a>
    - <a href="Miscellaneous-Events.html#fight-events"
      class="reference internal">Fight Events</a>
      - <a href="Miscellaneous-Events.html#basic-fight-quote"
        class="reference internal">Basic Fight Quote</a>
      - <a href="Miscellaneous-Events.html#id1" class="reference internal">Basic
        Fight Quote+</a>
      - <a href="Miscellaneous-Events.html#specific-fight-quote"
        class="reference internal">Specific Fight Quote</a>
      - <a href="Miscellaneous-Events.html#default-fight-quote"
        class="reference internal">Default Fight Quote</a>
    - <a href="Miscellaneous-Events.html#talk-conversations"
      class="reference internal">Talk Conversations</a>
    - <a href="Miscellaneous-Events.html#base-conversations"
      class="reference internal">Base Conversations</a>
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
- Miscellaneous Events
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/events/Miscellaneous-Events.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="miscellaneous-events" class="section">

# Miscellaneous Events<a href="Miscellaneous-Events.html#miscellaneous-events"
class="headerlink" title="Link to this heading"></a>

*last update v0.1*

<div id="death-events" class="section">

## Death Events<a href="Miscellaneous-Events.html#death-events" class="headerlink"
title="Link to this heading"></a>

The <span class="pre">`unit_death`</span> trigger fires whenever ANY
unit dies. You can create events that happen when a certain unit dies by
catching this trigger with the right condition.

For instance, to create a death quote for Eirika’s death and then cause
the player to game over:

Condition:
<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Eirika'`</span>
(We only want Eirika’s death to trigger this event)

Event Commands:

<div class="highlight-default notranslate">

<div class="highlight">

    u;Eirika;FarRight
    s;Eirika;Brother... I'm sorry
    expression;Eirika;CloseEyes
    r;Eirika
    remove_unit;Eirika
    lose_game

</div>

</div>

![ExampleDeathEvent](./media/1dd44f64327b1503544b9b64a60cc6b533e46a47.png)

</div>

<div id="fight-events" class="section">

## Fight Events<a href="Miscellaneous-Events.html#fight-events" class="headerlink"
title="Link to this heading"></a>

To create fight quotes that happen before fighting (for instance, before
fighting a boss), you can use the <span class="pre">`combat_end`</span>
trigger. It fires whenever ANY interaction between units happens. So you
will need to set up the right condition to make sure your event only
happens at the right time.

<div id="basic-fight-quote" class="section">

### Basic Fight Quote<a href="Miscellaneous-Events.html#basic-fight-quote" class="headerlink"
title="Link to this heading"></a>

When the boss has only one quote that they say the first time they enter
combat, you can check whether either unit is the boss. Make sure the
“Only Once” box is checked, otherwise this event will fire everytime the
boss is in combat.

<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Lyon'`</span>` `<span class="pre">`or`</span>` `<span class="pre">`unit2.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Lyon'`</span>

</div>

<div id="id1" class="section">

### Basic Fight Quote+<a href="Miscellaneous-Events.html#id1" class="headerlink"
title="Link to this heading"></a>

If the boss could be healed or otherwise supported by his fellows, you
will want to make sure that the boss only says his lines when fighting
your characters.

<span class="pre">`(unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Lyon'`</span>` `<span class="pre">`and`</span>` `<span class="pre">`unit2.team`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'player')`</span>` `<span class="pre">`or`</span>` `<span class="pre">`(unit.team`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'player'`</span>` `<span class="pre">`and`</span>` `<span class="pre">`unit2.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Lyon')`</span>

</div>

<div id="specific-fight-quote" class="section">

### Specific Fight Quote<a href="Miscellaneous-Events.html#specific-fight-quote"
class="headerlink" title="Link to this heading"></a>

If the boss has a specific fight quote for a specific unit, you can use
a special function to check whether the boss is in combat with that
unit.

<span class="pre">`check_pair('Lyon',`</span>` `<span class="pre">`'Eirika')`</span>

</div>

<div id="default-fight-quote" class="section">

### Default Fight Quote<a href="Miscellaneous-Events.html#default-fight-quote"
class="headerlink" title="Link to this heading"></a>

If the boss has a specific fight quote for certain units, but a default
fight quote used for all other combatants, you can use another function
to check whether the boss should be using the default. The second
argument to <span class="pre">`check_default`</span> should be a list of
the characters that the boss has a specific fight quote for.

<span class="pre">`check_default('Lyon',`</span>` `<span class="pre">`['Eirika',`</span>` `<span class="pre">`'Ephraim'])`</span>

For all of these events, make sure to check the “Only Once” box so they
only occur once (otherwise they’d get quite repetitive).

</div>

</div>

<div id="talk-conversations" class="section">

## Talk Conversations<a href="Miscellaneous-Events.html#talk-conversations"
class="headerlink" title="Link to this heading"></a>

The first step for talk conversations is to set up a potential talk
conversation. You tell the engine you’d like two characters to be able
to talk to one another.

I like to put my setup at the top of the
<span class="pre">`level_start`</span> event for the chapter, so I’d
write:

<div class="highlight-default notranslate">

<div class="highlight">

    add_talk;Eirika;Franz
    add_talk;Seth;Franz

</div>

</div>

This sets up a one way talk opportunity between Eirika and Franz, and
between Seth and Franz. The first character is the one that initiates
the conversation. If you want either character to be able to initiate,
just add it twice, but with the characters reversed.

<div class="highlight-default notranslate">

<div class="highlight">

    add_talk;Eirika;Franz
    add_talk;Franz;Eirika

</div>

</div>

Once that has been done, you can write the actual conversation that will
occur when the player actually selects **Talk**.

Create an event with the <span class="pre">`on_talk`</span> trigger, and
write the content of the conversation in the event. Since
<span class="pre">`on_talk`</span> fires for every talk, if you have
more than one talk conversation per level, you can specify which units
are the ones talking in the conditional. For a conversation that Seth
initiates with Franz:

<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Seth'`</span>` `<span class="pre">`and`</span>` `<span class="pre">`unit2.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Franz'`</span>

![ExampleTalkEvent](./media/95de3c4fd7e7a1df07bcb3c51b57522c06a344a9.png)

</div>

<div id="base-conversations" class="section">

## Base Conversations<a href="Miscellaneous-Events.html#base-conversations"
class="headerlink" title="Link to this heading"></a>

Base conversations are very similar to Talk conversations in overall
structure. You set up a base conversation by deciding on the name of the
base conversation that will appear in the Base Convos menu. Then at the
beginning of the level, use the
<span class="pre">`add_base_convo`</span> command to tell the engine
that this is an available base conversation

<span class="pre">`add_base_convo;Guard`</span>` `<span class="pre">`Duty`</span>

Create an event with the <span class="pre">`on_base_convo`</span>
trigger, and write the content of the conversation in the event. Since
<span class="pre">`on_base_convo`</span> fires for every base
conversation, you need to narrow it down to the specific base
conversations you’d like this event to fire for. For the
<span class="pre">`Guard`</span>` `<span class="pre">`Duty`</span> base
conversation, you set the condition to:

<span class="pre">`unit`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Guard`</span>` `<span class="pre">`Duty'`</span>

At the end of the base conversation, you can use the
<span class="pre">`ignore_base_convo`</span> or
<span class="pre">`remove_base_convo`</span> commands to either gray out
the base conversation in the menu, or remove it altogether.

![ExampleBaseEvent](./media/aa8febc53e23abf1e1176906293e9706b336dda2.png)

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Region-Events.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Region Events"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Test-Events.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Test Events">Next <span
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
