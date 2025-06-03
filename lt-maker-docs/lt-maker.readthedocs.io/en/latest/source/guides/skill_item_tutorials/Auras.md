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
    - <a href="Auras.html#" class="current reference internal">3. Auras - Hex,
      Bond and Focus</a>
      - <a href="Auras.html#required-editors-and-components"
        class="reference internal">Required editors and components</a>
      - <a href="Auras.html#skill-descriptions" class="reference internal">Skill
        descriptions</a>
      - <a href="Auras.html#step-1-create-a-class-skill-an-an-effect-skill"
        class="reference internal">Step 1: Create a Class Skill an an ‘Effect
        Skill’</a>
      - <a href="Auras.html#step-2-a-add-the-aura-component-to-the-class-skill"
        class="reference internal">Step 2.A: Add the Aura component to the Class
        Skill</a>
      - <a href="Auras.html#step-3-add-the-other-components-to-the-effect-skill"
        class="reference internal">Step 3: Add the other components to the
        ‘Effect Skill’</a>
      - <a
        href="Auras.html#step-2-b-3-c-focus-add-the-condition-component-to-the-class-skill"
        class="reference internal">Step 2.B → 3.C: [Focus] Add the Condition
        component to the Class Skill</a>
      - <a
        href="Auras.html#step-4-test-the-stat-alterations-and-effects-in-game"
        class="reference internal">Step 4: Test the stat alterations and effects
        in-game</a>
      - <a
        href="Auras.html#optional-step-add-the-hidden-component-to-the-effect-skill"
        class="reference internal">Optional Step: Add the Hidden component to
        the ‘Effect Skill’</a>
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
- 3\. Auras - Hex, Bond and Focus
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/skill_item_tutorials/Auras.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<span class="small"><span class="pre">`Originally`</span>` `<span class="pre">`written`</span>` `<span class="pre">`by`</span>` `<span class="pre">`Hillgarm.`</span>` `<span class="pre">`Last`</span>` `<span class="pre">`Updated`</span>` `<span class="pre">`2022-09-01`</span></span>

<div id="auras-hex-bond-and-focus" class="section">

# 3. Auras - Hex, Bond and Focus<a href="Auras.html#auras-hex-bond-and-focus" class="headerlink"
title="Link to this heading"></a>

Auras are passive effects that apply to all units of a given type within
a radius, targeting either allies or enemies. Once the unit leaves the
radius, they no longer get the effects from the aura.

In this guide we will make an an ally based aura, an enemy based aura,
and a passive that checks how many enemies are within a radius.

**INDEX**

- **Required editors and components**

- **Skill descriptions**

- **Step 1: Create a Class Skill an an ‘Effect Skill’**

- **Step 2.A: Add the an Aura component to the Class Skill**

- **Step 3: Add the other components to the ‘Effect Skill’**

  - Step 3.A: **\[Hex\]** Add the Hit component

  - Step 3.B: **\[Bond\]** Add the Upkeep Damage component

- **Step 2.B → 3.C: \[Focus\] Add the Condition component to Class
  Skill**

- **Step 4: Test the stat alterations and effects in-game**

- **Optional Step: Add the Hidden component to the ‘Effect Skill’**

<div id="required-editors-and-components" class="section">

## Required editors and components<a href="Auras.html#required-editors-and-components" class="headerlink"
title="Link to this heading"></a>

- Skills:

  - Attribute components - Class Skills, **Hidden (optional)**

  - Combat components - Hit

  - Advanced components - Condition

  - **Status components - Aura, Aura Radius, Aura Target, and Upkeep
    Damage**

- Objects, Attributes and Properties:

  - **unit_funcs - check_focus(unit, {integer})**

</div>

<div id="skill-descriptions" class="section">

## Skill descriptions<a href="Auras.html#skill-descriptions" class="headerlink"
title="Link to this heading"></a>

- **Hex** - Adjacent enemies have -15 Hit.

- **Bond** - At the start of your phase, restore 10 HP of all allies
  within 3 spaces.

