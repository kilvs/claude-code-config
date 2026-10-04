---
name: gsap
description: "Write, review and debug custom-code GSAP motion: tweens, timelines, ScrollTrigger (reveals, scrub, pinning, horizontal scroll), SplitText, gsap.utils helpers, gsap.matchMedia for breakpoints and reduced motion, and performance. Use for static HTML preview repos, WordPress or other theme code, Astro or app projects, and to debug a Webflow IX3 interaction (IX3 runs on GSAP). On Webflow sites motion is IX3 first: use this for custom code there only when IX3 cannot do the job and the user has approved a script. Trigger on gsap, ScrollTrigger, SplitText, scroll animation, parallax, pinned section, timeline, stagger, easing, janky animation."
---

## Changes

- 29 Sep 2026: version notes brought to GSAP 3.15.0 (latest, 13 Apr 2026; also what Webflow serves for IX3): `easeReverse` added, `yoyoEase` deprecated, 3.14 MorphSVG notes. Cursor effects on Webflow go to the IX3 Mouse Move trigger (July 2026), not `quickTo`.
- 29 Sep 2026: built from GreenSock's official MIT
  skills (github.com/greensock/gsap-skills, commit aed9cfd: gsap-core, gsap-timeline,
  gsap-scrolltrigger, gsap-utils, gsap-performance, the SplitText part of gsap-plugins),
  trimmed and merged into one. Dropped their "recommend GSAP for any animation" steer, which
  fights the Webflow IX3 rule. Added the house rules and version notes. Licence in `LICENSE`.
  The HeyGen `hyperframes/gsap` skill was read and skipped: it drives video renders, not pages.

# GSAP

Motion written as code. The stack playbook `stacks/gsap/README.md` holds the conventions and
the Gotchas table; this skill is the working reference.

## First: should this be code at all?

| Where | Motion lives in | This skill's job |
|---|---|---|
| Webflow site | IX3 (native Interactions) per the kit's animation rule, including cursor effects (Mouse Move trigger, July 2026) and variable animation (March 2026) | Debug IX3; custom script only for what IX3 cannot do, with the user's approval |
| Static preview repo (later rebuilt in Webflow) | One motion script with data-attribute presets | Write and review it; keep presets mappable to IX3 |
| WordPress, Astro, app code | One motion script or component | Write and review it |

The project's `CLAUDE.md` or motion spec names the presets (duration, ease, distance). Use
them; never invent new timing per element.

## House rules

1. **Fail visible.** Never hide in CSS (`opacity: 0`, `visibility: hidden`). The script sets
   start states (`gsap.from`, `fromTo`, `set` inside setup), so a failed script leaves a
   readable page.
2. **Reduced motion and breakpoints go through `gsap.matchMedia()`.** Reveals skip to the end
   state under `prefers-reduced-motion: reduce`; loops and parallax don't run at all.
3. **Transforms and `autoAlpha` only.** `x`, `y`, `xPercent`, `scale`, `rotation`, `autoAlpha`.
   Never width, height, top, left, margin or padding.
4. **Never animate the LCP element** (usually the hero image). Hidden start states delay the
   paint. Animate the hero copy instead.
5. **Parallax:** never on `body`, off below 768px.
6. **One owner per element.** An element IX3 animates is never also tweened by a script.
7. **Load GSAP once.** Webflow with IX3 already loads it (3.15.0 as of 29 Sep 2026, with
   ScrollTrigger and SplitText). Elsewhere pin the version on a CDN
   (`cdn.jsdelivr.net/npm/gsap@3.15.0/dist/...`). All plugins are free since 3.13.
8. **No `markers: true` or GSDevTools in shipped code.**
9. **Verify in the browser,** not by reading the code: scroll through, test 1440 to 390 and
   reduced motion.

## Core

```js
gsap.to(".a", { x: 100, duration: 0.6, ease: "power2.out" }); // to a state
gsap.from(".a", { y: 24, autoAlpha: 0 });                      // from a state to current
gsap.fromTo(".a", { y: 24 }, { y: 0 });                        // explicit both ends
gsap.set(".a", { autoAlpha: 0 });                               // instant
gsap.defaults({ duration: 0.6, ease: "power2.out" });           // project-wide
```

