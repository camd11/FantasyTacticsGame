Feasibility of Recreating Thracia 776 Mechanics in Lex Talionis
Introduction and Scope

This project aims to replicate all major gameplay mechanics of Fire Emblem: Thracia 776 using the open-source Lex Talionis (LT) engine
feuniverse.us
. We will not recreate Thracia’s story maps or original art, but instead implement the mechanics in a set of custom demonstration maps using existing free assets (e.g. from the FE-Repo graphics repository
github.com
and LT’s sample content). The focus is on gameplay systems such as:

    Fatigue (units tire out and may be forced to rest)
    serenesforest.net

    Capture (subdue enemies to seize their items)
    serenesforest.net

    Leadership Stars (lead units confer hit/avoid bonuses)
    serenesforest.net
    serenesforest.net

    Movement Stars (chance for extra actions per turn)
    serenesforest.net

    Rescue/Carry Mechanics (carry allies or captured enemies with stat penalties)
    serenesforest.net

    Staff Accuracy (healing staves can miss)
    serenesforest.net
    serenesforest.net

    Dismounting (mounted units forced on foot indoors)
    serenesforest.net

    Escape Objectives (maps where units must escape via a point)
    serenesforest.net

    Other unique aspects: Pursuit Critical Coefficient (crit bonus on follow-ups), stealing items, etc.
    feuniverse.us

Below, we analyze the available Thracia 776 data (via decompilation projects) and the capabilities of the LT engine for each mechanic. We then discuss how to showcase these systems in sample maps using existing assets, and outline an implementation strategy (what works out-of-the-box vs. what requires custom scripting). Finally, we identify any technical/design gaps and recommend next steps.
Thracia 776 Mechanics Reference (Decompilation Data)

The Thracia 776 community and decompilation by Zane Avernathy provide a wealth of information on the game’s inner workings. The FE5 disassembly project compiles a working ROM and includes documented data tables and code for most mechanics
github.com
. This suggests the mechanical data is largely complete – e.g. constants for fatigue thresholds, formulae for hit rates, etc., are either explicitly documented or can be derived from the disassembled code. The companion VoltEdge library defines many vanilla FE5 constants, structures, and memory maps
github.com
, which confirms known values (like each Leadership star = +3 Hit/Avoid, etc.) for use in our implementation.

Even without reading raw assembly, community resources (Serenes Forest, Fire Emblem Wiki, etc.) summarize Thracia’s mechanics consistent with the decomp. Key mechanics to replicate and their known details include:

    Fatigue: Characters accumulate fatigue points for actions in each chapter. If a unit’s Fatigue > Max HP at chapter’s end, they cannot be deployed in the next chapter
    serenesforest.net
    . Most actions give +1 fatigue, though using higher-rank staves adds more (e.g. higher-rank staves give 2–5 fatigue points)
    historyoftheemblem.tumblr.com
    . Fatigue resets if the unit sits out a map or consumes a Stamina Drink item. This system forces rotation of units and is core to Thracia’s balance
    serenesforest.net
    .

    Capture: A unique combat command that allows a unit to seize an enemy. When using Capture, the attacker’s offensive stats (Strength/Magic, Skill, Speed, Defense) are halved during that battle
    serenesforest.net
    . If the enemy is reduced to 0 HP, and the attacker’s Build (constitution) exceeds the enemy’s Build, the enemy is captured (essentially picked up like a rescued unit)
    lt-maker.readthedocs.io
    . The captor can then take all items from the captive. Notably, enemies can also capture the player’s units in Thracia, so the mechanic is symmetrical. Captured enemies can be released or will die if dropped in battle
    lt-maker.readthedocs.io
    lt-maker.readthedocs.io
    .

    Leadership Stars: Certain important characters have Leadership stars (★). In Thracia each star on any allied leader grants +3% Hit and +3% Avoid to all allies’ combat stats
    serenesforest.net
    serenesforest.net
    . These bonuses stack from multiple leaders and apply globally. (Enemies also have leadership giving their side bonuses.) This provides an incentive to deploy otherwise weak “leader” units for the teamwide boost
    serenesforest.net
    .

    Movement Stars: Some units have a number of small stars (☆) on their profile. Each Movement Star gives a 5% chance for that unit to gain a “Re-move”, i.e. act again after ending their turn
    serenesforest.net
    . For example, 2 movement stars = 10% chance to move again. Only one extra action can trigger per turn at most. When it activates, a musical note ♪ appears and the unit is refreshed. This mechanic can occasionally swing strategies (enemies can have it too)
    serenesforest.net
    serenesforest.net
    .

    Rescue (Allies) & Carrying: Thracia introduced the modern Rescue mechanic
    serenesforest.net
    . A unit can rescue an ally if the rescuer’s Build is greater than the target’s Build (mounts count as having +5 bonus Build for this check)
    serenesforest.net
    . Mounted units (or any unit with extremely high Build) themselves cannot be rescued
    serenesforest.net
    . When carrying an ally (or captured enemy), the carrier suffers significant stat penalties: Strength, Magic, Skill, Speed, and Defense are halved while carrying
    serenesforest.net
    . (If the carried character’s Build is more than half the carrier’s, the carrier’s Movement is also halved as an extra penalty
    serenesforest.net
    .) These heavy penalties balanced the benefits of rescue/capture, and are more severe than the GBA games (which only cut Speed). We must replicate these effects.

    Staff Hit/Miss: In Thracia, healing and status staves are not guaranteed to hit. The Staff accuracy formula is: Hit% = Staff’s base hit + (4 × user’s Skill), capped at 99%
    serenesforest.net
    serenesforest.net
    . Most staves have a base 60 hit (except a few like Torch at 100)
    serenesforest.net
    . This means a healer with low Skill can fail to heal or inflict status. (Notably, an RN roll of 0–99 is used, so staves can hit at displayed 0% and miss at 99% due to how the RNG is handled
    reddit.com
    .) The game does not consume a staff use on a miss, and if a heal misses, the unit can immediately retry (Thracia even has a rare “double staff” effect where certain staves may attempt twice if the first doesn’t fully heal)
    gamefaqs.gamespot.com
    . The critical takeaway is the engine must allow staves to perform a hit check.

    Dismounting: As in FE3, mounted units in Thracia can Dismount to fight on foot
    serenesforest.net
    . All indoor chapters force mounted units to automatically dismount at the start
    serenesforest.net
    . When dismounted, a unit’s mounted movement type is replaced by infantry movement (often with lower Move stat), and typically they are restricted to using swords (lances/axes cannot be used on foot)
    serenesforest.net
    . Dismounting can also be done voluntarily on the world map or at will in outdoor maps, usually to avoid effective damage or terrain penalties. We need to handle class changing and weapon access changes for this mechanic.

    Escape Objectives: Some Thracia maps use Escape as the win condition
    serenesforest.net
    . The player must move units to a specific escape point. A famous twist in Thracia is that any player unit left behind after the lord escapes is considered captured (permanently removed) – so the game encourages escaping with all units and having the lord escape last. We will want to replicate escape points as a level objective and enforce the “leave last or lose units” rule for authenticity. Other chapter goals like survival/defense exist too, but those are standard in many FE games.

    Pursuit Critical Coefficient (PCC): Every player unit in Thracia has a hidden PCC value (usually 0–5). This is a multiplier to their critical hit rate on the second attack of a round (i.e. if the unit doubles)
    feuniverse.us
    . For example, a unit with PCC=3 and base crit 10% will have 30% crit on their follow-up strike. This mechanic makes certain units far deadlier on their second hit. It’s unique to FE4/FE5 and must be incorporated into how criticals are calculated during double attacks.

    Steal: Thieves in Thracia can steal any item or weapon from an enemy, so long as the thief’s Build is ≥ the enemy’s Build (and the thief’s Build ≥ item weight, for weapons)
    serenesforest.net
    . Unlike the GBA games, the enemy can be wielding the item – the thief will straight up take their equipped weapon if strong enough. This allowed for mass item theft sprees in Thracia
    serenesforest.net
    . Implementing this means allowing a “Steal” command that checks Build and item weight, not just Speed like later games.

In summary, the Thracia decomp and documentation appear comprehensive and applicable. All formulas and conditions for these mechanics are known (either via official data or community research). We can confidently use these values (e.g. 5% per movement star, +3% per leadership star, staff hit formula, etc.) in our replication. The disassembly’s data tables (e.g. growth rates including Build growth, base stats, item stats, etc.) can be referenced to ensure our implementations match the original’s numbers. The decomp project’s completeness also implies no major mechanic is “unknown” – any nuance can be double-checked (for instance, verifying how exactly escape penalties are applied in the code, or how fatigue resets). Thus, Thracia’s mechanical data is sufficiently complete to guide our implementation, even if extracting exact code will require reading assembly. We will primarily rely on documented formulas (as above) to implement these systems in the new engine.
Lex Talionis Engine Capabilities for Each Mechanic

