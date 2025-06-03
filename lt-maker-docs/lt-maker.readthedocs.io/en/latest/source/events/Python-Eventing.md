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
  - <a href="Python-Eventing.html#"
    class="current reference internal">Python Eventing</a>
    - <a href="Python-Eventing.html#why-use-python-eventing"
      class="reference internal">Why use Python Eventing?</a>
    - <a href="Python-Eventing.html#python-event-sample"
      class="reference internal">Python Event Sample</a>
      - <a href="Python-Eventing.html#dialogue"
        class="reference internal">Dialogue</a>
      - <a href="Python-Eventing.html#for-loop" class="reference internal">For
        Loop</a>
      - <a href="Python-Eventing.html#variables"
        class="reference internal">Variables</a>
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
- Python Eventing
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/events/Python-Eventing.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="python-eventing" class="section">

<span id="pythoneventing"></span>

# Python Eventing<a href="Python-Eventing.html#python-eventing" class="headerlink"
title="Link to this heading"></a>

*last updated v0.1*

*If you haven’t read <a href="Event-Overview.html#eventoverview"
class="reference internal"><span
class="std std-ref">Event-Overview</span></a> yet, please do so before
reading this article.*

While the event script can be written with the traditional Event
Commands (as demonstrated in the
<a href="Event-Overview.html#eventcommands"
class="reference internal"><span class="std std-ref">Event Commands
Section</span></a>), the intrepid scripter can take advantage of Python
syntax to achieve more sophisticated functionality. Rather than using a
simplified custom syntax, the Python Eventing engine allows you to write
scripts in fully integrated Python.

<div id="why-use-python-eventing" class="section">

## Why use Python Eventing?<a href="Python-Eventing.html#why-use-python-eventing"
class="headerlink" title="Link to this heading"></a>

For the casual user, there is no real advantage (or disadvantage) in
doing so.

For users that use eventing to implement abilities, do calculations, and
so on, the advantages are numerous.

For example: working with variables and doing calculations in original
command form is clumsy, as there are no intuitive semantics for
assigning and accessing non-primitive variables. Moreover, Event Script
does not distinguish well between string objects and non-string objects,
leading to situations like these:

<div class="highlight-default notranslate">

<div class="highlight">

    game_var;seen_maps;v('seen_maps') + [v('next')]
    game_var;next_reward;'{v:the_reward}'

</div>

</div>

Which are difficult to parse - <span class="pre">`[v('next')]`</span> is
a variable name wrapped in a string wrapped inside a variable getter
wrapped inside a list wrapper, placed as the argument of a variable
setter. <span class="pre">`'{v:the_reward}'`</span> is a variable string
getter wrapped inside a string. These are needless levels of
indirection. In Python Eventing, this would be rendered as:

<div class="highlight-default notranslate">

<div class="highlight">

    seen_maps.append(next)
    next_reward = the_reward

</div>

</div>

Ultimately, Python Eventing is a cleaner and more maintainable method of
writing events.

Python Eventing also gives you access to all standard Python functions,
notably including list operations. You can sort lists, create lists,
append to lists, and so forth, that are difficult to impossible to do in
traditional event script.

</div>

<div id="python-event-sample" class="section">

## Python Event Sample<a href="Python-Eventing.html#python-event-sample" class="headerlink"
title="Link to this heading"></a>

For the most part, there are only three things that one needs to know
about Python Eventing.

1.  To have a script use the Python Eventing engine, you must include
    the text <span class="pre">`#pyev1`</span> at the top.

2.  There are three important characters when writing an LT command.
    <span class="pre">`$`</span> at the beginning of a line indicates
    that you’re calling an event command. ` ` - a space - is the
    delimiter for event command arguments. Finally,
    <span class="pre">`,`</span> - the comma - ends the command and
    delimits the beginning of the section of flags. For example, to add
    a portrait, instead of the event script
    <span class="pre">`add_portrait;Seth;left;no_block`</span>, you
    might do
    <span class="pre">`$add_portrait`</span>` `<span class="pre">`"Seth"`</span>` `<span class="pre">`"left",`</span>` `<span class="pre">`no_block`</span>.
    You can use parenthesis if you need to add spaces to an argument:
    <span class="pre">`$add_portrait`</span>` `<span class="pre">`("Seth"`</span>` `<span class="pre">`+`</span>` `<span class="pre">`"_hurt")`</span>` `<span class="pre">`"left",`</span>` `<span class="pre">`no_block`</span>.

3.  All lines that do not begin with a <span class="pre">`$`</span>
    character will be parsed as normal Python.

Here are some snippets that illustrate the appearance and syntax of
Python Events.

<div id="dialogue" class="section">

### Dialogue<a href="Python-Eventing.html#dialogue" class="headerlink"
title="Link to this heading"></a>

The following event snippet creates a SpeakStyle - a collection of
formatting hints for a speak command. In this case, it indicates that
the <span class="pre">`eirika`</span> style refers to a style using
<span class="pre">`Eirika`</span> as the speaker, and has a text box 3
lines tall.

> <div>
>
> **N.B.** The <span class="pre">`say`</span> command appears to spread
> out over five lines. You can format individual commands across
> multiple lines using line breaks - usually entered via the
> <span class="pre">`Shift-Enter`</span> key combination. You **cannot**
> use normal newlines (input via the <span class="pre">`Enter`</span>
> key) in the middle of event commands.
>
> </div>

<div class="highlight-python notranslate">

<div class="highlight">

    #pyev1

    eirika = SpeakStyle('eirika_speak_style', speaker="Eirika", num_lines=3)

    $add_portrait eirika "FarLeft" ExpressionList=["Smile", "CloseEyes"] Slide="right"
    $say eirika "Four score and seven years ago"
                "our fathers brought forth, upon this continent,"
                "a new nation, conceived in liberty,"
                "and dedicated to the proposition"
                "that all men are created equal." FontColor="green"
    $remove_portrait eirika

</div>

</div>

</div>

<div id="for-loop" class="section">

### For Loop<a href="Python-Eventing.html#for-loop" class="headerlink"
title="Link to this heading"></a>

The following event snippet spawns 5 civilians near the unit
<span class="pre">`Bone`</span>. For those familiar with Python, this is
an ordinary for loop. It’s important to note that you can put most
normal event commands inside Python for loops as well.

<div class="highlight-python notranslate">

<div class="highlight">

    #pyev1
    for i in range(5):
        $make_generic str(i) "Citizen" 1 "player"
        $add_unit str(i) "Bone" "immediate" "closest"

</div>

</div>

</div>

<div id="variables" class="section">

### Variables<a href="Python-Eventing.html#variables" class="headerlink"
title="Link to this heading"></a>

The following event is an example of how you might use python variables
to hold onto references to specific units and ease calculation. In
normal event script, these would be crammed into single, dense,
unreadable lines.

<div class="highlight-python notranslate">

<div class="highlight">

    #pyev1

    seth_unit = u("Seth")
    reduced_hp = seth_unit.get_current_hp() - 5
    reduced_luck = seth_unit.stats['LCK'] - 5

    $set_stats seth_unit {"HP": reduced_hp, "LCK": reduced_luck}, immediate

    $add_portrait seth_unit "Right"
    $say seth_unit "What happened to my HP?" NumLines=1

</div>

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Test-Events.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Test Events"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Event-Debugger.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Debugger">Next <span
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
