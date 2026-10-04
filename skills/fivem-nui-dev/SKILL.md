---
name: fivem-nui-dev
description: Build NUI, the in-game web UI layer for FiveM resources — the HTML/CSS/JS menus, HUDs, panels, and interfaces players see in-game, plus the Lua-to-NUI bridge that drives them. Plain HTML/CSS/JS by default (no build step, no npm; the game loads the files directly), with notes on graduating to React/Vue + a bundler. Covers the html manifest entry, the message protocol (SendNUIMessage out, fetch + RegisterNUICallback back), focus and cursor handling (SetNuiFocus and the stuck-cursor pitfall), the open/close lifecycle, in-game styling, HUDs vs panels, and a scaffold. Use whenever someone wants to create, design, style, wire up, or debug a FiveM in-game interface — a menu, HUD, shop, inventory, phone, notification, or scoreboard — or any "show a screen in-game" task. Triggers include make a NUI, build a HUD, in-game menu, SendNUIMessage, RegisterNUICallback, SetNuiFocus, cursor stuck. Defaults to plain web with server-validated actions. Do NOT use for Lua gameplay logic (use fivem-lua-dev) or RAGE:MP/alt:V.
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# FiveM NUI Dev

Build the **NUI** — the web-based UI layer FiveM renders on top of the game. A NUI is literally a web page (HTML/CSS/JS) your resource ships, drawn by the game's embedded Chromium (CEF). This skill owns the *web layer and the bridge* that connects it to your Lua; it leans on the other FiveM skills for everything behind the bridge.

## What this owns, and what it doesn't

- **This skill** — the `html`/`ui_page` manifest wiring, the page itself (HTML/CSS/JS), the **message protocol** in both directions, NUI **focus/cursor** handling, the open/close lifecycle, styling for in-game legibility, and debugging the web side.
- **`fivem-lua-dev`** — the Lua realms, events (`RegisterNetEvent`, `TriggerServerEvent`), threads, natives, frameworks. The *client* Lua that talks to your NUI lives at this boundary; the deeper Lua patterns are there (`lua-scripting.md`).
- **`fivem-lua-dev/references/security.md`** — the trust boundary. **A NUI is a client; it is never trusted.** Anything a NUI callback asks the server to do must be server-validated, exactly like any other client event. This skill repeats the rule but doesn't re-derive it.
- **`fivem-job-builder` / `fivem-mission-builder`** — own the *logic* behind a job panel or mission tracker; this skill builds their *screens* and wires the bridge.

## Plain web first — and why (the npm question)

Start plain: an `index.html`, a `style.css`, an `app.js`. **The game loads these files directly from your resource folder — there is no build step, no `npm install`, no bundler.** You edit a file, restart the resource (or refresh), and it's live. This is the right default for menus, HUDs, shops, notifications, scoreboards — the vast majority of NUIs.

You only need npm + a build tool (Vite/webpack) when you go **React/Vue or TypeScript**: those don't run in the browser as-is, so a bundler compiles them down to the static `index.html`/`.js`/`.css` the game actually loads. At that point the manifest still points at the *built output*, not your source. Signs you've outgrown plain: lots of dynamic lists/state, component reuse across many screens, or a UI big enough that hand-managed DOM is error-prone. Until then, plain keeps the loop tight. The build-based path is sketched in `references/build-vs-plain.md` for when you get there.

## The mental model

Two worlds, one bridge:

- **Lua side (the game client)** can *send to* the NUI with `SendNUIMessage({ ... })` and *receive from* it via `RegisterNUICallback(name, cb)`. It controls whether the NUI has input focus with `SetNuiFocus(hasFocus, hasCursor)`.
- **Web side (the page)** *receives* Lua messages via `window.addEventListener('message', ...)` and *sends back* with `fetch('https://<resource>/<callback>', { method:'POST', body: JSON.stringify(...) })`.

Data flows Lua → NUI as messages; actions flow NUI → Lua as fetch callbacks. That round trip is the whole skill — get it right and everything else is styling. `references/nui-bridge.md` is the core.

## Start-to-finish path

Read the referenced file before each step; the bridge details and focus pitfalls are exactly what's easy to get subtly wrong.

