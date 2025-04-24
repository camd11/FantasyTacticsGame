# Fire Emblem: Thracia 776 - Consolidated Mechanics Specification

## 1. Core Gameplay Loop

### 1.1. Turn Structure & Phases
- **System:** Turn-based strategy RPG on a grid map.
- **Phases:** Gameplay cycles through:
    - **Player Phase:** Player controls all allied (blue) units. Each unit typically gets one move and one action (Attack, Staff, Item, Trade, Capture, Rescue, Wait, etc.).
    - **Enemy Phase:** AI controls all enemy (red) units.
    - **Other Phase (NPC):** AI controls allied NPC (green) or neutral (yellow) units.
- **Action Economy:** Standard is one action per unit per turn. Exceptions include Movement Stars granting extra turns and specific command interactions (e.g., Multi-Trade).
- **Objective:** Varies by chapter (Seize, Escape, Defend, Defeat Boss). See Section 8.3.
- **Permadeath:** Units whose HP drops to 0 are permanently removed from the game. Items they carried are lost.
- **Game Over:** Occurs if the main Lord (Leif) reaches 0 HP, or if specific mission-critical objectives fail (e.g., protected NPC dies).

### 1.2. Map Interaction & Basic Actions
- **Grid:** Square-tile based map affecting movement and combat. Only one unit per tile (unless carrying another).
- **Cursor Control:** Player uses a cursor to select units, view information, and issue commands.
- **Menu-Driven Commands:** Actions are selected from a context-sensitive menu (Move, Attack, Staff, Item, Capture, Rescue, Trade, Wait, Dismount, Door, Chest, Talk, Escape, Give, Take, Supply).
- **Movement:** Select unit, choose destination within highlighted range based on Movement stat and terrain costs.
- **Combat Initiation:** Select 'Attack' after moving (or in place) if an enemy is in range. A battle forecast displays Hit %, Damage, and Critical % for both units.
- **Fog of War (FoW):** Some maps obscure visibility beyond a unit's vision range. See Section 8.2.
- **User Interface:** Top-down map view. Unit stats and inventory accessed via menus or status screens. Original game lacks global enemy range display.

## 2. Unit Statistics

### 2.1. Primary Stats
Defines unit capabilities. Universal stat cap is 20 for all stats except HP (80).
- **HP (Hit Points):** Health. Reaching 0 causes permadeath/game over. Threshold for Fatigue activation. Does not regenerate mid-battle unless via skill, item, or specific terrain.
- **Str (Strength):** Increases damage dealt by physical weapons (Swords, Lances, Axes, Bows). Physical Attack = Str + Weapon Might.
- **Mag (Magic):** Increases damage dealt by magical Tomes and magic swords (at range 2). Also acts as magical defense (Resistance) against magic attacks. Used in Mag vs Mag check for status staves. Magical Attack = Mag + Tome Might.
- **Skl (Skill):** Affects Hit Rate (Accuracy), Critical Hit Rate, Staff Accuracy, and activation rate of %Skills (Luna, Sol, Astra, Continue). Hit Rate heavily influenced (uses 2 * Skl).
- **Spd (Speed):** Affects Avoidance (Avo), Attack Speed (AS) for determining follow-up attacks, and eligibility for the Steal command.
- **Lck (Luck):** Minorly affects Hit Rate and Avoidance (+1 per point). Reduces enemy critical hit chance (Crit Evade = Lck / 2). Affects Miracle activation and Devil Axe backfire rate.
- **Def (Defense):** Reduces damage taken from physical attacks. Physical Defense = Def + Terrain Def Bonus.
- **Bld (Build / Constitution):** Mitigates Attack Speed penalty from physical weapon Weight. Determines ability to Rescue/Capture. Affects Stealing heavier items. Can increase via level-ups (rare growth).
- **Mov (Movement):** Base number of tiles movable on standard terrain. Can increase via level-ups (very rare growth).

