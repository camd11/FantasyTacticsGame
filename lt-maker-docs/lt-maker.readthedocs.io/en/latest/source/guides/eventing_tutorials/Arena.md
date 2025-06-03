<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

<a href="../../../index.html" class="icon icon-home">lt-maker</a>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" spy="affix" role="navigation"
aria-label="Navigation menu">

<span class="caption-text">Contents:</span>

- <a href="../../home.html" class="reference internal">Lex Talionis
  Wiki</a>

<span class="caption-text">Getting Started:</span>

- <a href="../../getting_started/index.html"
  class="reference internal">Getting Started</a>

<span class="caption-text">Editor Guides:</span>

- <a href="../../editors/Editors-Overview.html"
  class="reference internal">Editors Overview</a>
- <a href="../../editors/index.html"
  class="reference internal">Editors</a>

<span class="caption-text">Events:</span>

- <a href="../../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../Guides-Overview.html" class="reference internal">Guides
  Overview</a>
- <a href="../index.html" class="reference internal">Guides</a>
  - <a href="../setup_tutorials/index.html"
    class="reference internal">Project Setup Tutorials</a>
  - <a href="index.html" class="reference internal">Eventing Tutorials</a>
    - <a href="Arena.html#" class="current reference internal">GBA-style
      Arena</a>
      - <a href="Arena.html#prerequisites"
        class="reference internal">Prerequisites</a>
      - <a href="Arena.html#setting-up-the-event"
        class="reference internal">Setting up the event</a>
      - <a href="Arena.html#reference" class="reference internal">Reference</a>
    - <a href="Breakable-Walls.html" class="reference internal">Breakable
      Walls</a>
    - <a href="Death-Quotes.html" class="reference internal">Universal Death
      Quotes Tutorial</a>
    - <a href="Choices-and-Battle-Saves.html"
      class="reference internal">Choices and Battle Saves</a>
    - <a href="Unit-Groups.html" class="reference internal">Unit Groups</a>
    - <a href="Achievements.html" class="reference internal">Achievements</a>
    - <a href="A-Simple-Mercenary-Shop.html" class="reference internal">A
      Simple Mercenary Shop Tutorial</a>
    - <a href="Promotion-Personal-Skills.html"
      class="reference internal">Promotion Personal Skills Tutorial</a>
  - <a href="../skill_item_tutorials/index.html"
    class="reference internal">Skill and Item Tutorials</a>

<span class="caption-text">appendix:</span>

- <a href="../../appendix/Text-Formatting-Commands.html"
  class="reference internal">Text Formatting Commands</a>
- <a href="../../appendix/Item-Component-Reference.html"
  class="reference internal">Item Component Dictionary</a>
- <a href="../../appendix/Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="../../appendix/Special-Variables.html"
  class="reference internal">Special Variables</a>
- <a href="../../appendix/Special-Tags.html"
  class="reference internal">Special Tags</a>
- <a href="../../appendix/trigger-reference.html"
  class="reference internal">Event Triggers</a>
- <a href="../../appendix/Random-Seed-Mechanics.html"
  class="reference internal">Random Seed Mechanics</a>
- <a href="../../appendix/FAQ.html" class="reference internal">Frequently
  Asked Questions</a>
- <a href="../../appendix/Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="../../appendix/index.html" class="reference internal">Code
  Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../../index.html" class="icon icon-home"
  aria-label="Home"></a>
- [Guides](../index.html)
- [Eventing Tutorials](index.html)
- GBA-style Arena
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/eventing_tutorials/Arena.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="gba-style-arena" class="section">

# GBA-style Arena<a href="Arena.html#gba-style-arena" class="headerlink"
title="Link to this heading"></a>

*last updated 22-01-31*

![Screenshot of GBA arena menu screen created by this
tutorial](./media/aad3dcd2b22732afa0b2da3539df4aece8cb70a9.png)

This tutorial will explain how to create an arena where your units can
fight, earn experience and money, and potentially die. In this guide, an
arena based off the Fire Emblem GBA games will be created, but the
features shown here are powerful enough to create significantly
different variants on the base idea.

These relatively new event editor features give you, the game designer,
significant freedom in creating all sorts of choices and menus that you
can show the player. This means we can create a version of the GBA arena
without actually touching any Python code.

<div id="prerequisites" class="section">

