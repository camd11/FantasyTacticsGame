# Thracia-Mechanics Showcase: Specification Summary

This document summarizes the core gameplay mechanics of *Fire Emblem: Thracia 776* to be implemented in the Lex Talionis engine for the "Thracia-Mechanics Showcase" project. It is based on the analysis of [`GuidingResearch.md`](GuidingResearch.md).

## 1. Core Gameplay Mechanics to Implement

The following core gameplay mechanics from *Fire Emblem: Thracia 776* have been identified for implementation:

1.  **Fatigue**: Units tire from actions and may be unable to deploy ([`GuidingResearch.md:10`](GuidingResearch.md:10), [`GuidingResearch.md:50-56`](GuidingResearch.md:50-56)).
2.  **Capture**: Units can subdue enemies to seize their items, with stat penalties during the attempt ([`GuidingResearch.md:13`](GuidingResearch.md:13), [`GuidingResearch.md:58-65`](GuidingResearch.md:58-65)).
3.  **Leadership Stars (★)**: Leader units confer global Hit/Avoid bonuses to allies ([`GuidingResearch.md:16`](GuidingResearch.md:16), [`GuidingResearch.md:67-72`](GuidingResearch.md:67-72)).
4.  **Movement Stars (☆)**: Units have a chance to gain an extra action per turn ([`GuidingResearch.md:20`](GuidingResearch.md:20), [`GuidingResearch.md:74-79`](GuidingResearch.md:74-79)).
5.  **Rescue/Carry Mechanics**: Units can carry allies or captured enemies, incurring stat penalties ([`GuidingResearch.md:23`](GuidingResearch.md:23), [`GuidingResearch.md:81-91`](GuidingResearch.md:81-91)).
6.  **Staff Accuracy**: Healing and status staves have a chance to miss based on user's Skill ([`GuidingResearch.md:26`](GuidingResearch.md:26), [`GuidingResearch.md:93-102`](GuidingResearch.md:93-102)).
7.  **Dismounting**: Mounted units are forced to dismount indoors, changing stats and weapon access ([`GuidingResearch.md:30`](GuidingResearch.md:30), [`GuidingResearch.md:104-110`](GuidingResearch.md:104-110)).
8.  **Escape Objectives**: Maps can require units to escape from designated points, with penalties for units left behind ([`GuidingResearch.md:33`](GuidingResearch.md:33), [`GuidingResearch.md:112-115`](GuidingResearch.md:112-115)).
9.  **Pursuit Critical Coefficient (PCC)**: Units have a hidden multiplier for critical hits on follow-up attacks ([`GuidingResearch.md:36`](GuidingResearch.md:36), [`GuidingResearch.md:116-119`](GuidingResearch.md:116-119)).
10. **Stealing Items**: Thieves can steal items (including equipped weapons) based on Build comparison ([`GuidingResearch.md:36`](GuidingResearch.md:36), [`GuidingResearch.md:120-124`](GuidingResearch.md:120-124)).

## 2. Detailed Mechanic Behaviors and Rules

### 2.1. Fatigue
*   **Accumulation**: Units gain fatigue for actions. Most actions: +1 fatigue ([`GuidingResearch.md:52`](GuidingResearch.md:52)). Higher-rank staves: +2 to +5 fatigue ([`GuidingResearch.md:52-53`](GuidingResearch.md:52-53)).
*   **Deployment Penalty**: If a unit's `Fatigue > Max HP` at chapter's end, they cannot be deployed in the next chapter ([`GuidingResearch.md:50-51`](GuidingResearch.md:50-51)).
*   **Reset**: Fatigue resets if the unit sits out a map or consumes a Stamina Drink item ([`GuidingResearch.md:54`](GuidingResearch.md:54)).
*   **LT Implementation Notes**:
    *   Enable Fatigue constant in LT, set `_fatigue = 1` for Thracia-style deployment restriction ([`GuidingResearch.md:136-137`](GuidingResearch.md:136-137), [`GuidingResearch.md:144-145`](GuidingResearch.md:144-145)).
    *   LT's default fatigue accumulation (e.g., +1 per chapter deployed) may need adjustment via event scripting for per-action fatigue ([`GuidingResearch.md:146-149`](GuidingResearch.md:146-149)).
    *   Stamina Drink: item effect sets unit's fatigue to 0 ([`GuidingResearch.md:152`](GuidingResearch.md:152)).