### 2.2. Derived Stats
Calculated from primary stats and equipment.
- **Attack (Atk):** Str + Weapon Might (physical) OR Mag + Tome Might (magical). Effective bonus triples Might (x3).
- **Attack Speed (AS):**
    - Physical: AS = Spd - MAX(0, Weapon Weight - Bld)
    - Magical: AS = Spd - Weapon Weight (Build does not mitigate tome weight)
    - Used for doubling checks and Avoid calculation.
- **Hit Rate (Displayed):** (Weapon Hit + (Skl * 2) + Lck + Support Bonus + Leadership Bonus + Charisma Bonus + Weapon Triangle Bonus) - Target Avoid. Capped between 1% and 99%.
- **Avoid (Displayed):** (AS * 2) + Lck + Support Bonus + Leadership Bonus + Charisma Bonus + Terrain Avo Bonus.
- **Critical Rate (Displayed):** (Weapon Crit + Skl + Support Bonus) - Target Crit Evade. Capped at 25% for the first attack in combat unless via Wrath skill. PCC applies multiplier only on follow-up attacks.
- **Crit Evade (CEv):** (Target Lck / 2) + Support Bonus. Reduces enemy critical chance.

### 2.3. Special Stats & Traits
- **Leadership Stars (★):** Unit trait (0-5 stars). Each star from a deployed leader (Leif, certain enemies) grants +3 Hit and +3 Avoid to all allied units on the map. Stacks if multiple leaders present (sum total stars * 3).
- **Movement Stars (MS / ♪):** Unit trait (0-5 stars). Grants a (5 * MS)% chance to gain a second action (move and act again) after completing the first action in a turn. Activation indicated by ♪ icon.
- **Fatigue:** Hidden counter. Increases with actions (combat, staff use, dance, steal). If Fatigue > Max HP at chapter end, unit cannot deploy next chapter (unless Leif or S-Drink used). Resets when unit sits out a chapter. See Section 5.2.
- **Pursuit Critical Coefficient (PCC):** Hidden character value (0-5). Multiplies unit's calculated critical rate ONLY on follow-up attacks (second hit onwards). First hit crit chance capped at 25% (unless Wrath). PCC = 0 means no critical hits on follow-ups.

## 3. Combat System

### 3.1. Combat Flow
1.  **Initiation:** Attacker strikes first (unless Ambush skill).
2.  **Counter-Attack:** Defender strikes back if possible (survived, has weapon for range).
3.  **Follow-up (Attacker):** If Attacker AS >= Defender AS + 4, attacker strikes again.
4.  **Follow-up (Defender):** If Defender AS >= Attacker AS + 4, defender strikes again (if survived).
- **Skill Modifiers:** Skills like Ambush (Vantage) change attack order. Skills like Continue (Adept), Astra add extra hits. Brave weapons grant immediate extra hits. Wrath guarantees crit on counter.

### 3.2. Combat Formulas
(Refer to Section 2.2 Derived Stats for formula details: AS, Hit, Avoid, Damage, Critical.)
- **Damage Calculation:**
    - Physical Dmg = MAX(0, (Attacker Atk * Eff Bonus) * Crit Bonus - (Target Def + Terrain Def))
    - Magical Dmg = MAX(0, (Attacker Atk * Eff Bonus) * Crit Bonus - (Target Mag + Terrain Def))
    - Effective Bonus (Eff Bonus): x3 Might if weapon is effective.
    - Critical Bonus (Crit Bonus): x2 final damage if critical hit occurs.
- **Hit Calculation:**
    - Final Hit % = MIN(99, MAX(1, Attacker Hit Rate - Target Avoid Rate))
    - Uses 1 RN system (displayed % is actual %).
- **Critical Calculation:**
    - Final Crit % = MAX(0, (Attacker Crit Rate - Target Crit Evade))
    - Capped at 25% for first hit.
    - On follow-up attacks, Final Crit % = MAX(0, (Attacker Crit Rate - Target Crit Evade) * PCC)
- **Doubling (Follow-up / Pursuit):** Occurs if unit's AS is 4 or more points higher than opponent's AS.

