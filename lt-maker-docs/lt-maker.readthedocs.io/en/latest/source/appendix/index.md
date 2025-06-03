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

- <a href="Text-Formatting-Commands.html" class="reference internal">Text
  Formatting Commands</a>
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
- <a href="index.html#" class="current reference internal">Code
  Documentation</a>
  - <a href="game-state-reference.html" class="reference internal">GameState
    class</a>
  - <a href="level-reference.html" class="reference internal">Level
    Object</a>
  - <a href="unit-reference.html" class="reference internal">UnitObject
    class</a>
  - <a href="region-reference.html" class="reference internal">RegionObject
    class</a>
  - <a href="region-reference.html#regionprefab-class"
    class="reference internal">RegionPrefab class</a>
  - <a href="party-reference.html" class="reference internal">Party
    Object</a>
  - <a href="unit_funcs-reference.html" class="reference internal">Unit
    Helper Functions</a>
  - <a href="item_funcs-reference.html" class="reference internal">Item
    Helper Functions</a>
  - <a href="query_funcs-reference.html" class="reference internal">Useful
    Functions</a>
  - <a href="constants-reference.html"
    class="reference internal">Constants</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- Code Documentation
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/index.rst"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="code-documentation" class="section">

# Code Documentation<a href="index.html#code-documentation" class="headerlink"
title="Link to this heading"></a>

Documentation for many of the functions and objects utilized by the
engine.

These functions and objects can be refrenced in your own events and
conditions.

<div class="toctree-wrapper compound">

<span class="caption-text">Documentation</span>

- <a href="game-state-reference.html" class="reference internal">GameState
  class</a>
  - <a href="game-state-reference.html#app.engine.game_state.GameState"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">GameState</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.is_displaying_overworld"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.is_displaying_overworld()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.level"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.level</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.level_nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.level_nid</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.current_party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.current_party</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.tilemap"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.tilemap</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.bg_tilemap"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.bg_tilemap</code></span></a>
    - <a href="game-state-reference.html#app.engine.game_state.GameState.mode"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.mode</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.party</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_party()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.units</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.regions"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.regions</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_data"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_data()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_unit"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_unit()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_klass"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_klass()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_convoy_inventory"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_convoy_inventory()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_item"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_item()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_skill"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_skill()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_region"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_region()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_region_under_pos"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_region_under_pos()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_ai_group"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_ai_group()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.ai_group_active"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.ai_group_active()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_units_in_ai_group"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_units_in_ai_group()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_all_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_all_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_player_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_player_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_enemy_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_enemy_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_enemy1_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_enemy1_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_enemy2_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_enemy2_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_other_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_other_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_team_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_team_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_travelers"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_travelers()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_player_units_and_travelers"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_player_units_and_travelers()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_rescuer"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_rescuer()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_rescuers_position"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_rescuers_position()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_all_units_in_party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_all_units_in_party()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_units_in_party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_units_in_party()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_all_player_units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_all_player_units()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.is_roam"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.is_roam()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_roam_unit"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_roam_unit()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.check_dead"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.check_dead()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.check_alive"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.check_alive()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_terrain_nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_terrain_nid()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_all_formation_spots"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_all_formation_spots()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_open_formation_spots"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_open_formation_spots()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_money"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_money()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_bexp"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_bexp()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_random"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_random()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_random_float"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_random_float()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_random_choice"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_random_choice()</code></span></a>
    - <a
      href="game-state-reference.html#app.engine.game_state.GameState.get_random_weighted_choice"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameState.get_random_weighted_choice()</code></span></a>
- <a href="level-reference.html" class="reference internal">Level
  Object</a>
  - <a href="level-reference.html#app.engine.objects.level.LevelObject"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">LevelObject</code></span></a>
    - <a href="level-reference.html#app.engine.objects.level.LevelObject.nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.nid</code></span></a>
    - <a href="level-reference.html#app.engine.objects.level.LevelObject.name"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.name</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.tilemap"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.tilemap</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.bg_tilemap"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.bg_tilemap</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.party</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.music"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.music</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.objective"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.objective</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.units"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.units</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.regions"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.regions</code></span></a>
    - <a
      href="level-reference.html#app.engine.objects.level.LevelObject.ai_groups"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">LevelObject.ai_groups</code></span></a>