### 2.2. Capture
*   **Attempt**: A combat command. Attacker's Strength/Magic, Skill, Speed, and Defense are halved during the capture combat ([`GuidingResearch.md:58-59`](GuidingResearch.md:58-59)).
*   **Success Condition**: If the enemy is reduced to 0 HP AND the attacker's `Build > enemy's Build`, the enemy is captured ([`GuidingResearch.md:60-61`](GuidingResearch.md:60-61)). Unarmed enemies or those who cannot fight back can be captured regardless of Build ([`GuidingResearch.md:200-203`](GuidingResearch.md:200-203)).
*   **Outcome**: Captor can take all items from the captive ([`GuidingResearch.md:62`](GuidingResearch.md:62)). Captives are carried like rescued units.
*   **Symmetry**: Enemies can also capture player units ([`GuidingResearch.md:62`](GuidingResearch.md:62)).
*   **Disposition**: Captured enemies can be released or will die if dropped in battle ([`GuidingResearch.md:62-63`](GuidingResearch.md:62-63)).
*   **LT Implementation Notes**:
    *   Implement via a custom Combat Art ("Capture") and global events, following LT's tutorial ([`GuidingResearch.md:157-162`](GuidingResearch.md:157-162)).
    *   Combat Art applies stat-halving to attacker ([`GuidingResearch.md:165-166`](GuidingResearch.md:165-166)).
    *   Post-battle event checks success conditions (HP=0, Build check, or unarmed) ([`GuidingResearch.md:170-173`](GuidingResearch.md:170-173)).
    *   Use `pair_up` command (with `Pair Up` constant disabled) to carry the enemy ([`GuidingResearch.md:175-178`](GuidingResearch.md:175-178)).
    *   Item transfer may involve temporarily changing captive's faction ([`GuidingResearch.md:181-183`](GuidingResearch.md:181-183)).
    *   Dropping a captive results in their death (event script sets HP to 0 on capture, kills if on map and not carried) ([`GuidingResearch.md:185-191`](GuidingResearch.md:185-191)).
    *   Event at chapter end to kill any remaining carried enemies ([`GuidingResearch.md:194-195`](GuidingResearch.md:194-195)).
    *   Carrier penalties (see Rescue/Carry) apply ([`GuidingResearch.md:206-208`](GuidingResearch.md:206-208)).

### 2.3. Leadership Stars (★)
*   **Effect**: Each star (★) on any allied leader unit grants `+3% Hit` and `+3% Avoid` to all allied units' combat stats ([`GuidingResearch.md:67-69`](GuidingResearch.md:67-69)).
*   **Stacking**: Bonuses stack from multiple leaders and apply globally ([`GuidingResearch.md:70`](GuidingResearch.md:70)).
*   **Symmetry**: Enemy leaders also provide these bonuses to their side ([`GuidingResearch.md:70`](GuidingResearch.md:70)).
*   **LT Implementation Notes**:
    *   Enable "Global Leadership Stars" constant in LT ([`GuidingResearch.md:215-216`](GuidingResearch.md:215-216), [`GuidingResearch.md:222-223`](GuidingResearch.md:222-223)).
    *   Define a "LEAD" stat representing the number of stars a unit possesses ([`GuidingResearch.md:226-228`](GuidingResearch.md:226-228)).
    *   Define equations `LEAD_HIT = 3 * unit.LEAD` and `LEAD_AVOID = 3 * unit.LEAD` ([`GuidingResearch.md:230-232`](GuidingResearch.md:230-232)).
    *   LT engine should automatically sum LEAD from all deployed allies and apply bonuses ([`GuidingResearch.md:236-237`](GuidingResearch.md:236-237)).

### 2.4. Movement Stars (☆)
*   **Effect**: Each Movement Star (☆) gives a `5% chance` for the unit to gain a "Re-move" (act again after ending their turn) ([`GuidingResearch.md:74-75`](GuidingResearch.md:74-75)). (e.g., 2 stars = 10% chance).
*   **Limit**: Only one extra action can trigger per turn at most ([`GuidingResearch.md:76`](GuidingResearch.md:76)).
*   **Indicator**: A musical note (♪) appears when activated ([`GuidingResearch.md:77`](GuidingResearch.md:77)).
*   **LT Implementation Notes**:
    *   Implement as a passive skill or via event scripting ([`GuidingResearch.md:248-252`](GuidingResearch.md:248-252)).
    *   Units have a stat (e.g., `MSTARS`) or skill instances indicating star count ([`GuidingResearch.md:256`](GuidingResearch.md:256)).
    *   Use an event trigger on `unit_wait`: if unit has stars, roll 1-100. If `roll <= (5 * unit.MSTARS)`, refresh the unit ([`GuidingResearch.md:258-260`](GuidingResearch.md:258-260)).
    *   Use LT's unit refresh mechanism (similar to Dancer effect) ([`GuidingResearch.md:261-263`](GuidingResearch.md:261-263)).
    *   Ensure only one activation per turn cycle (e.g., using a flag) ([`GuidingResearch.md:264`](GuidingResearch.md:264)).

### 2.5. Rescue/Carry Mechanics
*   **Rescue Condition**: Rescuer's `Build > target's Build` ([`GuidingResearch.md:83`](GuidingResearch.md:83)). Mounted units gain a `+5 bonus to Build` for this check ([`GuidingResearch.md:83-84`](GuidingResearch.md:83-84)).
*   **Unrescuable**: Mounted units themselves cannot be rescued ([`GuidingResearch.md:85-86`](GuidingResearch.md:85-86)).
*   **Carrier Penalties**:
    *   Strength, Magic, Skill, Speed, and Defense are halved ([`GuidingResearch.md:87-88`](GuidingResearch.md:87-88)).
    *   If `carried unit's Build > (carrier's Build / 2)`, carrier's Movement is also halved ([`GuidingResearch.md:89-91`](GuidingResearch.md:89-91)). (The document implies the carrier's mount bonus might apply here too, [`GuidingResearch.md:295-296`](GuidingResearch.md:295-296)).