### 3.3. Weapon Triangle
- **Physical:** Swords > Axes > Lances > Swords. Advantage grants +5 Hit, disadvantage imposes -5 Hit. No damage modification.
- **Magical (Anima):** Fire > Wind > Thunder > Fire. Advantage +5 Hit, disadvantage -5 Hit.
- **Light/Dark vs Anima:** Both Light and Dark magic have +5 Hit advantage against Fire, Wind, and Thunder. Anima magic suffers -5 Hit against Light/Dark. Light and Dark are neutral against each other.
- **Outside Triangle:** Bows, Staves are not part of the triangle.

### 3.4. Staff Usage & Accuracy
- **Staff Actions:** Using healing, status, or utility staves consumes a turn action.
- **Staff Accuracy:** Staves can miss. Hit Rate = MIN(99, MAX(1, Base Staff Hit + (User Skl * 4))).
    - Base Staff Hit = 100 for Torch staff.
    - Base Staff Hit = 60 for most other staves (Heal, Mend, Warp, Status, etc.).
- **Status Staff Condition:** Status staves (Sleep, Silence, Berserk, Thief) also require User Mag > Target Mag to potentially succeed. They automatically fail if Target Mag >= User Mag, or if target is on a Throne/Gate.
- **Staff Double-Casting:** Heal (Live), Mend (Relive), Physic (Reblow) have a chance to activate twice: (User Spd + User Skl + User Lck) / 2 %. Second cast only occurs if target is not fully healed by first cast.

### 3.5. Combat Skills Summary
(See Section 6 for detailed skill list)
- **Activation:** Most combat skills (Adept, Luna, Sol, Astra, Pavise) activate based on a % chance (usually Skl%). Wrath and Ambush have conditional triggers.
- **Effects:** Modify attack order (Ambush), add attacks (Adept, Astra, Brave weapons), guarantee criticals (Wrath), heal user (Sol), ignore defense (Luna), negate damage (Pavise), prevent enemy crits/skills (Awareness/Nihil).

## 4. Progression Systems

### 4.1. Experience (EXP) and Leveling
- **EXP Gain:** Awarded for combat actions (hitting, defeating enemies), staff usage (gives WExp only), dancing, stealing. Formula depends on relative levels and class power. Defeating higher-level enemies yields more EXP. Killing bosses or thieves grants bonus EXP.
- **Level Up:** Occurs at 100 EXP. Each stat has a % chance to increase by 1 based on character's growth rates.
- **Growable Stats:** HP, Str, Mag, Skl, Spd, Lck, Def, Bld, Mov can all potentially increase on level-up. Bld and Mov growth chances are typically very low (1-5%).
- **Stat Caps:** Universal cap of 20 for Str, Mag, Skl, Spd, Lck, Def, Bld. HP cap is 80. Mov cap 20.
- **Growth Modification:** Crusader Scrolls held in inventory modify growth rates for that level-up. Elite skill/mode doubles all EXP gain.

### 4.2. Promotion
- **Method:** Most units promote at Lv 10+ using a consumable Knight Proof item.
- **Universality:** Knight Proof works for nearly all promotable classes (Cavalier, Mage, Fighter, etc.).
- **Exceptions:** Leif (story event), Linoan (story event), Lara (Thief -> Dancer via event). Pre-promoted units cannot promote further.
- **Gains:** Promotion grants fixed stat bonuses based on class change, increases weapon ranks by one level (50 WExp) in existing proficiencies, and may grant proficiency (Rank E) in new weapon types. Stat gains cannot exceed the universal caps.

### 4.3. Weapon Experience (WExp) & Ranks
- **Ranks:** E (lowest) -> D -> C -> B -> A (highest). '*' rank for personal weapons.
- **WExp Gain:** +1 WExp per use for physical weapons and tomes. Staves grant WExp based on rank (E=1, D=2, C=3, B=4, A=5, *=10).
- **Rank Up:** Requires 50 WExp to advance one rank level (e.g., E to D needs 50 WExp).
- **Effect:** Rank determines which weapons/staves a unit can equip. Higher ranks allow use of more powerful equipment. No inherent combat bonuses are granted by rank itself.

