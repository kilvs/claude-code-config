---
name: interactions
description: How motion works on this site. Webflow's native Interactions with GSAP (IX3) is the only engine, authored as site-scoped presets that elements opt into with a data-animate attribute, plus component-scoped motion, native cursor effects (Mouse Move) and a tiny state helper for the nav (dropdowns one at a time, the burger's slide-in menu; never the native Navbar element). Reference this skill whenever creating, editing, reviewing or converting any animation, transition, scroll effect, hover effect, nav or accordion behaviour, or motion arriving from Figma, Relume or legacy interactions.
---

# Interactions (IX3)

Motion on this site is **Webflow's native Interactions with GSAP (IX3)**. Every tween lives in the Interactions panel, where the designer, the Designer canvas and the `data_interactions_tool` MCP tool can all see and edit it. Presets are shared, site-scoped interactions; an element opts in by carrying one attribute. Decided 22 Sep 2026.

## 1. Engine hierarchy (the law)

1. **Never Classic Interactions (IX2).** Legacy engine; mixing engines loads two runtimes.
2. **Never a custom-code GSAP script for tweens.** No `gsap.to()` in an embed. If a motion cannot be expressed in IX3, propose it to the site owner; do not write it in JS.
3. **JavaScript holds state only.** One compact helper (section 8) keeps in-bar nav dropdowns to one open at a time, sets attributes and ARIA, and may fire `Webflow.require('ix3').emit('event')`. Custom-event interactions resolve their targets at load, so they suit page-wide effects, never per-item state.
4. **Every animation arriving from outside** (Figma prototype, Relume template motion, GitHub code, IX2 legacy) is mapped to a preset before anything new is authored. See section 10.

## 2. The preset vocabulary (`data-animate`)

A preset is one **site-scoped** IX3 interaction whose trigger and actions target the attribute selector. An element joins by adding `data-animate="<preset>"` in Element Settings. No class, no per-element authoring.

| `data-animate` | Trigger | What plays | Timing (from the Animation collection) |
|---|---|---|---|
| `fade-in` | scroll | opacity 0 → 100% | duration/base 0.6s, ease power2.out (index 5) |
| `fade-up` | scroll | opacity 0 → 100%, y 24 → 0 | 0.6s, distance/fade-up 1.5rem (24px) |
| `fade-down` | scroll | opacity 0 → 100%, y -24 → 0 | 0.6s |
| `fade-left` | scroll | opacity 0 → 100%, x 24 → 0 | 0.6s |
| `fade-right` | scroll | opacity 0 → 100%, x -24 → 0 | 0.6s |
| `scale-in` | scroll | opacity 0 → 100%, scale 0.95 → 1 | 0.6s, scale/reveal |
| `slide-left` | scroll | x 24 → 0 (opacity untouched) | 0.6s |
| `slide-right` | scroll | x -24 → 0 | 0.6s |
| `stagger` | scroll | children fade-up in sequence. **Authored in the Interactions panel**, not through the API (the API needs a class filter for child targets); never as a pre-made Component | 0.6s, stagger/base 0.1s |
| `split-lines` | scroll | SplitText lines with mask, each line rises | 0.6s, stagger/base 0.1s |
| `split-words` | scroll | SplitText words with mask, each word rises | 0.6s, stagger/tight 0.05s |
| `split-letters` | scroll | SplitText characters with mask, each letter rises | 0.6s, stagger/fine 0.02s (24 Sep 2026: line, word and letter as separate presets, since attribute selectors are plain) |
| `parallax` | scroll, scrub | y -10% → 10% across the section, scale 1.2 so no gaps | scrub 1; never on `body`; off on 767 and 479 |
| `lift` | hover | scale 1 → 1.03 in, back out | duration/fast 0.25s, scale/hover |
| `press` | click | scale 0.97 → 1 | duration/fast 0.25s, scale/press |
| `pulse` | load, loop | scale 1 → 1.04 → 1, yoyo, repeat | duration/slower 2.4s, scale/pulse; only on the active item |
| `ring` | hover | a `[data-animate-ring]` child scales 1 → 1.4 and fades | duration/slow 1s, scale/ring |
| `marquee` | load, loop | the track moves x 0 → -50% and repeats; content duplicated once | marquee/speed 40px per second |