*   **LT Implementation Notes**:
    *   Use LT's `Pair Up` system with the `Pair Up` constant disabled to act as classic Rescue ([`GuidingResearch.md:277-279`](GuidingResearch.md:277-279)).
    *   Adjust rescue condition from default Aid/Con to Build vs. Build. This might involve setting unit `Aid = Build`, or creating a custom "Rescue" skill/event ([`GuidingResearch.md:285-287`](GuidingResearch.md:285-287)).
    *   Implement Thracia's severe stat penalties via a "Carrying" status effect or conditional skill/equations ([`GuidingResearch.md:292-294`](GuidingResearch.md:292-294), [`GuidingResearch.md:299`](GuidingResearch.md:299)).
    *   Script the Movement penalty condition ([`GuidingResearch.md:294-297`](GuidingResearch.md:294-297)).
    *   Use events to prevent mounted units from being targeted for rescue ([`GuidingResearch.md:305-307`](GuidingResearch.md:305-307)).

### 2.6. Staff Accuracy
*   **Formula**: `Hit% = Staff's base hit + (4 * user's Skill)`, capped at 99% ([`GuidingResearch.md:93-95`](GuidingResearch.md:93-95)).
*   **Base Hit**: Most staves have 60 base hit (e.g., Heal). Some differ (e.g., Torch staff is 100) ([`GuidingResearch.md:96-97`](GuidingResearch.md:96-97)).
*   **RNG**: Uses a single RN roll (0-99), so staves can hit at displayed 0% and miss at 99% ([`GuidingResearch.md:98-99`](GuidingResearch.md:98-99)).
*   **On Miss**: Staff use is not consumed. Unit can immediately retry (if a heal misses) ([`GuidingResearch.md:100`](GuidingResearch.md:100)).
*   **LT Implementation Notes**:
    *   Implement via custom item properties/equations or event scripting ([`GuidingResearch.md:311-314`](GuidingResearch.md:311-314)).
    *   Define staves with a base hit stat and apply the `60 + 4*Skill` formula, capped at 99% ([`GuidingResearch.md:318-326`](GuidingResearch.md:318-326)).
    *   If using event scripting: on staff use, roll RN, compare to formula. If miss, display "Miss" and do not apply effect ([`GuidingResearch.md:329-331`](GuidingResearch.md:329-331)).
    *   Ensure durability is not consumed on miss (scripted) ([`GuidingResearch.md:333-334`](GuidingResearch.md:333-334)).
    *   Implement immediate retry on miss if feasible, or note as a simplification if not ([`GuidingResearch.md:573-575`](GuidingResearch.md:573-575)).
    *   Ensure a single RN (0-99) is used for staff accuracy checks ([`GuidingResearch.md:344-346`](GuidingResearch.md:344-346)).

