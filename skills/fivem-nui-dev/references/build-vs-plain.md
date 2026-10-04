# Build vs Plain — when to graduate from plain HTML to a build setup

Plain HTML/CSS/JS is the default and the right choice for most NUIs (SKILL.md says why). This file is for the moment plain genuinely isn't enough and you're considering React/Vue + a bundler — what changes, where npm fits, and the tradeoff. Read it only when plain is hurting, not preemptively.

## The signs you've outgrown plain

Graduate when the *UI's* complexity, not the gameplay's, is the pain:

- **Lots of dynamic, stateful lists/views** — an inventory with drag/drop, a phone with many apps, a crafting tree. Hand-managing the DOM for these is error-prone and verbose.
- **Component reuse across many screens** — the same card/row/modal appears everywhere and you're copy-pasting markup and event wiring.
- **Shared UI state** that several parts of the page must stay in sync with — plain `app.js` becomes a tangle of manual updates.
- **A team / TypeScript** — you want types and a component model for maintainability.

If you have a three-button menu, a HUD, or a simple shop list — none of these apply. Stay plain.

## What actually changes (and what doesn't)

The **bridge is identical**. `SendNUIMessage`, `RegisterNUICallback`, `SetNuiFocus`, `fetch` to `https://<resource>/...`, the message protocol, focus/lifecycle discipline — all exactly the same (`nui-bridge.md`, `nui-focus-lifecycle.md` still govern). React/Vue only changes **how you author the page**; the game still loads a static `index.html` + bundled JS/CSS.

What changes:
- You write components (`.jsx`/`.vue`/`.ts`) instead of editing `index.html`/`app.js` directly.
- A **bundler (Vite is the common choice)** compiles those into static `dist/index.html`, `dist/assets/*.js`, `dist/assets/*.css`.
- **`fxmanifest.lua` points at the built output**, not your source:
  ```lua
  ui_page 'web/dist/index.html'
  files {
      'web/dist/index.html',
      'web/dist/assets/*.js',
      'web/dist/assets/*.css',
  }
  ```
- You commit/ship the `dist/` build (or build on deploy). The game never sees your `src/`.

## Where npm fits

This is the cost you're taking on:

- `npm install` (once, and on dep changes) pulls the framework + bundler into `node_modules`.
- `npm run dev` gives a hot-reloading dev server you preview in a browser (fast iteration on layout/logic *outside* the game).
- `npm run build` produces the `dist/` the game loads. You run this before testing in-game and before shipping.
- Inside the game you always run the **built** output — there's no dev server in CEF.

So the loop becomes: edit source → `npm run build` → restart resource (or have a watch step) → test in-game. Heavier than plain's "edit file → restart resource."

## The Vite shape (typical)

```
my_nui/
├── fxmanifest.lua          -- points at web/dist
├── client.lua              -- the bridge (unchanged from plain)
├── server.lua              -- validates actions (unchanged; still server-authoritative)
└── web/
    ├── package.json
    ├── vite.config.js       -- base: './' so asset paths are relative (important for NUI)
    ├── index.html
    ├── src/
    │   ├── main.jsx
    │   └── components/...
    └── dist/                -- built output the game loads (gitignore src, ship dist)
```

Two Vite gotchas specific to NUI:
- Set `base: './'` (relative asset paths) in `vite.config.js` — absolute `/assets/...` paths resolve wrong under the NUI URL scheme and 404 in-game.
- The NUI message listener and fetch helper go in your framework code the same as plain — wire `window.addEventListener('message', ...)` in a top-level effect/hook so it attaches once on mount.

## Dev-loop tip: preview outside the game

Because the bridge is just `window.postMessage` and `fetch`, you can develop most of the UI in a normal browser with `npm run dev` by **mocking** the bridge: a small shim that fakes incoming `message` events and logs outgoing `fetch`es. Build the look and interactions fast in the browser, then build and test the real bridge in-game. (This works for plain pages too — open `index.html` in a browser and paste fake messages in the console.)

## The honest tradeoff

| | Plain HTML/CSS/JS | React/Vue + Vite |
|---|---|---|
| Setup | none | npm, bundler, config |
| Dev loop | edit → restart resource | edit → build → restart resource (or watch) |
| Good for | menus, HUDs, shops, simple panels | complex stateful UIs, big apps, reuse |
| Bridge | same | same |
| Risk | DOM spaghetti at scale | over-engineering a simple UI |

Pick the build only when the UI complexity earns the setup cost. For your typical FiveM resource UI, plain wins. When you build something phone-sized or inventory-sized, the build pays off — and the bridge knowledge you already have carries straight over.