- **Focus** - Critical +10 while no ally is within 3 spaces.

</div>

<div id="step-1-create-a-class-skill-an-an-effect-skill"
class="section">

## Step 1: Create a Class Skill an an ‘Effect Skill’<a href="Auras.html#step-1-create-a-class-skill-an-an-effect-skill"
class="headerlink" title="Link to this heading"></a>

This time we will need two different skill entries to create a single
skill effect. Only one of them will have the **Class Skill component**.

As usual, we need different **Unique IDs** for both. The naming
convention is up to your personal preference. In this tutorial, I will
be using *SKILLNAME* for the **Class Skill** and *SKILLNAME_EFFECT* for
the *‘Effect Skill’*.

We also want our skills to have the same **Display Name** and **Icon**.

![3_1](./media/119dd345bf1e33c9b92d520f3bab97ca34f22e54.png)

The **Description** can also be the same, but you may remove the
distance from it.

![3_2](./media/fe8a608f3cd54159dd8f60a0951b3026a4052a7f.png)

</div>

<div id="step-2-a-add-the-aura-component-to-the-class-skill"
class="section">

## Step 2.A: Add the Aura component to the Class Skill<a href="Auras.html#step-2-a-add-the-aura-component-to-the-class-skill"
class="headerlink" title="Link to this heading"></a>

Auras are composed of three components - **Aura component**, **Aura
Range component** and **Aura Target component**. All of them can be
found within the **Status Components** menu, represented by the **Sharp
Sound Wave icon**.

![3_3](./media/e3535623eaa2723dec3a99c15b5c9b83cb3061c4.png)

Once you add one of them, the other two will be added as well, and the
same applies to removal.

![3_4](./media/d5188cf9e8c7803fe9ce0e40fc8e7bcc85e5d1b1.png)

| Component Name  | Description                                          | Value                                                          |
|-----------------|------------------------------------------------------|----------------------------------------------------------------|
| **Aura**        | Defines the effect (**Skill**) that will be applied. | Skill                                                          |
| **Aura Range**  | Defines the radius of the aura, in a rhombus shape.  | Integer                                                        |
| **Aura Target** | Defines if the aura will target allies or enemies.   | Object - **ally**, **enemy** or **unit** (both ally and enemy) |

For the **Aura component**, we want to set it to the ID of the other
skill we created. We also need to set the **Aura Range component** to
the corresponding distance - 1 for *Hex* and 3 for *Bond* and *Focus*.
At last, the Aura Target should take *enemy* for *Hex* and *ally* for
*Bond*. Focus will be assigned once we get into its dedicated step.

![3_5](./media/a1db583865452a9fcdc62dca5a93115be34e3f22.png)

The SKILL will be displayed as any other skill in the **unit information
window**, meanwhile the effect will be displayed in the status section
for every unit that is affected.

![3_6](./media/c5f73d6c8ae1beb21fdefab5ec8c89f479384f26.png)

</div>

<div id="step-3-add-the-other-components-to-the-effect-skill"
class="section">

## Step 3: Add the other components to the ‘Effect Skill’<a href="Auras.html#step-3-add-the-other-components-to-the-effect-skill"
class="headerlink" title="Link to this heading"></a>

<div id="step-3-a-hex-add-the-hit-component" class="section">

### Step 3.A: \[Hex\]( Add the Hit component<a href="Auras.md#step-3-a-hex-add-the-hit-component"
class="headerlink" title="Link to this heading"></a>

The end result should look like this:

![3_7](./media/72accdb5c56eec7f905d798b110976075de0ba7b.png)

</div>

<div id="step-3-b-bond-add-the-upkeep-damage-component" class="section">

### Step 3.B: \[Bond\]( Add the Upkeep Damage component<a href="Auras.md#step-3-b-bond-add-the-upkeep-damage-component"
class="headerlink" title="Link to this heading"></a>

The **Upkeep Damage component** can also be found within the **Status
Component** menu.

![3_8](./media/e01d9ee664ad367048652f30657d0880cf78b02a.png)