### 2.7. Dismounting
*   **Trigger**: Mounted units can dismount voluntarily (outdoors) or are forced to dismount at the start of indoor chapters ([`GuidingResearch.md:104-107`](GuidingResearch.md:104-107)).
*   **Effects**:
    *   Movement type changes to infantry, often with lower Move stat ([`GuidingResearch.md:108`](GuidingResearch.md:108)).
    *   Restricted to using swords (lances/axes become unusable) ([`GuidingResearch.md:108-109`](GuidingResearch.md:108-109)).
    *   Stats may be slightly adjusted ([`GuidingResearch.md:372-373`](GuidingResearch.md:372-373)).
*   **LT Implementation Notes**:
    *   Implement via class changing events/skills ([`GuidingResearch.md:353-356`](GuidingResearch.md:353-356)).
    *   Create duplicate dismounted classes (e.g., "Paladin (Foot)") with adjusted stats, movement, and weapon ranks (swords only) ([`GuidingResearch.md:358-360`](GuidingResearch.md:358-360)).
    *   Forced Dismount: Pre-chapter event for indoor maps changes class of mounted units ([`GuidingResearch.md:362-364`](GuidingResearch.md:362-364)).
    *   Voluntary Dismount: A command for mounted units on outdoor maps triggers class change and ends turn. A "Mount" command could revert this ([`GuidingResearch.md:365-367`](GuidingResearch.md:365-367)).
    *   Weapon restrictions handled by dismounted class's weapon ranks ([`GuidingResearch.md:368-371`](GuidingResearch.md:368-371)).

### 2.8. Escape Objectives
*   **Win Condition**: Player must move units to a specific escape point on the map ([`GuidingResearch.md:112-113`](GuidingResearch.md:112-113)).
*   **Penalty**: If the main lord escapes, any player unit remaining on the map is considered captured and permanently removed from the roster ([`GuidingResearch.md:113-114`](GuidingResearch.md:113-114)). The lord should ideally escape last.
*   **LT Implementation Notes**:
    *   Implement via event scripting ([`GuidingResearch.md:386-388`](GuidingResearch.md:386-388)).
    *   Designate escape tile(s)/region. Use event triggers like `unit_arrive` or `unit_end_movement` ([`GuidingResearch.md:391-392`](GuidingResearch.md:391-392)).
    *   If a non-lord unit escapes, remove them from the map (or flag as escaped) ([`GuidingResearch.md:393-395`](GuidingResearch.md:393-395)).
    *   If the main lord escapes:
        1.  Loop through all remaining player units on the map and flag them as captured/killed (e.g., remove from roster or apply permanent death status) ([`GuidingResearch.md:396`](GuidingResearch.md:396), [`GuidingResearch.md:400-401`](GuidingResearch.md:400-401)).
        2.  Trigger chapter end (e.g., using `win_game` command) ([`GuidingResearch.md:408`](GuidingResearch.md:408)).