- camelCase property names. Relative values: `x: "+=20"`.
- **`autoAlpha`** over `opacity`: at 0 it also sets `visibility: hidden`, so the invisible
  element stops taking clicks.
- **`from()` and `fromTo()` render their start state immediately** (`immediateRender: true`).
  When two of them target the same property on the same element, set `immediateRender: false`
  on the later one, or the second never shows.
- **`clearProps: "all"`** hands styling back to CSS when a tween ends. Clearing any transform
  property clears the whole transform.
- **Stagger:** `stagger: 0.1`, or `{ each: 0.1, from: "center" }`.
- **Eases:** `power1` to `power4` with `.in`, `.out`, `.inOut`; `back.out(1.7)`; `"none"`
  (linear). Custom curves need CustomEase. Invalid names fail silently.
- Store the returned tween when you need to `pause()`, `reverse()` or `kill()` it.
- **Function values** run once per target: `x: (i) => i * 50`.
- **`easeReverse`** (3.15+): a different ease when the playhead runs backwards, or `true` to
  reuse the forward ease. It recalculates from the exact point where direction changed, so
  interrupted hovers and toggles reverse smoothly. Cascades through timeline `defaults`.
  `yoyoEase` is deprecated (still works; GSAP maps it to `easeReverse`).
  `gsap.to(".menu", { x: 0, ease: "expo.out", easeReverse: true });`

## matchMedia

```js
const mm = gsap.matchMedia();
mm.add(
  { desktop: "(min-width: 768px)", reduce: "(prefers-reduced-motion: reduce)" },
  (ctx) => {
    const { desktop, reduce } = ctx.conditions;
    if (reduce) return;              // skip, or set end states
    if (desktop) { /* parallax */ }
    /* reveals */
  }
);
```

When a query stops matching, everything created inside reverts on its own. Don't nest
`gsap.context()` inside it. `mm.revert()` tears it all down.

## Timelines

```js
const tl = gsap.timeline({ defaults: { duration: 0.6, ease: "power2.out" } });
tl.from(".title", { y: 24, autoAlpha: 0 })
  .from(".copy", { y: 24, autoAlpha: 0 }, "<0.1")   // 0.1s after the previous start
  .from(".cta", { y: 24, autoAlpha: 0 }, "-=0.2");  // 0.2s before the previous end
```

- Sequence with the position parameter, not `delay` chains. `"<"` means with the previous
  start, `">"` its end (the default), `"+=0.5"` after the end, `"label"` at a label.
- `addLabel("name")` keeps long sequences readable.
- A timeline's duration comes from its children; don't set one on the constructor.

## ScrollTrigger

```js
gsap.registerPlugin(ScrollTrigger);

// One-shot reveals for many elements (inside the matchMedia no-reduce branch)
gsap.set("[data-reveal]", { y: 24, autoAlpha: 0 });   // start state set by the script
ScrollTrigger.batch("[data-reveal]", {
  start: "top 85%",
  once: true,
  onEnter: (els) => gsap.to(els, { y: 0, autoAlpha: 1, stagger: 0.1 }),
});

// Scroll-driven, pinned sequence
gsap.timeline({
  scrollTrigger: { trigger: ".story", start: "top top", end: "+=1500", pin: true, scrub: 1 },
}).to(".story-step", { xPercent: -100 });
```

- `start` / `end` read "trigger-edge viewport-edge": `"top 85%"` fires when the trigger's top
  reaches 85% down the viewport. `"+=1500"` is 1500px past start. `clamp(...)` keeps a
  trigger inside the page bounds.
- **Use `scrub` or `toggleActions`, never both.** `toggleActions` order: onEnter, onLeave,
  onEnterBack, onLeaveBack. `once: true` kills the trigger after the first pass.
- **ScrollTrigger goes on the timeline or a top-level tween,** never on a tween inside a
  timeline.