Lex Talionis is a flexible Python-based FE engine that already supports many advanced features. Impressively, LT has explicit support or workarounds for most Thracia-specific systems – either as built-in toggleable options or via its robust event and skill scripting system
feuniverse.us
. The engine’s documentation and community (particularly the LT Maker documentation and FE Universe forums) confirm that Thracia 776 mechanics are considered and largely achievable in LT. Below we examine each target mechanic in terms of LT engine support and the expected implementation approach:
Fatigue System

Engine support: Yes (toggleable) – Lex Talionis includes a Fatigue constant that can be enabled in the game’s constants editor
lt-maker.readthedocs.io
. When turned on, the engine will track fatigue points for each unit across chapters. The behavior can be configured via a special variable _fatigue: setting _fatigue = 1 will implement the classic Thracia effect where if a unit’s fatigue >= their max HP, they are barred from deployment in the next chapter
lt-maker.readthedocs.io
. The engine can also handle alternative fatigue behaviors (e.g. applying status effects when fatigued) by using other values of this variable
lt-maker.readthedocs.io
, but for Thracia we’ll use the mode that prevents unit deployment once fatigue threshold is exceeded (Thracia’s threshold is exactly the unit’s HP)
serenesforest.net
.

Implementation: This feature is largely plug-and-play. We will enable the Fatigue constant in LT’s constants config and set _fatigue = 1 for Thracia-style rules
lt-maker.readthedocs.io
. The engine will then automatically accumulate fatigue for each unit when deployed. By default, LT adds fatigue each time a unit is used in a map (likely +1 per chapter deployed)
lt-maker.readthedocs.io
. We may need to extend this to increment fatigue per action (Thracia accumulates points for every combat or staff use, not just per chapter). If the engine’s default is too simplistic, we can use LT’s event system to increment a unit’s fatigue variable after each battle or staff use. However, given LT’s emphasis on replicating Thracia, it might already handle per-action fatigue – this needs verification. In any case, adjusting fatigue accumulation via scripting is feasible if needed (e.g., an event trigger on each action to unit.fatigue += 1, and perhaps extra for staff usage if we want to mirror the rank-based increments).

For deployment restrictions, LT will automatically exclude fatigued units if _fatigue is set to 1
lt-maker.readthedocs.io
. We should confirm the UI signals this (e.g., the unit might be grayed out or marked “Fatigued” on the prep screen). If not, we can modify the pre-battle menu via the engine’s modifiable code to display a fatigue icon or simply prevent selection with a message. Additionally, implementing Stamina Drinks is straightforward: we can create an item that, when used, sets a unit’s fatigue to 0 (this can be done with LT’s item effect scripting).

Overall, LT provides the structure for fatigue – we mostly need to tune the details to Thracia’s exact formula. This is a big win, as managing persistence of fatigue between chapters manually would be complex; instead the engine’s game variables handle it inherently. We will double-check that “Max HP” is indeed used as the fatigue limit (likely the engine uses the unit’s HP stat as the threshold by default, matching Thracia). Given these capabilities, Fatigue can be replicated with minimal custom code, aside from possibly increment adjustments and ensuring the UI communicates fatigue status.
Capture Mechanic

Engine support: Partially (requires custom events/skills) – Lex Talionis does not have Thracia-style capture as a simple default command, but it absolutely can be implemented through its skill and event system. In fact, the official LT documentation provides a step-by-step “Creating a Capture skill” tutorial specifically for Thracia/Fates capture
lt-maker.readthedocs.io
lt-maker.readthedocs.io
. This demonstrates that the engine is capable of the capture workflow with some scripting. The LT approach uses a custom Combat Art (a special attack command) and global events to simulate the capture process.

Implementation: We will follow the LT capture tutorial closely. The high-level strategy is:

    Define a Capture command/skill: In LT, one can create a new command (like a combat art named “Capture”) that is available to certain units (we’ll likely give it to all player units or those who meet a condition). This capture attack will be set up to automatically halve the attacker’s key stats during combat
    lt-maker.readthedocs.io
    (the tutorial shows how to apply stat modifiers for the battle). That replicates the reduced stats in Thracia’s capture attempt
    serenesforest.net
    .

    Post-battle check event: We create a global event that triggers after combat if the Capture command was used. This event will check if the defender died and the capture conditions are met (attacker’s Build > enemy’s Build, or if enemy is unarmed – Thracia lets you capture unresisting enemies automatically)
    lt-maker.readthedocs.io
    lt-maker.readthedocs.io
    . In LT’s event scripting, this is done with if conditions on unit stats and equipment.

    Rescuing the enemy: If conditions pass, the event will “rescue” the enemy unit. LT does not distinguish between rescuing allies and capturing enemies in its mechanics – instead it uses the same underlying system (the Pair Up/Rescue functionality). The tutorial uses the pair_up command to attach the defeated enemy to the player unit as if rescuing them
    lt-maker.readthedocs.io
    . We will ensure the engine’s Pair Up constant is disabled (so it acts in simple rescue mode, not Fates dual-stance mode) and then use it to carry enemies. The documentation notes that if Pair Up is off, the pair_up command effectively performs a classic rescue
    lt-maker.readthedocs.io
    . So the player unit will now be carrying the enemy.

    Item transfer: Once captured (i.e. the enemy is now a carried unit), the player can trade items off the captive. In Fire Emblem, you can normally trade with a unit you are rescuing, and since LT now treats the enemy as a “rescued” unit, trading their items should be possible. In the tutorial, they actually change the enemy to a player-team unit temporarily to facilitate item transfer
    lt-maker.readthedocs.io
    . We might follow that approach – e.g. set the enemy’s faction to ally upon capture so their items can be taken, then handle their fate on release.

    Releasing or dropping: We must handle what happens when a captured enemy is dropped. In Thracia, dropping a captured enemy kills them (they disappear from the map, presumed dead or fled). The LT tutorial handles this by a clever trick: it sets the captured unit’s HP to 0 immediately after capture and keeps them in the rescued state
    lt-maker.readthedocs.io
    . Units with 0 HP don’t die until they’re on the map and an update occurs, so as long as you keep them carried, they linger. The moment you drop them, an event checks for any unit with 0 HP on the map and formally kills them
    lt-maker.readthedocs.io
    . This ensures that captives die upon being dropped (or at chapter end if still held). We will implement those global events (“Kill unit if HP=0 when not carried”) as per the guide
    lt-maker.readthedocs.io
    .

    Preventing escape/recruit bugs: The tutorial suggests adding a safeguard so that if a chapter ends while you are still carrying an enemy, you don’t accidentally “recruit” that enemy in the next map
    lt-maker.readthedocs.io
    . We will include an event at chapter victory to automatically kill any carried enemy before proceeding, mimicking Thracia’s assumption that you cannot bring a captured enemy out of the chapter.

In summary, Capture will require moderate custom scripting, but we have a proven template to follow
lt-maker.readthedocs.io
lt-maker.readthedocs.io
. This involves creating a new skill and writing a few event scripts, but no engine source-code modifications. The mechanical specifics (halved stats, build check) are all supported by LT’s scripting API. We should also implement the Thracia nuance that if an enemy has no weapon or only a staff, you can capture them regardless of Build
lt-maker.readthedocs.io
(because they can’t fight back). The event script already accounts for that, checking if the enemy cannot deal damage and then allowing capture unconditionally
lt-maker.readthedocs.io
.

One thing to verify is the stat penalties while carrying: After capturing, the unit is effectively rescuing an enemy. In Thracia, as noted, the rescuer’s stats remain halved until they drop the enemy
serenesforest.net
. LT’s base rescue mechanic (from GBA) typically imposes a Skill/Speed penalty or uses the aiding unit’s Aid stat, but not a full half reduction. We likely need to implement the Thracia carry penalties. This can be done by giving a status or skill to any unit that is carrying someone which halves their stats. LT’s skill system could potentially apply a stat modifier when a unit is in “pair_up” state. If this isn’t built-in, we can create an event that triggers on rescue (capture) to apply a status effect called “Carrying” that reduces the unit’s Strength/Magic/Skill/Speed/Defense by 50%. LT allows defining custom status effects or conditional stat equations, so this is doable. (For example, we might define equations for effective Strength that check “if unit is carrying another, use half of base Strength” – the engine’s stat formula editor is very flexible.)

With these considerations, Capture is feasible in LT. It’s not a one-click setting, but the combination of custom combat arts and events covers it. The decomp data (and Serenes) gave us the exact conditions and stat modifications to replicate, and LT’s tutorial confirms no unknown blockers exist. We will allocate time to carefully test edge cases (multiple captures, capturing bosses, etc.), but overall this appears implementable with the LT engine’s provided tools
feuniverse.us
.
Leadership Stars