### 2.9. Pursuit Critical Coefficient (PCC)
*   **Nature**: A hidden stat (usually 0-5) for each player unit ([`GuidingResearch.md:116-117`](GuidingResearch.md:116-117)).
*   **Effect**: Multiplies the unit's critical hit rate on their second attack of a combat round (i.e., if the unit performs a follow-up attack) ([`GuidingResearch.md:117`](GuidingResearch.md:117)).
    *   Example: Base crit 10%, PCC=3 → 30% crit on follow-up ([`GuidingResearch.md:118`](GuidingResearch.md:118)).
    *   If PCC=0, crit on follow-up is 0% ([`GuidingResearch.md:578`](GuidingResearch.md:578)).
*   **LT Implementation Notes**:
    *   May be a built-in toggle or require formula adjustment in LT ([`GuidingResearch.md:415-417`](GuidingResearch.md:415-417)).
    *   If manual: Add a hidden "PCC" stat to units. Modify the critical rate formula in LT's Equations editor to check if it's a follow-up attack and then multiply crit chance by `attacker.PCC` ([`GuidingResearch.md:420-421`](GuidingResearch.md:420-421)).
    *   Verify if LT has a constant or option for "FE5 crit rules" or "Follow-up Criticals" ([`GuidingResearch.md:425`](GuidingResearch.md:425), [`GuidingResearch.md:577-578`](GuidingResearch.md:577-578)).

### 2.10. Stealing Items
*   **Eligibility**: Thieves can steal items ([`GuidingResearch.md:120`](GuidingResearch.md:120)).
*   **Conditions**:
    *   Thief's `Build >= enemy's Build` ([`GuidingResearch.md:120-121`](GuidingResearch.md:120-121)).
    *   For weapons: Thief's `Build >= item's weight` ([`GuidingResearch.md:121`](GuidingResearch.md:121)).
*   **Target Items**: Can steal any item, including the enemy's equipped weapon ([`GuidingResearch.md:120-122`](GuidingResearch.md:120-122)).
*   **Exclusivity**: Thracia thieves cannot capture ([`GuidingResearch.md:446`](GuidingResearch.md:446)).
*   **LT Implementation Notes**:
    *   Modify LT's existing "Steal" skill or create a new one ([`GuidingResearch.md:434`](GuidingResearch.md:434)).
    *   Change the success condition from Speed-based (GBA default) to Build-based as per Thracia rules ([`GuidingResearch.md:436-438`](GuidingResearch.md:436-438), [`GuidingResearch.md:440-443`](GuidingResearch.md:440-443)).
    *   If the default skill is not configurable, implement via a custom event:
        *   Player selects "Steal" command on an adjacent enemy.
        *   An item selection menu appears.
        *   Event checks Build and item weight conditions for the selected item.
        *   If conditions pass, transfer item from enemy to thief inventory ([`GuidingResearch.md:443-444`](GuidingResearch.md:443-444)).

## 3. Potential Ambiguities and Clarifications Needed

The following areas from [`GuidingResearch.md`](GuidingResearch.md) indicate potential ambiguities or require further clarification, particularly regarding Lex Talionis (LT) engine capabilities or specific Thracia 776 data:

*   **Fatigue**:
    *   LT's default fatigue accumulation rate (per action vs. per chapter) needs verification ([`GuidingResearch.md:147-149`](GuidingResearch.md:147-149)).
    *   LT's default UI for displaying fatigued units on prep screens ([`GuidingResearch.md:151-152`](GuidingResearch.md:151-152)).
    *   Confirmation that LT uses unit's Max HP as the fatigue threshold ([`GuidingResearch.md:153-154`](GuidingResearch.md:153-154)).
*   **Capture & Rescue/Carry Penalties**:
    *   LT's default stat penalties for carrying a unit (GBA-like vs. Thracia's severe halving) and if built-in support exists for Thracia-style penalties ([`GuidingResearch.md:207-208`](GuidingResearch.md:207-208)).
    *   Configurability of LT's default rescue condition (Aid vs. Build) without source code modification ([`GuidingResearch.md:285-290`](GuidingResearch.md:285-290)).
    *   Feasibility of implementing the exact Build-based Movement penalty for carrying heavy units, or if simplification is needed ([`GuidingResearch.md:296-297`](GuidingResearch.md:296-297)).