1. **Wire the manifest.** Add `ui_page 'html/index.html'` and list your `files { 'html/index.html', 'html/style.css', 'html/app.js' }` in `fxmanifest.lua` so the game ships and loads them. Shape in `references/nui-bridge.md`.
2. **Scaffold the resource.** `python scripts/scaffold_nui.py --name myui --kind menu --output <dir>` (kinds: `menu`, `hud`, `panel`). Emits a runnable resource — manifest, `client.lua` with the bridge wired, and `html/` with a clean starting page, the message listener, the fetch helper, and open/close handling. `--help` for options.
3. **Define the message protocol.** Decide the small set of message `type`s Lua sends in (e.g. `open`, `close`, `setData`) and the callbacks the NUI posts back (e.g. `buyItem`, `uiClose`). Keep it a tiny, explicit vocabulary. `references/nui-bridge.md`.
4. **Handle focus and the lifecycle correctly.** Open = show the page + `SetNuiFocus(true, true)`; close = hide + `SetNuiFocus(false, false)` + always post a close callback so Lua and the page agree. This is where most NUIs break (stuck cursor, trapped input) — `references/nui-focus-lifecycle.md`.
5. **Build the screen and style it for in-game.** Layout, contrast, and sizing that read over a busy game scene; transparent background for HUDs; pointer-events discipline. `references/nui-styling.md`.
6. **Validate actions server-side, then debug.** Every callback that *does something* (spend money, give item) is a request the server must validate — never trust the NUI. Then use the CEF devtools to debug the web side. Security pointer below; debugging in `references/nui-bridge.md`.

## Hard rules

These prevent the failures specific to *NUI*.

**A NUI is an untrusted client.** Anything a NUI callback asks for — buy this, give that, set my job — is a request, validated server-side exactly like any other client event (`fivem-lua-dev/references/security.md`). A player can open the CEF devtools and fire any callback with any payload, so the callback handler must re-check eligibility, ownership, price, and bounds on the server. Never let a NUI's number be the amount, or its item id be granted unchecked.

**Always release focus, always agree on state.** Every open path that calls `SetNuiFocus(true, ...)` must have a close path that calls `SetNuiFocus(false, false)`. The page and Lua must never disagree about whether the UI is open. The classic bug — cursor stuck on screen, player can't move — is an unreleased focus. Route every close (button, ESC, action-complete) through one close function on each side.

**Don't trap the player.** If the NUI takes keyboard focus, give an explicit way out (a close button *and* an ESC handler that posts back to Lua). Test that pressing ESC always frees the player, even mid-action.

**HUDs take no focus.** A passive HUD (health, money, speedometer) must never call `SetNuiFocus` — it draws on top and lets all input pass to the game. `pointer-events: none` on non-interactive overlays so clicks reach the game. Only interactive panels/menus take focus.

**Keep the message vocabulary small and explicit.** A handful of named message `type`s and named callbacks, each with a known shape. Sprawling, ad-hoc messages are unmaintainable and easy to get wrong. Bound and check payloads on both sides.

**Don't block or thrash.** Don't `SendNUIMessage` every frame for data that changes slowly — push on change, or throttle HUD updates to a sane rate. Per-frame NUI spam costs performance.

**Plain until you need the build.** Don't reach for React/Vite for a three-button menu. The build step is a cost; pay it only when component/state complexity earns it.

## Reference files

Read the one matching the task.

- `references/nui-bridge.md` — the core: the `ui_page`/`files` manifest wiring, `SendNUIMessage` out and the `window.message` listener, `fetch` back and `RegisterNUICallback`, the named-message protocol pattern, passing data in / actions out, the `cb('ok')` callback-response convention, and debugging with the CEF devtools (`/html` URL, console). Read first, for any NUI work.
- `references/nui-focus-lifecycle.md` — the part everyone gets wrong: `SetNuiFocus(focus, cursor)` semantics, open/close lifecycle, the single-close-path pattern, the ESC/keyboard escape hatch, why the cursor gets stuck and how to never let it, and HUD-vs-panel focus discipline. Read for any interactive (focus-taking) NUI and any "cursor stuck / can't move / won't close" bug.
- `references/nui-styling.md` — making it read in-game: transparent vs opaque backgrounds, contrast and sizing over a live scene, `pointer-events` discipline, responsive scaling across resolutions, fonts/icons without external CDNs at runtime, simple open/close transitions, and HUD layout (anchored, non-interactive). Read for layout/styling/legibility work.
- `references/build-vs-plain.md` — when and how to graduate from plain to a build setup: the signs you've outgrown plain, the React/Vue + Vite shape, where npm fits, that the manifest points at *built output*, the dev-loop tradeoff, and how the bridge is identical either way (only the page authoring changes). Read only when plain is genuinely no longer enough.

## Scaffold

`python scripts/scaffold_nui.py --name <name> --kind <menu|hud|panel> --output <dir>`

Emits a runnable plain-HTML/CSS/JS NUI resource with the manifest, the Lua bridge (send + callbacks + focus handling) in `client.lua`, and an `html/` page with the message listener, fetch helper, and a correct open/close path already wired. TODOs mark what you customize (content, message types, styling). Run `--help` first. No build step required to run it.
