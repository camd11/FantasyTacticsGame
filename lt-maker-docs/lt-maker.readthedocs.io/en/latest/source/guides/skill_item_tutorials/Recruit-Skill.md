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
  - <a href="../eventing_tutorials/index.html"
    class="reference internal">Eventing Tutorials</a>
  - <a href="index.html" class="reference internal">Skill and Item
    Tutorials</a>
    - <a href="Creating-Items.html" class="reference internal">0. Creating
      Items</a>
    - <a href="Direct-Passives.html" class="reference internal">1. Direct
      Passives - Hit +20, MAG +2 and Gamble</a>
    - <a href="Conditional-Passives-I.html" class="reference internal">2.
      Conditional Passives I - Lucky Seven, Odd Rhythm, Wrath and Quick
      Burn</a>
    - <a href="Conditional-Passives-II.html" class="reference internal">4.
      Conditional Passives II - Warding Blow, Rainlashslayer</a>
    - <a href="Conditional-Passives-III.html" class="reference internal">3.
      Conditional Passives III - Tomefaire, Axe Breaker and Wyrmbane</a>
    - <a href="Tile-Passives.html" class="reference internal">4. Tile Oriented
      Passives - Outdoor Fighter and Indoor Fighter</a>
    - <a href="Auras.html" class="reference internal">3. Auras - Hex, Bond and
      Focus</a>
    - <a href="Skill-Swap.html" class="reference internal">[System] Skill
      Swap</a>
    - <a href="Creating-Capture.html" class="reference internal">Capture
      skill</a>
    - <a href="Recruit-Skill.html#" class="current reference internal">Recruit
      Skill</a>
      - <a href="Recruit-Skill.html#description"
        class="reference internal">Description</a>
      - <a href="Recruit-Skill.html#tutorial"
        class="reference internal">Tutorial</a>
    - <a href="Summoning.html" class="reference internal">Summoning</a>
    - <a href="Shelter-Skill.html" class="reference internal">Shelter
      Skill</a>
    - <a href="Multi-Items.html" class="reference internal">Multi Items</a>
    - <a href="Nihil.html" class="reference internal">Nihil</a>

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
- [Skill and Item Tutorials](index.html)
- Recruit Skill
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/skill_item_tutorials/Recruit-Skill.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="recruit-skill" class="section">

# Recruit Skill<a href="Recruit-Skill.html#recruit-skill" class="headerlink"
title="Link to this heading"></a>

<div id="description" class="section">

## Description<a href="Recruit-Skill.html#description" class="headerlink"
title="Link to this heading"></a>

I want a skill that:

- Grants an **ability** called **Recruit.**

- When this **ability** is used, recruits the enemy that it is used on.

</div>

<div id="tutorial" class="section">

## Tutorial<a href="Recruit-Skill.html#tutorial" class="headerlink"
title="Link to this heading"></a>

**Step 1: Create an event that changes the target’s team.**

<span dir="">Open the event editor and create a **global** event</span>.
<span class="pre">`{unit2}`</span> is the reference to the target in
Events that are called on skills.

![des](./media/72d8b8ad7fe36839cd0063465bfb5f41016886cc.png)

<span dir="">I left the AI setting blank. Enter whatever script you want
to give the unit. I recommend just setting it to no AI.</span>

**Step 2: Create an Item that calls this event.**

![des2](./media/162497596707b5a6c82e5e53f0fe34ab808a1657.png)

<span dir="">The Event on Hit component must refer to the event script
you just made.</span> That field is what calls the event specifically.

**Step 3: Create a Skill that is an Ability, and that uses your new
Item.**

<span dir="">Open the skill editor and create a new skill. This skill
will let a unit use the item you just made as an ability from the action
menu.</span>

![des4](./media/b0d5b854b04ccffc51986e1536f092910d52829e.png)

**Step 4: Add this skill to a unit or class.**

![des5](./media/e4ae4f6dba2ac48824f5641e1048ca3a2e3b006b.png)

<span dir="">That’s all there is to it. Note that right now it’s
extremely overpowered and game-breaking as it can recruit any unit (even
bosses) and always works as long as the item hits. You will need to
tailor it to work like you want by editing the item components and the
event script.</span>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Creating-Capture.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Capture skill"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Summoning.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Summoning">Next <span
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