*   **Movement Stars**:
    *   Exact level of built-in LT support for Movement Stars (toggleable feature, example skill, or fully custom script) ([`GuidingResearch.md:248-252`](GuidingResearch.md:248-252)).
    *   Specific LT command/method for refreshing a unit's action ([`GuidingResearch.md:261-263`](GuidingResearch.md:261-263)).
*   **Staff Accuracy**:
    *   Whether LT has a direct toggle for "staves can miss" or if it requires custom item/equation setup ([`GuidingResearch.md:311-312`](GuidingResearch.md:311-312)).
    *   LT's support for conditional accuracy equations based on item type (staff vs. weapon) ([`GuidingResearch.md:327-329`](GuidingResearch.md:327-329)).
    *   Availability of specific LT item properties/components to manage staff accuracy behavior ([`GuidingResearch.md:332-333`](GuidingResearch.md:332-333)).
    *   Default UI behavior for displaying staff hit percentages, especially with event-based implementations ([`GuidingResearch.md:340-341`](GuidingResearch.md:340-341)).
    *   Complexity of implementing "miss does not consume turn/use" and "immediate retry" ([`GuidingResearch.md:100`](GuidingResearch.md:100), [`GuidingResearch.md:573-575`](GuidingResearch.md:573-575)).
*   **Dismounting**:
    *   Extent of LT's built-in transformation features applicable to mount/dismount toggling ([`GuidingResearch.md:367-368`](GuidingResearch.md:367-368)).
*   **Pursuit Critical Coefficient (PCC)**:
    *   Whether LT has direct built-in support (e.g., a stat or toggle) for PCC or if it requires custom formula modification ([`GuidingResearch.md:415-418`](GuidingResearch.md:415-418), [`GuidingResearch.md:423-425`](GuidingResearch.md:423-425)).
*   **Stealing Items**:
    *   Configurability of LT's default "Steal" skill conditions (Speed vs. Build) ([`GuidingResearch.md:440-443`](GuidingResearch.md:440-443)).
*   **General Engine Behavior**:
    *   LT's default RNG system (1RN vs. 2RN) and availability of an option for 1RN to match Thracia ([`GuidingResearch.md:618-622`](GuidingResearch.md:618-622)).
    *   Terminology alignment: LT's "Con" vs. Thracia's "Build" ([`GuidingResearch.md:603-605`](GuidingResearch.md:603-605)).

## 4. Data Extraction Requirements

The following data will need to be extracted or referenced from *Fire Emblem: Thracia 776* (e.g., via `FireEmblem5/` ROM data and `FE5Tools/` utilities, or community resources like Serenes Forest based on decompiled data):

*   **Unit Stats**:
    *   Base stats for all player and enemy units (HP, Str, Mag, Skl, Spd, Def, Luk, Mov, Build/Con) ([`GuidingResearch.md:125`](GuidingResearch.md:125)).
    *   Build stat values for all characters and classes (critical for Capture, Rescue, Steal).
    *   Pursuit Critical Coefficient (PCC) values for relevant player units ([`GuidingResearch.md:116`](GuidingResearch.md:116)).
    *   Number of Leadership Stars for leader units ([`GuidingResearch.md:67`](GuidingResearch.md:67)).
    *   Number of Movement Stars for units possessing them ([`GuidingResearch.md:74`](GuidingResearch.md:74)).
*   **Item Data**:
    *   Base Hit for all staves (e.g., Heal, Mend, Restore, Torch) ([`GuidingResearch.md:96-97`](GuidingResearch.md:96-97)).
    *   Weight (Wt) for all items, especially weapons (for Steal and potentially carry penalties) ([`GuidingResearch.md:121`](GuidingResearch.md:121)).
    *   List of higher-rank staves and their specific fatigue point additions ([`GuidingResearch.md:52-53`](GuidingResearch.md:52-53)).
*   **Class Data**:
    *   Base stats for classes.
    *   Weapon ranks for mounted classes and their corresponding dismounted versions ([`GuidingResearch.md:108-109`](GuidingResearch.md:108-109)).
    *   Movement stats for mounted and dismounted classes.
