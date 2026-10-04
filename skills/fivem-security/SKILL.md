---
name: fivem-security
description: Architectural guidance for securing FiveM resources against cheats, unauthorized event triggers, and malicious data manipulation, and for auditing scripts to find the holes. Core philosophy is NEVER TRUST THE CLIENT. The client runs on the player's machine and can be fully compromised, so every action affecting game state, the economy, or other players MUST be validated on the server. Built around the Golden Rules (server authority, never trust parameters, server-side distance checks, rate limiting), with a rules breakout, an audit checklist, and an optional drop-in validation helper. Use whenever someone wants to secure, harden, audit, or threat-model a FiveM resource, asks is this exploitable, wants to stop money or item dupes, prevent event spam or unauthorized triggers, or validate client arguments. Triggers include secure my script, is this exploitable, harden this resource, audit this code, server-authoritative, stop the dupe, anti-cheat. Do NOT use for general FiveM scripting (use fivem-lua-dev).
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# FiveM Security

Architectural guidance for securing FiveM resources against cheats, unauthorized event triggers, and malicious data manipulation — and a tool for auditing existing scripts to find where they leak. This is the deeper, standalone authority on security; `fivem-lua-dev/references/security.md` is the shorter in-line version, and the job/mission/NUI skills all assume these rules. When the task is "is this safe / make this safe / why is this being exploited," this skill leads.

## Core Philosophy: NEVER TRUST THE CLIENT

The client is in the hands of the user, which means it can be fully compromised. A cheater can modify client Lua, fire any `RegisterNetEvent` handler with any arguments, spoof values, replay events, and read everything in the client and shared realms. Therefore:

> **Every action that affects game state, the economy, or other players MUST be validated on the server.**

The client's job is **input and display**. It may *request*; the server *decides*, *validates*, and *persists*. Nothing the client sends is true until the server confirms it against state the server owns. This is not paranoia — public FiveM servers are probed constantly, and a single trusting handler is enough to mint infinite money or dupe items.

## The Golden Rules

These four rules are the whole skill in miniature. Every detailed pattern in `rules/` is an application of one of them.

1. **Server Authority.** The server dictates the truth; the client only requests actions. Money, items, jobs, prices, cooldowns, ownership, and any position that gates an action live and are decided server-side. → `rules/events.md`
2. **Never Trust Parameters.** Always validate arguments sent from the client. If a client says "give me $50," the server checks whether the client *earned* it, not whether the client *claims* it. Amounts, ids, item names, indices — all attacker-chosen until validated against a server-side whitelist or server-owned state. → `rules/parameters.md`
3. **Distance Checks.** Always check distance on the server side before allowing an interaction (looting, selling, entering a zone, using a target). A client can claim to be anywhere; the server compares the player's server-known coordinates to the real interaction point. → `rules/distance.md`
4. **Rate Limiting.** Prevent event spamming with server-side cooldowns or debouncing on critical actions. Even a fully-validated payout can be farmed by replay if there's no cadence guard. → `rules/rate-limiting.md`

## How to use this skill

Two modes, same rules:

- **Building** — writing a new resource or feature. Apply the Golden Rules as you write: every networked event gets source capture, authorization, parameter validation, state verification, distance, and rate-limiting as applicable. The optional helper (`scripts/sv_security.lua`) gives you ready-made `validatePlayer` / `validateDistance` / `rateLimit` functions so the checks come out identical every time.
- **Auditing** — reviewing or threat-modeling existing code. Walk the audit checklist below against each server handler, name the exploit each gap enables, and fix it. The deliverable is a prioritized list of holes + the corrected handlers.

## The audit checklist

For **every** `RegisterNetEvent`/`lib.callback.register` on the server, confirm:

