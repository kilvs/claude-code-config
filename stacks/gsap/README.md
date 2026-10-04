# GSAP playbook (custom-code motion)

**Status:** occasional. Playbook started 29 Sep 2026.

## What it is used for
Motion written as code: the motion script in static HTML preview repos, theme and app code,
and custom behaviour on Webflow sites that IX3 cannot do. On Webflow, motion is IX3 first
(`stacks/webflow/`, memory `webflow-motion-is-ix3.md`); IX3 runs on GSAP, so this stack also
explains IX3 bugs.

## Conventions
- Load the skill `skills/gsap/` for any GSAP work. Its "House rules" are the conventions:
  fail visible, `gsap.matchMedia()` for breakpoints and reduced motion, transforms and
  `autoAlpha` only, never the LCP element, parallax never on `body` and off below 768, one
  owner per element, GSAP loaded once.
- One motion script per site, driven by data-attribute presets named in the project's motion
  spec. Presets in a preview repo must map one to one onto IX3 presets, so the Webflow
  rebuild is a lookup, not a translation.
- Pin the GSAP version. Before using SplitText's `mask`, `autoSplit` or `onSplit`, check the
  pinned version is 3.13 or later.

## Accounts and tools
No accounts. GSAP from `cdn.jsdelivr.net/npm/gsap@<version>/` (3.15.0 is current, 13 Apr 2026;
Webflow's IX3 serves the same), all plugins free since 3.13.
Chrome DevTools Performance panel with 4x CPU throttle for scroll-heavy pages. GSDevTools and
`markers: true` while building only.

## Gotchas that became rules
| Date | What happened | Rule |
|---|---|---|
| 29 Sep 2026 | An IX3 load animation on the hero image kept it hidden until the footer scripts ran; mobile LCP hit 5.7s | Never animate the LCP element; animate the hero copy |
| 29 Sep 2026 | GreenSock's skills say `text-wrap: balance` interferes with SplitText | On a split heading, turn balance off and set the breaks deliberately |
| 29 Sep 2026 | GSAP 3.15 deprecated `yoyoEase` | Use `easeReverse` |
| 29 Sep 2026 | IX3 gained Mouse Move (Jul 2026) and variable animation (Mar 2026) | Cursor effects and token-driven motion on Webflow are IX3, not a script |

## Pointers
`skills/gsap/SKILL.md` (adapted from github.com/greensock/gsap-skills, MIT),
https://gsap.com/docs/v3/, `stacks/webflow/README.md` and the kit's `interactions.md` for IX3.