*   **Mechanic-Specific Constants/Formulas**:
    *   Exact fatigue points for various actions if more detailed than "+1 for most" ([`GuidingResearch.md:52`](GuidingResearch.md:52)).
    *   Any specific conditions or nuances for mechanics not fully detailed in [`GuidingResearch.md`](GuidingResearch.md) but present in decompiled data.

## 5. Lex Talionis Engine Features to Leverage

[`GuidingResearch.md`](GuidingResearch.md) indicates several Lex Talionis engine features that can be directly leveraged or customized:

*   **Constants Editor** ([`lt-maker.readthedocs.io`](lt-maker.readthedocs.io/en/latest/_images/constants-editor.png:1)):
    *   Fatigue system toggle and `_fatigue` variable ([`GuidingResearch.md:134-137`](GuidingResearch.md:134-137)).
    *   "Global Leadership Stars" toggle ([`GuidingResearch.md:215-216`](GuidingResearch.md:215-216)).
    *   `Pair Up` constant (to disable for classic rescue) ([`GuidingResearch.md:177-178`](GuidingResearch.md:177-178)).
    *   Potential settings for RNG mode (1RN/2RN) and PCC ([`GuidingResearch.md:416`](GuidingResearch.md:416), [`GuidingResearch.md:621-622`](GuidingResearch.md:621-622)).
*   **Skill, Event, and Combat Art System**:
    *   Custom Combat Arts (for Capture) ([`GuidingResearch.md:160`](GuidingResearch.md:160)).
    *   Global and unit-specific event triggers (`unit_wait`, `unit_arrive`, post-battle, chapter start) ([`GuidingResearch.md:170`](GuidingResearch.md:170), [`GuidingResearch.md:258-259`](GuidingResearch.md:258-259), [`GuidingResearch.md:362`](GuidingResearch.md:362)).
    *   Event commands: `pair_up`, `change_class`, `remove_unit`, `win_game`, item manipulation commands ([`GuidingResearch.md:175`](GuidingResearch.md:175), [`GuidingResearch.md:363`](GuidingResearch.md:363), [`GuidingResearch.md:398`](GuidingResearch.md:398), [`GuidingResearch.md:408`](GuidingResearch.md:408), [`GuidingResearch.md:444`](GuidingResearch.md:444)).
    *   Item effect scripting (for Stamina Drink) ([`GuidingResearch.md:152`](GuidingResearch.md:152)).
    *   Custom status effects (e.g., "Carrying") ([`GuidingResearch.md:208`](GuidingResearch.md:208)).
    *   Modifiable "Steal" skill ([`GuidingResearch.md:434`](GuidingResearch.md:434)).
*   **Database Editors (Stats, Items, Classes, Equations)**:
    *   Defining custom stats (LEAD, MSTARS, PCC, Build) ([`GuidingResearch.md:226-227`](GuidingResearch.md:226-227)).
    *   Defining item properties (staff base hit) ([`GuidingResearch.md:318`](GuidingResearch.md:318)).
    *   Creating and modifying classes (for dismounted versions) ([`GuidingResearch.md:358-360`](GuidingResearch.md:358-360)).
    *   Custom stat equations (for leadership bonuses, staff accuracy, crit formulas, carrying penalties) ([`GuidingResearch.md:230-232`](GuidingResearch.md:230-232), [`GuidingResearch.md:299`](GuidingResearch.md:299)).
*   **UI Customization**:
    *   Potential modification of pre-battle menus and status screens for displaying new info (fatigue, stars) ([`GuidingResearch.md:151-152`](GuidingResearch.md:151-152), [`GuidingResearch.md:240-241`](GuidingResearch.md:240-241)).
*   **General**:
    *   Game variables for persistent data (fatigue, map properties) ([`GuidingResearch.md:153`](GuidingResearch.md:153), [`GuidingResearch.md:362`](GuidingResearch.md:362)).
    *   Transformation system (analogous to dismounting) ([`GuidingResearch.md:353-356`](GuidingResearch.md:353-356)).

This summary should serve as a foundational document for the project's specification and subsequent pseudocode design.