Rules:
- Scroll presets start at `"top 85%"`, play once (`enter: play`, the rest `none`), and are authored as **FromTo** actions so the from-state is in the interaction. Initial Appearance is panel-only and is never relied on.
- A **load** version of a reveal exists for the hero only: `data-animate="fade-up-load"`. Attribute selectors must be plain (`[name]` or `[name="value"]`; no `:not()`, no chained attributes), so the load variant is its own value, and the interaction's `wf:load` trigger has no target while its action targets the attribute.
- **No per-element timing.** IX3 timing is typed per interaction, so there is no `data-animate-delay` or `-duration`. A block that needs different timing gets a **page-scoped** or **component-scoped** copy of the preset, named after the block and logged in the decision log. Sequencing inside a hero is a stagger on the content wrapper, not delays on children.
- `stagger`, `ring`, `pulse` and `marquee` are **authored in the Interactions panel** (22 Sep 2026). No Component is created for them at the start of a build. Re-tested through the API on 29 Sep 2026 (test interactions "Kit test T1 to T6" on Sample Slider Test 51), all **accepted and stored, not yet proven to play**: loops as action-level `timing: { repeat: -1, yoyo: true }` (the documented surface; a timeline `settings` bag also stores but is not documented), and a stagger on the trigger's own children as action target `{ "extensionKey": "wf:any-element", "value": "*", "filterContext": { "relationship": "direct-child-of", "filterBy": ["wf:trigger-only", ""] } }` with `timing.stagger`. If a Preview confirms both, `stagger`, `pulse` and `marquee` become API-authorable site presets; until then they stay panel-authored. Never use a `wf:selector` child target for this: it matches children across the whole page.
- **Verified live on 22 Sep 2026**: `fade-up` on an attribute target tweens from opacity 0 / y 24 to rest on scroll; `split-lines` splits into `gsap_split_line-mask` wrappers whose lines rise; `parallax` scrubs with scroll at scale 1.2. The reveal fires when ScrollTrigger refreshes after load, so an element already in view may start a moment late; it still completes.

## 3. Behaviours (`data-nav`, `data-accordion`, `data-tabs`)

| Root attribute | Parts | Who does what |
|---|---|---|
| `data-nav="slide"` on the nav root | `data-nav-toggle="menu"` (the burger, a real `button`), `data-nav-panel="menu"` (the links panel) | **No native Navbar element** (1 Oct 2026). Below 992px the helper toggles `is-open` on the panel (the class shows it), sets `aria-expanded` and the button's label, locks page scroll, closes on Escape (focus back to the burger), on a link tap and when the window widens to desktop, and emits `nav-menu-open` / `nav-menu-close`. `Custom: nav-menu-open` slides the panel in (`xPercent` 100 to 0) and `Custom: nav-menu-close` slides it back out (0 to 100), both with a `main` breakpoint `dont-animate` rule so the desktop links never move. The burger is three div lines (`navbar_burger-line-top/-middle/-bottom`, one class per moving part) that the same two interactions morph to an X and back with To actions (`tt: 0`, `y` and `rotation` on the outer lines, `opacity` on the middle one), never two swapped images (1 Oct 2026: "animate that fluidly to X using IX3"). To actions hold no from-state at rest, so the burger never loads as an X. |
| `data-nav="dropdown"` on an in-bar item | `data-nav-toggle` (a real `button`), `data-nav-panel` | Desktop pointers (`(hover: hover) and (min-width: 992px)`) open it on **hover only**: a mouse click does nothing there, and leaving waits 200ms (hover intent) so crossing the gap to the list never closes it (1 Oct 2026: it snapped shut and reopened). Touch and screens below 992px open it on click. Keyboard Enter/Space (a click with `event.detail === 0`) toggles it everywhere. One open at a time; `is-open` on the panel shows it; outside click and Escape close. `Custom: nav-open` fades the panel down and `Custom: nav-close` fades it back up. Structure: toggle, then a panel wrapper (`data-nav-panel`, `is-open` shows it, absolutely positioned and centred under the toggle) holding the visible list (the card IX3 animates). The wrapper's `padding-top` bridges the gap down to the list, so the hover never breaks; set it so the list sits the nav card's outer inset below the card. Inside the mobile menu the same dropdown expands in place (the wrapper goes `position: static` below 992px). |
| `data-accordion`, `data-tabs` | (dropped) | **Not part of the standard** (22 Sep 2026: "Let's not do the accordion thing anymore"). Tested live: an IX3 custom-event interaction resolves its selector targets once at load, so a state attribute the helper sets later cannot steer it. Accordions and tabs, when a site needs them, are built per site in the Designer, not as presets. |