Engine support: Yes (built-in toggle with configuration) – Lex Talionis directly supports FE5-style leadership bonuses. In the Constants Editor, there is an option for “Global Leadership Stars” which can be enabled
lt-maker.readthedocs.io
. The documentation outlines the steps to set this up
lt-maker.readthedocs.io
lt-maker.readthedocs.io
:

    Enable Global Leadership Stars: Check the box for this constant, which tells the engine to activate leadership star functionality
    lt-maker.readthedocs.io
    .

    Define a LEAD stat: In LT’s Stats editor, we create a new stat (let’s call it “LEAD”) that represents the number of leadership stars a unit has
    lt-maker.readthedocs.io
    . We would assign this stat to relevant characters (e.g. Leif might have 1 or 2, Finn has some, etc., as in Thracia).

    Provide equations for the bonus: We then define equations (in the Equations editor) named LEAD_HIT and LEAD_AVOID which determine how much Hit and Avoid bonus each star provides
    lt-maker.readthedocs.io
    . To match Thracia, these equations will simply be = 3 * unit.LEAD (since each star is +3%). The engine will then add that many points to hit and avoid for all allies if a unit with LEAD stars is on the team.

Once configured, the engine handles applying the leadership bonuses globally in calculations. We can confirm the formula against Thracia: Serenes Forest states Leadership bonus = (Sum of allied leadership stars) × 3 to Hit and Avoid
serenesforest.net
serenesforest.net
. We will replicate exactly that. If multiple units have stars, their contributions add up (LT will presumably sum the LEAD stat of all deployed allied units automatically as part of the equation context).

Implementation: This feature is straightforward. We need to create the stat and equations, and assign the stat value to appropriate units in our project’s database. For demonstration, we might designate one player unit with a leadership star and maybe simulate an enemy leader with stars to show enemy bonuses. LT handles the rest: during combat it will calculate hit rates including the leadership modifiers for each side. The heavy lifting (ensuring it updates when units join/leave, etc.) is managed by the engine.

One consideration is UI display: We should ensure the leadership star stat is visible on the unit’s status screen (likely we can show “★: 1” or similar). The LT engine might not have a default UI element for leadership, but since we added it as a normal stat, it can be shown alongside other stats. If needed, we can add an icon (a star symbol) next to that stat in the UI layout so it’s clear. This is a minor UI customization.

Overall, Leadership stars are essentially plug-and-play in LT
feuniverse.us
. We just align the numbers to Thracia’s (+3 per star) and the engine’s built-in support covers the effect across the whole team.
Movement Stars (Extra Move Chance)

Engine support: Indirect (achievable via skill/event scripting) – Movement stars are not a common mechanic in most FE games, so LT doesn’t list a one-click constant for them. However, the FEU community indicates that Movement Stars are possible in LT, either as an easily scriptable skill or even already included in some capacity
feuniverse.us
. In a forum comparison, it’s noted that “Movement Stars are in LT either as default toggle-able systems, or you can easily event them with Skills.”
feuniverse.us
. This suggests the engine might have some support (perhaps an example skill) but likely we will implement it ourselves using LT’s event system.

Implementation: We can implement movement stars as a passive skill that grants a chance to refresh the unit at end of turn. Here’s an approach:

    Give units a stat or skill indicating how many movement stars they have (e.g. an integer stat MSTARS or simply use the number of instances of a “Movement Star” skill).

    Use an event trigger on unit wait (when a unit ends their turn) to attempt activation. LT supports triggers like unit_wait for events
    lt-maker.readthedocs.io
    . We can set up a global event: On unit wait: if unit has >0 movement stars, generate a random number (1–100) and if ≤ (5 × stars) then grant that unit another action.

    To “grant another action”, we likely use the engine’s action management: LT can mark a unit as active again by resetting their turn status. There might be a direct command for refreshing a unit (similar to the Dancer’s effect). If not, we could simulate by removing and re-adding the unit to turn queue. However, LT being a Fire Emblem engine almost certainly has a built-in way to refresh a unit (since dancers exist).

    We also need to ensure it only activates at most once. Our event will only run when the unit manually waits, so that inherently means one chance per turn. If a unit gets refreshed, and then acts again and waits again, we might allow a second roll (Thracia’s exact behavior is debated, but generally a unit with multiple stars effectively has one combined percentage; once they get one extra action, that’s it for that turn). To keep it simple, we assume at most one extra action per turn. We may implement a flag so that if a unit’s movement star triggered, it won’t trigger again in the same turn cycle.

LT’s skill system could also handle this by defining a skill component with an “activation rate”. The forum mentions that skills can have activation rates based on arbitrary conditions
feuniverse.us
. We might create a skill called “Movement Star” with an activation rate of 5% per star, that on activation triggers a refresh. If LT allows custom skill effects, we can code an effect to refresh the unit. Alternatively, use the event method described. Either way, it’s definitely achievable with a small script.

Engine example: In SRPG Studio (a different engine) movement stars were implemented with a rule “once activated it won’t activate again for X turns”
feuniverse.us
, but Thracia doesn’t have a multi-turn cooldown (it’s just per turn chance). We will implement Thracia’s version. The LT side doesn’t require altering the core engine – just adding our custom logic in the project’s events or skill definitions.

Thus, while not a toggle, Movement Stars can be implemented with minimal scripting. We will test this carefully (to ensure the refresh doesn’t glitch the turn order or AI). The LT engine’s flexibility in event triggers should make this reliable. In terms of UI, we should present the number of movement stars on the unit’s screen (Thracia showed small ★ icons). We might simply list a stat or a skill description like “Movement ★★” to indicate two stars, so players know the unit has that ability.
Rescue Mechanics (Allies and Items)

Engine support: Yes (via Pair-Up/Rescue system, though default behavior is GBA-like) – Lex Talionis has a “Pair Up” system that, when disabled, essentially serves as a traditional Rescue system
lt-maker.readthedocs.io
. The engine’s default rescue conditions use the GBA formula (Aid ≥ target’s Con)
feuniverse.us
by default, which is slightly different from Thracia’s Build-based rule. Also, the stat penalties in GBA rescue are just -AS (attack speed) penalty, not halving all stats. We will need to adjust both the condition and penalties to mirror Thracia.

Implementation:

    Rescue condition: We have two options: (a) Repurpose the Pair Up constant as “Rescue” – if enabled, LT might always allow rescue command. But the forum snippet suggests “the rescue condition is still Aid >= Con, though.”
    feuniverse.us
    . If we cannot easily change that via settings, we might disable the built-in rescue and implement our own command similar to capture. The simplest is to stick with LT’s rescue but tweak the stats: in our project, we can set each unit’s Aid stat equal to their Build (so effectively Aid and Con become Build for everyone). And ensure mounted units have a high Con or special flag to mimic “mounted can rescue regardless”. Alternatively, use events: For example, create a “Rescue” skill that appears as a command when adjacent to an ally, and in the event check if unit.Build > target.Build or unit is mounted then pair_up them. This is similar to how we do capture but without needing to fight. This custom approach might be more accurate to Thracia’s logic.

    LT’s engine likely already has the code to physically pick up and drop units (since pair_up covers it). So we will leverage that – either by calling the pair_up action via an event (which we know works from the capture script) or by letting the player use the built-in Rescue command if it exists in the UI. If using built-in, we must accept the Aid formula or alter the underlying formula. The engine is open-source Python, so in principle we could modify the rescue condition check in code to use Build instead of Aid. That’s a possible low-level fix if needed.

    Stat penalties while rescuing: As noted, Thracia halves nearly all stats when carrying
    serenesforest.net
    . The engine’s pair_up might not automatically do that, aside from maybe reducing speed. We will implement a “Carrying” status effect (or a conditional skill) that applies to any unit currently rescuing another. This status can apply a -50% modifier to Strength, Magic, Skill, Speed, Defense, and potentially halved Movement depending on weight conditions
    serenesforest.net
    . We have the exact condition from Thracia: if the carried unit’s Build > half of carrier’s Build (with +5 allowance if carrier is mounted) then halve Movement as well
    serenesforest.net
    . It might be cumbersome to reproduce the weight allowance exactly, but we can approximate by simply halving Move whenever carrying an ally and maybe not if the carrier is much larger. Given our limited scope, we might simplify: e.g. always halve Move when rescuing an enemy (since enemies generally weigh a lot), and for rescuing allies, we could ignore the fine detail or incorporate a check if needed. Because we can fetch unit stats via events, we can script the exact condition (it’s just an if in an event or equation).

For applying the stat reductions, LT allows custom stat equations or temporary stat debuffs. For example, we could override the formula for Speed to something like: Speed = baseSpeed / 2 if unit.status("Carrying") is active. Alternatively, apply a hidden skill to the rescuer that has “-X to stats” effects (some engines let you create skills that modify stats while present).

    Dropping mechanics: Dropping an allied unit should restore the rescuer’s stats. This will happen automatically if we remove the “Carrying” status upon drop. We’ll ensure to test that picking up and dropping triggers the right events (LT likely has an event trigger for drop as well, or we can tie it to the unit no longer being in pair-up).

