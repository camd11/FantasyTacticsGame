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
    - <a href="Arena.html" class="reference internal">GBA-style Arena</a>
    - <a href="Breakable-Walls.html" class="reference internal">Breakable
      Walls</a>
    - <a href="Death-Quotes.html" class="reference internal">Universal Death
      Quotes Tutorial</a>
    - <a href="Choices-and-Battle-Saves.html"
      class="reference internal">Choices and Battle Saves</a>
    - <a href="Unit-Groups.html" class="reference internal">Unit Groups</a>
    - <a href="Achievements.html#"
      class="current reference internal">Achievements</a>
      - <a href="Achievements.html#basic-functionality"
        class="reference internal">Basic Functionality</a>
      - <a href="Achievements.html#secret-achievements"
        class="reference internal">Secret Achievements</a>
      - <a href="Achievements.html#player-record-storage"
        class="reference internal">Player record storage</a>
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
- Achievements
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/eventing_tutorials/Achievements.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="achievements" class="section">

# Achievements<a href="Achievements.html#achievements" class="headerlink"
title="Link to this heading"></a>

You may wish to create an achievement system for your game.
Alternatively, you may simply want to save content outside of a given
save file. This could be for a New Game+ feature, an Undertale-like
playthrough system, or timeline shenanigans. This guide will cover all
of these potential use cases.

<div id="basic-functionality" class="section">

## Basic Functionality<a href="Achievements.html#basic-functionality" class="headerlink"
title="Link to this heading"></a>

The create_achievement command creates a new achievement with the given
specifications and saves it to saves/PROJECTID-achievements.p.

<span class="pre">`create_achievement;Sample;Test`</span>` `<span class="pre">`Goal;It's`</span>` `<span class="pre">`only`</span>` `<span class="pre">`a`</span>` `<span class="pre">`test!`</span>

Try it out by putting this line before a base event command in any given
level. Test the level and go to Codex \> Achievements.

![TestAchievement](./media/30a49d3971926082d1cc876d7a7ebb37cf7edad4.png)

Voila! You have an incomplete achievement listed there. Of course, we’d
like to have the player be able to complete that achievement.

In any event you’d like, place this command:

<span class="pre">`complete_achievement;Sample;1`</span>

Where Sample is the NID of the achievement you created above. Run that
event then check the records screen again - the achievement will be
complete!

</div>

<div id="secret-achievements" class="section">

## Secret Achievements<a href="Achievements.html#secret-achievements" class="headerlink"
title="Link to this heading"></a>

Many games have achievements for defeating endgame bosses. In order to
avoid spoilers for those bosses, we’d like to hide some achievement
information from the player.

The first option we have is to only run the create_achievement command
when the boss is first defeated. That way the achievement won’t appear
in the Records menu early, since it won’t exist.

Most game platforms, like Steam, display certain achievements as
“Locked” prior to their completion. Let’s implement a system for our
game.

Create a new achievement.

<span class="pre">`create_achievement;KillGodOrSomething;???;Continue`</span>` `<span class="pre">`the`</span>` `<span class="pre">`story`</span>` `<span class="pre">`to`</span>` `<span class="pre">`unlock;hidden`</span>

![LockedAchievement](./media/3bbee357506c0c8d3f5501650f18065f36d0f27e.png)

Players can see that they haven’t unlocked all achievements, but will
naturally later on. We can use the update_achievement command to change
the details of the displayed achievement.

<span class="pre">`update_achievement;KillGodOrSomething;Kill`</span>` `<span class="pre">`God;You`</span>` `<span class="pre">`managed`</span>` `<span class="pre">`to`</span>` `<span class="pre">`slay`</span>` `<span class="pre">`a`</span>` `<span class="pre">`deity.`</span>

![UnlockedAchievement](./media/f3999f99499aa993cd29a080cc16f3e209b8df97.png)

The details of the achievement have been updated.

</div>

<div id="player-record-storage" class="section">

## Player record storage<a href="Achievements.html#player-record-storage" class="headerlink"
title="Link to this heading"></a>

I’d like to remember if the player has completed the game. I can’t keep
that data tied to a particular save file, so the persistent record
system is perfect here.

Similarly to achievements, we’ll create a new record first.

<span class="pre">`create_record;CompleteGame;False`</span>

When you create or update a new record, remember that you must provide
it a valid Python expression after the name. It is therefore recommended
that you provide one of True, False, or a number unless you are
confident you know what you’re doing.

Similar to achievements, you can use update_record or replace_record to
change the value later. You can also check the value of records, as seen
below.

<div class="highlight-default notranslate">

<div class="highlight">

    if;RECORDS.get("CompleteGame")
        speak;Eirika;I've won before
    else
        speak;Eirika;I haven't won yet.
    end

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Unit-Groups.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Unit Groups"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="A-Simple-Mercenary-Shop.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="A Simple Mercenary Shop Tutorial">Next <span
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
