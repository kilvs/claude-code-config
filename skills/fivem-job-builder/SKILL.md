---
name: fivem-job-builder
description: Build complete custom JOBS for FiveM roleplay servers — the full playable system, not just the framework API call. Primary target is Qbox (qbx_core) on the full ox stack (ox_lib, ox_target, ox_inventory), QBCore and ESX noted. Three archetypes. Legal loop jobs (delivery, mechanic, garbage, fishing). Illegal jobs (drug runs, robberies, heists with risk/reward and police). Whitelisted jobs (police/EMS with grades, duty, restricted access). Covers job registration, grades and pay, the ox_target loop with blips, server-authoritative payouts, ox_inventory rewards, persistence, and a runnable scaffold. Use whenever someone wants to create, build, balance, or debug a FiveM job, gang, or profession — "make a mechanic job," "build a drug selling script," "police job with ranks," or any job-loop/economy gameplay. Defaults to Qbox-native, server-authoritative code. Do NOT use for non-job FiveM scripting (use fivem-lua-dev), single-player GTA mods, or RAGE:MP/alt:V.
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# FiveM Job Builder

Build a **custom job** for a FiveM roleplay server as a complete, playable system. A "job" here is the full gameplay loop a player steps into — getting the job, going on duty, doing the work at interaction points in the world, getting paid and rewarded, with the server enforcing every reward. This skill takes you from "I want a mechanic job" to a running resource.

