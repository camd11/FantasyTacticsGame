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

- <a href="Text-Formatting-Commands.html#"
  class="current reference internal">Text Formatting Commands</a>
  - <a href="Text-Formatting-Commands.html#dialogue-formatting-commands"
    class="reference internal">Dialogue Formatting Commands</a>
  - <a href="Text-Formatting-Commands.html#general-formatting-commands"
    class="reference internal">General Formatting Commands</a>
  - <a href="Text-Formatting-Commands.html#evaluated-descriptions"
    class="reference internal">Evaluated Descriptions</a>
    - <a href="Text-Formatting-Commands.html#what-are-they"
      class="reference internal">What Are They</a>
    - <a href="Text-Formatting-Commands.html#evaluated-variables"
      class="reference internal">Evaluated Variables</a>
    - <a href="Text-Formatting-Commands.html#examples"
      class="reference internal">Examples</a>
      - <a href="Text-Formatting-Commands.html#item-ownership"
        class="reference internal">Item Ownership</a>
      - <a href="Text-Formatting-Commands.html#dynamic-gender-and-pronouns"
        class="reference internal">Dynamic Gender and Pronouns</a>
      - <a href="Text-Formatting-Commands.html#kill-tracker"
        class="reference internal">Kill Tracker</a>
    - <a href="Text-Formatting-Commands.html#advanced-usage"
      class="reference internal">Advanced Usage</a>
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

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- Text Formatting Commands
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/Text-Formatting-Commands.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="text-formatting-commands" class="section">

# Text Formatting Commands<a href="Text-Formatting-Commands.html#text-formatting-commands"
class="headerlink" title="Link to this heading"></a>

*written by rainlash* *last updated 2024-11-13*

<div id="dialogue-formatting-commands" class="section">

## Dialogue Formatting Commands<a href="Text-Formatting-Commands.html#dialogue-formatting-commands"
class="headerlink" title="Link to this heading"></a>

In order to have your in-game dialog between characters or between the
narrator and the player flow well and be more interesting to read, you
can use several special dialog commands.

<span class="pre">`{w},`</span>` `<span class="pre">`{wait}`</span>:
Waits for the user to press A. Automatically placed at the end of any
speak command unless text ends with {no_wait}.

<span class="pre">`{no_wait}`</span>: Place at the end of a dialog and
the dialog will not wait for the user to press A.

<span class="pre">`{br},`</span>` `<span class="pre">`{break}`</span>:
Line break.

<span class="pre">`{clear}`</span>: Clear the text and line break.

<span class="pre">`|`</span>: shorthand for
<span class="pre">`{w}{br}`</span> in sequence.

<span class="pre">`{semicolon}`</span>: Adds a
<span class="pre">`;`</span>

<span class="pre">`{lt}`</span>: Adds a <span class="pre">`<`</span>

<span class="pre">`{gt}`</span>: Adds a <span class="pre">`>`</span>

<span class="pre">`{lcb}`</span>: Adds a <span class="pre">`{`</span>

<span class="pre">`{rcb}`</span>: Adds a <span class="pre">`}`</span>

<span class="pre">`{tgs}`</span>: Toggles whether the speaking sound
occurs.

<span class="pre">`{tgm}`</span>: Toggles whether the portrait’s mouth
will move while talking.

<span class="pre">`{max_speed}`</span>: After this command, dialog will
be drawn immediately to the screen.

<span class="pre">`{starting_speed}`</span>: After this command, dialog
will be drawn at the normal speed to the screen.

<span class="pre">`{command:??},`</span>` `<span class="pre">`{c:??}`</span>:
Allows you to run any event command inline while dialog is being drawn
to the screen. For instance:
<span class="pre">`s;Eirika;I'm...`</span>` `<span class="pre">`so....`</span>` `<span class="pre">`{c:set_expression;Eirika;CloseEyes}`</span>` `<span class="pre">`sleepy...`</span>

</div>

<div id="general-formatting-commands" class="section">

## General Formatting Commands<a href="Text-Formatting-Commands.html#general-formatting-commands"
class="headerlink" title="Link to this heading"></a>

The below formatting can be used in both dialogue and most description
boxes for units/items/skills/etc.

<span class="pre">`<red>`</span>: Can be used to turn the font to red
color. Turn back to normal with <span class="pre">`</red>`</span> or
<span class="pre">`</>`</span>. Can also use
<span class="pre">`<blue>`</span>, <span class="pre">`<green>`</span>,
etc.