- <a href="unit-reference.html" class="reference internal">UnitObject
  class</a>
  - <a href="unit-reference.html#app.engine.objects.unit.UnitObject"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">UnitObject</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.nid</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.prefab_nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.prefab_nid</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.generic"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.generic</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.persistent"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.persistent</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.ai"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.ai</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.ai_group"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.ai_group</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.roam_ai"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.roam_ai</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.faction"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.faction</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.team"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.team</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.portrait_nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.portrait_nid</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.affinity"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.affinity</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.klass"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.klass</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.variant"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.variant</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.name"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.name</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.desc"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.desc</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.party"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.party</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.level"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.level</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.exp"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.exp</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.stats"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.stats</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.growths"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.growths</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.growth_points"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.growth_points</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.stat_cap_modifiers"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.stat_cap_modifiers</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.wexp"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.wexp</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.position"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.position</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.starting_position"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.starting_position</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.previous_position"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.previous_position</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.traveler"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.traveler</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.strike_partner"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.strike_partner</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.lead_unit"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.lead_unit</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.dead"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.dead</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.is_dying"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.is_dying</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.items"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.items</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.has_rescued"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.has_rescued</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.has_taken"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.has_taken</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.has_given"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.has_given</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.has_dropped"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.has_dropped</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.has_run_ai"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.has_run_ai</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_max_hp"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_max_hp()</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.get_hp"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_hp()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_max_mana"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_max_mana()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_mana"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_mana()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_max_fatigue"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_max_fatigue()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_fatigue"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_fatigue()</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.get_exp"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_exp()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.add_skill"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.add_skill()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.remove_skill"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.remove_skill()</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.skills"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.skills</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.stat_bonus"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.stat_bonus()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_stat"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_stat()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_growth"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_growth()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_stat_cap"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_stat_cap()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_damage_with_current_weapon"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_damage_with_current_weapon()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_accuracy_with_current_weapon"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_accuracy_with_current_weapon()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_avoid_with_current_weapon"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_avoid_with_current_weapon()</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.tags"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.tags</code></span></a>
    - <a href="unit-reference.html#app.engine.objects.unit.UnitObject.get_ai"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_ai()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_roam_ai"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_roam_ai()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.accessories"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.accessories</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.nonaccessories"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.nonaccessories</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_skill"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_skill()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_weapon"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_weapon()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_accessory"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_accessory()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.can_equip"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.can_equip()</code></span></a>
    - <a
      href="unit-reference.html#app.engine.objects.unit.UnitObject.get_internal_level"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">UnitObject.get_internal_level()</code></span></a>
- <a href="region-reference.html" class="reference internal">RegionObject
  class</a>
  - <a href="region-reference.html#app.engine.objects.region.RegionObject"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">RegionObject</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.nid</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.region_type"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.region_type</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.position"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.position</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.size"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.size</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.sub_nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.sub_nid</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.condition"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.condition</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.time_left"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.time_left</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.only_once"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.only_once</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.interrupt_move"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.interrupt_move</code></span></a>
    - <a
      href="region-reference.html#app.engine.objects.region.RegionObject.hide_time"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">RegionObject.hide_time</code></span></a>
- <a href="region-reference.html#regionprefab-class"
  class="reference internal">RegionPrefab class</a>
  - <a href="region-reference.html#app.events.regions.Region"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">Region</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.nid</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.region_type"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.region_type</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.position"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.position</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.size"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.size</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.sub_nid"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.sub_nid</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.condition"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.condition</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.time_left"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.time_left</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.only_once"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.only_once</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.interrupt_move"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.interrupt_move</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.hide_time"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.hide_time</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.area"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.area</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.center"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.center</code></span></a>
    - <a href="region-reference.html#app.events.regions.Region.contains"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.contains()</code></span></a>
    - <a
      href="region-reference.html#app.events.regions.Region.get_all_positions"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">Region.get_all_positions()</code></span></a>
- <a href="party-reference.html" class="reference internal">Party
  Object</a>
  - <a href="party-reference.html#app.engine.objects.party.PartyObject"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">PartyObject</code></span></a>
