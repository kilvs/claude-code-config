---
name: fivem-lua-dev
description: Build and develop GTA V FiveM roleplay servers and Lua resources. Covers the full path from zero to a running server (FXServer artifacts, txAdmin, Cfx.re keys, MySQL, server.cfg, local to public VPS hosting), deep FiveM Lua scripting (client/server realms, events, natives, threads, callbacks, ox_lib/oxmysql), the RP frameworks ESX Legacy, QBCore, and Qbox (recommended), spawning and controlling world entities (peds, vehicles, objects, entity physics, animations, blips/markers/zones), and integrating custom maps, MLOs, vehicles, and clothing via the stream folder. Scaffolds a runnable resource and a server.cfg. Trigger on creating or hosting a FiveM/GTA RP server, writing or debugging a FiveM Lua resource, fxmanifest.lua, server.cfg, txAdmin, natives, ox_lib, oxmysql, ESX, QBCore, Qbox, spawning peds/vehicles/objects, custom maps, MLO, ymap, streaming, or RP jobs/economy/inventory. Do NOT use for single-player GTA mods (Script Hook V, trainers), RAGE:MP or alt:V, 3D asset authoring (Blender), or non-FiveM Lua.
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# FiveM / Lua Server Development

Build GTA V roleplay servers on FiveM (Cfx.re's FXServer) and write the Lua resources that run on them. This skill takes someone from "no server" to "running, scriptable RP server," and goes deep on the scripting once the server is up.

## The honest landscape (verify the fast-moving bits)

FiveM moves fast — artifact builds, framework versions, and recommended libraries change often, and the Cfx.re org structure has shifted over time. State the stable concepts confidently, but when a specific version number, download URL, current "recommended" build, or "which framework is winning right now" matters to the answer, **web-search to confirm** rather than asserting from memory. Point people at official sources: `docs.fivem.net`, the Cfx.re portal/forums, and the framework's own docs (`qbcore.net`, the Qbox and ESX GitHub orgs).

This skill is for **FiveM specifically** — not single-player GTA mods (Script Hook V, trainers), and not the separate RAGE:MP or alt:V platforms, which have different runtimes and APIs.

## Start-to-finish path

This is the route from nothing to a running RP server. Each step has depth in a reference file; read the referenced file before doing the step rather than improvising from memory, because the environment-specific details (paths, key registration, manifest syntax) are exactly the things that are easy to get subtly wrong.

1. **Decide local vs public, and which framework.** Build and learn **locally first** (Windows PC, free, friends can join via port-forward), then move to a VPS for a public server. Pick a framework before installing — see "Choosing a framework" below. Default recommendation for a new server: **Qbox**.
2. **Install the server.** Download FXServer **artifacts**, run `FXServer.exe`, complete **txAdmin** setup in the browser, link your **Cfx.re account**, generate a **server key**. For a framework server you'll also stand up **MySQL**. Full walkthrough (local and VPS) in `references/server-setup.md`.
3. **Deploy the framework.** Use a txAdmin **recipe/template** (Qbox/QBCore/ESX) for the fast path, or install the framework resources manually for control. Framework specifics in `references/frameworks.md`.
4. **Configure `server.cfg`.** License key, DB connection string, `ensure` lines, endpoints, max players, admin principals. Generate a sane starting `server.cfg` with `scripts/generate_server_cfg.py` (it asks which framework and wires the right `ensure` order). Detail in `references/server-setup.md`.
5. **Write resources and build the world.** This is the real work. Scaffold a runnable starter with `scripts/scaffold_resource.py`, then build out. Scripting depth in `references/lua-scripting.md`, resource structure in `references/resource-anatomy.md`. Putting gameplay into the world — NPCs, vehicles, props, interaction points — is in `references/world-entities.md`; adding custom maps/MLOs/vehicles/clothing is in `references/maps-and-streaming.md`.
6. **Harden and go public.** Server-authoritative design, anti-cheat basics, rate limiting, admin allowlists (`references/security.md`), then VPS deployment and the server list (`references/server-setup.md`).

## Choosing a framework

All three are RP frameworks providing players, jobs, money, inventory, and a resource ecosystem. They share concepts; APIs differ.

- **Qbox** — a modern, optimized fork of QBCore with cleaner structure and ongoing active development; built around the `ox_*` libraries (`ox_lib`, `oxmysql`, `ox_inventory`, `ox_target`). **Recommended for new servers** — cleanest forward path and the largest pool of compatible new scripts. Choose unless you have a specific reason not to.
- **QBCore** — very large existing script ecosystem and lots of tutorials. Choose if you're following QBCore-specific tutorials/assets or buying QBCore-targeted scripts. Watch for stale 2022-era `qb-core` forks — a red flag.
- **ESX Legacy** — the long-standing framework, maximum existing-script compatibility, big back-catalogue. Choose if your team already knows ESX or you're committed to ESX-targeted assets.

Whatever you pick, match every script/asset to that framework and its version; mixing framework targets is the main source of "it doesn't work." Modern scripts increasingly depend on `ox_lib`/`oxmysql` regardless of framework — install those early.

## Scaffolds

- **Starter resource**: `python scripts/scaffold_resource.py --name my_resource --framework qbox --output <dir>` (frameworks: `standalone`, `qbox`, `qbcore`, `esx`). Emits a runnable resource — `fxmanifest.lua`, `client.lua`, `server.lua`, `config.lua` — wired with a command, an event round-trip, and a server-side validation example so the trust boundary is shown by default. `--help` for options.
- **server.cfg**: `python scripts/generate_server_cfg.py --framework qbox --name "My Server" --output <dir>` — produces a `server.cfg` with the correct `ensure` ordering for the chosen framework, endpoints, license-key placeholder, DB connection placeholder, and sane defaults. `--help` for options.

Run `--help` on either before assuming flags. Both emit placeholders (never real keys/passwords) for you to fill.

## Hard rules

These prevent the failures that actually bite FiveM developers. Apply them throughout.

**The server is the authority. Never trust the client.** The client runs on the player's machine and can be modified by cheaters. Any decision that matters — money, items, position validation, permissions, purchases — must be made and verified **server-side**. The client may *request*; the server *decides*. Treating a client event as truth (e.g. a client telling the server "give me $10,000") is the single most common and most damaging FiveM mistake. See `references/security.md`.

**Validate every client→server event.** Register server events expecting hostile input: check the source player's right to do the thing, sanitize arguments, and confirm against server state (do they actually have the item? are they near the shop?). Never use the values a client passes as authoritative.

**Use the right realm.** FiveM Lua runs in three realms — `client`, `server`, and `shared`. Natives and events differ by realm; calling a client native server-side (or vice versa) silently fails or errors. Be deliberate about where each file/function runs (`references/lua-scripting.md`).

**Don't block the main thread.** Lua resources run cooperatively. A `while true do end` without a `Wait()` freezes the entire resource (and can hitch the server). Always `Wait()` in loops; use `Citizen.CreateThread`/`CreateThread` and event-driven patterns instead of busy-waiting.

**Optimize idle cost (resmon).** Per-frame loops (`Wait(0)`) are expensive. Increase wait intervals when nothing's happening, use events/state bags over polling, and check resource monitor (`resmon`) — a well-behaved script idles well under ~0.05ms client-side. Bad loops are the top cause of laggy servers.

**Name and depend explicitly.** Every resource has an `fxmanifest.lua` declaring `fx_version`, `game`, realms, and dependencies. Load order matters — declare `dependencies` and use `ensure` so frameworks/libraries load before the resources that need them (`references/resource-anatomy.md`).

**Never paste keys or DB passwords into shared files or screenshots.** The Cfx.re license key and MySQL credentials live in `server.cfg` (kept private), not in resources or anything committed publicly.

## Reference files

Read the one matching the task; they carry the detail that's error-prone to recall.

- `references/server-setup.md` — installing FXServer artifacts, txAdmin first-run, Cfx.re account + server keys, MySQL setup, `server.cfg` anatomy, port forwarding for local play, and moving to a VPS + getting listed. Read for any "set up / host / deploy the server" task.
- `references/lua-scripting.md` — FiveM Lua in depth: the three realms, events (`RegisterNetEvent`, `TriggerServerEvent`, `TriggerClientEvent`), natives and how to find them, threads/`Wait`, state bags, server callbacks, `ox_lib`/`oxmysql` usage, and the common beginner gotchas. Read for any scripting task.
- `references/resource-anatomy.md` — `fxmanifest.lua` fields, resource folder layout, realm file lists, `dependencies`/`ensure`/load order, the `[category]` folder convention, and how `ox_lib`/`oxmysql` are wired in. Read when structuring a resource or debugging "resource won't start."
- `references/frameworks.md` — ESX vs QBCore vs Qbox: core APIs (getting a player, money, jobs, items), exports/events each exposes, how they relate (Qbox⊃QBCore lineage), and how to write a script that targets one cleanly. Read when working inside or against a framework.
- `references/security.md` — server-authoritative design in practice, the client trust boundary, validating events, anti-cheat realities (and why client-side "anti-cheat" is weak), rate limiting, and admin/permission handling. Read before going public and whenever money/items/permissions are involved.
- `references/world-entities.md` — spawning and controlling peds (NPCs, scenarios, AI tasks, relationship groups), vehicles, and objects/props; manipulating entity physics via natives (velocity, force, ragdoll, freeze); animations, particles (ptfx), and sound; and placing gameplay in the world with blips, markers, and zones/`ox_target`. Read for any "spawn/control an NPC, car, prop," world-interaction, or entity-physics task.
- `references/maps-and-streaming.md` — how custom level content enters a server: the `stream/` folder, map mods (`.ymap`), MLOs (custom interiors + `data_file` declarations), custom vehicles/clothing, performance/crash limits, IPL toggling of built-in interiors, and signposts to the external authoring tools (CodeWalker, Sollumz, OpenIV). Read for "add a custom map/MLO/car/clothing," streaming, or level-content integration. Note: this skill covers *integrating/streaming* assets, not authoring 3D models (a separate craft).