## 5. Unique Game Systems

### 5.1. Capture
- **Purpose:** Primary method to acquire enemy items/weapons due to scarcity of gold and shops.
- **Conditions:** Player unit initiates Capture command vs adjacent, unmounted enemy. Requires Player Bld > Enemy Bld (if player is unmounted) OR player is mounted. Melee weapon required.
- **Execution:** Combat occurs with initiator's Str/Mag/Skl/Spd/Def halved. If enemy HP reaches 0, they are captured (not killed).
- **Post-Capture:** Captor carries the enemy. Captor suffers halved stats (Str/Mag/Skl/Spd/Def) and potentially halved Movement (if captive Bld > Carrier Bld/2).
- **Item Seizure:** Use Trade/Item command with captive to take their inventory.
- **Release:** Use Release command to free the captive (removes them from map, counts as spared, not killed for recruitment flags).
- **Enemy Capture:** Enemies can capture player units under similar conditions (especially if player unit is unarmed/weak). Captured player units lose items to the enemy and are carried off map (lost until Ch 21x potentially).

### 5.2. Fatigue
- **Accumulation:** Units (except Leif) gain Fatigue points for actions (Combat +1, Staff use +1 to +5 based on rank, Dance +1, Steal +1). Fatigue is cumulative across chapters.
- **Threshold:** If Fatigue > Max HP at the end of a chapter, the unit is "Fatigued".
- **Consequence:** Fatigued units cannot be deployed in the next chapter (forced rest).
- **Recovery:** Fatigue resets to 0 if a unit sits out a chapter. Can be instantly reset using a consumable S Drink item during preparations.
- **Impact:** Forces roster rotation and strategic management of unit usage.

### 5.3. Dismounting
- **Trigger:** Mounted units (Cavalry, Fliers) automatically dismount upon entering indoor maps. Can be done voluntarily outdoors.
- **Effects:**
    - Unit changes to corresponding infantry class.
    - Stats are reduced (loses "mounting gains").
    - Movement type changes to infantry (lower Mov, different terrain costs).
    - Weapon access changes, typically restricted to Swords only.
    - Loses mount-specific weaknesses (e.g., anti-cavalry weapons) but gains infantry vulnerabilities.
    - Loses Canto ability.
- **Remounting:** Possible on outdoor maps via Mount command. Restores stats, movement, weapon access, Canto.

### 5.4. Rescue
- **Action:** Unit uses 'Rescue' command on adjacent ally.
- **Condition:** Rescuer Bld > Target Bld. Mounted units count as having 20 Bld for this calculation only.
- **Effect:** Rescuer picks up ally. Carried ally removed from map temporarily.
- **Penalties:** Rescuer suffers halved stats (Str/Mag/Skl/Spd/Def). Movement halved if carried unit Bld > Carrier Bld / 2 (adjusted for mount bonus).
- **Utility:** Protect weakened units, transport low-Mov units.
- **Take/Drop/Give:** Commands allow transferring carried units between adjacent allies. 'Drop' places carried ally on adjacent tile (uses action).

### 5.5. Support System
- **Mechanism:** Fixed, hidden relationships between certain characters. Provides bonus if units are within 3 tiles.
- **Bonus:** Typically +10 Hit, +10 Avoid, +10 Crit, +10 Crit Evade per supporting unit in range. Some pairs give +20. Stacks up to +30 total bonus from supports. Often one-way.
- **No Conversations:** Supports exist from start, no building required.
- **Charisma Skill:** Grants +10 Hit/Avo aura to allies within 3 tiles (Nanna, Delmud, King Sword). Stacks with supports and leadership.

### 5.6. Movement Stars (Re-Action)
- **Mechanism:** Unit has 0-5 Movement Stars (MS).
- **Effect:** After completing an action, (5 * MS)% chance to gain another full turn (move and act again).
- **Impact:** Adds randomness, enables powerful action chains.

