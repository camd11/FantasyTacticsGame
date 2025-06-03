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
    - <a href="Shelter-Skill.html" class="reference internal">Shelter
      Skill</a>
    - <a href="Multi-Items.html" class="reference internal">Multi Items</a>
    - <a href="Nihil.html#" class="current reference internal">Nihil</a>

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
- Nihil
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/guides/skill_item_tutorials/Nihil.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="nihil" class="section">

# Nihil<a href="Nihil.html#nihil" class="headerlink"
title="Link to this heading"></a>

In ordinary Fire Emblem, Nihil negates the effects of certain skills so
that they cannot be used against the bearer of Nihil.

With a custom component, we can achieve a similar effect. As one would
imagine, this makes use of the <span class="pre">`condition`</span>
hook.

Unfortunately, because the <span class="pre">`condition`</span> hook
does not work in combat, this requires a few supporting hooks to be made
use of. This is modeled off of the
<span class="pre">`combat_component`</span> Component.

In short, this component will be put on the skill **to be cancelled by
Nihil**. The player will put this component on cancellable skills, and
create a custom <span class="pre">`Nihil`</span> that serves as a
placeholder for this component to react to.

<div class="highlight-python notranslate">

<div class="highlight">

    class NihiledBy(SkillComponent):
        nid = 'nihiled_by'
        desc = "Takes a list of skills as its value. If a skill from this list is present on `target`, then *this* skill does not work."
        tag = SkillTags.CUSTOM

        expose = (ComponentType.List, ComponentType.Skill)
        value = []

        ignore_conditional = True
        _condition = True

        def pre_combat(self, playback, unit, item, target, item2, mode):
            all_target_nihils = set(self.value)
            for skill in target.skills:
                if skill.nid in all_target_nihils:
                    self._condition = False
                    return
            self._condition = True

        def post_combat_unconditional(self, playback, unit, item, target, item2, mode):
            game.on_alter_game_state()
            self._condition = True

        def condition(self, unit, item):
            return self._condition

        def test_on(self, playback, unit, item, target, item2, mode):
            game.on_alter_game_state()
            self.pre_combat(playback, unit, item, target, item2, mode)

        def test_off(self, playback, unit, item, target, item2, mode):
            game.on_alter_game_state()
            self._condition = True

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Multi-Items.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Multi Items"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="../../appendix/Text-Formatting-Commands.html"
class="btn btn-neutral float-right" accesskey="n" rel="next"
title="Text Formatting Commands">Next <span
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