**Upkeep** is the term used to refer to the beginning of the phase. For
instance, a player unit’s upkeep is the beginning of the player phase,
and an enemy unit’s upkeep is the beginning of the enemy phase.

We can convert this component into a healing effect by assigning a
negative value. The end result should look like this:

![3_9](./media/0514053e8a1c20e0469196abac54a31bbe23d121.png)

</div>

</div>

<div id="step-2-b-3-c-focus-add-the-condition-component-to-the-class-skill"
class="section">

## Step 2.B → 3.C: \[Focus\] Add the Condition component to the Class Skill<a
href="Auras.html#step-2-b-3-c-focus-add-the-condition-component-to-the-class-skill"
class="headerlink" title="Link to this heading"></a>

Focus will be significantly different from the other two. We don’t
actually need the **Aura component** for this skill, since this skill
does not affect other units. Its only role here will be aesthetic, to
show the range of the at which focus is gained.

The only requirement to make it into a tracker is to set the **Aura
Target component** value to *None*.

![3_10](./media/db619e5ae5355cf8edfc3a144e92e9d1fb67eb38.png)

Ideally, we should also set the **Aura component** value to a ‘*generic
empty skill*’ instead of a dedicated *‘Effect Skill’*, as it can be
reused for any other range tracker.

![3_11](./media/a72fa5b269567d7e6eef142beeb7f535d1fb3d6e.png)

For our condition, we need to use a method that comes with the **Lex
Talionis** engine. The file **unit_funcs** (*Unit Functions*) contains
some methods that expand on the **unit** object scope and/or interact
with other objects outside it.

To check how many enemy units are within the user radius, we can use the
method **unit_funcs.check_focus(unit, {integer})**. This method can take
two values, the first is a **unit** and the second should be an integer
number greater than 0. The {integer} value is set to 3 by default if no
value is assigned. Our line should be:

<div class="highlight-none notranslate">

<div class="highlight">

    unit_funcs.check_focus(unit, 3)

</div>

</div>

**or**

<div class="highlight-none notranslate">

<div class="highlight">

    unit_funcs.check_focus(unit)

</div>

</div>

Now we add our conditional operator to check whether there are exactly 0
ally units within a range of 3:

<div class="highlight-none notranslate">

<div class="highlight">

    unit_funcs.check_focus(unit, 3) == 0

</div>

</div>

The end result should look like this:

![3_12](./media/a033c7f3ebf4cca923d55743e7977c30dc14d48d.png)

</div>

<div id="step-4-test-the-stat-alterations-and-effects-in-game"
class="section">

## Step 4: Test the stat alterations and effects in-game<a
href="Auras.html#step-4-test-the-stat-alterations-and-effects-in-game"
class="headerlink" title="Link to this heading"></a>

For auras in particular, we need more units to be on our testing map.
Set at least one ally and one enemy unit, then move the unit with the
aura skill to check if the effects are applied when the ally or enemy is
inside the aura radius.

![3_13](./media/d89b5beea5814e55c54f3999202b4b89529ad6b2.png)

The aura radius will also be displayed whenever you hover over any unit
that carries an aura, even enemy units.

![3_14](./media/52b1c04280d6d4dfc8c898e07df37fef64c53cfe.png)

</div>

<div id="optional-step-add-the-hidden-component-to-the-effect-skill"
class="section">

## Optional Step: Add the Hidden component to the ‘Effect Skill’<a
href="Auras.html#optional-step-add-the-hidden-component-to-the-effect-skill"
class="headerlink" title="Link to this heading"></a>

By default, every skill added to an unit will be displayed as an
inspectable element, either as a class skill or as a status, in the
**unit information window**. We can disable that property by adding the
**Hidden component**, found within the **Attribute Components** menu.

![3_15](./media/4117bd78b205ecce1d5f5d850391912a2d647ac2.png)

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Tile-Passives.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev"
title="4. Tile Oriented Passives - Outdoor Fighter and Indoor Fighter"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Skill-Swap.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="[System] Skill Swap">Next <span
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