**Verified 22 Sep 2026:** `wf:custom` triggers fire from `Webflow.require('ix3').emit(name)`, but their `wf:selector` action targets are resolved when the runtime loads, not when the event fires. A selector that depends on state set later matches nothing useful, and the same elements are tweened every time. The state helper therefore only serves the nav dropdown exclusivity; it lives in the Global Scripts component (section 8).

## 4. Naming interactions

`[Trigger]: [preset or block]` in the Interactions panel: `Scroll: fade-up`, `Load: fade-up`, `Hover: lift`, `Custom: nav-open`, `Scroll: home-hero-parallax` (a page-scoped one-off). Timelines are named for what they do (`Reveal`, `Hover in`, `Hover out`).

## 5. Scope

- **Site** for every preset in section 2 and the custom-event behaviours.
- **Component** (with variants when only some variants move) for motion that belongs to a Component: card hover, nav timelines, testimonial slider. Targets inside are `[componentId, elementId]`. Component-scoped interactions travel with the component into Shared Libraries (Webflow, 16 Apr 2026), and a single instance can carry its own interaction for a one-off.
- **Class toggles** use the **Set** action (`tt: 3`, `wf:class` with `addClass` / `removeClass` / `toggleClass`). It needs the class's real style id, which is why runtime `is-*` classes live on the Style Guide page (builder section 10a).
- **Pages** for a one-off (hero parallax on the home page). Logged.

## 5a. Cursor effects (Mouse Move trigger)

Cursor-driven motion (tilt, magnetic buttons, spotlight, elements that follow the pointer, cursor trails) is native IX3 since 20 Jul 2026: the **Mouse Move** trigger, the **Mouse Follow** action and **Interval** actions. Never write a pointer script for it.

- The trigger normalises the pointer to X and Y progress from 0 to 1 over the trigger element (or the whole viewport), with smoothing (50ms by default) and a resting position (centre) when the pointer leaves.
- Timelines take a role: `mouseX` and `mouseY` scrub a timeline from the pointer position (tilt, parallax, spotlight); `interval` fires once every N pixels of travel (default 100) for trails. An `interval` timeline also moves the element to the cursor unless `setMouseX` / `setMouseY` are turned off.
- Playback: `prefers-reduced-motion` is `dont-animate` (the API rejects `skip-to-end` on a continuous trigger). Touch screens have no hover pointer, so the effect must be decoration only, never the way to reach content.
- Through MCP (tested 29 Sep 2026): trigger `{ "extensionKey": "wf:mouse-move", "config": {}, "target": <element or { "extensionKey": "wf:viewport", "value": "" }> }` (`config` is required even when empty; the host stamps `controlType: "continuous"`), and each timeline carries `"triggerMetadata": { "role": "mouseX" }`. A mouse-move trigger with no target saves and never fires.
- Scope: a cursor effect on a Component is **component-scoped**, so it travels with the component.

