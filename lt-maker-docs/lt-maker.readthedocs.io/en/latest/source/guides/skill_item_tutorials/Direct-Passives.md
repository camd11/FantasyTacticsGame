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
    - <a href="Direct-Passives.html#" class="current reference internal">1.
      Direct Passives - Hit +20, MAG +2 and Gamble</a>
      - <a href="Direct-Passives.html#required-editors-and-components"
        class="reference internal">Required editors and components</a>
      - <a href="Direct-Passives.html#skill-descriptions"
        class="reference internal">Skill descriptions</a>
      - <a href="Direct-Passives.html#step-1-create-a-skill"
        class="reference internal">Step 1: Create a Skill</a>
      - <a href="Direct-Passives.html#step-2-assign-the-skill"
        class="reference internal">Step 2: Assign the Skill</a>
      - <a href="Direct-Passives.html#step-3-add-combat-component"
        class="reference internal">Step 3: Add combat component</a>
      - <a href="Direct-Passives.html#step-4-test-the-stat-alterations-in-game"
        class="reference internal">Step 4: Test the stat alterations in-game</a>
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
- 1\. Direct Passives - Hit +20, MAG +2 and Gamble
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/skill_item_tutorials/Direct-Passives.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<span class="small"><span class="pre">`Originally`</span>` `<span class="pre">`written`</span>` `<span class="pre">`by`</span>` `<span class="pre">`Hillgarm.`</span>` `<span class="pre">`Last`</span>` `<span class="pre">`Updated`</span>` `<span class="pre">`2022-09-01`</span></span>

<div id="direct-passives-hit-20-mag-2-and-gamble" class="section">

# 1. Direct Passives - Hit +20, MAG +2 and Gamble<a href="Direct-Passives.html#direct-passives-hit-20-mag-2-and-gamble"
class="headerlink" title="Link to this heading"></a>

Despite the name, skills are actually effects, which covers everything
from statuses (buffs/debuffs) to skills and additional actions. They can
be applied into units or terrain, and be triggered by other skills,
items, or events. In this tutorial series we will focus on class skills
as these can be less intuitive to make.

All of the elements used will be listed at the start of each guide, with
the new items written in **bold**. Each step will be fully described at
the first time, all following occurrences will be listed as the step
name instead.

**INDEX**

- **Required editors and components**

- **Skill descriptions**

- **Step 1: Create a Skill**

  - Step 1.1: Create a Class Skill

- **Step 2: Assign the Skill**

  - Step 2.1A: Assign the Skill to an Unit

  - Step 2.1B: Assign the Skill to a Class

  - Step 2.2: Inspect the skill in-game

- **Step 3: Add a combat components**

  - Step 3.A: **\[Hit +20\]** Add a Hit component

  - Step 3.B: **\[MAG +2\]** Add a Stat Change component

  - Step 3.C: **\[Gamble\]** Add a Stat Change component and a Crit
    component

- **Step 4: Check the stat alterations in-game**

- **Conclusion**

<div id="required-editors-and-components" class="section">

## Required editors and components<a href="Direct-Passives.html#required-editors-and-components"
class="headerlink" title="Link to this heading"></a>

- **Skills:**

  - **Attribute components - Class Skills**

  - **Combat components - Stat Change, Hit and Crit**

- **Units**

- **Classes**

</div>

<div id="skill-descriptions" class="section">

## Skill descriptions<a href="Direct-Passives.html#skill-descriptions" class="headerlink"
title="Link to this heading"></a>

- **Hit +20** - Grants +20 Hit.

- **MAG +2** - Grants +2 Magic.

- **Gamble** - Grants -5 Hit and +10 Crit.

</div>

<div id="step-1-create-a-skill" class="section">

## Step 1: Create a Skill<a href="Direct-Passives.html#step-1-create-a-skill" class="headerlink"
title="Link to this heading"></a>

Open the **Skill Editor** in the **Edit Menu** and create a new
**Skill**.

![1_1](./media/2f5f5960b08e64538b7362cf5735450ad24a9451.png)

Our new skill has to have a completely unique name for the **Unique ID**
field. This will be how the engine will identify which skill is being
used or called. By default, the engine will auto fill the **Display
Name** with the **Unique ID** value, but you may change it at will. I’ll
be changing my skill name to be in lower case.

We can also give our skill a **Description** and an **Icon**, these are
important for in-game inspection.