<span class="pre">`<icon>??</>`</span>: Paste any 16x16 icon with a name
directly into the text. For instance,
<span class="pre">`<icon>Waffle</>`</span>.

<span class="pre">`<text>`</span>: Can be used to change the font. Turn
back to normal with <span class="pre">`</text>`</span> or
<span class="pre">`</>`</span>. Can also use
<span class="pre">`<nconvo>`</span>,
<span class="pre">`<narrow>`</span>,
<span class="pre">`<iconvo>`</span>,
<span class="pre">`<bconvo>`</span>, etc.

<span class="pre">`<wave>`</span>: Can be used to change the text
effect. Turn back to normal with <span class="pre">`</wave>`</span> or
<span class="pre">`</>`</span>. Can also use
<span class="pre">`<wave2>`</span>, <span class="pre">`<sin>`</span>,
<span class="pre">`<jitter>`</span>,
<span class="pre">`<jitter2>`</span>, etc. Advanced usage: some text
effects may have arguments that can be used to customize the effect. For
example, wave has a <span class="pre">`amplitude`</span> argument that
can be used to customize the amplitude of vertical wave oscillation. The
exact usage would look like
<span class="pre">`<wave`</span>` `<span class="pre">`amplitude=4.5>some`</span>` `<span class="pre">`text</>`</span>.
The general format for effect arguments is
<span class="pre">`<effect`</span>` `<span class="pre">`arg1=val1`</span>` `<span class="pre">`arg2=val2`</span>` `<span class="pre">`...>`</span>.
Parsing for arguments is whitespace and case sensitive. For a full
effect list look at
<span class="pre">`app/engine/graphics/text/text_effects.py`</span>.
Both <span class="pre">`TextEffect`</span> and
<span class="pre">`CoordinatedTextEffect`</span> classes are available
to use as text effects in dialog, and the corresponding names for each
effect is under the effect class as its <span class="pre">`nid`</span>
and the available arguments for each effect is the arguments to its
<span class="pre">`__init__`</span> function excluding
<span class="pre">`self`</span> and <span class="pre">`idx`</span>
arguments.

</div>

<div id="evaluated-descriptions" class="section">

## Evaluated Descriptions<a href="Text-Formatting-Commands.html#evaluated-descriptions"
class="headerlink" title="Link to this heading"></a>

<div id="what-are-they" class="section">

### What Are They<a href="Text-Formatting-Commands.html#what-are-they" class="headerlink"
title="Link to this heading"></a>

Some descriptions in the editor allow you to use evaluated text. These
are things like <span class="pre">`{v:}`</span> and
<span class="pre">`{e:}`</span>.

Specifically at the moment this includes:

1.  Unit descriptions

2.  Item descriptions and skill descriptions

</div>

<div id="evaluated-variables" class="section">

### Evaluated Variables<a href="Text-Formatting-Commands.html#evaluated-variables"
class="headerlink" title="Link to this heading"></a>

The evaluated text for the statements above all have access to a few
common variables.

Like all evaluated statements evaluated text has access to a variable
called <span class="pre">`game`</span>. This is the variable for the
game state.

All descriptions also have access to a variable called
<span class="pre">`self`</span>. This refers to the variable in the
engine code that represents the object that the description belongs to.
For example, the <span class="pre">`self`</span> variable for a unit
description refers to a unit object in the engine code. Likewise for
items and skills.

Items and skill descriptions have access to an additional variable
called <span class="pre">`unit`</span>. This variable refers to the unit
that currently owns this item or skill. This is equivalent to the
statement <span class="pre">`{e:game.get_unit(self.owner_nid)}`</span>
and is just a convenience variable.

</div>

<div id="examples" class="section">

### Examples<a href="Text-Formatting-Commands.html#examples" class="headerlink"
title="Link to this heading"></a>

<div id="item-ownership" class="section">

#### Item Ownership<a href="Text-Formatting-Commands.html#item-ownership"
class="headerlink" title="Link to this heading"></a>

This is a simple concrete example. We can add a description for who’s
item it is in the item description. For example if Seth is holding a
Steel Sword, we can modify the description of a Steel Sword to be
<span class="pre">`{unit}'s`</span>` `<span class="pre">`{e:self.name}`</span>