### 5.7. Leadership Stars
- **Mechanism:** Unit has 0-5 Leadership Stars (LS).
- **Effect:** Total LS of deployed allied leaders * 3 = % bonus to Hit and Avoid for all allies on map.
- **Impact:** Global passive buff rewarding deployment of leaders.

## 6. Skills System

Skills provide passive bonuses or trigger active effects. Acquired via character/class innate, weapon equip, or consumable Manuals.

- **Adept (Continue):** (AS)% chance for an extra attack.
- **Ambush (Vantage):** Attack first when initiated upon by enemy.
- **Astra (Shooting Star Sword):** (Skl)% chance for 5 consecutive hits at half damage.
- **Awareness (Nihil):** Negates enemy battle skills and critical hits (except Wrath).
- **Bargain:** Halves shop prices (Unused skill/manual).
- **Big Shield (Pavise):** (Level)% chance to negate incoming damage.
- **Canto:** Innate for mounted units. Allows using remaining movement after acting (except after Capture).
- **Charge (Accost/Duel):** If user/enemy survive combat round and user HP high, triggers another round.
- **Charisma (Charm):** Passive aura. Allies within 3 tiles gain +10 Hit/Avo.
- **Dance:** Command. Refresh adjacent ally's turn. (Dancer class only).
- **Elite (Paragon):** Doubles EXP gain.
- **Luna (Moonlight Sword):** (Skl)% chance to ignore enemy Def/Mag. Guarantees hit.
- **Miracle (Prayer):** (Luck * 3)% chance to guarantee dodge if attack would be lethal. Or guarantees dodge if HP is critically low.
- **Sol (Sun Sword):** (Skl)% chance to absorb HP equal to damage dealt. Guarantees hit.
- **Steal:** Command. Allows Thief/Thief Fighter to steal eligible items if Spd > target Spd and Bld > item Wt.
- **Wrath:** Guaranteed critical hit on counter-attacks (enemy phase).

## 7. Items & Equipment

### 7.1. Inventory & Convoy
- **Unit Inventory:** Max 7 items/weapons per unit.
- **Trading:** Multi-item trade between adjacent allies. Consumes initiator's action. Can swap equipped weapon of target unit even if target has moved.
- **Convoy:** Storage (128 items). Accessible in preparations menu and rare Supply tiles on maps.
- **Durability:** Weapons/staves have limited uses. Break at 0 uses. Broken items are placeholders.
- **Repair:** Extremely limited. Primarily via Safy's personal Repair staff (5 uses total).

### 7.2. Item Lists
(Includes consumables, utility items, stat boosters, skill manuals, Crusader Scrolls)

- **Consumables:** Vulnerary (full heal, 3 uses), Antidote (cure poison, 3 uses), Holy Water (+7 Mag decaying, 1 use), Torch item (FoW vision, 1 use).
- **Keys:** Door Key (1 use), Bridge Key (1 use), Chest Key (20 uses), Lockpick (Thief only, 30 uses).
- **Utility:** S Drink (reset fatigue, 1 use), Knight Proof (promotion, 1 use), Member Card (access Secret Shops).
- **Stat Boosters (Rings):** Permanently increase stats (+7 HP, +3 Str/Skl/Spd/Lck/Bld, +2 Mag/Def, +2 Mov). Single use.
- **Skill Manuals:** Teach a specific skill permanently. Single use. (Elite, Charge, Ambush, Wrath, Continue, Awareness, Sol, Luna manuals exist).
- **Crusader Scrolls:** Held items. Modify growth rates (specific +/- % per scroll). Negate non-Wrath critical hits on holder. Stackable growth effects. (12 unique scrolls: Baldo, Hezul, Dain, Noba, Neir, Odo, Ulir, Tordo, Fala, Sety, Blaggi, Heim).