In summary, basic rescue is supported (since LT can carry units), but Thracia-specific nuances require customization. This includes altering the rescue eligibility to use Build and implementing the stronger stat penalties. These are manageable via LT’s scripting. We already handle enemy capture as a special case of rescue; handling ally rescue is simpler (no combat, just condition and pair_up). So we’ll mirror that pattern.

One more aspect: Thracia did not allow mounted units to be rescued at all
serenesforest.net
. We should enforce that – e.g. if a unit is mounted (or has max Build due to mount), the Rescue command shouldn’t appear for them as target. We can ensure our event checks for that.

All told, after implementing these adjustments, the rescue/carry system will function much like Thracia’s. We will need to communicate to the player the heavy stat penalty (maybe via a tooltip or by visibly halving the stats on the status screen when carrying, which the engine might show if it recalculates stats). Given the engine’s flexibility and the fact that pair_up (rescue) is a core feature, this is feasible. It will require some testing to avoid unintended interactions with the engine’s default pair up or AI, but no major roadblocks are apparent.
Staff Accuracy (Hit/Miss for Staves)

Engine support: Not explicitly, but configurable via item stats/equations – In standard Fire Emblem engines, healing staves always hit by default (no RNG). LT doesn’t mention a specific toggle for “staves can miss”, but it does allow one to define custom hit formulas and item properties. We can leverage that to reproduce Thracia’s staff hit mechanics. The FEU post cites “Heal Staves missing” as one of the FE5 systems available in LT (either by default or easily scripted)
feuniverse.us
, implying that the engine is capable of handling it.

Implementation: There are a couple of ways to do this in LT:

    Using Item Hit and Equations: We can define healing staves as items with a hit rate (e.g. 60 for a basic Heal staff) and possibly a custom accuracy equation. LT’s Equations Editor likely lets us specify the formula for staff accuracy separately from weapon accuracy. If not separate, we might treat staff uses as an attack under the hood. One approach: set the staff to have Weapon Hit = 60, and ensure the standard accuracy formula already includes 2×Skill + Luck etc. However, Thracia’s staff formula is different from normal weapon accuracy (it uses 4×Skill and ignores target avoid, etc.)
    serenesforest.net
    . We might do a custom equation specifically for staff items: for instance, LT might allow an item to have a special component or tag that changes accuracy calc. The simplest hack: treat the staff as if it were a status-inflicting attack with might 0, so that the engine uses the combat hit formula on it. Then mimic Thracia’s formula by adjusting the equation or stats:

        Thracia: Staff Hit = 60 + 4×Skill (cap 99). Normal weapons: Hit = WeaponHit + 2×Skill + Luck + etc.
        serenesforest.net
        . These are different.

        We could set the staff’s WeaponHit to 0 and then create a special accuracy formula for staff uses: e.g. an equation that if item is a staff, uses 4×Skill + a constant. Alternatively, an easier route is to incorporate the 4×Skill into the item’s “Hit” stat itself: e.g. if a unit’s Skill is X, we want total = 4X + 60. That’s not constant, so better to use an equation.

If LT doesn’t support conditional equations by weapon type directly, we have another method:

    Event scripting on staff use: We can intercept the usage of a staff with an event. For example, when a staff is used, before applying the effect, roll an RN and compare to hit chance formula manually. If the roll fails, display a “Miss” message and do not heal. If succeed, apply the heal normally. LT’s event system is powerful enough to cancel an action or branch logic. This is a bit manual but guarantees we follow the exact formula. We could even incorporate the 99% cap by capping the calculated hit.

Using events might be simpler given the formula differences, unless the engine authors already anticipated this. The presence of “Heal staves missing” in conversation suggests perhaps there’s built-in support or at least known solutions. Possibly the engine might allow us to mark a staff item with a property causing it to behave like an attack (some engines have a flag like “Staff accuracy uses Tech stat” etc.).

We should also mimic Thracia’s behavior of not consuming durability on a miss. By default, if we treat a staff like an attack, a miss would still consume the item use. We can circumvent that: if we script the miss via events, we simply don’t call the “consume use” action on a miss. If using the engine’s item system, we might have to override durability consumption (maybe by giving the staff a dummy infinite use and manually reducing it on a successful use).

It’s a bit intricate, but definitely doable with LT’s scripting. The accuracy formula itself (4×Skill + fixed base) we have from Serenes
serenesforest.net
, so no guesswork needed.

Testing and UI: We should ensure the hit chance is displayed to the player. Ideally, when a player selects the staff and target, the engine’s combat forecast (or some UI) should show “Hit: xx%”. If we implement this purely through events, the default UI might not show a percent. However, if we manage to integrate it into the item’s stats/equation, the game might show it like an attack forecast. Perhaps the easiest way: define staves as weapons that target allies and deal “negative damage” (heal) – some engines allow that. If LT doesn’t allow negative damage, we might not get an auto-forecast. In that case, we could simply display the hit in the staff’s description or via a pop-up (“Nanna’s heal chance: 78%”).

Given our scope is demonstration, it’s acceptable if this is a little hidden; but for authenticity we prefer the engine show the hit rate. We’ll explore LT’s item component system (the docs likely list components for items – maybe a “Heal” component that could include an accuracy).

In short, staves with hit rates can be implemented either by configuring them as hit-based actions or by scripting outcome. The engine’s flexibility ensures we can enforce the miss chance. This will require careful scripting but no engine modification. We will base the values directly on Thracia (e.g. a Mend staff also base 60 hit, etc., so all normal staves 60 + 4×Skill). The cap at 99% is important; we’ll enforce that in our formula or script (to avoid 100% cases). The random number should be 0–99 to allow the famous 0% hit possibility
reddit.com
– LT likely uses 2RN by default for combat, but for staff we might want to force a single RN. If the engine’s general hit uses 2RN (GBA style), our custom routine should use a single RN to mimic Thracia. That’s another detail: we might need to override the RN method for staff accuracy. If using events, we can directly roll 0–99.

Thus, Staff hit/miss is feasible. It’s a bit of custom work, but nothing conceptually impossible. We’ll test scenarios of staff misses and double staff (Thracia’s “double staff” effect probably can be omitted for simplicity unless we’re being completionist – it only affected a few healing staves doubling if the first heal didn’t top off HP
serenesforest.net
, which is an obscure mechanic).
Dismounting

Engine support: Indirect (via class change events/transformations) – LT doesn’t have a default “Dismount” button like FE3/5, but it is designed to allow class changing via events or skills (the engine even supports things like Laguz transformations, which are analogous to mounting/dismounting)
feuniverse.us
. The forum notes mention that transformations and temporary class changes are possible and can be used for dismount mechanics
feuniverse.us
. So we will implement dismount by swapping the unit’s class.

Implementation: We will use duplicate classes for mounted vs. dismounted states. For example, if we have a Paladin class (mounted), we create a counterpart class “Paladin (Foot)” with the following differences: reduced movement, possibly adjusted stats (Thracia often gave slightly lower stats when dismounted), and weapon rank limitations (only swords if originally lance knight, etc.). We will also prepare foot versions for pegasus knights, horse knights, etc., each with correct weapon accessibility.

There are two aspects to handle:

    Forced indoor dismount: We can tag each map as indoor or outdoor via a game variable or level setting. At the start of an indoor chapter, we run an event that loops through all player units and for any unit that is on a mount class, we change them to their dismounted class. LT’s event system likely has a change_class(unit, newClass) command. We must also probably unequip any disallowed weapons (or the engine will simply prevent their use if the weapon ranks don’t match – which is fine). We also might have to adjust their inventory if, say, they had a lance equipped; possibly auto-equip a sword if available. This can be done via events too (check inventory for a sword, if none, leave them with the lance which will be unusable but that’s okay for demo).

    Voluntary dismount command: Thracia allowed the player to dismount at will on the map (except it was mandatory indoors). We could implement a Dismount command available to mounted units on outdoor maps. This would simply trigger a class change to foot and perhaps consume that unit’s action for the turn (dismounting usually took the whole turn in FE3/5). We can mirror that: create a command “Dismount” that is enabled for units with a mount. When selected, run an event to change that unit’s class to the dismounted version, and maybe grey them out for the turn. Similarly, we could allow a “Mount” command to get back on (though in Thracia, mounting could be done at the start of your turn if you were dismounted on an outdoor map).

For demonstration, we might not need to get into toggling back and forth too much – it may suffice to show forced dismount indoors, and perhaps one scenario of voluntary dismount outdoors. The engine’s support for temporary class transformations can simplify this. If LT allows definition of a transformation (like “when dismount skill is used, temporarily change class and adjust stats”), that could automate switching back later. However, since indoor maps explicitly force it, we might just handle it with events rather than an explicit toggle by the player.

Weapon limitations: We’ll rely on the class definitions: e.g. if “Paladin (Foot)” class only has sword rank, then after class change any lances/axes on the unit will appear but be unusable (the engine typically won’t let you wield a weapon you lack rank for). This matches Thracia’s rule that dismounted units can’t use their mount-only weapons
serenesforest.net
. We should test that the engine gracefully handles that (it likely will, similar to how FE engines handle items when you class-change and lose a weapon rank – the item stays but is red). This is fine for a demonstration.

