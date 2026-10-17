# LEGENDARY SPACE — Project Handover
*Living-universe tactics sandbox · Ben (Rodeo Games / Perchang IP) · Handover written 16 Oct 2026 (evening: situation picker), superseding the July and 8 Oct notes*

Read this top to bottom before touching the file. It is the only context a fresh session has.

---

## 1. WHAT THIS IS NOW

A **full game**, no longer a publisher demo (Ben's ruling, 1 Oct). Single-file HTML5 canvas turn-based tactics, built on Ben's sci-fi novel *Legendary Space*. The publisher demo (Hooded Horse) remains in play but is not the finish line.

**Three pillars — every change is judged against them:**
1. **Turn-based whenever action is on screen, real-time otherwise.** Free-roam on the concourse; irons out = turn-based.
2. **Everything is physically modelled. NO percentage dice.** Outcomes are comparisons of real stats, line of sight, distance, nerve vs intimidation. Never add an RNG roll to resolve an action.
3. **The game sets the scene; the player's in-game tools write the ending.** Event popups INFORM (single OK/UNDERSTOOD button, identify the actor, pause the world). They never offer solution buttons. Resolution happens through existing verbs: draw irons, walk up and talk, report to a constable, steal, buy, chase. (Exception: *verbs at a physical location* — COMPLY/RESIST to a search, BUY/STEAL on a shelf card — are fine; those are the player's actions, not the game resolving an event for them.)

**Standing rules from Ben:** any systemic action must be explained to the player by a popup or log line; British spelling in UI ("Armour"); **no long dashes (em dashes) anywhere the player reads** (17 Oct: all stripped; `TU2` greps every string literal for `—`/`\u2014` and fails the build on one, so write prose with commas, colons, full stops or `·` separators); crimes attach to the OPERATOR who did them, never the crew; rap sheets never fade ("why would a file fade from a computer?"); the world must keep a memory (per-run cast, per-visit arrivals); build one situation at a time.

**Vision ("taking your shot"):** the player picks/creates TWO operators who land at Crossport (Gateway) with minimal gear and no ship, and write their own story through systems — police, factions, crime, commerce. Ship-less start NOT yet implemented (Ben wants to test other systems first; dev boot still owns the Orrix). Failure model undecided.

---

## 2. FILES

| File | Where | Status |
|---|---|---|
| `skill_shot_prototype.html` | `/mnt/user-data/outputs/` | **THE deliverable**, ~800 KB single file. 365-test suite green. |
| `smoketest_snapshot.js` | `/mnt/user-data/outputs/` | The full harness. **Refresh every delivery** — it is the only harness that survives an environment reset. |
| `legendary_space_snapshot_v1.html`, `_v2.html` | `/mnt/user-data/outputs/` | Sacred fallbacks. NEVER touch. |
| `HANDOVER.md` | `/mnt/user-data/outputs/` | This document. |
| `game_local.html`, `smoketest.js`, `check2.js` | `/home/claude/` | **EPHEMERAL — wiped on container reset** (happened again 14→16 Oct). Restore: `cp` the two outputs files to `/home/claude/game_local.html` and `/home/claude/smoketest.js`. |
| GitHub mirror | `BenMurch1945/leg-space` (main) | **STALE — holds the 21 July upload (197 KB, pre-law/commerce).** On 16 Oct the container reset wiped `/mnt/user-data/outputs/` too; the only current copies were Ben's downloads. **Ask Ben to attach the latest prototype + `smoketest_snapshot.js` if outputs is empty.** Push the current build to the mirror when push access is granted. |

The harness reads `/home/claude/game_local.html` via `readFileSync`.

---

## 3. WORKFLOW (hard-won — follow exactly)