## 6. Playback rules (set on every interaction)

| Preset kind | `prefers-reduced-motion` | Breakpoints |
|---|---|---|
| Reveals (fade, scale, slide, stagger, split-lines, split-words, split-letters) | `skip-to-end` (content shows in its final state) | all |
| Loops (pulse, marquee) and ring | `dont-animate` | all |
| Cursor effects (Mouse Move) | `dont-animate` (the only option on a continuous trigger) | all |
| Parallax | `dont-animate` | `dont-animate` on `small` and `tiny` |
| Behaviours (nav) | `skip-to-end` | all |

Fail visible still applies: the from-state lives in the interaction, never in a class with `opacity: 0`, so a page without the IX3 runtime shows everything.

## 7. Timing values (the Animation collection is the source)

IX3 cannot read a variable for a duration, so the Animation collection (`variables` skill, section 7) is the **table every preset is authored to**. Changing a token means re-authoring the presets that use it, logged.

**Variables can be animated** (Webflow, 26 Mar 2026). A `wf:variable` action sets or tweens variable values: page-wide with `targets: []`, or scoped to the targeted elements. Use it for motion that is really a token change (a Theme shift when a dark section scrolls in, an accent that warms on hover) instead of animating each element. Shape: `properties: { "wf:variable": { "variable": { "variables": [{ "variableId": "variable-…", "value": { "type": "color", "value": "…" } }] } } }`; value types are `number`, `length`, `percentage`, `color` and `ref` (another variable). Read the variable ids with `data_variable_tool`, never guess them.

| Token | Value | IX3 field |
|---|---|---|
| duration/instant · fast · base · slow · slower | 0.15 · 0.25 · 0.6 · 1 · 2.4 s | `timing.duration` (a bare number is seconds) |
| stagger/tight · base · loose | 0.05 · 0.1 · 0.2 s | `timing.stagger.each` |
| distance/fade-up · fade-up-large · hover-lift · slide-in | 1.5 · 3 · 0.25 · 2 rem | `x` / `y` in px (24, 48, 4, 32) |
| scale/hover · press · reveal · pulse · ring | 1.03 · 0.97 · 0.95 · 1.04 · 1.4 | `scale` |
| ease | power2.out | `timing.ease: 5` (index; strings are rejected). power1.out 2, power3.out 8, sine.inOut 30, back.out 14 |

## 8. The state helper (the only JavaScript)

One script in the **Global Scripts** component (builder section 9), one banner per job, each inside the ready gate (`window.Webflow.push`, builder section 14), so it runs after `webflow.js` and IX3 have loaded. It never tweens. Two jobs since the native Navbar left the standard (1 Oct 2026): in-bar nav dropdowns open one at a time, and the burger opens the slide-in menu. It sets `data-state`, `aria-expanded` and the panels' `is-open` class (a combo anchored on the Style Guide, builder section 10a), and emits IX3 custom events for the motion. Closing is animated too: the helper emits `nav-close` / `nav-menu-close` at once and removes `is-open` only after the matching close timeline (0.25s dropdown, 0.4s menu; instant under reduced motion), so keep the script's `CLOSE_MS` equal to the timeline duration. On a page with no nav it returns at once.