Stat adjustments: Thracia often reduced mounted units’ stats slightly when dismounted (e.g. -1 or -2 to some stats, and fixed their movement to a set value). We can bake those differences into the class bases of the dismounted classes, or ignore minor differences if not crucial. At minimum, movement will drop (say from 8 to 5, for cavalry). We already covered weapon rank differences.

Thus, Dismounting is very feasible through class change events. It will require creating duplicate classes and writing a few event scripts, but no engine modifications. We will ensure the indoor maps automatically flip units to foot at the start (and maybe flip back at chapter end or on the world map before the next outdoor deployment – though if the next chapter is outdoor, we can just include an event at its start to remount everyone who has a stored “preferred” class. Another method: keep one “mounted” boolean in each unit’s data and just use that along with map type to determine which version of class to load on deployment).

Since our project is small, a simpler approach: treat indoor chapters as separate scenarios where units come in pre-dismounted. We could physically change their class at the end of the previous chapter if the next is indoor, etc. But using a pre-battle event is cleaner.

Player experience: We should provide an indicator when a unit is dismounted. Perhaps by class name (the class name can say “(dismounted)”), or an icon in their portrait. Thracia had different sprites for mounted vs foot. We’ll likely be using GBA assets, so we could even swap the battle sprite if desired (the repo might have both mounted and foot sprites for some classes). This would visually reinforce the mechanic.

In conclusion, with LT’s event system and class flexibility, Mount/Dismount will be implemented reliably
feuniverse.us
. It’s mostly content work (creating classes, writing events) rather than any unknown engine coding. We will test that AI enemies on mounts also dismount indoors if needed (Thracia forced player characters; enemy behavior varied but often enemies were just set as infantry in indoor maps by design. We can simply not give indoor enemies a mount in our maps).
Escape Objectives

Engine support: Yes (via event scripting, possibly a built-in win condition) – LT supports customizable win conditions for chapters. While it doesn’t explicitly advertise an “Escape” goal in the UI by default, we can implement it through events: e.g. “if unit X reaches tile Y, chapter ends”. The FEU thread indicates Escape points are supported as either default or via events
feuniverse.us
. It’s likely not a pre-made toggle, but trivial to script.

Implementation: There are two parts: (1) how to trigger chapter completion when escaping, and (2) the Thracia-specific twist of capturing remaining units.

    Escape point trigger: We will designate a specific map tile (or area) as the escape point (like a stairway or edge of map). Then use LT’s event triggers such as unit_arrive or unit_end_movement on that tile. We can filter for the lord character if we only want the chapter to end when the main lord escapes (common in Thracia). In Thracia, usually all units can escape but you must have the main lord escape last; story ends when lord escapes. We can set up the event: If a player unit ends movement on escape tile:

        If that unit is not the main lord, remove (or flag as escaped) that unit from the map (they effectively leave). We might just hide them or move them to some holding area. Thracia gives some EXP for escaped units but we can ignore that detail.

        If that unit is the main lord: trigger the chapter end. But before ending, apply the penalty to any units still on the map (see next).

    LT’s event system can remove units or mark them as escaped easily. Possibly LT even has an escape(unit) command given that it was mentioned as supported; if not, we do manually by remove_unit and perhaps record that they escaped in a variable if needed.

    Units left behind penalty: When the main lord escapes, any ally remaining is “captured” (they don’t return in Thracia). To replicate this, as soon as the lord’s escape event runs, we loop over all remaining player units on the map and flag them as captured/killed. In practice, we can simply remove them from the roster or mark a permanent death for those units. Since our demo likely won’t carry over a full roster across many maps, we might not need to worry about reusing those units anyway. But for authenticity, we will simulate it: e.g., display a message “[Unit] was left behind!” and not allow them in later maps. Implementation-wise, if we were continuing a campaign, we’d set a status on them that prevents deployment (or remove them entirely from the party list via an event command). LT should allow editing the roster via events.

If we want, we can enforce that the player actually escapes all units: i.e. only allow ending the chapter when lord is last. Thracia doesn’t force it (you can end it with lord early but then you lose others). We might add a warning prompt in our context, but the penalty itself is the teacher.

Given that our project is just showcasing, we could contrive a scenario where the player is incentivized to escape all and then use lord. But at least we should demonstrate that if they don’t, units are lost. This can be done by a scripted narrative event on escape of the lord: “The remaining units have been captured by the enemy...”.

Engine notes: LT likely doesn’t have a built-in notion of “escaped” state for units, but that’s fine. We treat it as removing units and maybe altering some persistent variable if it were a longer game.

Victory conditioning: We will mark the chapter victory when the main lord escapes (assuming either all others are gone or not). LT’s level editor allows setting a condition or just using an event with win_game command to end the map. We’ll use the event approach.

Thus, Escape objectives are easily handled by LT’s event scripting. This is a common customization and doesn’t require any engine hack. The only complexity is the additional Thracia rule of losing units, which is also straightforward to script.

We’ll use one of our sample maps specifically to demonstrate an escape scenario. This will let us show this unique objective type works.
Pursuit Critical (Follow-up Critical Coefficient)

Engine support: Yes (toggle or formula adjustment) – The FEU commentary explicitly lists PCC (also called FCC) as one of the Thracia systems present in LT
feuniverse.us
. This implies the engine can handle altering critical hit calculations on follow-up attacks. It’s likely implemented as either a stat or an equation. Possibly the engine might have a stat for “Crit Coefficient” that multiplies crit on second attack. If not a dedicated toggle, it can be done via the formula.

Implementation: We have a few ways:

    We could add a hidden stat “PCC” for each unit and then adjust the critical rate formula in LT’s Equations editor. For example, normally Crit chance = Skill% + weapon/etc –> we can modify it: If attack is a follow-up (second strike), multiply crit chance by attacker.PCC. The engine’s equation system might allow conditional logic or at least separate calculation for first vs second attack. If that’s tricky, an alternative:

    Use LT’s skill activation system: e.g., create a skill that triggers on a follow-up hit that forces it to crit if a random roll under (Crit% * (PCC-1)) succeeds. But that’s convoluted; better to integrate in damage calc.

Given that the forum said PCC is “in LT”, I suspect the engine might already handle it if enabled. Possibly in constants or an optional rule in the config. We should search the LT documentation for “PCC” or “Follow-up crit”. (If not easily found, we assume we’ll implement manually via equations.)

We know Thracia’s values – each unit has a set PCC. For demonstration, we can give a couple of units noticeable PCC values (e.g. one with PCC 0 or 1, one with PCC 5 to show the difference). The effect is mainly visible if they have some base crit chance and double attack an enemy. We can rig an example to demonstrate (like give a hero 30% crit and PCC 5, so first hit 30%, second hit 150% (capped to 100 obviously), guaranteeing a crit on second hit – players can see the difference).

Conclusion on PCC: It should be implementable either via built-in engine support or with a custom critical equation. This is likely a minor effort relative to other mechanics. We will ensure to test that normal 1RN vs 2RN doesn’t affect our critical calculations. (Thracia uses 1 RN for hit, but crit calculation itself isn’t an RN issue beyond the chance, so that’s fine.)
Steal (Item Theft by Thieves)

Engine support: Partially (likely via skill customization) – LT certainly has the concept of a Thief ability to steal, since GBA FE had it. By default, that would be: a thief can steal a non-weapon item if thief’s Speed > enemy’s Speed. Thracia’s steal is different (Build vs Build, and can steal weapons). We will modify the conditions.

Implementation: We can modify the Steal skill or create a new one:

    Allow selection of an adjacent enemy with items. Then for each item, decide if it can be stolen. In Thracia, you can steal any single item (including equipped weapon) if your Build ≥ enemy Build (and in practice, the item’s weight ≤ your Build as well, though since Build usually equals Con/weight in Thracia, that condition overlaps – basically a strong unit can steal heavy weapons).

    We can drop the item weight nuance or include it: we have item weight values, so we could require thief’s Build ≥ item weight too.

    In LT, we’ll implement it as: when the Steal command is used on an enemy, open a item choice menu (the engine likely has a built-in flow for steal: pick an item from target’s inventory). We then check conditions – we might need to override the default check (which is probably speed-based). Possibly the engine’s Steal skill can be configured with custom requirements (the FEU thread for SRPG listed options like weight and speed for steal)
    feuniverse.us
    . If LT’s skill system is similarly data-driven, we could directly set it to use Build instead of Speed.

    If not, we can script it manually: in an event, if conditions fail, display “Cannot steal”. If pass, move the item from enemy inventory to thief’s inventory. LT likely has commands to remove and add items between units.

We should also enforce Thracia’s detail: you cannot steal an item that is too heavy for you (which is essentially the Build check anyway). Also, thracia thieves cannot capture (only combat units can capture). In our demo, we can allow only non-thief units to capture and only thieves to steal, as per original.

