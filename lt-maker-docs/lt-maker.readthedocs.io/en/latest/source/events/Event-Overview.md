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
  - <a href="Event-Overview.html#" class="current reference internal">Event
    Overview</a>
    - <a href="Event-Overview.html#triggers"
      class="reference internal">Triggers</a>
    - <a href="Event-Overview.html#format"
      class="reference internal">Format</a>
    - <a href="Event-Overview.html#trigger-list"
      class="reference internal">Trigger List</a>
    - <a href="Event-Overview.html#conditions"
      class="reference internal">Conditions</a>
    - <a href="Event-Overview.html#event-commands"
      class="reference internal">Event Commands</a>
  - <a href="Conditionals.html" class="reference internal">Conditionals</a>
  - <a href="Region-Events.html" class="reference internal">Region
    Events</a>
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
- Event Overview
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/events/Event-Overview.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="event-overview" class="section">

<span id="eventoverview"></span>

# Event Overview<a href="Event-Overview.html#event-overview" class="headerlink"
title="Link to this heading"></a>

*last updated v0.1*

Events are a powerful tool for any game designer, allowing you to
implement unique dialogue, cutscenes, and action in your game.

An event consists of four things:

![Screenshot of event editor with these sections
labeled](./media/855f564f050aff2b92ef83ed929f8b846a389052.png)

1.  A unique **name** so that it can be uniquely identified in the
    engine

2.  A **trigger** that causes the event to activate

3.  A **condition** that is checked by the event when it triggers

4.  A list of event **commands** to run

Once a trigger has been fired by the engine, all events that subscribe
to that trigger are activated. The event’s condition is checked, and if
true, that event will occur. The event will run through it’s list of
event commands in order until complete, and the engine will then return
to its normal processing.

<div id="triggers" class="section">

## Triggers<a href="Event-Overview.html#triggers" class="headerlink"
title="Link to this heading"></a>

There are several default triggers that will fire when a certain state
is reached in the engine. The events you create can catch these triggers
and activate when appropriate.

Event Regions can create their own triggers which can also be caught by
the event system. See
<a href="Region-Events.html" class="reference internal"><span
class="doc std std-doc">Region Events</span></a> for more information.

</div>

<div id="format" class="section">

## Format<a href="Event-Overview.html#format" class="headerlink"
title="Link to this heading"></a>

<span class="pre">`trigger_name`</span>
{<span class="pre">`extra`</span>` `<span class="pre">`available`</span>` `<span class="pre">`inputs`</span>}:
Description and potential use case.

</div>

<div id="trigger-list" class="section">

## Trigger List<a href="Event-Overview.html#trigger-list" class="headerlink"
title="Link to this heading"></a>

![Screenshot of event editor trigger
list](./media/be4012f6afdf3b28bbea0782b9067215b4cdba9b.png)

1.  <span class="pre">`level_start`</span>: This trigger fires at the
    very beginning of the chapter. Useful for introductory dialogue or
    additional level setup.

2.  <span class="pre">`level_end`</span>: This trigger fires at the end
    of the chapter. Useful for ending chapter dialogue.

3.  <span class="pre">`turn_change`</span>: This triggers fires right
    before the turn changes to the player’s turn. Useful for dialogue or
    reinforcements.

4.  <span class="pre">`enemy_turn_change`</span>: This trigger fires
    right before the turn changes to the enemy team’s turn. Useful for
    “same turn reinforcements” and other evil deeds.

5.  <span class="pre">`enemy2_turn_change`</span>: This trigger fires
    right before the turn changes to the enemy2 team’s turn.

6.  <span class="pre">`other_turn_change`</span>: This trigger fires
    right before the turn changes to the other team’s turn.

7.  <span class="pre">`unit_death`</span>
    {<span class="pre">`unit`</span>,
    <span class="pre">`position`</span>}: This trigger fires whenever
    *any* unit dies (this includes generic units). Useful for death
    quotes.

8.  <span class="pre">`unit_wait`</span>
    {<span class="pre">`unit`</span>,
    <span class="pre">`position`</span>}: This trigger fires whenever a
    unit waits.

9.  <span class="pre">`unit_select`</span>
    {<span class="pre">`unit`</span>,
    <span class="pre">`position`</span>}: This trigger fires when the
    player selects a unit.

10. <span class="pre">`unit_level_up`</span>
    {<span class="pre">`unit`</span>}: This trigger fires right after a
    unit levels up.