## Prerequisites<a href="Arena.html#prerequisites" class="headerlink"
title="Link to this heading"></a>

It is expected that you, the reader, are already familiar with
<a href="A-Simple-Mercenary-Shop.html" class="reference internal"><span
class="doc std std-doc">A Simple Mercenary Shop Guide</span></a>. If you
aren’t, you may find it useful to understand that guide before diving
into this one.

</div>

<div id="setting-up-the-event" class="section">

## Setting up the event<a href="Arena.html#setting-up-the-event" class="headerlink"
title="Link to this heading"></a>

First, in your level, create an “event” region with sub_nid “Arena”.

![Screenshot of "event"
region](./media/c45135016af7444e5a254e92c11b42afba10e890.png)

Now, in the event editor, create a new global event called “Arena”. Set
the trigger to “Arena”. You can leave the condition as “True”, since any
unit can use the arena.

![Screenshot of event's main attributes in
editor](./media/b83fe05f46e65ddcdce73e60c68eaa8908bda041.png)

You now have an arena event, but nothing happens when you step in the
ring. Let’s fix that. We need to start by determining the class, weapon,
level, and stats of the enemy you will face in the arena. This will be a
lot of setting up and saving variables as we slowly narrow down the
choice of enemy.

First, fade to black

<span class="pre">`t;close`</span>

Then, determine your own class and save it to a variable.

<span class="pre">`level_var;EntrantClass;DB.classes.get(unit.klass)`</span>

Determine the enemy classes that are in your tier. We don’t want
promoted units fighting unpromoted units or vice versa.

<span class="pre">`level_var;ArenaEnemyKlassList;[k.nid`</span>` `<span class="pre">`for`</span>` `<span class="pre">`k`</span>` `<span class="pre">`in`</span>` `<span class="pre">`DB.classes`</span>` `<span class="pre">`if`</span>` `<span class="pre">`'ArenaIgnore'`</span>` `<span class="pre">`not`</span>` `<span class="pre">`in`</span>` `<span class="pre">`k.tags`</span>` `<span class="pre">`and`</span>` `<span class="pre">`k.tier`</span>` `<span class="pre">`==`</span>` `<span class="pre">`game.level_vars['EntrantClass'].tier]`</span>

Pick one at random.

<div class="highlight-default notranslate">

<div class="highlight">

    level_var;KlassRNG;game.get_random(0, len(game.level_vars['ArenaEnemyKlassList']) - 1)
    level_var;ArenaEnemyKlass;game.level_vars['ArenaEnemyKlassList'][game.level_vars['KlassRNG']]

</div>

</div>

Now assign the enemy a random level, but make sure that it’s close to
our entrant’s level. I decided to choose a random level within 4 levels
of our entrant’s level, making sure the level isn’t below 1 or above the
maximum allowed for the class.

<div class="highlight-default notranslate">

<div class="highlight">

    level_var;low_level;max(1, unit.level - 4)
    level_var;high_level;min(DB.classes.get(game.level_vars['ArenaEnemyKlass']).max_level, unit.level + 4)
    level_var;ArenaEnemyLevel;game.get_random(game.level_vars['low_level'], game.level_vars['high_level'])

</div>

</div>

Now we need to decide, based on the level chosen, what the player’s
wager must be in order to buy entry to the arena. We compare the chosen
level against the range of levels that were possible to pick. If it’s
closer to the high end, then the wager will also be on the high end. I
set my lowest wager possible to 550 and my highest wager possible to
1100. I also set it so that if the player has less than 550 gold, they
are still able to enter the arena by using all their money.

<div class="highlight-default notranslate">

<div class="highlight">

    level_var;ArenaPercent;(game.level_vars['ArenaEnemyLevel'] - game.level_vars['low_level']) / float(game.level_vars['high_level'] - game.level_vars['low_level'])
    level_var;ArenaWager;int(min(550 + game.level_vars['ArenaPercent'] * (1100 - 550), game.get_money()))

</div>

</div>

Next, we need to give our enemy a valid weapon they can use. It would be
no good if a Fighter shows up to the arena with an Iron Lance he can’t
wield. We investigate what kinds of weapons their class can wield and
pick from among the valid weapon types the one with the highest weapon
experience. This will crash if it picks a class that can’t wield any of
the weapon types, so make sure you mark those classes with the
“ArenaIgnore” tag in the class editor beforehand.

