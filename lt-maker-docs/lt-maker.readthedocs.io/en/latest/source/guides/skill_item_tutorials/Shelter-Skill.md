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
    - <a href="Recruit-Skill.html" class="reference internal">Recruit
      Skill</a>
    - <a href="Summoning.html" class="reference internal">Summoning</a>
    - <a href="Shelter-Skill.html#" class="current reference internal">Shelter
      Skill</a>
      - <a href="Shelter-Skill.html#description"
        class="reference internal">Description</a>
      - <a href="Shelter-Skill.html#tutorial"
        class="reference internal">Tutorial</a>
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
- Shelter Skill
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/skill_item_tutorials/Shelter-Skill.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="shelter-skill" class="section">

# Shelter Skill<a href="Shelter-Skill.html#shelter-skill" class="headerlink"
title="Link to this heading"></a>

<div id="description" class="section">

## Description<a href="Shelter-Skill.html#description" class="headerlink"
title="Link to this heading"></a>

I want a skill that:

- Grants an ability called **Shelter.**

- When the **ability** is used, an adjacent target becomes the user’s
  pair up partner

</div>

<div id="tutorial" class="section">

## Tutorial<a href="Shelter-Skill.html#tutorial" class="headerlink"
title="Link to this heading"></a>

**Step 1: Turn on pair up**

<span dir="">Open the constants editor and enable the pair up
constant</span>.

![shelter1](./media/5d8afcfe81d2f2b372d7a826e7ea93fe0366781a.png)

**Step 2: Create an event that does the pairing**

<span dir="">Open the event editor and navigate to global events</span>.
In a new event, enter the following code.

<div class="highlight-default notranslate">

<div class="highlight">

    move_unit;{unit2};{unit};normal;stack;no_follow
    pair_up;{unit2};{unit}

</div>

</div>

<span dir="">Do not set an event trigger. Name the event something like
“Shelter”</span>.

**Step 3: Create a shelter item**

<span dir="">Open the item editor and create a shelter item</span>.

![shelter2](./media/7ab6d375be7af94e3e034a491f28a9e6b243bd89.png)

<span dir="">While you can make the minimum and maximum range whatever
you want, this configuration will ensure a system that works like Fates
Shelter.</span>.

**Step 4: Create a shelter skill**

<span dir="">Open the skill editor and create a shelter skill</span>.

![shelter3](./media/38479b26a828a903e811f635bf960e3795245223.png)

<span dir="">Add a description and skill icon that you like</span>.

**Conclusion**

<span dir="">You’re done! Test the skill in a debug map to try it
out</span>.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Summoning.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Summoning"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Multi-Items.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Multi Items">Next <span
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
