---
name: fivem-mission-builder
description: Build scripted MISSIONS and repeatable EVENTS for FiveM roleplay servers, solo and co-op. Two modes on one engine. Directed/narrated missions (objective chains, dialogue beats, timers, fail conditions, branching, rewards) and repeatable random world events (heists, gang attacks, supply drops that spawn on a cooldown and players opt into). Qbox-first for rewards and inventory, with a framework-agnostic core that also runs standalone. Owns the orchestration layer. Mission state machine, objectives, triggers, per-player and shared group progress, win/lose, cleanup, and a runnable scaffold. Hands entity spawning to fivem-lua-dev and payouts to fivem-job-builder. Use whenever someone wants to create, script, or debug a FiveM mission, quest, scenario, story sequence, random event, heist, gang attack, or co-op objective. Defaults to server-authoritative Qbox-native code. Do NOT use for job/economy loops (use fivem-job-builder), general FiveM scripting (use fivem-lua-dev), single-player GTA mods, or RAGE:MP/alt:V.
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# FiveM Mission Builder

Build **missions and events** — the scripted layer that turns spawned peds, cars, and props into *gameplay with a goal*. A mission here is a sequence of objectives a player (or a group) works through, with triggers that start it, conditions that advance or fail it, and rewards at the end. This skill is the orchestration engine; it leans on the other two FiveM skills for the pieces it directs.

## Where this sits among the three FiveM skills

- **`fivem-lua-dev`** — the platform and the world. Spawning/controlling peds, vehicles, props, AI tasks, animations, blips/markers/zones, hosting, frameworks. **This skill calls into that one** for anything that puts an entity in the world.
- **`fivem-job-builder`** — job/economy loops and server-authoritative payouts. **This skill reuses that payout pattern** for mission rewards.
- **`fivem-mission-builder` (this one)** — the objective state machine on top: start a mission, advance through steps, check conditions, handle group sync, win/lose, reward. It owns *sequencing and state*, not entity creation or economy mechanics.