11. <span class="pre">`during_unit_level_up`</span>
    {<span class="pre">`unit`</span>, <span class="pre">`unit2`</span>}:
    This trigger fires when the unit levels up, right after the level up
    screen shows what stats have increased.

12. <span class="pre">`unit_weapon_rank_up`</span>
    {<span class="pre">`unit`</span>, <span class="pre">`item`</span>,
    <span class="pre">`position`</span>}: This trigger fires when unit’s
    weapon rank increases. Useful for Three Houses-like weapon ranks
    adding spells or skills on rank up.

13. <span class="pre">`combat_start`</span>
    {<span class="pre">`unit`</span>, <span class="pre">`unit2`</span>,
    <span class="pre">`item`</span>,
    <span class="pre">`position`</span>}: This trigger fires at the
    beginning of combat. Useful for boss fight quotes.

14. <span class="pre">`combat_end`</span>
    {<span class="pre">`unit`</span>, <span class="pre">`unit2`</span>,
    <span class="pre">`item`</span>,
    <span class="pre">`position`</span>}: This trigger fires at the end
    of combat. Useful for checking win or loss conditions.

15. <span class="pre">`on_talk`</span> {<span class="pre">`unit`</span>,
    <span class="pre">`unit2`</span>,
    <span class="pre">`position`</span>}: This trigger fires when two
    units “Talk” to one another.

16. <span class="pre">`on_support`</span>
    {<span class="pre">`unit`</span>, <span class="pre">`unit2`</span>,
    <span class="pre">`item`</span>,
    <span class="pre">`position`</span>}: This trigger fires when two
    units “Support” with one another. For this trigger,
    <span class="pre">`item`</span> contains the nid of the support rank
    (‘C’, ‘B’, ‘A’, or ‘S’, for example).

17. <span class="pre">`on_base_convo`</span>
    {<span class="pre">`unit`</span>}: This trigger fires when the
    player selects a base conversation to view. For this trigger,
    <span class="pre">`unit`</span> contains the title of the base
    conversation.

18. <span class="pre">`on_turnwheel`</span>: This trigger fires after
    the turnwheel is used.

</div>

<div id="conditions" class="section">

## Conditions<a href="Event-Overview.html#conditions" class="headerlink"
title="Link to this heading"></a>

Imagine you want an event to trigger when a specific unit dies. As
stated above, the <span class="pre">`on_unit_death`</span> trigger will
fire whenever **any** unit dies. So, if you create an event that
triggers on unit death, by default it will trigger on all deaths,
including enemy generics.

Setting a Condition allows you to limit the event to activate to only
when the Condition is true.

![Screenshot of example
condition](./media/2ca9a613deceab3022a29109429acc7b895ee7c8.png)

The <span class="pre">`on_unit_death`</span> trigger supplys the unit
that died under the name <span class="pre">`unit`</span>. So we can
simply enter
<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Eirika'`</span>
in the Condition box for our event. Now, if the unit that died had an
nid of <span class="pre">`Eirika`</span>, the event will activate.
Otherwise, the event will be ignored.

More information on what can be checked within a condition can be found
here: <a href="Conditionals.html" class="reference internal"><span
class="doc std std-doc">Conditionals</span></a>

</div>

<div id="event-commands" class="section">

<span id="eventcommands"></span>

## Event Commands<a href="Event-Overview.html#event-commands" class="headerlink"
title="Link to this heading"></a>

Event commands are written by you, the game designer, in order to
accomplish your goal for an event. For instance, if you want Eirika to
appear and say
<span class="pre">`Oh`</span>` `<span class="pre">`no!`</span> when she
dies, you could setup a <span class="pre">`on_unit_death`</span> event
with the condition
<span class="pre">`unit.nid`</span>` `<span class="pre">`==`</span>` `<span class="pre">`'Eirika'`</span>
and the text:

<div class="highlight-default notranslate">

<div class="highlight">

    add_portrait;Eirika;Right
    speak;Eirika;Oh no!
    remove_portrait;Eirika

</div>

</div>

There are many event commands available, and it is not expected that you
will remember them all off the top of your head. A searchable index of
event commands is available within the event editor.

![Screenshot of list of event
commands](./media/942faedbfef54cef7c4cc4175f09903de851aca1.png)

Feel free to check out the events that already exist in the default
project or the Lion Throne project. They can and should be used freely
as reference.

Also,
<a href="Miscellaneous-Events.html" class="reference internal"><span
class="doc std std-doc">Miscellaneous Events</span></a> contains
additional information on how to set up certain kinds of events.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="index.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="Events"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Conditionals.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Conditionals">Next <span
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