<div class="highlight-default notranslate">

<div class="highlight">

    level_var;ArenaWexpGain;DB.classes.get(game.level_vars['ArenaEnemyKlass']).wexp_gain
    level_var;ArenaItemDict;{'Sword': 'Iron Sword', 'Lance': 'Iron Lance', 'Axe': 'Iron Axe', 'Bow': 'Iron Bow', 'Staff': 'Heal', 'Light': 'Lightning', 'Anima': 'Fire', 'Dark': 'Flux'}
    level_var;ArenaWexpGainMaxNid;max(game.level_vars['ArenaWexpGain'].items(), key=lambda x: x[1].wexp_gain)[0]
    level_var;ArenaItem;game.level_vars['ArenaItemDict'][game.level_vars['ArenaWexpGainMaxNid']]

</div>

</div>

Now we actually instantiate the unit and their weapon. We add the unit
to the closest valid position nearby our arena entrant.

<div class="highlight-default notranslate">

<div class="highlight">

    make_generic;;{var:ArenaEnemyKlass};{var:ArenaEnemyLevel};enemy
    add_unit;{created_unit};{unit};immediate;closest
    give_item;{created_unit};{var:ArenaItem};no_banner

</div>

</div>

Finally, we can ask the player whether they actually want to fight. We
set up the menus and display boxes now.

![Screenshot of menus and display
boxes](./media/aad3dcd2b22732afa0b2da3539df4aece8cb70a9.png)

<div class="highlight-default notranslate">

<div class="highlight">

    change_background;Arena
    draw_overlay_sprite;Dialogue;menu_bg_clear;-4,8;0
    draw_overlay_sprite;ArenaPortrait;arena_portrait;4,4;1
    table;GoldDisplay;[game.get_money()];;;60;right;funds_display;;center;expression
    # Fade to arena background
    t;open

</div>

</div>

Check if the unit has a weapon and wants to wager the amount of gold we
determined in the processes above. If so, take their money and start the
fight. You’ll see that in the interact_unit command, we have the player
unit fight the created unit, in that order, so the player unit goes
first. We also set up the “arena” flag so the player can press B between
combat rounds to leave the combat early, forfeiting their wager. The
“20” indicates the maximum number of rounds that will occur. Lastly, the
“force_animation” flag forces the player to watch the animation if one
exists, even if they otherwise have animations turned off. This is to
hide the fact that the enemy unit was just spawned somewhere nearby, and
to give the player a chance to press B between combat rounds.

If the player unit doesn’t have a weapon or they refuse the wager, we
just tell them to get out of here.

<div class="highlight-default notranslate">

<div class="highlight">

    if;unit.get_weapon()
        choice;ArenaChoice;Would you like to wager {var:ArenaWager} gold?;Yes,No;;horizontal
        if;game.game_vars['ArenaChoice'] == 'Yes'
            sound;GoldExchange
            give_money;{eval:-game.level_vars['ArenaWager']};no_banner
            speak;;Good luck. Don't get yourself killed.;60,8;160;clear
            t;close
            interact_unit;{unit};{created_unit};;;20;arena;force_animation
            if;created_unit.is_dying or created_unit.dead
                t;open
                s;;So you won, eh? Here's your prize. {eval:2*game.level_vars['ArenaWager']} gold.;60,8;160;clear
                sound;GoldExchange
                give_money;{eval:2*game.level_vars['ArenaWager']}
                wait;200
            end
            has_attacked;{unit}
        else
            s;;What are you wasting my time for?;60,8;160;clear
        end
    else
        s;;What! You don't have a weapon! Get out of here!;60,8;160;clear
    end
    t;close

</div>

</div>

![Screenshot of Arena
combat](./media/69bbce5d0e6c367009a44aca83ef6d3580e98c08.png)

Now make sure to clean up after yourself. Remove the created unit from
the game. Also remember to remove the overlay sprites and tables you
created.

<div class="highlight-default notranslate">

<div class="highlight">

    change_background
    remove_unit;{created_unit};immediate
    rmtable;GoldDisplay
    remove_overlay_sprite;Dialogue
    remove_overlay_sprite;ArenaPortrait
    t;open

</div>

</div>

