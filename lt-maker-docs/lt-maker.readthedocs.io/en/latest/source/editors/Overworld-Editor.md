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

- <a href="Editors-Overview.html" class="reference internal">Editors
  Overview</a>
- <a href="index.html" class="reference internal">Editors</a>
  - <a href="Editors-Overview.html" class="reference internal">Editors
    Overview</a>
  - <a href="Level-Editor.html" class="reference internal">Level Editor</a>
  - <a href="Overworld-Editor.html#"
    class="current reference internal">Overworld Editor</a>
    - <a href="Overworld-Editor.html#overworld-editor-location-and-usage"
      class="reference internal">Overworld Editor Location and Usage</a>
    - <a href="Overworld-Editor.html#eventing-the-overworld"
      class="reference internal">Eventing the Overworld</a>
    - <a href="Overworld-Editor.html#overworld-nodes"
      class="reference internal">Overworld Nodes</a>
  - <a href="Event-Editor.html" class="reference internal">Event Editor</a>
  - <a href="database-editors/index.html"
    class="reference internal">Database Editors</a>
  - <a href="resource-editors/index.html"
    class="reference internal">Resource Editors</a>

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
- [Editors](index.html)
- Overworld Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/Overworld-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="overworld-editor" class="section">

# Overworld Editor<a href="Overworld-Editor.html#overworld-editor" class="headerlink"
title="Link to this heading"></a>

Given that you’re on a FE Hack-like engine’s repository, I dare to
assume that you know what the overworld is. This page will briefly
describe how to create an overworld in the editor and manage it in-game
via events.

<div id="overworld-editor-location-and-usage" class="section">

## Overworld Editor Location and Usage<a href="Overworld-Editor.html#overworld-editor-location-and-usage"
class="headerlink" title="Link to this heading"></a>

The Overworld Editor can be accessed via the overworld tab, in much the
same fashion as the Level Editor.
![image](./media/cb00eb107f2278c0fed031b470ad5b624732c699.png)

This is the overworld which ships with the
<span class="pre">`default.ltproj`</span> project. You can use this as a
base for your overworld, or create a new one. I’ll make a new one for
the benefit of the reader, but it’ll be uninspired. You’ll see.

**Click the Create New Overworld button to do the thing, and double
click to enter the
editor.**![image](./media/45f258515aee7270456e8af09b9a4bb46921571d.png)

On the left side, there are a lot of fields that are effectively
self-explanatory.

- **Overworld ID** is the internal ID of the overworld. Make it
  memorable, make it count.

- **World Name** is the name of the overworld that will be displayed in
  the game to the player.

- **Overworld Theme** allows you to select the theme that plays on the
  overworld first. Don’t be too attached; this can be changed via
  events, of course.

- **Select Tilemap** allows you to select one of the existing tilemaps
  to be used as the overworld background. Given that you can import any
  image as a tilemap, this should allow you to use an arbitrary image of
  your choice - maybe even one you made yourself - as your world map.

- **Border Width** is a number that indicates how thick the border of
  the map is. This border determines how close a cursor can get to the
  edge of the map. It’s fine leaving this at 0, but for those with fancy
  borders on their maps, it may be more immersive to make use of a more
  restrictive cursor area.

Let’s make an uninspired overworld:

![image](./media/33fa8901a41e86b3d9d32057b9cfd24fabaf5da0.png)

You can see that I’ve set the border to 1. The player cannot interact
with the red zone, so be sure that you don’t place anything important in
it.

Now, onto **nodes** and **roads**!

The instructions are at the bottom of the screen, but to reiterate, all
controls involve the mouse or the delete key. **Left-Click** selects an
object; **Right-Click** moves it, while **Ctrl+Right-Click** creates
roads. If a road does not start and end in a node it will not appear in
game. **Double-L-Click** creates nodes.

We can make two nodes and a road between:

![image](./media/cd77f53c07a2679a034ad97fa61a19fa8c8c9377.png)The fields
are as follows:

- **Node ID:** The ID of the node. You can’t choose this one, but that’s
  OK, because you can name the

- **Location Name**: You can name it whatever you like.

- **Level:** The level associated with this node. This is fairly
  important, as it indicates, in concert with the selected level, what
  set of events to use upon entering the node. Make sure to label your
  nodes with their proper levels!

- Finally, the clickable button at the bottom is the **Icon Selector**,
  where you can choose which icon to use to represent the node. You can
  see in the image above the use of the Forest Temple icon.

</div>

<div id="eventing-the-overworld" class="section">

## Eventing the Overworld<a href="Overworld-Editor.html#eventing-the-overworld"
class="headerlink" title="Link to this heading"></a>

This is one of those sections where a picture is worth a thousand words,
and a gif with 60 frames by definition would be worth sixty thousand
words. Incidentally, I’ll be using the default overworld instead of the
pile of garbage I created above, so please open
<span class="pre">`default.ltproj`</span> for reference.

You can find this event in <span class="pre">`default.ltproj`</span>,
level 1, <span class="pre">`Outro`</span>.

![image](./media/5b8d64fcf88d4c4e2bc2b03d9518d6411ca7857e.png)

<div class="highlight-default notranslate">