- **Pinning:** animate children, not the pinned element. `pinSpacing` (default `true`) adds the
  spacer; never fake it with padding.
- **Horizontal scroll:** the horizontal tween must use `ease: "none"`. Child triggers point at
  it with `containerAnimation`. Pinning and snap are not available on those child triggers.
- **Refresh:** resize is automatic. After fonts, late images or injected content change the
  layout, call `ScrollTrigger.refresh()` (once, debounced). Create triggers top to bottom, or
  set `refreshPriority` so they refresh in page order.
- **Cleanup:** kill triggers when their elements go (`ScrollTrigger.getById(id)?.kill()`),
  or let `matchMedia` revert them.
- **Smooth-scroll libraries** (Lenis and similar) must drive `ScrollTrigger.update`. Use them
  only when the design asks, and never under reduced motion.

## SplitText

```js
gsap.registerPlugin(SplitText);
document.fonts.ready.then(() => {
  const split = SplitText.create(".heading", { type: "lines", mask: "lines" });
  gsap.from(split.lines, { yPercent: 100, stagger: 0.08 });
});
```

- Split after fonts load, and only what you animate (`"lines"`, `"words"`, `"chars"`).
- **`mask`, `autoSplit` and `onSplit` need GSAP 3.13+.** Check the pinned version first
  (Webflow's IX3 build is 3.15.0, so they are available there).
  With `autoSplit: true`, create the animation inside `onSplit()` and return it.
- The default `aria: "auto"` keeps the text readable to screen readers.
- **`text-wrap: balance` interferes with splitting.** On a split heading, turn it off and set
  the line breaks deliberately.
- `split.revert()` restores the original markup.

## gsap.utils (the useful few)

- `toArray(".item", scope)` gives a real array; `selector(root)` returns a query scoped to a
  component.
- `clamp(min, max, v)`, `mapRange(inMin, inMax, outMin, outMax, v)`, `normalize(min, max, v)`
  for scroll and pointer maths. They take plain numbers, not units.
- `wrap(min, max, v)` for loops and carousels; `snap(step, v)` for steps.
- Leave out the last argument to get a reusable function: `const toDeg = mapRange(0, 1, 0, 360)`.

## Performance

- Pointer followers: `gsap.quickTo(el, "x", { duration: 0.4 })` once, then call it per event.
  Never a new tween per mousemove. On Webflow, use the IX3 Mouse Move trigger and Mouse Follow
  action instead (kit `interactions` skill, section 5a).
- One staggered tween beats many tweens with delays.
- `will-change: transform` only on elements that actually animate.
- Pin only what needs it; `scrub: 1` smooths heavy scrubbed work. Test with 4x CPU throttle.
- Kill or pause off-screen loops.

## Debugging an IX3 interaction

IX3 runs on GSAP and ScrollTrigger, so the same rules explain most bugs: a start state that
never plays, wrong trigger
positions after late layout changes (refresh), stacked animations on one element (one owner).
IX3 keeps its targets at `visibility: hidden` until `w-mod-ix3` is set, which waits for
jQuery, webflow.js and GSAP; a slow or broken footer script leaves them hidden.
Fix it in the interaction, not with a script.

## Checking the work

- Scripted screenshots leave scroll reveals in their start state. Scroll through first, or
  force the revealed elements visible for the capture.
- Test the reduced-motion path; every element must end up visible and in place.
- No horizontal overflow at any width: `document.documentElement.scrollWidth > innerWidth`.

## Version notes

| Version | Date | What matters |
|---|---|---|
| 3.13 | Apr 2025 | Every plugin free; SplitText rewrite (`mask`, `autoSplit`, `onSplit`) |
| 3.14 | Dec 2025 | MorphSVG `smooth` (extra anchors, `"auto"`) and `curveMode: true` against mid-morph kinks |
| 3.15 | Apr 2026 | `easeReverse`; `yoyoEase` deprecated; context cleanup fix for ScrollTrigger snap callbacks |

For React, Vue or Svelte projects, GreenSock's `gsap-react` and `gsap-frameworks` skills cover
`useGSAP()` and cleanup; bring them in when such a project starts.