Congrats! You have now successfully implemented the GBA Arena. It’s not
perfect yet as the special UI commands are still missing a couple of
small features, but the functionality is complete. Feel free to modify
the event code above to meet your own special arena requirements.

</div>

<div id="reference" class="section">

## Reference<a href="Arena.html#reference" class="headerlink"
title="Link to this heading"></a>

Here is the full code used in this tutorial:

<div class="highlight-default notranslate">

<div class="highlight">

    # GBA style arena
    transition;Close
    # Determine Enemy's class, level, and item, along with associated Wager
    level_var;EntrantClass;DB.classes.get(unit.klass)
    level_var;ArenaEnemyKlassList;[k.nid for k in DB.classes if 'ArenaIgnore' not in k.tags and k.tier == game.level_vars['EntrantClass'].tier]
    level_var;KlassRNG;game.get_random(0, len(game.level_vars['ArenaEnemyKlassList']) - 1)
    level_var;ArenaEnemyKlass;game.level_vars['ArenaEnemyKlassList'][game.level_vars['KlassRNG']]
    level_var;low_level;max(1, unit.level - 4)
    level_var;high_level;min(DB.classes.get(game.level_vars['ArenaEnemyKlass']).max_level, unit.level + 4)
    level_var;ArenaEnemyLevel;game.get_random(game.level_vars['low_level'], game.level_vars['high_level'])
    level_var;ArenaPercent;(game.level_vars['ArenaEnemyLevel'] - game.level_vars['low_level']) / float(game.level_vars['high_level'] - game.level_vars['low_level'])
    level_var;ArenaWager;int(min(550 + game.level_vars['ArenaPercent'] * (1100 - 550), game.get_money()))
    level_var;ArenaWexpGain;DB.classes.get(game.level_vars['ArenaEnemyKlass']).wexp_gain
    level_var;ArenaItemDict;{'Sword': 'Iron Sword', 'Lance': 'Iron Lance', 'Axe': 'Iron Axe', 'Bow': 'Iron Bow', 'Staff': 'Heal', 'Light': 'Lightning', 'Anima': 'Fire', 'Dark': 'Flux'}
    level_var;ArenaWexpGainMaxNid;max(game.level_vars['ArenaWexpGain'].items(), key=lambda x: x[1].wexp_gain)[0]
    level_var;ArenaItem;game.level_vars['ArenaItemDict'][game.level_vars['ArenaWexpGainMaxNid']]
    # Actually instantiate unit
    make_generic;;{var:ArenaEnemyKlass};{var:ArenaEnemyLevel};enemy
    add_unit;{created_unit};{unit};immediate;closest
    give_item;{created_unit};{var:ArenaItem};no_banner
    # Now move to Arena
    change_background;Arena
    draw_overlay_sprite;Dialogue;menu_bg_clear;-4,8;0
    draw_overlay_sprite;ArenaPortrait;arena_portrait;4,4;1
    table;GoldDisplay;[game.get_money()];;;60;right;funds_display;;center;expression
    # Fade to arena background
    transition;open
    if;unit.get_weapon()
        choice;ArenaChoice;Would you like to wager {var:ArenaWager} gold?;Yes,No;;horizontal
        if;game.game_vars['ArenaChoice'] == 'Yes'
            sound;GoldExchange
            give_money;{eval:-game.level_vars['ArenaWager']};no_banner
            speak;;Good luck. Don't get yourself killed.;60,8;160;clear
            transition;close
            interact_unit;{unit};{created_unit};;;20;arena;force_animation
            if;created_unit.is_dying or created_unit.dead
                transition;open
                speak;;So you won, eh? Here's your prize. {eval:2*game.level_vars['ArenaWager']} gold.;60,8;160;clear
                sound;GoldExchange
                give_money;{eval:2*game.level_vars['ArenaWager']}
                wait;200
            end
            has_attacked;{unit}
        else
            speak;;What are you wasting my time for?;60,8;160;clear
        end
    else
        speak;;What! You don't have a weapon! Get out of here!;60,8;160;clear
    end
    transition;close
    # Clean up
    change_background
    remove_unit;{created_unit};immediate
    rmtable;GoldDisplay
    remove_overlay_sprite;Dialogue
    remove_overlay_sprite;ArenaPortrait
    transition;open

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="index.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="Eventing Tutorials"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Breakable-Walls.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Breakable Walls">Next <span
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
