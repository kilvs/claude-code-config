# NUI Styling — making it read in-game

A NUI is drawn over a live, moving, colourful game scene at whatever resolution the player runs. Styling that looks fine on a white browser tab can be illegible in-game. This file is the styling discipline that makes a NUI read and behave. Read for layout/legibility work.

## Transparent by default

The NUI page covers the whole screen, but your UI usually shouldn't. Make the page background transparent and only paint the panel:

```css
html, body {
    margin: 0; height: 100%;
    background: transparent;     /* critical — otherwise you black out the game */
    overflow: hidden;
    font-family: 'Inter', sans-serif;   /* a bundled font, not a runtime CDN — see below */
}
```

A black or white `body` background is a classic mistake — it hides the entire game behind your page. Only the panel itself gets a background.

## Show/hide without leaving a focus-trap

Drive visibility with a class, and keep the page non-interactive when hidden:

```css
body { opacity: 0; pointer-events: none; transition: opacity .15s ease; }
body.visible { opacity: 1; pointer-events: auto; }
```

When hidden (`opacity:0; pointer-events:none`) clicks pass through to the game even if focus logic lagged — a safety net. (It is *not* a substitute for releasing `SetNuiFocus`; see `nui-focus-lifecycle.md`.)

## Contrast and sizing over a busy scene

The scene behind your UI is unpredictable (bright desert, dark alley). Don't rely on the game for contrast:

- Give panels a **solid or strongly-tinted background** (e.g. `rgba(20,22,28,0.92)`) so text is readable over anything. Pure transparency for text-bearing panels fails over bright scenes.
- **High text contrast** — near-white text on a dark panel, or vice versa. Avoid mid-grey on mid-tint.
- A subtle **drop shadow or border** separates the panel from the scene: `box-shadow: 0 8px 40px rgba(0,0,0,.5)`.
- Size for a **TV-distance read**, not a desk monitor — players sit back. Bigger base font (16–20px at 1080p), generous padding, clear hit targets.

## Responsive scaling across resolutions

Players run 1080p, 1440p, 4K, ultrawide. Size relative to the viewport so the UI scales:

- Use `vh`/`vw`/`vmin` or `%` for panel dimensions and position, not fixed px for layout.
- Keep font sizes scalable: a root `font-size` in `vh` (e.g. `font-size: 1.6vh`) and `rem` elsewhere makes the whole UI scale with screen height.
- Test mentally at both 1080p and 4K — a fixed 400px panel is huge at 1080p and tiny at 4K; `40vh` is consistent.
- Anchor HUDs to edges with `position: fixed` + `vh/vw` offsets so they sit correctly on any aspect ratio, including ultrawide.

## `pointer-events` discipline

This decides whether a click hits your UI or the game:

- **Interactive panel/menu**: `pointer-events: auto` on the panel; the page has focus, clicks land on buttons.
- **HUD / passive overlay**: `pointer-events: none` on everything so all clicks fall through to the game. If one widget in a HUD is clickable, set `pointer-events: auto` on *that element only*.
- A non-interactive decorative layer over an interactive panel should be `pointer-events: none` so it doesn't eat clicks meant for the panel beneath.

## Fonts and icons without runtime CDNs

In-game, the NUI may have no/limited internet, and you don't want a UI that depends on a CDN being up. **Bundle assets, don't fetch them at runtime:**

- **Fonts**: ship the `.ttf`/`.woff2` in the resource, declare with `@font-face`, and list the files in `fxmanifest.lua` `files{}`. Don't `<link>` Google Fonts at runtime.
- **Icons**: bundle an icon font or inline SVGs; don't pull an icon CDN at runtime.
- **Images**: ship them in the resource and list them in `files{}`. A missing `files{}` entry = 404 in-game (works in browser, blank in game).

```css
@font-face {
    font-family: 'Inter';
    src: url('fonts/Inter.woff2') format('woff2');
}
```

## Simple transitions

A short fade/slide makes open/close feel intentional without costing performance:

```css
.menu { transform: translateY(8px); transition: transform .15s ease, opacity .15s ease; }
body.visible .menu { transform: translateY(0); }
```

Keep transitions short (~150ms) and on `transform`/`opacity` (cheap to animate). Avoid animating layout properties (width/top) every frame.

## HUD layout (anchored, non-interactive)

A HUD is a fixed, edge-anchored, non-interactive overlay updated by `SendNUIMessage`:

```css
#hud { position: fixed; left: 2vw; bottom: 3vh; pointer-events: none; }
#hud .stat { /* readable over any scene: tinted bg + high-contrast text */
    background: rgba(0,0,0,.45); color: #fff; padding: .4vh .8vw; border-radius: .6vh;
}
```

```js
// updated by pushes from Lua, no focus, no callbacks
window.addEventListener('message', (e) => {
    if (e.data.type === 'hud') {
        document.getElementById('health').textContent = e.data.health + '%';
    }
});
```

Throttle HUD pushes from Lua to a sane rate (a few times a second for slow-changing values) rather than every frame — see the "don't thrash" rule in SKILL.md.

## Styling checklist
- [ ] `body` background transparent; only panels painted.
- [ ] Panels have a tinted/solid background + high-contrast text + separation (shadow/border).
- [ ] Sized in viewport units so it scales 1080p → 4K and ultrawide.
- [ ] `pointer-events` correct: panel `auto`, HUD/overlay `none`.
- [ ] Fonts/icons/images bundled and listed in `files{}` — no runtime CDNs.
- [ ] Hidden state is `opacity:0; pointer-events:none` as a safety net (not a focus substitute).