1. **Patch with Python `rep(old, new)` using `assert src.count(old) == 1`.** Write the whole patch as a script in the scratchpad; it is atomic (nothing writes on a mismatched anchor). On an assertion failure the file is untouched — fix the anchor and re-run the whole script.
2. **Anchor spelling is the recurring trap.** Original game code contains REAL unicode characters (`·`, `’`). Code *I* authored via double-escaped Python strings contains literal `\u00B7`/`\u2019` escapes in the JS. (Em dashes are gone from the file as of 17 Oct; don't reintroduce them.) Grep the exact text before writing an anchor. A full-width parenthesis `（` once slipped into a patch — `node --check` catches it.
3. **After every change**: re-extract the script (`re.search(r'<script>(.*)</script>', src, re.S)` → `check2.js`) → `node --check check2.js` → `node smoketest.js | grep -c ': PASS'` (count with the colon; a stray "FAIL" word in flag text broke bare counting once) → battery. **Fold these into ONE shell call** to save tokens.
4. **Batteries**: 10 runs is enough; 20–30 was belt-and-braces. Count strict `': PASS'` lines; grep `': FAIL'` for culprits. Each full run takes ~12 s.
5. **Deliver**: `cp` both files to outputs, `cmp` to verify, then `SendUserFile` on the prototype. If Ben's browser serves a stale cached copy (it happened on the 14th and cost a day), deliver under a fresh filename.
6. **No IIFEs in the game script.** The harness export shim replaces the first literal `})();` to inject `window.__G = {…}`.
7. **Tests that fail after a design change are usually stale fixtures.** Check design intent before "fixing" the game. Conversely several real bugs were only found by tests.
8. **Span excisions are surgery**: census every symbol defined inside a span before deleting it (Aug 10 lesson). After any splice, `grep -c "function name"` for duplicates.
9. **Token discipline** (Ben raised cost on 16 Oct): one feature per request; fat tool calls; targeted greps over hundred-line reads; start a fresh conversation when the context gets long.
10. A reply "stopped by a safety classifier" is not an error; the build is unaffected. Don't reproduce the withheld content.

---

## 4. THE HARNESS (`smoketest.js`)

Stubbed DOM + canvas evaluates the real script. Key facts:
- `pump(n, dtMs)` advances frames; `tNow` is the clock; `performance.now()` is stubbed to it.
- **`showEventModal` returns `false` headless** (no `querySelector`), so modal callbacks are never clicked in tests → **export granular verb functions and test those** (e.g. `bzSearchAccept`, `shopSteal`, `packEquip`).
- `els` registry caches DOM stubs by id; `__fills` records `fillText` calls (BN1 used it).
- Synthetic bullets need `trail: [], pierced: new Set()`.
- Every port test starts `G.PORT_LEVELS.gateway = G.CROSSPORT_PORT; G.doShipReset(); G.enterPort();` (EM2 deletes the level earlier) and ends `G.undockToDeck(); G.doShipReset();`. After a fight, resolve it (`checkWin()`) or `portFight` leaks into later tests.
- Civs are parked out of the way with `cv.x = W*0.95; cv.y = H*0.05; cv.errand = null`.
- Beat patrol wanders constables: tests that stage a face-to-face stop pin `dr.beat = {at:null, wt:999}`.
- Tests that need the crew hidden from enemies put them inside the hull (`W*0.5, H*0.5`).
- Labels in use (grep before naming): AA AC AI AL AM AP AR BA BE BF BK BL BN BO BR BV BZ CD CG CH CL CM CN CR CS CT CU CV CW CY DD DP DS ED EM ET EV EX FA FC FD FF FL FR FS FT GE GH GM GR GS HP HR HW IJ IR KB KD KO KP LD LG LO LP LR MG MP MS NC NG NM NV NW OB OW PB PD PH PK PL PM PN PO PR PT PV PZ QM RC RD RG RK RO RP RS RW SB SC SE SG SH SI SK SL SM SP SQ SS ST SW SY TB TM TN TU UA UC UL UN VA WD WG WN WR WS WT WV.
- Export shim (line ~63) lists everything reachable as `G.*`; extend it when adding verbs.
- **`G.sitDealAll(true)`** is switched on at the top of the test run: the picker deals EVERY open ambient so fixtures that pump into cutpurses/stops/faces are deterministic. SI1/SI4 switch it off to test the 1–2 narrowing and back on after. Any new test that needs a specific situation live must not assume the roll.
- **Faces in tests**: `faceTrigger(key, cv)` forces a face onto a given civ; `faSetup()` parks the crowd, pins the beat, and adds `familiarface` to the visit's picks. Headless, the face modals auto-take their first action (DRAW / TAKE IT / TAKE THE PAPER) because `showEventModal` returns `false`.

---

## 5. WORLD DATA

- **Rook System** (`GALAXY`, Ben's doc 16 Oct): ids `spindle` (Spindle Outpost), `rook` (Rook Transit Terminal), `gateway` (**Crossport** — the map we play on), `sanarar` (The High Terraces), `raft` (The Anchorage; full weapon market; debris halo on the star map), `ghostglass` (Window Camp; name pending), `solace` (Solace Landing; provisional). Each node: `name`, `port`, `tag`, `blurb`, `danger`, `temp`. `PORT_DESCS`/`PORT_AREAS`/`PORT_HUES`/`RUMOURS` keyed the same. Contract `LEVELS` re-homed: Open Ground→sanarar, Night Market→raft, Arachne caves→spindle, corporate→ghostglass, Corridor→rook.
- **`OLD_NODES`** in `worldEnsure()` migrates saves from the retired placeholder chart (solreach→gateway etc.). `ports.solreach` → `ports.gateway`.
- **World store**: `ship.world = {v, seed, ports:{gateway: facts}, orgs:{constabulary, freightring, greymarket, tradersguild: {rep, noticed}}}`. `bz()` = `portFacts('gateway')`; `bzSet(patch)` merges + saves; `ship.world.bazaar` is a legacy alias to the same object. `worldEnsure()` heals old saves (adds shop, orgs, migrates ids).
- **Facts fields** (bazaarSeed): crate situation (`crateHolder`, `witnessed`, `varricKnows`, `boughtFromJune`, `resolved`, `heat`, `lawAware`, `confronted`, `copHunt`…), `deadCast`, `successorDay`, `raps` (per operator), `searchedT`, `caruso`, `shop` (Kestrel's shelves), `metDay`, `varricAsked`.
- **`FACTIONS`**: constabulary, freightring ("Crossport Freight Ring" — Varric), greymarket (Hask), tradersguild (Kestrel). Ben wants a collective term for guilds/mobs/factions — undecided.
- **Cast** (`BAZAAR_CAST`): Varric (trader, freightring), June (worker), Hask (barkeep, greymarket), Kestrel (keeper, tradersguild), Dren & Brev (constables). `BZ_SUCCESSOR` Vask; `BZ_RESERVES` five response officers. `bzCastOf(name)`.
- **Crossport map** `CROSSPORT_PORT`: sealed frame, 3 arches (`doors`), venues (Chapel NW, Freight Ring office W, Kestrel Outfitters NE with 5 `shelves`, Slow Orbit/The Pit SE, June's crate apron SW), `spots` (tagged by kind), 16 extra `anchors`, `crowd: 34`, `shipZone` (the Orrix hull; civs never path through it).

---

## 6. SYSTEMS (all built, all tested)

### Concourse / free-roam
- Crowd tide: `crowdSpawn/crowdTick` at arches, gait (25% meanderers), errands via `errandNew` (visit/chat/cross) + special kinds (law, gawk, follow, stalk, slink, bolt, deliver, rob, home, approach). `errandTick(cv, dt)` is the dispatcher.
- **Pathfinding (rebuilt 17 Oct)**: `civTravel(cv, tx, ty, speed, dt)` is the one verb for EVERY walker — the tide, cast, constables, responders' followers, cleaners. Under it: `CNAV` is an 18 px **clearance grid** (`clr` 12: a cell is blocked if any standing wall expanded by 12 px, the hull, or the map edge touches it). Standing = high walls and low walls with ≥30% chunks alive (`CNAV.solid`); **rubble is floor**. Rebuilt when `walls.length`, W/H or the ship zone change, or when `cnavDirty()` is called — `damageChunk` calls it, so shredded cover re-plans within a frame. `civPathTo` = A* (binary heap, octile, no corner cutting, 60k-expansion cap); start snaps to the nearest free cell within 8, goal within 20 (`cnavFreeNear`); unreachable goal → path to the closest cell reached; string-pulled with `cnavLineFree` (grid LOS); the final leg to the exact target uses the walker's own radius (`civLineClearR(..., cv.r+1)`) so a body against a wall is reachable. `civTravel` caches the grid line test 250 ms (`cv._lc`) and the path 1.1 s (`cv._nav`); three failed steps → the walker is stood on the nearest free cell centre and re-plans (nobody stays in a wall). `civLineClear(a,b)` = wall-accurate capsule r 10 with bbox prefilter (kept for callers). Response-pack followers path to their formation slot, or to the leader if the slot is in a wall. Tests `NV1–NV3` (`nvLane()` probes for clear floor; never place test geometry on the hull at centre-map).
- `inShipZone`, `openGround(x,y,r)`, `outOfShipZone`.
- **Popups pause the world**: `showEventModal` → `simPauseStart()`; any button → `simResume()` which shifts every deadline (`respT, crimeT, friskPend.at, friskT, knots, searchedT, worldBeatT`) by the pause length. Frame loop zeroes `realDt`; `tickProps` returns early.
- **Irons**: `ironsToggle()` (#ironsbtn, bottom-left) enters/leaves turn-based without enemies. Empty enemy turn = **world beat**: `startEnemyTurn` sets `phase='enemy'`, `worldBeatT = now+1200`; the frame loop ends it. The crowd/thieves/witnesses move only during enemy phase in combat.
- `squadMoveToggle()` (#sqbtn) — squad fans around a tap.

### Law
- **Rap sheets** `facts.raps[opName] = {minor, major, what[]}`; `rapsOf/rapAdd/rapClear/rapsAnyMajor`. Major → `respT` 40 s countdown (DOM `#respClock`) → `BZ_RESERVES` pack through one arch → scene → patrol circuit (`respRouteBuild`) → sight (cone 300/LOS; <95 waives cone) of a major-rap operator → `bzArrest` modal.
- **Witnesses** `bzCrimeWitness(x,y,crime,op)`: constables (700 major/340 minor, LOS) write it themselves; else bravest civilian (`witnessNerve`) runs (`witnessRun` → 'law' errand, "!" overhead) to a cop or arch; kill the runner, kill the story. Officer deaths are read off cams at fight resolution/break-off (`killedBy`, `copCamFlush`).
- **Stops**: `bzSearch` (RESIST = minor rap + fight) → `bzFrisk` 10 s bar → `bzSearchResults` (stolen → fine 60/30 + `bzConfiscate`; badge gear → termination) ; `bzArrest` ("GET DOWN ON THE GROUND") → `bzArrestComply` fine 250/125 + confiscate + rapClear. Good-citizen gate waves through. Law-reads-faces runs on a 0.5 s throttle (`_bzSeeT`), skips `respond/hunt` cops.
- **Beat**: `beatTick(cv, dt)` — off-duty constables walk 60–230 px around their post at 52 px/s, pause, scan. Duty flags skip it: `pursue, respond, chase, escort, sweep, hunt`.
- **Both badges respond** to a crime report (`copHunt` → all converge via `civTravel`).
- **Break-off**: in a port fight, 3 consecutive enemy turns with no officer perceiving any operator (`canPerceive`, hearing 60 px counts) → `portFightBreakOff()`: fallen officers read off cams, live officers become **hunters** (`cv.hunt`, sweep spots, re-draw on sight with no second reading; downed wanted operators are processed where they lie), downed operators STAY down (`_noAutoStand`), cuffed prisoners processed via `bzArrestComply`. Banner counts "OUT OF SIGHT · n/3".
- **Cuffs**: constables walk to downed operators and cuff at reach (`copCuffPass`); cuffed = down-timer frozen; `standUp` takes them back. End-of-turn order: cuffs → dying die → scent check.
- **Officer tooltip**: HOLDS A WARRANT · NAMES / HUNTING · NAMES.
- **Manhunt/escort/sweep** live in `tickProps` law region (gated `shipDeck && !deckCombat && portDock && facts.active && facts.at === portDock`).

### Crime (NPC side)
- Cutpurse scheduler (`state.crimeT`, 15–35 s then 30–60 s): `crimeStage` picks a purposeful perp and a dwelling mark; stalk (timeout 22 s) → `bzNpcCrimeAct`. Witnessed by a nearby operator → `crookPromote` (named thief: Lelt/Whisper/Sorrel/Pike, knife, runner stats), `state.sawCrime`, scene popup, then **slink**: loiters 50–300 s working the crowd, then leaves by an arch. Cop chase rumbles slink→bolt. Verbs: `portTalk` cutpurse negotiation (take the cut / demand the pouch = strength+weapon vs brave), report to any constable (`crimeTip`), `crimeStepIn` block, shoot (armed civs convert to enemies with `wasCiv`; their body carries what they stole).
- Sleepers: plain 'Vey' (heat), knife 'Sliver' (grey ≤−2), star 'Caruso Veil'.

### Commerce
- **Universal stash**: `PACKABLE` includes weapons; 4-slot pack; verbs `lootTake` (any weapon, even unrated), `packEquip(c, pi, slot)` (old piece takes the pocket, provenance both ways), `unequipToPack`, `lootLeave`. Drag wiring in `openCharSheet`. Sized-items grid is on the backburner.
- **Provenance**: items carry `own/ownFac`; `provOf/provSet` for slots; `armoury` entries `{key, own, ownFac}|string`; `contrabandOfOp` feeds searches.
- **Kestrel Outfitters**: `facts.shop = shopSeed()` (5 of 10 weapons, priced ×1.05–1.30). Shelves drawn on the floor; hover tip (type line, big price, stat deltas vs selected operator); click → walk → `eqCardOpen(i)` card (name, PRIMARY/SIDEARM · group, NOT RATED, price, blurb, stat rows with green/red deltas, BUY / BUY & SEND TO SHIP / STEAL / LEAVE IT). Verbs `shopBuy/shopSend/shopSteal`. Porter **Tobb** carries deliveries to the ramp (`deliver` errand); 25% a nearest-hands robber (`rob` errand, 175 px/s) snatches it — collar returns it, body carries it, escape loses it. Steal: keeper sees (320/LOS) → runs to the law → **leads the officer back** (`home` errand + `escort`) → officer **sweeps the shopfront** 60 s; unseen → stocktake 60–120 s later (unnamed, "WARY"); KO'd keeper reports on waking (`grudge`); dead keeper → shop ownerless (TAKE), guild −2 → **GUILD PAPER** (no guild trade; hunters banked).
- Standing gates (`facRepCross`): constab +2 good citizens; grey +2 under the counter; ring +2 vouches; grey −2 knifeman; guild −2 paper.

### Placement & situations (16 Oct)
- `portAnchors(lvl)` = tagged spots (`SPOT_TAGS` by kind) + `lvl.anchors`. `placeAt(req, rng, used)` with `{tags, near, far, los, fallback}`; `placeBeside`. `rngFor(key)` is a seeded PRNG from `world.seed|portId|key`. **Placements are re-rolled from the seed on every port build, never stored** — editing the map in the Designer just re-rolls. `castPlacements()`: crate on a `freight` anchor, June 60–110 px away in LOS, Varric a `stall` ≥500 px from June, Hask a `counter`. `state.placed` holds the roll; the crate prop uses it.
- Landing logs "Docked at Crossport, Gateway. Port roll XXXX. Build 17 Oct · TIDY." (`BUILD` constant — bump it every delivery). A stored `visit` carries `reg` (sorted registry ids); a save whose `reg` differs re-deals the same visit, so a new build never inherits a stale hand.
- `SITUATIONS` registry: `crate` has `met()` (clock starts on first contact with June/Varric or Varric's approach) and `tick()` (30 days unattended → June sells it herself: `crateHolder 'lost'`, `resolved 'junesold'`, Varric cold). `situationsTick()` runs on landing and every frame on the concourse.
- **Varric's approach**: 6–16 s after an operator is on open ground, Varric walks over (`approach` errand, 45 s give-up), scene popup with the offer, `varricAsked`, back to his stall.

### Situation picker (16 Oct, evening)
- Registry entries carry a spec: `kind` ('chain' | 'ambient'), `weight`, `req` `{dayMin, lawMin, lawMax, rep:[{fac,min,max}]}`, `excludes:[ids]`, `cast:[names that must be alive]`, `pinned()` (mid-flight, kept across visits), `done()` (spent for this run). Live: `crate` (chain, pinned while `!resolved && (metDay != null || crateHolder !== 'june')`), `lightfingers` (ambient: cutpurse scheduler), `stopsearch` (ambient, `lawMin: 1`: minor-rap stops; **warrants are always served regardless**).
- `situationPick(force)` runs in `enterPort()` before the port build. **A visit = a day at a port**: same day re-lands reuse the roll; a new day bumps `visit.n`. `force` re-rolls the same visit (same n, same seed → same hand). Draw: pinned first → one chain by weighted draw from `rngFor('situations|'+n)` → ambients: whole pool if ≤2, else 1–2. Stored in `facts.visit = {n, day, seed, picks}` — the one placement-ish thing that IS stored, because it's world memory. Logs "Situations in play: A · B · C." (or the quiet-port line) on each new roll.
- `situationLive(id)` gates: crate prop on the apron, Varric's approach, June/Varric crate dialogue (idle lines otherwise), cutpurse scheduling, minor-rap `bzSearch`. **An unrolled save (`!facts.visit`) runs everything**, as before. `lawStrength()` = living named constables + Vask once arrived. `situationOpen(id, picks)` is the prerequisite check; `situationDraw(pool, rng)` the only dice, seeded.
- Adding a situation = one registry entry + `situationLive('id')` guards on its triggers. Tests `SI1–SI5` cover determinism, pinning/spending, prerequisites, exclusion (via a throwaway `testx` entry), and the gates.

---

### A Familiar Face (16 Oct, night) — the second situation
- Registry: `familiarface` (ambient, weight 2). Fires **once per visit**: 10–25 s after an operator is on open ground (`state.faceT`), `faceTrigger()` takes a plain tide civ 320–900 px away that is only visiting/chatting/crossing, names it from `FACE_NAMES`, rolls the face from `FACES` with `rngFor('face|'+visit.n)`, writes `facts.ff = {n, face, name, state: 'coming'|'met'|'done', outcome}`, "!" overhead, and sends it running (`approach` errand with `spd`). `faceArrive` opens the popup; `faceTick` (runs every frame on the concourse, in or out of combat) fires the RESOLVED popup via `faceResolve(outcome, text)`.
- **assassin**: popup, single DRAW → `faceAssassinFight`: `makeBoarder('runner')` with `wasCiv` + **`defence: true`**, `enterDeckCombat`, banner KNIFE OUT, `state.ffEnemy`. Resolves dead / outcold / fled (melted back into the tide at break-off).
- **friend**: returns a sidearm (`WPN_SLOTS.sidearm` first unrestricted key) into the target's pack with `own: <operator>`; pack full → he keeps it. Stays in the crowd as kind `friend` (OLD FRIEND). Resolved on the click.
- **fan**: kind `fan`, errand `fan` (follows nearest operator not in the ship zone, never past the ramp, 150–240 s then leaves by an arch), `brave: 20` so he is always the witness who runs. Gunfire → `spooked`, bolts. Resolves told / spooked / gone / dead. `FACE_FAMOUS` by the target's race.
- **help**: TAKE THE PAPER / NOT OUR BUSINESS. Paper → `facts.ffPaper = {level: <Spindle contract idx>, day}`; `postingOpen` treats that posting as open for 10 days. (Contracts still deploy only at their own port — the paper opens the door, the crew still flies.)
- **Self-defence is a crime grade** (`'defence'`): `kill()` uses it when `e.defence`. A constable who sees it: no rap, `cv.attend = <operator>`, `cleanupCall()`. A civilian who sees it runs; on reaching a badge: no rap, `attend`, `cleanupCall()`. Attending officer (law region, free-roam) walks to the operator → `bzSearch` ("about the knife"). Reach for 'defence' is the major 700; nerve threshold is the major 0.
- **Recovery crew** (the clean-up system): `bodiesOnFloor()` = dead civs + dead enemies, not bagged, not in the ship zone. `cleanupCall()` spawns `BZ_CLEANUP` (Marrow, Tallis; kind `cleaner`, fac constabulary) at the arch nearest the first body — no-op if a crew is already on the floor or nothing is down. Errand `cleanup`: nearest unclaimed body (`claimed`), 2.5 s lift, body removed from its array (`bagged`), `cv.bag++`, then `er.leaving` = nearest arch → `gone`. Waits during combat. **The beat finds bodies**: in the law region, an off-duty constable within 300 px/LOS of an unseen body marks `lawSeen`, logs "A BODY", calls the crew. No attribution without a witness — the body is just cleared.
- Tooltips: KNOWS YOU / OLD FRIEND / STARSTRUCK·SPOOKED / RECOVERY · n BAGGED. `portTalk` lines for cleaner, fan, friend.
- Tests `FA1–FA5`. Banked: GCAT representative and old enemy faces (need operator history); the assassin's client; the fan recognising a *real* famous NPC.

### The front door (17 Oct)
- **Boot**: the tail still runs `shipLoad(); worldEnsure(); renderRoster();` then `titleShow()`. Headless `titleShow` returns false (no `querySelector` on stubs) and tests drive the verbs directly. `#bnNewGame` on the ship screen now returns to the title.
- **Title** (`#titleScreen`, z 80): LEGENDARY SPACE · strapline · NEW GAME · CONTINUE (caption "DAY n · PORT · A & B", disabled with no save) · corner link SHIP SCREEN · DESIGNER (old roster/dev screen) · BUILD stamp. NEW over an existing save → `showEventModal` confirm (WRITE OVER IT / KEEP IT); one save only (`SHIP_SAVE_KEY`).
- **`OPERATOR_PRESETS`** (20): the founding four + 16 new, 4 races (human, amarok, vampire, minotaur) × 4 classes (soldier, runner, breaker, mancer), every pairing, four doubled. All standard issue `{primary:'stdautogun', sidearm:'stdknife'}` — a pistol can't be a primary under `slotLegal`, so "sidearm + knife" literally would need a slot-rule change; parked. Every preset carries `bio`; `openCharSheet`/roster cards now prefer `d.bio` over `CHAR_BIOS[i]`.
- **`newGameStart()`**: `doShipReset()` (option (b): the Orrix, 500 CR, seeded world — the dev reset underneath, which tests still use and which restores the founding four), `opPick.idx=[0,1]`, `opApply()` (SQUAD_DEFS = two clones, `rosterSelection=[0,1]`, save), `enterPort()`, `opPickShow()` (overlay `#opPick` z 82, world paused). Arrows `opPickCycle(slot, ±1)` skip the other slot's index; GO (`opPickGo`) re-applies and re-enters the port only if the pair changed, resumes, logs the ramp line.
- **`ship.where`** ('port' | 'deck') saved/loaded; `enterPort` sets 'port', `undockToDeck` sets 'deck' and saves. `continueGame()` → `enterPort()` when where==='port' (and the port plan exists), else the ship screen as before.
- Tests `FD1` (presets) and `FD2` (new game, arrows, GO, save round-trip, continue). Verified visually in headless Chromium (title → picker → port, no page errors).
- **Next for this strand** (Ben, 17 Oct): ship-less landing (Varko owns the Orrix), the operator creator, multi-map ports (doors load districts; police station for arrests). Then back to situations.

### Tidy-up (17 Oct)
- `enterPort` adds the `deck` body class (free-roam UI) itself when not in combat, plus `resize()`/`updateHud()`, so a port entered from the title or picker no longer shows the turn bars. Also resets `state.faceT` so a fresh landing starts the familiar-face clock afresh (this was also hijacking tide civs in older fixtures).
- A witnessed crime carries its place: `bzCrimeWitness` sets `crime.at = {x, y}`; when the runner reaches a constable, that officer gets `cv.scene` ("SHOW ME WHERE") and walks there in the law region (before `attend`/beat), marks bodies within 160 px `lawSeen`, logs, calls `cleanupCall()`. The response detail already targets `respScene`. Test `TU1`.

### Fixes (16 Oct, late)
- **Bodies don't wall each other in**: `buildMoveGraph` skips a squadmate already overlapping the mover; `squadUnstack(c, from)` steps a stacked body a clear radius away (deterministic angle, wall-aware), called from `standUp` and from `deckSeparate` when two still bodies sit on one spot. Tests `UN1`.
- **Melee hits bystanders**: `civStruck(cv, dmg, team, owner, sed, src)` is the one law for a civilian struck by anything — lifted out of the bullet loop (which now calls it) and used by the blade/charge dash contact loop in `followRun` and by `bluntSlam`. Thief → converts, badge → `startConstableFight`, sedative → KO, else dead + witnesses/keeper/cam logic. Tests `UN2`.
- **Quartermaster removed**: no `store` station in either port layout, no `shop` area in `PORT_AREAS` for any port, no deck-station branch, label gone. `renderStore/buyWeapon/sellWeapon/sellSalvage` still exist (dormant; QM tests still exercise them). **Lost venues**: field-salvage SELL ALL and the grey-market +2 UNDER THE COUNTER shelf had no home but the store — the grey +2 popup now just says Hask will deal direct. Re-home both at Hask's bar when Ben wants it. Non-Crossport ports now have no shop at all until they get shelves.

## 7. KNOWN GOTCHAS

- Day 0 is falsy — use `== null` checks for day stamps.
- `exitDeckCombat` auto-stands downed operators unless `state._noAutoStand`.
- Civ `ko` is permanent for collared thieves (`collared`); everyone else wakes in 35–55 s.
- The law region in `tickProps` is dead when `facts.at !== state.portDock` — the migration keeps them equal.
- `deckLive` gate: civs move in free-roam OR enemy phase only.
- The END TURN button only zeroes AP; the frame loop's phase-end check calls `startEnemyTurn`.
- Chase/escort/sweep/hunt set `pursue`; `beatTick` defers to it.

---

## 8. NEXT STEPS (Ben's plan, agreed 16 Oct)

1. ~~Situation picker~~ **DONE 16 Oct.** Still open from it: per-run cast variation (which named faces a run gets) and per-visit arrivals (new faces per landing) — the picker only rolls situations today.
2. ~~First new situation~~ **A Familiar Face DONE 16 Oct.** Library (from `docs/star_system_and_ports_v0.1.txt`, 19 entries): Light Fingers ✓, Stop and Search ✓, A Familiar Face ✓, Varric's Package ✓; Wrong Address, The Unpaid Mechanic, Something Got Loose, Going Cheap, The Competition, The Collector, The Job Interview, Fire in the Market, The Abduction, The Bounty Hunter, The Guild Dispute, The Riot, Emergency Landing, Port Lockdown, The Blackout, The Guild War. One at a time. Ben wants **multi-map ports** (doors load other districts; police station for arrests) — after situations.
3. ~~Starting pair picker~~ DONE 17 Oct (title + presets). Then: creator (later), ship-less landing (Varko owns the Orrix; acquisition is an opportunity in the Ship Graveyard), Spindle as a small outpost map, other Gateway ports.
4. Open design questions: collective term for guilds/mobs/factions; failure model; whether June "moves around a little with the package" within a visit.

**Banked backlog** (do not build unasked): insurance hunters / vengeful families for a dead keeper; lock-up + bail + breakout contracts; distraction heist (keeper "engaged" after a conversation); armour/gear on shelves; cargo hauling & smuggling between ports (needs multi-port); sized inventory grid; character creator; organisations with heads/successions; word-travels-between-ports; blood-price settlement; HANDOVER refresh each milestone.

*The thesis, proven in-build: every projectile is honest, every crime has a witness or doesn't, every badge has a name and a memory, and the port is the same place with different people in it every time you land.*