Given Lex Talionis’s flexibility, Steal can be adapted. It’s likely less effort than capture since no combat is involved. It’s mostly adjusting the condition to use Build. If we have trouble modding the default skill, a custom event-based steal command is fine.

We will demonstrate stealing by, for example, letting a thief steal a weapon from an enemy instead of fighting. The impact of removing the enemy’s weapon mid-battle can also be illustrated (the enemy would then be unarmed, making them easy prey or capturable without resistance – a common Thracia tactic).
Summary of Engine Support vs Custom Work

To consolidate the above analysis, below is a table of each key mechanic and how Lex Talionis can support it, plus the implementation approach:
Mechanic	Supported in LT?	Implementation in Project
Fatigue	Yes (toggleable constant)
lt-maker.readthedocs.io
lt-maker.readthedocs.io
	Enable Fatigue in constants. Engine tracks fatigue across chapters. Use _fatigue = 1 so units with fatigue ≥ HP cannot be deployed
lt-maker.readthedocs.io
. May add event scripts to increment fatigue per action (if not automatic) and implement Stamina Drink item. Built-in deployment restrictions handle resting units.
Capture	Yes (via custom skill & events)
lt-maker.readthedocs.io
feuniverse.us
	Follow LT’s Capture skill tutorial. Create a “Capture” combat art that halves attacker stats
lt-maker.readthedocs.io
. After combat, use global events to check if enemy died and Build condition
lt-maker.readthedocs.io
, then use pair_up to rescue the enemy
lt-maker.readthedocs.io
. Allow item trading from captive, and kill captive on drop or chapter end
lt-maker.readthedocs.io
lt-maker.readthedocs.io
. Requires moderate scripting but proven feasible.
Leadership Stars	Yes (built-in support)
lt-maker.readthedocs.io
lt-maker.readthedocs.io
	Enable Global Leadership Stars constant. Define a “LEAD” stat and assign star values to units
lt-maker.readthedocs.io
. Add equations so each star grants +3 Hit/Avoid to allies (matches Thracia formula
serenesforest.net
serenesforest.net
). Engine will automatically apply these bonuses globally. Just ensure the stat is visible on unit screens.
Movement Stars	Yes (via skill/event)
feuniverse.us
	Implement as a passive skill with activation rate. E.g. for each ☆, give ~5% chance to act again after ending turn
serenesforest.net
. Use an event trigger on unit_wait to roll RNG and refresh the unit if successful. Ensure only one extra action per turn. This requires custom scripting, but LT’s event system supports it.
Rescue (Allies)	Yes (via Pair Up system)
lt-maker.readthedocs.io
	Use LT’s rescue (pair_up) mechanic but adjust to Thracia rules. Possibly disable Pair Up’s fancy features and treat it as GBA-style rescue. Modify rescue condition: use Build vs Build (can script our own Rescue command if needed). Apply stat-halving penalties to rescuers (e.g. via a “Carrying” status) to mimic Thracia’s severe drop in Str/Mag/Skl/Spd/Def
serenesforest.net
. Use events to enforce mounted units cannot be rescued, etc. Mostly custom logic on top of existing carry mechanics.
Staff Hit/Miss	Yes (via custom item logic)
feuniverse.us
	Define healing staves with hit rates. Implement accuracy formula = 60 + 4×Skill, cap 99
serenesforest.net
serenesforest.net
. Possibly use custom equations or an event to perform hit check on staff use. Ensure a miss does not consume the staff or the turn (the engine may need an event to allow immediate retry if miss, as in Thracia). No built-in toggle, but can be scripted via item components or events.
Dismounting	Yes (via class change events)
feuniverse.us
	Create dismounted versions of each mounted class (adjust movement and weapon access)
serenesforest.net
. Use a pre-chapter event for indoor maps to auto-change mounted units to their foot class. Optionally, add a “Dismount/Mount” command for manual use in outdoor maps (trigger class swap and end turn). Engine supports temporary class switching (used similarly for Laguz or transformations)
feuniverse.us
. This is achieved with event scripting and class data setup.
Escape Objectives	Yes (via events)
feuniverse.us
	Script events for escape tiles: when a unit reaches the escape point, remove that unit from map. If main lord escapes, trigger chapter end. Prior to ending, loop through any remaining allies and mark them captured/removed (simulating Thracia’s penalty). Use LT’s win_game or level end event to conclude. The engine allows custom win conditions, so this is straightforward.
Pursuit Critical	Yes (supported by engine)
feuniverse.us
	If not already active, implement via critical chance equation. E.g. define a PCC stat for units. In the crit calculation, if it’s the unit’s follow-up attack, multiply their crit rate by PCC. The engine likely has an easier way (possibly a flag to use FE5 crit rules). We will confirm and use whichever method ensures follow-up crits are boosted appropriately.
Steal	Yes (via skill, needs tweak)	Use or modify LT’s Steal skill. Change condition to attacker’s Build ≥ enemy Build (and possibly ≥ item weight) instead of speed. Allow stealing of equipped weapon. Likely implement via an event that transfers the item if conditions are met. The engine can handle inventory swaps and has UI for selecting an item to steal. Minimal coding needed beyond condition check.

Table: Thracia 776 Mechanics and Lex Talionis Support

As the table shows, every core Thracia mechanic can be reproduced in Lex Talionis, with varying amounts of customization. Several (fatigue, leadership, PCC, escape) are either directly supported or very light to add. The more complex ones (capture, dismount, movement stars, staff accuracy) require custom scripts or creative use of engine features, but the engine was built with this level of modability in mind. Notably, a community post emphasizes that “Other FE5-specific systems are either already in the engine or easily made.”
feuniverse.us
– our findings agree with this sentiment.
Demonstration Maps and Asset Utilization

Since we are not recreating Thracia’s storyline or exact maps, we will design a small set of custom maps to showcase the implemented mechanics. The goal is to illustrate each feature clearly using existing LT-compatible graphics from sources like the FE-Repo (Klokinator’s Fire Emblem graphics repository) and the default LT asset pack. This repository provides a vast collection of free-to-use portraits, animations, map tilesets, map sprites, and other graphics
github.com
, ensuring we have plenty of material to build a convincing FE-style presentation without original Thracia assets.

Graphics and Map Assets: We will use GBA-styled graphics (as LT natively uses GBA dimensions and asset formats). The FE-Repo includes map tilesets and even premade map designs. For example, it has interior castle tiles, outdoor plains, etc., that we can use to create layouts reminiscent of Thracia scenarios (but not identical to actual chapters). We can also use existing GBA FE portraits to stand in for characters (or choose a set of generic or community-made portraits to assign to our demonstration units). Battle animations for classes (knight, paladin, pegasus knight, thief, etc.) are available in the repo, so all unit types we need can be represented with appropriate sprites. This saves us from drawing or ripping any Thracia graphics.

Sample Map Designs: We will prioritize quality over quantity – a handful of well-crafted scenarios is better than many filler maps. Based on the mechanics to showcase, we propose the following illustrative maps:

    Map 1: “Supply Raid” (Outdoor, open-field) – A small skirmish in which the player can utilize the Capture and Steal mechanics heavily. For instance, an enemy boss carries a valuable item or weapon; the player is encouraged to capture them to obtain it. Another enemy might hold a different item that a Thief character can steal. We’ll include a playable healer with low skill to demonstrate Staff miss chances during the battle (e.g. have them attempt to heal an ally under fire, showing that the heal can fail). Enemies can be arranged such that one is easy to capture (unarmed or weakened, to demonstrate how capture works with halved stats), and maybe an enemy brigand could capture one of the player’s units (to shock the player and let them recapture them – if we want to show the AI capturing, though that might complicate the demo). This map will familiarize the player with capture (the tutorial or an NPC can prompt: “Try capturing that enemy to seize their weapon!”). It will also showcase staff accuracy (the UI will show a hit % when using heal, or we’ll show the result of a miss). We’ll use a grassy or road tileset from FE-Repo with maybe a storage shed or supply point to justify the scenario theme.

    Map 2: “Escape the Fortress” (Indoor, escape objective) – An indoor castle map where the player’s team must dismount and escape. We’ll start this chapter in an indoor setting; thanks to our code, any mounted units (say, a cavalier and a pegasus knight in the player party) will automatically dismount on deployment
    serenesforest.net
    . This immediately lets the player see their movement is reduced and maybe their lance icon is greyed out (since they can only use swords now) – evidencing the dismount effect. The objective will be to reach a designated escape staircase within a turn limit (simulating urgency). On the enemy side, we can include an enemy commander with a Leadership star, giving his troops a visible Hit/Avoid boost (we can highlight that “The enemy leader’s authority inspires the soldiers (+Hit/Avo)”). The player might also have an allied unit with a leadership star so we can see the tug-of-war of bonuses (the engine will apply both allied and enemy leadership effects in calculations). We will also include at least one player unit with a Movement Star in this map. For example, a fast swordmaster character could have 1 or 2 movement stars (5–10% chance). During playtesting, we’d ensure their extra action triggers at least once on average – if not, we might quietly boost their activation rate for the demo (or give them 3 stars = 15% for demo purposes) so the player sees the “♪” indicator and the unit getting a second turn. The map gameplay: the player navigates corridors, maybe rescues a weak ally prisoner (showing Rescue of an ally in a tight spot), fights through some enemies, all while the enemy tries to block their escape. Once they reach the escape tile, we demonstrate the escape objective: units that escape are removed from the map, and if the main lord escapes prematurely, a scripted event will “capture” any stragglers (for demonstration we might actually encourage doing it the wrong way once to show the consequence). However, ideally the player will evacuate everyone, then the lord – at which point we trigger the chapter end. This map packs in dismounting, leadership stars, movement stars, rescue, and the escape condition all in one coherent scenario. It might be the capstone demonstration.

    (Optional) Map 3: “Final Stand” (Outdoor defense) – If needed, a third map could be used to showcase anything not yet fully demonstrated, or to allow the fatigue system to come into play more. For instance, after two consecutive maps, some of the player’s best units would be Fatigued. We can show at the start of Map 3 that those units are grayed out/unavailable due to fatigue, forcing the player to use a different squad. This map could be a simple defensive hold or another skirmish, primarily to illustrate fatigue impact on army management. We might include a PCC demonstration here explicitly: perhaps an enemy or ally with a high PCC to show a follow-up crit. However, PCC is subtle to notice unless pointed out, so we might instead include it as a footnote in our dialogue/tutorial rather than design a map around it. If Map 3 isn’t needed for any new mechanic, we could integrate the fatigue showcase into Map 2’s preparation phase (e.g., after Map 1, we show a screen where one unit is “Fatigued – must rest” and cannot be deployed in Map 2). This way, the player experiences the effect of fatigue directly in the second scenario.