- [ ] **Source captured first.** `local src = source` on line one, before any `Wait()` (a yield lets `source` change). The server sets `source`; the client can't spoof it.
- [ ] **Player resolved and authorized.** Got the framework player from `src`; confirmed they may do this (job/grade/admin/ownership).
- [ ] **Every parameter validated.** Type-checked, range-checked, and — for ids/names — checked against a server-side whitelist. No client-supplied amount, price, or balance used as authoritative.
- [ ] **Verified against server state.** They actually hold the item/money; the thing they reference actually exists and is theirs.
- [ ] **Distance checked server-side** for any in-world interaction, against server-known coords.
- [ ] **Rate-limited** if the action is sensitive or repeatable.
- [ ] **SQL parameterized** (`?` placeholders), never string-concatenated from client input.
- [ ] **No secrets in client/shared realm** (keys, DB creds, webhook URLs live in `server.cfg`/convars only).
- [ ] **Result is the server's** — the client is told the outcome, never trusted to compute it.
- [ ] **Callback `cb` always called** (for `lib.callback`/NUI callbacks) so the client side doesn't hang.

A handler that can't tick every applicable box is a hole. Name the exploit (dupe, free money, teleport-loot, spam-farm, privilege escalation) so the fix is motivated, not mechanical.

## Hard rules

**Treat every networked event as a public, hostile-facing endpoint.** Anyone on the server can call it with anything. Design the handler as if an attacker is calling it, because one will.

**Whitelist, never blacklist.** Accept known-good item names, actions, and ids from a server-side set. Trying to enumerate and reject bad input always misses a case.

**Client-side "anti-cheat" is not a security boundary.** Detection that runs on the client can be disabled or spoofed by the same cheater. Real protection is architectural — if the server never trusts the client, most cheats can't achieve anything that matters. Spend effort on server authority, not client detection theater. Third-party anti-cheats help at the margins; they never replace server-authoritative design.

**Minimize the event surface.** Every `RegisterNetEvent` is an attack entry point. Don't register networked events you don't need; don't expose internal helpers as net events.

**Validate entity ownership** before acting on any entity a client references — a client can pass an entity handle it doesn't own.

**Gate admin actions with server-side ACE checks**, never a client claim of being admin. `IsPlayerAceAllowed(src, ...)` on the server; principals/aces in `server.cfg`.

**Log sensitive actions server-side** (money, item spawns, admin commands) with the player identifier — logs are how you find an exploit after the fact. Never log secrets.

## Reference files

Read the one matching the task. Each is a Golden Rule applied in depth.

- `rules/events.md` — Golden Rule 1. Structuring and validating `RegisterNetEvent`/`TriggerServerEvent` and `lib.callback` to prevent unauthorized execution: source capture, the source-after-Wait pitfall, authorization, the full safe-handler template, minimizing event surface, and `lib.callback` specifics. Read first for any event-handling work.
- `rules/parameters.md` — Golden Rule 2. Validating client arguments: type/range checks, the whitelist-not-blacklist principle, why a client-supplied amount/price/id is never authoritative, sanitizing ids/names before inventory or SQL, parameterized queries, and the classic dupe/free-money exploits this stops. Read whenever a handler takes arguments from the client.
- `rules/distance.md` — Golden Rule 3. Server-side distance checks: why client position is untrustworthy, comparing server-known ped coords to the real interaction point, choosing a sane radius, server-validated zones, and the teleport-loot / remote-interaction exploits this prevents. Read for any in-world interaction (loot, sell, use, enter).
- `rules/rate-limiting.md` — Golden Rule 4. Server-side cooldowns and debouncing: per-player cadence guards, sequence gating (can't do step 3 without 1 and 2), diminishing returns, why even a validated payout farms without this, and cleaning up per-player state on disconnect. Read for any sensitive or repeatable action.

## The optional helper

`scripts/sv_security.lua` is a small, dependency-free server-side module with ready-made validators so the checks are identical across your resources. Drop it into a resource and `require` it (or copy the functions). It uses `ox_lib` if present but does not require it. Functions: `validatePlayer(src)`, `validateDistance(src, coords, radius)`, `rateLimit(src, key, ms)`, `validateAmount(v, min, max)`, `inWhitelist(value, set)`. It is a convenience, not the point — the rules are the point. `scripts/scaffold_secure_event.py --name myevent --output <dir>` emits a correctly-structured handler using the helper as a starting template.