```js
// ===== STATE HELPER: NAV DROPDOWNS =====
// One in-bar dropdown open at a time. Desktop pointers open it on hover (with a short grace
// period on the way out, so crossing the gap to the list never closes it); touch and screens
// below 992px open it on click; keyboard Enter/Space toggles it everywhere.
// State, ARIA and the panel's is-open class only; IX3 does the motion. On close the class
// comes off after the Custom: nav-close timeline (0.25s), so the panel animates out.
window.Webflow ||= [];
window.Webflow.push(() => {
  const items = [...document.querySelectorAll('[data-nav="dropdown"]')].filter(
    item => item.querySelector('[data-nav-toggle]') && item.querySelector('[data-nav-panel]')
  );
  if (!items.length) return;

  const CLOSE_MS = 250;
  const HOVER_OUT_MS = 200;
  const emit = name => window.Webflow?.require?.('ix3')?.emit(name);
  const hover = window.matchMedia('(hover: hover) and (min-width: 992px)');
  const still = window.matchMedia('(prefers-reduced-motion: reduce)');
  const timers = new WeakMap();
  const intent = new WeakMap();
  const toggleOf = item => item.querySelector('[data-nav-toggle]');
  const panelOf = item => item.querySelector('[data-nav-panel]');

  const set = (item, open) => {
    if ((item.dataset.state === 'open') === open) return;
    const panel = panelOf(item);
    item.dataset.state = open ? 'open' : 'closed';
    clearTimeout(timers.get(panel));
    if (open) panel.classList.add('is-open');
    else timers.set(panel, setTimeout(() => panel.classList.remove('is-open'), still.matches ? 0 : CLOSE_MS));
    toggleOf(item).setAttribute('aria-expanded', String(open));
    emit(open ? 'nav-open' : 'nav-close');
  };
  const closeAll = except => items.forEach(item => item !== except && set(item, false));

  items.forEach((item, i) => {
    const panel = panelOf(item);
    panel.id ||= `nav-panel-${i + 1}`;
    item.dataset.state = 'closed';
    toggleOf(item).setAttribute('aria-controls', panel.id);
    toggleOf(item).setAttribute('aria-expanded', 'false');
    toggleOf(item).addEventListener('click', event => {
      if (hover.matches && event.detail > 0) return;
      const open = item.dataset.state !== 'open';
      closeAll(item);
      set(item, open);
    });
    item.addEventListener('mouseenter', () => {
      if (!hover.matches) return;
      clearTimeout(intent.get(item));
      closeAll(item);
      set(item, true);
    });
    item.addEventListener('mouseleave', () => {
      if (!hover.matches) return;
      intent.set(item, setTimeout(() => set(item, false), HOVER_OUT_MS));
    });
  });

  document.addEventListener('click', event => {
    if (!event.target.closest('[data-nav="dropdown"]')) closeAll();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeAll();
  });
});

// ===== STATE HELPER: NAV MENU =====
// The burger opens the slide-in menu below 992px. State, ARIA, focus and scroll lock only;
// IX3 does the motion on nav-menu-open / nav-menu-close. On close the class comes off after
// the Custom: nav-menu-close timeline (0.4s), so the panel slides out.
window.Webflow ||= [];
window.Webflow.push(() => {
  const toggle = document.querySelector('[data-nav-toggle="menu"]');
  const panel = document.querySelector('[data-nav-panel="menu"]');
  if (!toggle || !panel) return;

  const CLOSE_MS = 400;
  const emit = name => window.Webflow?.require?.('ix3')?.emit(name);
  const desktop = window.matchMedia('(min-width: 992px)');
  const still = window.matchMedia('(prefers-reduced-motion: reduce)');
  let isOpen = false;
  let timer;
  panel.id ||= 'nav-menu';
  toggle.setAttribute('aria-controls', panel.id);
  toggle.setAttribute('aria-expanded', 'false');

  const set = open => {
    if (isOpen === open) return;
    isOpen = open;
    clearTimeout(timer);
    if (open) panel.classList.add('is-open');
    else timer = setTimeout(() => panel.classList.remove('is-open'), still.matches || desktop.matches ? 0 : CLOSE_MS);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.documentElement.style.overflow = open ? 'hidden' : '';
    emit(open ? 'nav-menu-open' : 'nav-menu-close');
  };

  toggle.addEventListener('click', () => set(!isOpen));
  panel.addEventListener('click', event => {
    if (event.target.closest('a')) set(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !isOpen) return;
    set(false);
    toggle.focus();
  });
  desktop.addEventListener('change', event => {
    if (event.matches) set(false);
  });
});
```