This is the **job-specific** companion to the broader `fivem-lua-dev` skill. If the task is general FiveM scripting, server hosting, world entity spawning, or maps/streaming, that skill owns it. This one owns jobs, professions, gangs, and their economy loops. When a job task also needs deep platform setup (server install, custom MLO for the job's building), lean on `fivem-lua-dev` for those parts.

## The non-negotiable: the server pays, never the client

Every job pays money or gives items. **The client must never decide its own reward.** A job script that listens for a client event saying "I finished the delivery, pay me $500" and pays out is the single most exploited pattern in FiveM — a cheater fires that event in a loop and prints money. This skill's whole spine is: the client *requests* progress, the server *verifies state and pays*.

Concretely, the server must confirm, on every payout:
- The player **actually holds the job** (and the right grade for grade-gated rewards).
- They are **physically at the right place** (distance check against the server's known coordinates — never trust a position the client sends).
- They **actually have the required items/state** to complete the step (e.g. the package, the harvested crop) — checked via `ox_inventory` server exports, not a client claim.
- The step is **happening in a plausible sequence and cadence** (can't complete step 3 without 1 and 2; can't complete the same step 50 times a second — rate-limit/cooldown server-side).

If you find yourself writing `RegisterNetEvent('myjob:pay')` whose handler hands out money based on arguments the client passed, stop. That is the bug. See `references/job-economy.md`.

## Pick the archetype first

The archetype determines the whole structure. Identify it before writing anything.

- **Legal loop job** — delivery, mechanic, garbage, fishing, lumberjack, taxi. Player goes on duty, the script sends them to point A (pick up / start task), then point B (deliver / finish), pays them, loops. Low risk, steady pay, often no whitelist. The bread-and-butter archetype. → `references/legal-loop-jobs.md`
- **Illegal / criminal job** — drug harvesting & selling, store robbery, vehicle theft, heists. Risk/reward: better pay, but police get alerted, items can be lost, there's a chance of failure. Needs dispatch/alert integration and careful balancing so it's lucrative but not trivially farmable. → `references/illegal-jobs.md`
- **Whitelisted job** — police, EMS/ambulance, mechanic-shop-with-bosses. Grade-gated (ranks with different permissions and pay), explicit clock-in/clock-out (on/off duty), access to restricted items/vehicles/areas, and an allowlist controlling who can take the job at all. → `references/whitelisted-jobs.md`

Most real jobs are mostly one archetype with a borrowed piece (a legal job with a whitelist; an illegal job with grades). Build the archetype's spine, then add the borrowed piece from the other reference.

## Start-to-finish path

Read the referenced file before doing each step — the framework export names and ox API signatures are exactly the things that are easy to get subtly wrong from memory, and they shift between framework versions.

1. **Register the job with the framework.** Jobs live in the framework's shared job list (Qbox: `qbx_core/shared/jobs.lua`), defining the job name, label, and grades (each grade has a name, label, and `payment`). Whitelisted jobs set `whitelisted = true`. Detail and the exact table shape in `references/job-registration.md`.
2. **Scaffold the resource.** `python scripts/scaffold_job.py --name myjob --archetype legal --framework qbox --output <dir>` emits a runnable Qbox-native job resource — `fxmanifest.lua`, `config.lua`, `client.lua`, `server.lua` — wired with ox_target points, a server-validated payout, and the job/grade checks already in place. `--help` for archetypes (`legal`, `illegal`, `whitelisted`) and options.
3. **Build the loop & interaction points.** Place the job's world interactions with `ox_target` (boxzones / entity / model targets) and blips, gate each option on the player's job client-side for UX. Loop logic per archetype in its reference file.
4. **Wire server-authoritative rewards.** Every payout and item grant goes through a server callback/event that re-checks job, grade, distance, items, and cadence before calling `exports.qbx_core` money functions and `ox_inventory` item functions. This is `references/job-economy.md` and it is the part to get right.
5. **Add grades, duty, and persistence as the archetype needs.** Clock-in/duty state, grade permissions, and anything that must survive a reconnect (saved progress, society funds) — `references/whitelisted-jobs.md` for duty/grades, `references/job-economy.md` for persistence via `oxmysql`.
6. **Balance and test.** Tune pay-per-loop against time-per-loop so the job earns a sane hourly rate for your economy, verify a cheater firing the payout event directly gets nothing, and check `resmon` idle cost. → `references/job-economy.md` (balancing) and the Hard rules below.

## Idiomatic Qbox (don't write QBCore-in-disguise)

Qbox is **not** QBCore with a renamed export — writing it that way wastes the framework and ages badly. Default to the Qbox-native surface:

- Player/framework access: `exports.qbx_core` (e.g. `exports.qbx_core:GetPlayer(src)`), **not** `QBCore.Functions.GetPlayer`.
- Notifications, RPC/callbacks, UI, cooldowns, zones: `ox_lib` (`lib.notify`, `lib.callback`, `lib.points`, `lib.zones`).
- Items & stashes: `ox_inventory` server/client exports — never give items by trusting the client.
- Interactions: `ox_target`.
- DB: `oxmysql` (`MySQL.query`, `MySQL.insert`, etc.).
- Sync: prefer **state bags** over tick-based polling loops.

For QBCore and ESX, the *structure* is identical; only the export/event names change. `references/frameworks-jobs.md` has the side-by-side map (get player, add/remove money, job check, grade check, give/has item) so a Qbox job can be ported cleanly. Match every script to one framework + version; mixing targets is the top cause of "it doesn't work."

## Hard rules

These prevent the failures that specifically bite *job* scripts.

**The server pays, the client asks.** (Restated because it is the whole game.) No money or item ever leaves a handler that didn't independently verify job, grade, location, required items, and cadence server-side. Treat every client→server event as hostile input.

**Distance-check every "I'm here" claim against server-side coords.** The interaction point's real coordinates live in server config. When the client says "I'm at the dropoff," compare the player's *server-known* ped coords to that point and reject if they're not actually close. A client can lie about position.

**Cooldown and sequence-gate payouts server-side.** Track per-player job state on the server (current step, last-payout timestamp). Reject out-of-order or too-fast completions. Without this, even a "verified" payout can be farmed by replay.

**Gate grade-restricted rewards on the server's grade, not the client's.** Higher-grade pay, restricted items, and boss actions check `PlayerData.job.grade.level` as the *server* sees it.

**Whitelisted means server-enforced.** A whitelist that only hides the UI client-side is not a whitelist. The server must refuse the job action if the player isn't actually allowed and on duty.

**Don't block the thread; idle cheap.** Job loops that poll with `Wait(0)` tank the server. Use `ox_target`/`lib.points`/zones and events instead of busy-wait; widen `Wait()` when idle. A well-behaved job idles well under ~0.05ms client-side (`resmon`).

**Balance for hourly rate, not per-action.** Decide the target $/hour for the job in your economy, then set per-loop pay = target × (loop-time / 3600). An untuned job either starves players or wrecks the server economy.

**Never hardcode keys, DB creds, or webhook URLs in the resource.** Those live in `server.cfg`/convars, kept private.

## Reference files

Read the one matching the task.

- `references/job-registration.md` — registering the job in the framework's shared job list (Qbox `qbx_core/shared/jobs.lua` shape, QBCore/ESX equivalents), grades with `payment`, `whitelisted`/`type`/`offDutyPay` flags, and how the job name threads through every later check. Read first, before writing job logic.
- `references/legal-loop-jobs.md` — the go-here/do-this/get-paid loop: ox_target pickup & dropoff points, blips/zones, optional job vehicle spawn, progress bars (`lib.progressBar`), and a fully server-validated delivery payout end to end. The default archetype.
- `references/illegal-jobs.md` — risk/reward design: harvesting and selling loops, police dispatch/alert integration, failure chances, item loss, cooldowns and diminishing returns to stop farming, and selling to NPCs/peds with server-side price + inventory checks. Balancing illegal pay against risk.
- `references/whitelisted-jobs.md` — grades & permissions, clock-in/clock-out duty state (and `offDutyPay`), allowlist enforcement (server-side), restricted item/vehicle/area access by grade, and a boss/management menu pattern. Police/EMS-style jobs.
- `references/job-economy.md` — the heart: server-authoritative payout pattern (callback design, the full validation checklist), `exports.qbx_core` money functions, `ox_inventory` give/remove/has item server exports, `oxmysql` persistence for progress and society funds, rate-limiting/cooldowns, and how to balance $/hour. Read whenever money or items change hands.
- `references/frameworks-jobs.md` — Qbox ↔ QBCore ↔ ESX side-by-side: get player, add/remove money, get job, check grade, give/has/remove item, notify. Read when targeting or porting to a non-Qbox framework.

## Scaffold

`python scripts/scaffold_job.py --name <name> --archetype <legal|illegal|whitelisted> --framework <qbox|qbcore|esx> --output <dir>`

Emits a runnable, framework-correct job resource with the server-authoritative payout already wired and clearly marked TODOs for the parts you customize (coords, pay, items). Run `--help` before assuming flags. It emits placeholders only — never real keys.