When a mission needs to spawn five enemy peds, this skill defines *when and why* (objective 2 spawns them, objective 3 completes when they're dead) and delegates the *how* (the actual `CreatePed`, AI tasks, relationship groups) to `fivem-lua-dev`'s `world-entities.md`. Don't re-derive spawning here.

## Pick the mode first

Both modes run on the same engine (`references/mission-engine.md`); they differ in how they start and who they target.

- **Directed / narrated mission** — a deliberate, authored experience. The player *starts* it (NPC giver, item, command, zone), then moves through a fixed (optionally branching) sequence of objectives with text/dialogue beats, timers, and fail states, ending in a reward. Solo or a fixed co-op party. Think story mission, tutorial, quest. → `references/directed-missions.md`
- **Repeatable random event** — an ambient, server-wide occurrence. The *server* spawns it on a cooldown at one of several locations, broadcasts it, and any eligible player can opt in until it resolves or times out. Re-arms after a cooldown. Think roaming heist, gang attack, supply drop, bounty. → `references/random-events.md`

Most servers want both: authored missions for content, random events for ambient life. Build the engine once, then add each mode's launcher.

## Co-op and group state (read this early)

Solo is the easy case — one player, one state record. Co-op is where missions go wrong if you don't plan it. Decisions to make up front, detailed in `references/coop-and-state.md`:

- **Per-player vs shared progress.** Does each player track their own kills, or does the group share one objective counter? Most co-op missions use *shared* objective state with *per-player* presence.
- **Who owns the state.** The **server** owns mission state, always — the same trust rule as jobs. Clients render their copy and request advances; the server validates and decides. A client must never be able to declare "objective complete."
- **Join/leave/disconnect.** What happens when a party member drops mid-mission? Fail, continue short-handed, or backfill. Decide and handle `playerDropped`.
- **Sync.** Push state changes to all participants (state bags or targeted events), don't make clients poll.

## Start-to-finish path

Read the referenced file before each step — the engine shape and the sync details are exactly what's easy to get subtly wrong.

1. **Model the mission as data, not code.** A mission is a config table: an id, a start trigger, an ordered list of objectives (each with a type, target, completion condition, optional timer/fail), and a reward block. Authoring missions as data means the engine is written once and every mission is a table. Shape in `references/mission-engine.md`.
2. **Scaffold the resource.** `python scripts/scaffold_mission.py --name mymission --mode directed --framework qbox --output <dir>` (modes: `directed`, `random`; frameworks: `qbox`, `qbcore`, `esx`, `standalone`). Emits a runnable resource with the engine, one example mission, server-authoritative advance/complete, and group-sync wired. `--help` for options.
3. **Define objectives and triggers.** Pick objective types from the engine's vocabulary (goto, kill, collect, interact, escort, defend, capture, wait/survive) and wire the start trigger (NPC/item/command/zone for directed; server scheduler for random). Detail per mode in its reference file.
4. **Wire spawns through `fivem-lua-dev`.** Objectives that need entities call into the spawning patterns from that skill. Keep the *handles* server-tracked so cleanup is reliable.
5. **Handle win / lose / cleanup.** Success → reward (server-authoritative, `fivem-job-builder` pattern). Fail/timeout/abandon → clean up every spawned entity, blip, and zone, and reset state. Leaks here are the top cause of mission scripts degrading a server over time.
6. **Sync, test, and tune.** Verify co-op state stays consistent across join/leave, confirm a client can't skip objectives or self-reward, check cleanup leaves nothing behind, and tune pacing/difficulty/cooldowns. Engine + `references/coop-and-state.md`.

## Idiomatic Qbox + ox (don't write QBCore-in-disguise)

Default to the Qbox-native surface; the engine itself is framework-agnostic, only the reward/identity hooks touch the framework:

- Player/identity: `exports.qbx_core:GetPlayer(src)`, `citizenid` as the stable key.
- UI for objectives & dialogue: `ox_lib` (`lib.notify`, `lib.showTextUI`, `lib.progressBar`, `lib.points`, `lib.zones`). Markers/blips for objective locations.
- Sync: **state bags** for mission/objective state over tick polling.
- Rewards: the `fivem-job-builder` server-authoritative payout pattern (`exports.qbx_core` money, `ox_inventory` items) — never client-decided.
- DB (only if missions persist progress): `oxmysql`.

For **standalone** (no framework), the engine runs fully; you lose only the framework reward hooks (pay players via whatever your server uses, or make rewards cosmetic/item-based through ox_inventory if present). `references/mission-engine.md` shows the framework hook as a single swappable function. QBCore/ESX differ only in those hook names — see `fivem-job-builder`'s `frameworks-jobs.md` for the map.

## Hard rules

These prevent the failures specific to *missions and events*.

**The server owns mission state and decides completion.** Every objective advance, completion, and reward is validated server-side against state the server controls — position, kills credited by the server, items actually held, timer not expired. A client event saying "I finished objective 3" is a *request*, never the truth. Same trust boundary as jobs; missions just have more steps to exploit.

**Always clean up.** Every spawned ped/vehicle/object, every blip, marker, zone, and state-bag entry created by a mission must be deleted on success, failure, timeout, abandon, *and* resource stop. Track all handles in the mission's state record and tear them down in one cleanup function. Orphaned entities are the signature failure of amateur mission scripts and they accumulate until the server hitches.

**Gate triggers server-side.** Whether a player *may* start a mission (cooldown, job, level, party size, not already in one) is decided by the server. Don't let a client start ten missions at once or re-trigger a random event off cooldown.

**Make co-op state authoritative and synced.** Shared objective counters live on the server; participants receive pushed updates. Never let one client's report mutate another's view directly.

**Don't block the thread; idle cheap.** Mission loops (timers, zone checks, "are all enemies dead?") must `Wait()` and widen intervals when idle, or use events/state bags. A mission resource should idle near-zero when no mission is active. Tear down per-frame threads when the mission ends.

**Bound and validate every trigger argument.** Mission ids, objective ids, choice indices coming from clients are hostile input — check they exist in server config and that this player is actually on that step.

**Never hardcode keys/DB creds/webhooks** in the resource — they live in `server.cfg`/convars.

## Reference files

Read the one matching the task.

- `references/mission-engine.md` — the core: missions-as-data schema, the objective-type vocabulary (goto/kill/collect/interact/escort/defend/capture/survive), the server-side state machine (start → advance → complete/fail → reward → cleanup), the framework reward hook as a swappable function, state bags for sync, and the single cleanup pattern. Read first, for any mission work.
- `references/directed-missions.md` — authored missions: start triggers (NPC giver, item, command, zone), ordered & branching objective sequences, dialogue/text beats (`lib.showTextUI`/`lib.alertDialog`), per-objective timers and fail conditions, solo vs fixed-party, and a full worked example (a small multi-step mission end to end). Read for story/quest/scripted-scenario work.
- `references/random-events.md` — ambient events: the server scheduler (cooldown, location pool, max concurrent), broadcast/announce, opt-in and eligibility, the shared resolve condition, re-arm after cooldown, and despawn-on-timeout. Difficulty/reward scaling and anti-farm. A worked example (a roaming heist that any player can join). Read for repeatable world-event work.
- `references/coop-and-state.md` — the group layer: per-player vs shared progress, party formation and presence, authoritative server state + state-bag sync, join/leave/disconnect handling, distance/relevance scoping, and reward splitting across a group. Read for any co-op mission and whenever state correctness matters.

## Scaffold

`python scripts/scaffold_mission.py --name <name> --mode <directed|random> --framework <qbox|qbcore|esx|standalone> --output <dir>`

Emits a runnable resource with the mission engine, one example mission/event of the chosen mode, server-authoritative advance/complete/reward, group sync, and a complete cleanup function. TODOs mark the parts you customize (coords, objective targets, reward, dialogue). Run `--help` first. Emits placeholders only — never real keys.