This will be evaluated and displayed as
<span class="pre">`Seth's`</span>` `<span class="pre">`Steel`</span>` `<span class="pre">`Sword`</span>.

![SteelSwordDescription](./media/232c2350901eb3d3722912110622b79d3278efdd.png)
![SteelSwordDescription](./media/8d08b0c600f0af3b8ccadd55a61079782288b6a3.png)

</div>

<div id="dynamic-gender-and-pronouns" class="section">

#### Dynamic Gender and Pronouns<a href="Text-Formatting-Commands.html#dynamic-gender-and-pronouns"
class="headerlink" title="Link to this heading"></a>

If we wanted to add dynamic gender we can use this feature. For example
if we wanted dynamic gender for a certain unit, we can set a persistent
variable during unit creation and use it in the description.

<span class="pre">`"A`</span>` `<span class="pre">`wild`</span>` `<span class="pre">`{e:"man"`</span>` `<span class="pre">`if`</span>` `<span class="pre">`"{v:WildPronoun}"`</span>` `<span class="pre">`==`</span>` `<span class="pre">`"He"`</span>` `<span class="pre">`else`</span>` `<span class="pre">`"woman"`</span>` `<span class="pre">`if`</span>` `<span class="pre">`"{v:WildPronoun}"`</span>` `<span class="pre">`==`</span>` `<span class="pre">`"She"`</span>` `<span class="pre">`else`</span>` `<span class="pre">`"person"}`</span>` `<span class="pre">`raised`</span>` `<span class="pre">`in`</span>` `<span class="pre">`the`</span>` `<span class="pre">`forests`</span>` `<span class="pre">`of`</span>` `<span class="pre">`Nabu.`</span>` `<span class="pre">`Has`</span>` `<span class="pre">`a`</span>` `<span class="pre">`fear`</span>` `<span class="pre">`of`</span>` `<span class="pre">`blood`</span>` `<span class="pre">`and`</span>` `<span class="pre">`hates`</span>` `<span class="pre">`spiders."`</span>

Lets say <span class="pre">`WildPronoun`</span> was set to
<span class="pre">`"He"`</span> then the entire description would
evaluate to:
<span class="pre">`A`</span>` `<span class="pre">`wild`</span>` `<span class="pre">`man`</span>` `<span class="pre">`raised`</span>` `<span class="pre">`in`</span>` `<span class="pre">`the`</span>` `<span class="pre">`forests`</span>` `<span class="pre">`of`</span>` `<span class="pre">`Nabu.`</span>` `<span class="pre">`Has`</span>` `<span class="pre">`a`</span>` `<span class="pre">`fear`</span>` `<span class="pre">`of`</span>` `<span class="pre">`blood`</span>` `<span class="pre">`and`</span>` `<span class="pre">`hates`</span>` `<span class="pre">`spiders.`</span>

</div>

<div id="kill-tracker" class="section">

#### Kill Tracker<a href="Text-Formatting-Commands.html#kill-tracker" class="headerlink"
title="Link to this heading"></a>

We can add a kill tracker to an item or skill using this feature. We can
set a persistent variable tracking the number of kills a unique weapon
has been used for and show it in the description.

<span class="pre">`"A`</span>` `<span class="pre">`blade`</span>` `<span class="pre">`that`</span>` `<span class="pre">`has`</span>` `<span class="pre">`taken`</span>` `<span class="pre">`{v:UniqueWeaponKills}`</span>` `<span class="pre">`lives."`</span>

Lets say <span class="pre">`UniqueWeaponKills`</span> has tracked 10
kills so fa, then this description would evaluate to:
<span class="pre">`A`</span>` `<span class="pre">`blade`</span>` `<span class="pre">`that`</span>` `<span class="pre">`has`</span>` `<span class="pre">`taken`</span>` `<span class="pre">`10`</span>` `<span class="pre">`lives.`</span>

</div>

</div>

<div id="advanced-usage" class="section">

### Advanced Usage<a href="Text-Formatting-Commands.html#advanced-usage"
class="headerlink" title="Link to this heading"></a>

Since <span class="pre">`self`</span> refers to the object that the
description belongs to, you have access to all variables accessible from
that object. You can use that knowledge however you like.

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="../guides/skill_item_tutorials/Nihil.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Nihil"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="Item-Component-Reference.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Item Component Dictionary">Next <span
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