Notes: toggles are real `button`s with `type="button"` (accessibility rule), built as DOM elements with `dom_tag: button`. The panels' resting state is `display: none` in their class (a closed menu is not a reveal, so fail visible does not apply); the `is-open` combo shows them. Custom-event targets resolve at load, which is fine here because each nav panel exists once per page; target it by class (`wf:class`). The current-page dot and the icon swaps cannot be classes (Webflow adds `w--current` at runtime; a combo named `w--current` compiles to `._w--current`), so they live in the Global Styles NAVBAR banner. Keep the file compact, ES6, unminified.

## 9. Authoring through MCP (`data_interactions_tool`)

Read the tool's `guide` action once per session. Then, per preset, one `create_interaction`:

```json
{
  "name": "Scroll: fade-up",
  "scope": { "type": "site" },
  "conditionalPlayback": [{ "type": "prefers-reduced-motion", "behavior": "skip-to-end" }],
  "triggers": [{
    "extensionKey": "wf:scroll",
    "config": { "scrollTriggerConfig": { "start": "top 85%", "end": "bottom top", "enter": "play", "leave": "none", "enterBack": "none", "leaveBack": "none" } },
    "target": { "extensionKey": "wf:attribute", "value": "[data-animate=\"fade-up\"]" }
  }],
  "timelines": [{ "name": "Reveal", "actions": [{
    "id": "reveal", "name": "Fade up", "tt": 2,
    "targets": [{ "extensionKey": "wf:trigger-only", "value": "" }],
    "timing": { "duration": 0.6, "ease": 5 },
    "properties": { "wf:transform": { "opacity": ["0%", "100%"], "y": [24, 0] } }
  }]}]
}
```

Split text adds `"splitText": { "type": "lines", "mask": "lines" }` at action level (never inside `timing`) and `"stagger": { "each": 0.1 }` in `timing`. Parallax uses `scrub: 1` in `scrollTriggerConfig` with `start "top bottom"`, `end "bottom top"`. Custom events use `"extensionKey": "wf:custom"`, target `wf:body` `""`, and `config.pluginConfig.eventName`.

Learned on the guinea-pig site (22 Sep 2026): a `wf:attribute` trigger with a `wf:trigger-only` action target is accepted for scroll, hover and click; attribute selectors are plain only; a `wf:load` trigger takes no target, so its action targets the attribute; any child or descendant action target needs `filterContext.filterBy` with a real class, so site-wide stagger is impossible and lives in Components.

Gotchas the guide is firm on: opacity lives under `wf:transform`; `ease` is an index, `easing` is silently dropped; a bare `duration` number is seconds; `tt: 0` with a `[from, to]` pair is rejected; `timing.delay` is rejected (use `timing.position`); caps are 5 timelines, 20 triggers, 200 actions. `wf:trigger-only` as the action target is the way to animate the very element that matched the trigger; verify on the guinea pig that it works with an attribute trigger, else target the same attribute selector.

## 10. Converting motion from Figma, Relume, GitHub or IX2

1. **Inventory** every animation: element, trigger, motion, timing.
2. **Map to a preset.** Dissolve → `fade-in`; move in from below → `fade-up`; smart-animate scale → `scale-in`; sequential cards → `stagger` on the parent; heading reveal → `split-lines`.
3. **Tune by choosing the preset**, not by editing timing per element. Different timing means a scoped copy, logged.
4. **Extend the vocabulary** only for a genuinely new pattern. Add the interaction, the row in section 2, and the guinea-pig verification note.
5. **Flag what does not map.** Never silently drop or approximate motion from the source.

## 11. Verification before "done"

- Preview or publish to staging and watch it: a successful create is not proof it played.
- A scroll reveal completes with the element's top between 15% and 75% of the viewport at a normal scroll speed.
- Reduced motion on: reveals show their end state, loops are still, parallax is off.
- 767 and 479: parallax off, nothing animates layout properties (transforms and opacity only).
- Every interaction is named per section 4 and carries its playback rules.