- <a href="unit_funcs-reference.html" class="reference internal">Unit
  Helper Functions</a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.growth_rate"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">growth_rate()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.growth_contribution"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">growth_contribution()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.base_growth_rate"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">base_growth_rate()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.difficulty_growth_rate"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">difficulty_growth_rate()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.get_next_level_up"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_next_level_up()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.auto_level"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">auto_level()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.difficulty_auto_level"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">difficulty_auto_level()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.apply_stat_changes"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">apply_stat_changes()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.apply_growth_changes"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">apply_growth_changes()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.get_starting_skills"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_starting_skills()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.get_personal_skills"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_personal_skills()</code></span></a>
  - <a
    href="unit_funcs-reference.html#app.engine.unit_funcs.get_global_skills"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_global_skills()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.can_unlock"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">can_unlock()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.can_pairup"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">can_pairup()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.check_focus"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">check_focus()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.check_flanked"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">check_flanked()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.check_flanking"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">check_flanking()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.wait"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">wait()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.usable_wtypes"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">usable_wtypes()</code></span></a>
  - <a href="unit_funcs-reference.html#app.engine.unit_funcs.get_weapon_cap"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_weapon_cap()</code></span></a>
- <a href="item_funcs-reference.html" class="reference internal">Item
  Helper Functions</a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.is_magic"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">is_magic()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.is_ranged"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">is_ranged()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.is_heal"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">is_heal()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.available"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">available()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.has_magic"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">has_magic()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.can_use"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">can_use()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.can_repair"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">can_repair()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.has_repair"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">has_repair()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.buy_price"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">buy_price()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.sell_price"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">sell_price()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.repair_price"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">repair_price()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.create_item"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">create_item()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.get_all_items"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_all_items()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_all_items_with_multiitems"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_all_items_with_multiitems()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_all_items_and_abilities"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_all_items_and_abilities()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.is_weapon_recursive"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">is_weapon_recursive()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.is_spell_recursive"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">is_spell_recursive()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_all_items_from_multi_item"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_all_items_from_multi_item()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_all_tradeable_items"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_all_tradeable_items()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_all_storeable_items"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_all_storeable_items()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.get_num_items"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_num_items()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_num_accessories"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_num_accessories()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.too_much_in_inventory"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">too_much_in_inventory()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.inventory_full"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">inventory_full()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.get_range"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_range()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.get_range_string"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_range_string()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.get_max_range"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">get_max_range()</code></span></a>
  - <a href="item_funcs-reference.html#app.engine.item_funcs.num_stacks"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">num_stacks()</code></span></a>
  - <a
    href="item_funcs-reference.html#app.engine.item_funcs.can_be_used_in_base"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">can_be_used_in_base()</code></span></a>
- <a href="query_funcs-reference.html" class="reference internal">Useful
  Functions</a>
  - <a
    href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine"
    class="reference internal"><span class="pre"><code
    class="docutils literal notranslate">GameQueryEngine</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_item"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_item()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_subitem"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_subitem()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.has_item"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.has_item()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_skill"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_skill()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.has_skill"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.has_skill()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_klass"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_klass()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_class"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_class()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_closest_allies"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_closest_allies()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_units_within_distance"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_units_within_distance()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_allies_within_distance"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_allies_within_distance()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_units_in_area"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_units_in_area()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_debuff_count"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_debuff_count()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_units_in_region"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_units_in_region()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.any_unit_in_region"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.any_unit_in_region()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.is_dead"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.is_dead()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.u"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.u()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.v"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.v()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_support_rank"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_support_rank()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.get_terrain"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.get_terrain()</code></span></a>
    - <a
      href="query_funcs-reference.html#app.engine.query_engine.GameQueryEngine.has_achievement"
      class="reference internal"><span class="pre"><code
      class="docutils literal notranslate">GameQueryEngine.has_achievement()</code></span></a>
- <a href="constants-reference.html"
  class="reference internal">Constants</a>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Contributing_to_the_LTWiki.html"
class="btn btn-neutral float-left" accesskey="p" rel="prev"
title="Contributing to the LTWiki"><span class="fa fa-arrow-circle-left"
aria-hidden="true"></span> Previous</a>
<a href="game-state-reference.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="GameState class">Next <span
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