The number of maps will be kept limited (likely 2 main maps, with possibly a short lead-in map or interlude if needed to set the stage). This aligns with instructions to prioritize core feature demonstration over content volume. Each map is crafted to highlight specific Thracia mechanics in action:

    Map1: Capture, Steal, Staff miss (combat-focused, outdoor).

    Map2: Dismount, Escape, Leadership, Movement Star, Rescue (objective-focused, indoor).

    (Map3: Fatigue impact, PCC, etc., if not covered).

Use of Assets: We will reuse assets smartly. For instance, FE-Repo’s portraits let us assign distinct looks to a “Lord” character (maybe using Leif’s GBA portrait from hacks or a similar noble), a paladin knight (Finn-like), a thief (generic thief portrait), etc. The map sprites and animations for these classes are readily available (e.g. cavalier and paladin animations, thief animations, bishop for healers). Using GBA assets ensures full compatibility with LT (no need to downscale or recolor anything). The FE-Repo is explicitly meant to be imported into projects (LT can import from the repo easily
feuniverse.us
).

We will leverage the tilemaps for quick map building. For example, FE-Repo contains .tmx or image files of maps; even if we don’t copy a map wholesale, we can use them as a base and modify. The indoor castle tileset from GBA FE will be great for the escape map. The outdoor plains/fort tileset works for the capture map. By using familiar FE graphics, we make it intuitive for players to recognize terrain and objects (forests, walls, escape stairs, etc.).

No original Thracia art means we won’t have the exact Thracia character sprites (which differ from GBA style), but that’s acceptable for our demonstration. The mechanics are the focus, and the visuals will still read clearly as Fire Emblem. If desired, we can include the Thracia interface quirk of a music note for movement star procs – possibly the engine already does that, or we can simulate it (maybe an icon or an effect appears when it triggers).

Demonstration considerations: Each map will have some scripted guidance or at least a few tutorial pop-ups or NPC hints explaining the new mechanics, since they are unusual. For example, an NPC in Map1 could say “You can capture enemies to take their items – try it on that soldier!” Likewise, before Map2, a note can explain “All mounted units have dismounted indoors. Their lance weapons are disabled until they mount again.” This ensures that even players unfamiliar with Thracia understand what’s happening.

We will also ensure the mechanics are visible: e.g., for leadership, perhaps display an on-screen indicator of the bonus (some fan projects show an aura or an icon when leadership is in effect). If not via engine UI, we can convey it through dialogue (“As long as I’m here, our hit rates are higher!” says a leader character). The same goes for fatigue: clearly mark a fatigued unit in the prep screen with “Fatigued” text.

In summary, the sample maps are designed to show rather than tell the Thracia mechanics, using existing graphics to create a familiar FE environment. This approach avoids needing any of Thracia’s proprietary content while still demonstrating the gameplay. The FE-Repo assets guarantee that we have a rich library of maps and sprites to work with, so production of these maps will be efficient. We’ll focus on balancing the scenarios only insofar as needed to allow the mechanics to shine (the difficulty can be toned down; these maps are more like interactive showcases or proofs of concept, not meant to be deeply challenging gameplay set-pieces).
Implementation Strategy and Next Steps

With the analysis above, we can outline a practical plan to implement these mechanics in the Lex Talionis engine:

1. Leverage Built-in Systems First: We will start by enabling and configuring all the toggleable mechanics in LT, as these provide a baseline to build on. This includes turning on Fatigue and Leadership Stars in the constants, and verifying they work (e.g., play a test across two maps to see a unit become fatigued, and check that leadership bonus is applied in combat forecasts). We will also confirm if there's a direct setting for PCC or if we need to modify the crit formula. Setting these early gives us global systems to integrate other features into. Since these are largely plug-and-play, it’s a quick win to get them operational.

2. Implement Custom Mechanics Iteratively: For features that require scripting, we will tackle them one at a time in a test environment:

    Capture & Rescue: This is one of the most complex, so we’ll implement it in a small test map first. Following the LT guide, we’ll code the Capture command and events, then test capturing various enemy types (armed, unarmed, higher Build than player to test failure, etc.). We will also implement the stat-halving on capture/rescue and test that the player’s stats return after dropping. This step also covers the general rescue mechanic, since capture essentially piggybacks on rescue. We’ll adjust the allied rescue condition (perhaps by tweaking the engine code for Aid if necessary or using a custom command for rescue as with capture). Thorough testing here ensures stability – we need to avoid bugs like captured enemies becoming playable permanently or items duplicating, etc. The tutorial from LT likely guards against such issues
    lt-maker.readthedocs.io
    . We’ll also incorporate stealing as a related mechanic (since item transfer is similar). Once capture, rescue, and steal are working in isolation, we can be confident adding them to the full project.

    Dismount & Class Change: We will create the alternate classes for dismounted units in the database. Next, write a simple event that triggers on chapter start to swap classes if indoor. We’ll test that equipment and stats behave as expected post-swap. If needed, we might have to manually remove disallowed weapons (or just let them sit unusable). We’ll also test a manual Dismount command on an outdoor test map: have a cavalier dismount via command and ensure they can remount. LT’s transformation capabilities (if any built-in) could simplify the toggling back – if not, we’ll use two separate commands or context-based event (e.g., if unit is mounted and chooses “Dismount”, change class; if currently dismounted and on a mountable class, maybe allow “Mount” to revert, though Thracia only allowed mounting outside of combat scenarios). We should consider whether to allow re-mounting mid-chapter; Thracia allowed it on prep screen but not during an indoor battle. We might decide to restrict re-mount until map is over or if unit leaves (to keep it simple – in our indoor map scenario, units won’t mount until they are out). This implementation is straightforward but we must ensure no leftover status (like if a unit is dismounted at chapter end, do we automatically mount them next map if it’s outdoors? – we can handle that by an event at next map start or simply by making the class change only temporary for that level).

    Movement Stars: Implement the movement star skill/event. We’ll test by giving a high chance to see immediate results (like give 20% and see if the refresh triggers properly with the note animation). We must ensure that when refreshed, the unit’s state in LT (action done or not) is correctly reset. We’ll look into LT’s dancer implementation for guidance (the dancer action likely has an effect “refresh target unit”). We can reuse that logic for self-refresh. Testing will involve ending turns repeatedly with that unit to observe multiple procs and ensuring only one extra move max.

    Staff Accuracy: Implement and test the staff hit formula. Possibly create a dummy “Heal” staff and a healer with known skill and check multiple uses to see that misses occur at the expected rate. We will likely print the hit rate or ensure the UI can show it. We also test that a miss doesn’t use durability or end the turn if we want to replicate Thracia exactly. If replicating exactly is too tricky (the part where you don’t consume a use or action), we might simplify: we could allow the miss to still consume the turn, but highlight the concept that it could miss. However, Thracia’s actual mechanic was forgiving (no use consumed, and the unit can try again immediately). We can achieve that by simply not ending the healer’s turn on a miss (the engine might not allow that by default if it considered an action done – so we may have to force an extra action, similar to movement star, specifically for staff misses). Perhaps easier: implement staff uses as an attack that if “misses” does nothing, but the engine would still consider that an action taken. Overriding that is possible if we treat the staff use like a dance skill rather than a normal attack (i.e., allow multiple attempts). We can approximate Thracia’s effect by allowing a double cast skill (the calculation in Thracia essentially allowed two cast attempts in one action for some staves). If it gets too convoluted, we might compromise by at least showing misses but not giving the immediate retry – but since the user specifically mentioned staff hit/miss, likely they appreciate the uniqueness, so we’ll try to mirror it closely. This will be one of the trickier polish points.

    Escape and Other Events: Implement the escape tile event and test it on a small map. Ensure that when the lord escapes with units remaining, those units are flagged appropriately (for a short demo, we might literally kill them off for demonstration purposes). We’ll test multiple units escaping out of order, making sure we don’t accidentally trigger end early. Also ensure only player units trigger it, etc. That’s straightforward event logic.

    PCC (Criticals): If the engine already has it, we just need to populate the PCC values for units. If not, we will modify the critical hit formula. We can test by setting a unit’s PCC and simulating a double attack to see if the crit rate on the second hit is multiplied. If we have to implement, maybe use a flag on the weapon or attack sequence; but given the forum statement, perhaps enabling FE5 follow-up crit is a toggle. We’ll investigate LT’s documentation or possibly a constant for “Follow-up Criticals” (some fangame engines have that option). In any case, verifying it will involve looking at damage outcomes or the battle log to see if a crit occurred as expected. We should also be careful that if a unit has PCC=0 (some do in Thracia, meaning they can never crit on follow-up), that works (essentially second attack crit% becomes 0 regardless of base). That can be tested too.