### 7.3. Weapon & Staff Lists
(Refer to provided source documents for detailed tables of stats: Mt, Hit, Crit, Wt, Rng, Uses, Rank, Effects for all Swords, Lances, Axes, Bows, Anima Tomes, Light Tomes, Dark Tomes, and Staves, including Personal ('*') rank weapons.)
- **Key Weapon Effects:** Brave (2 hits), Effective (x3 Mt vs type), Poison, Sleep, Berserk, Magic Swords (ranged magic attack), Stat boosts (+Def, +Lck, etc.), Skill bestowal (Charisma, Elite, etc.).
- **Key Staff Effects:** Healing (single, AoE, ranged), Status inflict (Sleep, Silence, Berserk - requires Mag check), Status cure (Restore, Kia), Warp/Rescue/Rewarp (teleportation), Utility (Repair, Thief, Unlock, Torch).

## 8. Map Environment & Design

### 8.1. Terrain
- **Effects:** Provides combat bonuses (Avo, Def), HP recovery (Forts, Gates, Thrones, Churches), and imposes movement costs based on unit type (Infantry, Armor, Cavalry, Flier, Bandit, Pirate).
- **Key Terrain:** Plains (standard), Forest (+Avo/Def, slows ground), Mountain (high Avo/Def, restricts access), Peak (Brigand only, huge Avo), Sand (slows ground), Fort/Gate/Throne (+Def/Avo, Heal), Pillar (indoor forest), Water (Pirate/Flier only), Magic Circle (+Mag).
- **Flier Interaction:** Fliers ignore terrain movement costs but do not receive Avo/Def bonuses from terrain (except healing).

### 8.2. Fog of War (FoW)
- **Effect:** Obscures map (units and terrain) beyond vision range. Standard vision ~3 tiles.
- **Enhanced Vision:** Thieves have larger vision radius (~5+ tiles). Torch item/staff temporarily increases vision to 10 tiles (decays over turns).
- **Enemy AI in FoW:** In original Thracia 776, enemy AI largely ignores FoW limitations for movement and targeting (acts as if it has full visibility).
- **Bumping:** Moving into an unseen enemy stops movement one tile short.

### 8.3. Map Objectives & Design
- **Common Objectives:** Seize (Leif on Throne/Gate), Escape (All units out, Leif last), Defend (Survive turns or protect target).
- **Escape Rule:** If Leif escapes before other player units, remaining units are captured/lost.
- **Gaiden Chapters:** Optional side chapters unlocked by meeting specific conditions in previous chapter (e.g., save NPCs, finish within turn limit, visit location).
- **Reinforcements:** Enemies spawning mid-chapter, often triggered by turn count or player position. Can act immediately upon spawning (Ambush Spawns).
- **Design Philosophy:** Often puts player at disadvantage, emphasizes resource management (capture), utilizes Fog of War and status staves, may involve split deployments or NPC allies/enemies.

## 9. Enemy AI

- **Behavior:** Varies (Aggressive charge, Stationary guard, Pursuit, Flee).
- **Targeting:** Prioritizes units they can kill or damage heavily, especially those unable to counter-attack. Exploits low HP/Def.
- **Capture AI:** Will attempt to capture vulnerable player units (unarmed, low Bld) instead of killing. Captured units have items stolen and are carried towards escape points.
- **Steal AI:** Enemy thieves prioritize treasure chests, then may attempt to steal items from player units (if Spd/Bld sufficient).
- **Staff/Siege AI:** Uses status staves (Sleep, Berserk) on vulnerable targets (low Mag). Uses siege tomes/ballistae at max range. Unaffected by FoW for targeting.
- **Skill Use:** Uses innate/equipped skills automatically (e.g., Wrath, Charge).
- **FoW Behavior:** Ignores player FoW limitations for targeting/movement.

## 10. Classes
(Refer to provided source documents for detailed tables listing Base Stats, Max Stats (20/80), Movement Type, Weapon Ranks (including dismounted changes), Class Skills, and Promotion Paths for all playable classes.)
- **Key Class Features:** Determine weapon access, movement, base stats, innate skills (e.g., Steal for Thieves, Canto for Mounted).
- **Dismounting Impact:** Mounted classes have alternate stats/weapon sets when dismounted indoors.