![1_2](./media/3c38a4c68668c462cd1ad44369f230554cc96ff7.png)

For our skill to do anything, we need to assign **Components**. You can
do it by clicking on the icons below the description box, which will
open a menu with multiple options to pick from.

<div id="step-1-1-create-a-class-skill" class="section">

### Step 1.1: Create a Class Skill<a href="Direct-Passives.html#step-1-1-create-a-class-skill"
class="headerlink" title="Link to this heading"></a>

To make our skill into a proper class skill, we need to give it the
**Class Skill** component. The option can be found within the
**Attribute Components** menu, represented by the **Star icon**.

![1_3](./media/08f1e4f3e55f27ebffcb5e258aed3aed6fac6a9a.png)

Skills that have the **Class Skill component** will show an inspectable
icon under the character’s stats. It is recommended to use this
component on all personal and class skills.

![1_4](./media/6bfb282d62a83a5305ed38e8d7cf22fe1db2bd64.png)

All the added **components** will be displayed individually within the
component box. Skills can have as many components as you see fit but
only one of each. They can also be reordered by dragging them up and
down the box.

You can get some additional information on any given component by
hovering over them, both in menu and once they are added. It’s a great
feature to know if you want to swim on your own.

![1_5](./media/72d37c8befaaff8d9c484bac7ab1b6c2769b6ed6.png)

</div>

</div>

<div id="step-2-assign-the-skill" class="section">

## Step 2: Assign the Skill<a href="Direct-Passives.html#step-2-assign-the-skill"
class="headerlink" title="Link to this heading"></a>

Before we get our skill to do anything, we need to know how to assign
our skill to a unit for testing purposes. There are a couple of options
available but for this tutorial we will stick to the **Class** and
**Unit** options. You may choose which one of these methods to use.

We will be using Eirika as our target unit for the following steps.

<div id="step-2-1a-assign-the-skill-to-an-unit" class="section">

### Step 2.1A: Assign the skill to an Unit<a href="Direct-Passives.html#step-2-1a-assign-the-skill-to-an-unit"
class="headerlink" title="Link to this heading"></a>

Open the **Units Editor** in the **Edit Menu** and select the unit that
will get the skill. For this tutorial I will select the default **unit**
Eirika.

![1_6](./media/b6085cb54070127638cb0e7a1068af533247301d.png)

Click on the **+** button on the **Personal Skill** division to give
your unit a new skill, then select the desired skill. Keep the **Level**
parameter at 1 for testing purposes.

![1_7](./media/e600f64b387f5fed797f628d10c1b87423b81e22.png)

</div>

<div id="step-2-1b-assign-the-skill-to-an-unit" class="section">

### Step 2.1B: Assign the skill to an Unit<a href="Direct-Passives.html#step-2-1b-assign-the-skill-to-an-unit"
class="headerlink" title="Link to this heading"></a>

Open the **Classes Editor** in the **Edit Menu** and select the class
that will get the skill. For this tutorial I will select the default
**class** Eirika_Lord.

![1_8](./media/beae55748f16f0163e02263341de3fb28fc74071.png)

Click on the **+** button on the **Class Skill** division to give it a
new skill, then select the desired skill. You may change the **Level**
parameter in case you want to test other interactions.

![1_9](./media/a737cb38a6a8ab4948b81532e5ce4e2098e39a39.png)

</div>

<div id="step-2-2-inspect-the-skill-in-game" class="section">

### Step 2.2: Inspect the skill in-game<a href="Direct-Passives.html#step-2-2-inspect-the-skill-in-game"
class="headerlink" title="Link to this heading"></a>

Select the desired chapter for testing. This chapter must contain at
least one unit that had the skill assigned by the chosen method.

![1_10](./media/0a98bb77fb52782e95b2ce64d0766ad867dc9af5.png)

Click on the **Test Current Chapter** (F5) button in the **Test Menu**
to run it.

![1_11](./media/a258cc8207ac94f504e35ad8202259ab58406ab2.png)

With the game running, we can now inspect the unit with the **Info
Key**. The default inputs for it are the **scroll button** (mouse) or
the **C key** (keyboard).

![1_12](./media/17520dcb93d1d2d38f601a13fe56603d1899c116.png)

This will open the **unit information window**, allowing you to check
which effects are active.

If you assigned the **Class Skill component** to the skill, the icon
will displayed at page 1, at the bottom of the screen. Otherwise, it
will be displayed at page 3, within the status division, also at the
bottom.