<div class="highlight">

    speak;Eirika;Thank you, Tana.
    transition;Close
    end_skip
    #
    # Let's have some fun in the overworld. Remove the background:
    change_background
    # This command is necessary to load the overworld tilemap
    overworld_cinematic;Magvel (0)
    # The next two commands are self-explanatory. You'll use these to manipulate overworld data.
    reveal_overworld_node;Border Mulan (0);t
    set_overworld_position;Eirika's Group (Eirika);Border Mulan (0)
    #
    # Here are examples of overworld animations and sounds.
    # Notice that they are the same as the normal tilemap commands.
    transition;open;1500
    wait;1000
    sound;RefreshDance
    map_anim;AOE_Mend;Frelia Castle (2)
    reveal_overworld_node;Frelia Castle (2)
    wait;500
    sound;Mend
    reveal_overworld_road;Border Mulan (0);Frelia Castle (2)
    #
    # Because narration is more involved than dialogue, we need some different commands
    # to animate the narration window in.
    toggle_narration_mode;open;1000
    wait;500
    narrate;Narrator;Eirika and her companions have liberated the border castle.
    overworld_move_unit;Eirika's Group (Eirika);Frelia Castle (2);no_block
    narrate;Narrator;Alongside Princess Tana of Frelia, they ride to the Frelian Capital.
    wait;500
    transition;close
    toggle_narration_mode;close
    #

</div>

</div>

And you can see the results below:

![demo](./media/1130ee25ea6eeea5aada2ac0a69b64ec98b8b6ed.gif)

Not so painful, is it? There a variety of commands that are used in the
overworld. All of them are documented in the
<span class="pre">`Show`</span>` `<span class="pre">`Commands`</span>
button in the event editor; feel free to check them out.

</div>

<div id="overworld-nodes" class="section">

## Overworld Nodes<a href="Overworld-Editor.html#overworld-nodes" class="headerlink"
title="Link to this heading"></a>

This guide will serve as an introduction to the “Overworld Node Menu
Options” feature. If you have not done so, please read the guide on
Overworlds in order to familiarize yourself with how they work, before
reading this guide.

Overworld Node Menu Events are basically menu options that will appear
when a player selects an Overworld Node that they are standing on. When
selected, these options will call an event. There are various features
available to control how much access the player has to these options.

To demonstrate how this feature works, we will create an Overworld
Armory on Renais Castle.

Before we start with the new features, let’s set up the event we need.
![Picture1](./media/9de26e5b90fec6e3510be6c452da11593e66260c.png)

Keeping it short and simple for tutorial purposes. This event prompts
the player to select a unit from their party, and then initiates a shop
with that unit. The trigger, condition, and priority for this event do
not matter, Node Menu options ignore these.

**IMPORTANT**: The event **MUST** be Global (not tied to any level or
Debug), or else it cannot be called by the Overworld Node Menu Option.

Now that that’s set up, let’s walk through how to create a Node Menu
Option. Navigate to the Overworld Editor, and select any node (I will be
using Renais Castle, which is node NID 25 in the Sacred Stones project).
To create a menu option for the node, click on the “Create Event”
button.

![Picture2](./media/61406beb32b5a2387e7c7e4114a1c1e985bb69ba.png)
![Picture3](./media/3533cad1fc49eb8d656693d067b9a7889b0b66de.png)

The new option will be automatically selected, and you will be presented
with the following attributes.

Menu Option ID: This is the unique identifier of the option. Note that
this identifier is only unique for the Node itself (i.e., Two different
nodes can have an option with the ID of “Armory”, but a single node
cannot have 2 options of ID “Armory”).

Display Name: This is the name that is shown to the player in the menu.
Mostly just aesthetic.

Event: The event this option will call. Only Global events will be
available from this drop down.

Visible in Menu?: Whether this option is visible in the menu by default.
Can be changed during gameplay via events. If an option isn’t visible,
it cannot be selected even if it is enabled. If visible but not enabled,
the option will be grayed out.

Can be selected?: Whether this option is enabled by default. Can be
changed during gameplay via events. If an option isn’t visible, it
cannot be selected even if it is enabled. If visible but not enabled,
the option will be grayed out.

From here, we can set up our menu option.

![Picture4](./media/88b7e46cda3860a1cc55bd10a195d51060827320.png)

Our Node Menu Option is now ready! Time to test it in-engine. For this
example, I have set things up such that the Overworld is triggered after
the prologue, with both Border Mulan and Castle Renais being available.
I have also given the party some money.

We simply need to navigate the party onto Castle Renais, and… voila! Our
event is available.

![Picture5](./media/8721a5d715a6592c166410786152b28591a07bf5.png)

Let’s select our event and see what happens. We’re given a (kinda ugly,
I didn’t care about the aesthetics) menu prompting us to select the unit
to shop with.

![Picture6](./media/ba3c2a225d941f162ffe16f2fe93d95ed609043c.png)

Select any of them, and…!

![Picture7](./media/1d27e7d9b5543e0c10e0e1b53047f86bbcee71c7.png)

The shop works!

And that’s all it takes to make a simple Node Menu Option. In the next
tutorial, we will explore this feature in more depth, and go over the
events you can use to alter the player’s access to Node Menu Options.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Level-Editor.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Level Editor"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Event-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Event Editor">Next <span
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