3. Integration and Interplay: Once each mechanic works in isolation, we integrate them in the actual sample maps. We’ll need to ensure they interact correctly. For example, consider a scenario: a mounted unit with a movement star captures an enemy. Potential interactions:

    Does the movement star event still trigger after a capture? (Probably yes, since the unit still ended its turn – but if we refresh a unit that’s carrying someone, that could be weird. We should probably prevent a freshly captured-carrying unit from acting again for balance, but Thracia never had that combination because movement stars weren’t on mounted units IIRC; still possible if Finn had one? Actually Finn has one movement star in Thracia, and he can capture – theoretically he could capture and then re-move, albeit still carrying. What would Thracia do? Likely allow it. Our engine should handle it, but we need to test if our refresh logic accounts for “if unit has someone rescued, they can still move again”). We might allow it, it’s not game-breaking in a demo.

    If a unit is fatigued to the point of removal, ensure they can’t circumvent it by some trick (the engine likely robustly disallows deploying them, but we should test that units flagged fatigued truly don’t appear).

    If an enemy with leadership star is captured or killed, the leadership bonus should immediately drop off – that should happen automatically since that unit is no longer on field or no longer enemy. We can check that in combat forecast swings.

    Steal vs capture: a thief could steal an enemy’s weapon making them unarmed, and then any unit can capture them regardless of Build (because our event says if enemy can’t fight, capture succeeds
    lt-maker.readthedocs.io
    ). That’s a valid Thracia tactic. We should ensure our capture event includes that edge case (the tutorial did include it
    lt-maker.readthedocs.io
    ). We’ll test that flow.

    Dropping a unit on an escape tile: if a player tries to cheese by dragging a captive to an escape, do we let them escape with a captive? Thracia didn’t allow carrying an enemy through an escape point (you had to drop or release them first). We can decide whether to simulate that; probably not needed to worry, but our event might accidentally consider a carried unit still “on map” at end. We might just kill any carried enemy on escape event anyway to avoid logical holes.

4. User Interface and Clarity: With mechanics in place, we’ll refine the UI/UX:

    Add stat displays for new stats: Fatigue (maybe not visible as a stat but as a status), Leadership (display star count), Movement Stars (perhaps just mention in ability list), PCC (we could display it as a number or leave it hidden since it was hidden in Thracia too; but for transparency in a demo, maybe show it).

    Add icons if available (FE-Repo might have icons for the fatigue or movement star – maybe not, but we can create small star icons).

    Ensure the combat forecast reflects leadership, terrain, etc., properly so that if a player compares to expectations from Thracia they match.

    Localization of terms: e.g. call Build as “Con” or “Bld” consistently, since GBA uses Con. We might rename Con to “Bld” to avoid confusion, as Thracia had both Con and Build conceptually (but essentially synonyms). Since Lex Talionis likely uses Con (constitution) in GBA terms, and we are using Build in our text, we’ll align those (potentially they are the same stat in our project).

5. Testing and Balancing: We will perform extensive testing of each scenario:

    Mechanic functionality testing: e.g., deliberately fatigue a unit by spamming fights in Map1 and see if they sit out Map2. Use a savestate or dev tools to adjust fatigue as needed to test boundary conditions (like exactly equal to HP vs just over HP).

    AI testing: Does the AI ever use capture? In Thracia, enemies would capture player units under certain conditions (e.g. capture rather than kill if they want items). We likely don’t need to implement enemy capture AI for demonstration (that’s beyond scope unless we really want to mirror it). We can script one enemy to capture a green unit as a demonstration possibly. But implementing full AI capture logic might be complex and not necessary for a fan demo. We will likely skip enemy-initiated capture for now (just ensure nothing breaks if an enemy tries).

    Edge cases: e.g., what if a unit with a leadership star is fatigued and can’t be deployed – obviously then no bonus from them, which is fine. Or if a unit with movement stars is rescued by another, do we still allow the refresh? (We could ignore that scenario).

    Difficulty and Tutorialization: Because these features are complex, we’ll keep enemy difficulty low so the player has time to experiment. We will incorporate some tutorial text on first occurrence of each mechanic.

6. Final adjustments and Gaps: Identify any gaps where the engine might not fully replicate Thracia:

    One known difference: The RNG system. Thracia used a single RN for hit calculation (with the peculiarity of 0-99 range)
    serenesforest.net
    , whereas GBA (and possibly LT by default) uses 2 RN for hit to skew towards displayed values. If Lex Talionis by default uses GBA’s 2RN, our hit rates (especially for low values) won’t feel like Thracia’s. Given our scope, we may actually want to switch to 1 RN to be authentic. The LT documentation mentions Random Seed Mechanics and perhaps an option to use single-RN mode
    lt-maker.readthedocs.io
    . If available, we will enable single RN for the project (the Constants Editor might have a setting for Fates/RD true hit or something; if not, we could override the hit calculation to one RN via a small code tweak). This is a subtle point but could be considered for authenticity.

    We should note such differences and decide whether to address them. For example, if we cannot easily allow “staff miss doesn’t consume turn”, we might choose to leave that out and note it as a minor deviation for simplicity. But ideally, we try to match it.

Given all mechanics seem feasible, there aren’t major design gaps. The main technical challenges lie in scripting certain behaviors (particularly capture and staff misses), but we have clear directions to implement those. The design challenges are ensuring players understand these mechanics in the demo, since they are unusual. But that can be solved with good instruction and scenario design as noted.

7. Next Steps / Recommendations:

    Begin implementation as outlined, starting with engine configuration and gradually adding features.

    Frequently consult the Thracia decomp or Serenes for any unclear formula (e.g., double-checking if movement star is indeed one roll for all stars or multiple rolls – we have it as a single combined chance which is correct).

    Engage with the LT community if needed. Since LT has an active community of developers (some of whom have worked on FE4/FE5 remakes on LT
    forums.serenesforest.net
    ), if we encounter any engine limitation, we can search for existing solutions or ask (for instance, someone might have already made a “staff hit rate” plugin or a “mount/dismount” utility that we could use).

    After implementing, conduct internal playtesting of the full sequence of maps, then possibly have an external tester try it without prior knowledge to see if the mechanics are understandable and stable.

By following this plan, we expect to recreate Thracia 776’s core gameplay systems with high fidelity in the LT engine. The combination of LT’s built-in toggles and its robust scripting system provides us all the tools necessary – as our analysis shows, no insurmountable technical barriers remain. It will require careful scripting and testing (especially for capture/rescue and the interplay of multiple mechanics), but it is well within the capability of the engine.

Finally, once the demo maps and mechanics are complete, we recommend writing documentation for the project detailing how each Thracia mechanic was implemented in LT. This not only helps future maintainers but also contributes to the LT knowledge base for others who may want to use similar features in their fan projects. For example, packaging the capture system or the dismount system as modular components (with credit to LT’s guide and any code we wrote) could benefit the community.

In conclusion, recreating Thracia 776’s mechanics in Lex Talionis is feasible and practical. The Thracia decomp provides accurate mechanical blueprints, and Lex Talionis offers the necessary flexibility to implement them. The planned sample maps will effectively demonstrate each feature using readily available assets, thereby achieving the project’s goals without legal or artistic hurdles. With meticulous implementation and testing, the end result will be a faithful “Thracia mechanics showcase” that both fans and developers can learn from.