![1_13](./media/1a8d498e4c5b745b84a5a308b4fda5e6d006d1b0.png)

Use the **Info Key** again to check the name and description of your
skill.

![1_14](./media/14de0d77e7cce4a64edfd2a7c47ec5a27a284950.png)

</div>

</div>

<div id="step-3-add-combat-component" class="section">

## Step 3: Add combat component<a href="Direct-Passives.html#step-3-add-combat-component"
class="headerlink" title="Link to this heading"></a>

All the components we will use in this tutorial belong to the **Combat
Components** menu, represented by the **(Single) Sword icon**.

![1_15](./media/80eb16790caa4ebde6e358f52573f03ce59c720f.png)

<div id="step-3-a-hit-20-add-a-hit-component" class="section">

### Step 3.A: \[Hit +20\]( Add a Hit component<a href="Direct-Passives.md#step-3-a-hit-20-add-a-hit-component"
class="headerlink" title="Link to this heading"></a>

For *Hit +20*, we will need the **Hit component**. This component is an
individual integer type. It will only apply an increment to the **Hit
stat**.

![1_16](./media/6856639be5026b679e45c18ddb0a74c7e4e49b93.png)

By default, the component will add the value to the **Hit stat**, always
being positive, but it can be negative if specified. Set the value to
20.

![1_17](./media/795f6f6f1dcb0f55310e6bc628389dbc1b823877.png)

The end result should look like this:

![1_18](./media/7ea5e9ab64c74411ef5c44b197cb725bd94d4762.png)

In-game, the **Hit stat** value is always displayed as its total sum. To
check if it is working properly, you can enable and disable the skill
comparing the stat changes for both scenarios.

</div>

<div id="step-3-b-mag-2-add-a-stat-change-component" class="section">

### Step 3.B: \[MAG +2\] Add a Stat Change component<a
href="Direct-Passives.html#step-3-b-mag-2-add-a-stat-change-component"
class="headerlink" title="Link to this heading"></a>

For *MAG +2*, we will need the **Stat Change component**.

![1_19](./media/5a92bbcde08e7d419df682786c2f29fa3ff4984a.png)

The **Stat Change component** is the one responsible for handling
additive **base stats** operations. It is similar to the **Hit
component** but instead of being a single stat, it is a list of all base
stats. We can add multiple stats to this component.

![1_20](./media/25236eb29a0438d235afca361afe63bddc96f7a3.png)

To add a new stat, click on the **+** button. Select the MAG **Stat**
and assign its **Value** to 2.

![1_21](./media/0894d0080d70e5ba1d590581fca3866f802ab5fe.png)

The end result should look like this:

![1_22](./media/d293bd5ebd54d46834904fb0753704c02cedcdd9.png)

The majority of the **base stats** will have their value split into
**base value** and **bonus value** (in green). We can easily check it
in-game by inspecting the unit.

![1_23](./media/7b091d7b4899d8aba5e2bbb7494b162f6ab9ff44.png)

</div>

<div id="step-3-c-gamble-add-a-hit-component-and-a-crit-component"
class="section">

### Step 3.C: \[Gamble\] Add a Hit component and a Crit component<a
href="Direct-Passives.html#step-3-c-gamble-add-a-hit-component-and-a-crit-component"
class="headerlink" title="Link to this heading"></a>

For Gamble, we need to add both the **Hit component** and the **Crit
component**.

![1_24](./media/b0ba7b21deeff544a63aa4493896078af3765a20.png)

This time we will give **Hit component** a negative value. The end
result should look like this:

![1_25](./media/4d0c13c9fa93fa340134e5d421b26c60e3f5e8df.png)

</div>

</div>

<div id="step-4-test-the-stat-alterations-in-game" class="section">

## Step 4: Test the stat alterations in-game<a href="Direct-Passives.html#step-4-test-the-stat-alterations-in-game"
class="headerlink" title="Link to this heading"></a>

All we have left is to check if our skill is working or not. Run a Test
where your playable unit has the skill and check the stats, then do the
same without the skill.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Creating-Items.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="0. Creating Items"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Conditional-Passives-I.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="2. Conditional Passives I - Lucky Seven, Odd Rhythm, Wrath and Quick Burn">Next
<span class="fa fa-arrow-circle-right" aria-hidden="true"></span></a>

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
