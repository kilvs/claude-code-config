# Animation Reference (native IX3)

Canonical source: `webflow-agent-instructions/template/webflow-skills/interactions.md` (the Webflow skill deployed to every site). This file is the designer-facing summary so a spec names presets correctly. Do not duplicate the preset table here; edit the kit skill.

Decided by the user on 22 Sep 2026: motion is **Webflow's native Interactions with GSAP (IX3)**. No Classic Interactions, no custom-code GSAP tweens. JavaScript holds state only (accordion, tabs, one-active groups) and fires IX3 custom events.

## How a design names motion

| In the spec | On the element | What plays |
|---|---|---|
| reveal | `data-animate="fade-up"` (or `fade-in`, `fade-down`, `fade-left`, `fade-right`, `scale-in`, `slide-left`, `slide-right`) | scroll reveal at `top 85%`, 0.6s, once |
| sequence | `data-animate="stagger"` on the parent | children fade-up 0.1s apart |
| heading reveal | `data-animate="split-lines"`, `"split-words"` or `"split-letters"` | masked lines, words or letters rising |
| hero on load | `data-animate="fade-up-load"` (hero only) | same reveal, on page load |
| depth | `data-animate="parallax"` on the image wrap | scroll-scrubbed drift, off below 768 |
| hover | `data-animate="lift"` / `"ring"` | scale 1.03 / expanding ring |
| tap | `data-animate="press"` | scale 0.97 and back |
| attention | `data-animate="pulse"` on the active item only | 2.4s loop |
| ticker | `data-animate="marquee"` | 40px per second, pauses on hover |
| nav | `data-nav="push\|slide\|dropdown"` + `-toggle`, `-panel` | panel-authored Navbar timeline |
| cursor | Mouse Move trigger, component-scoped | tilt, magnetic, spotlight or follow; `dont-animate` under reduced motion |

No per-element delay or duration exists. Different timing is a scoped copy of the preset, logged.

## Handoff note

List motion compactly in the build note: `home_legacy_content → stagger; home_legacy_image_wrap → scale-in; home_hero_heading → split-lines; home_hero_image_wrap → parallax`. Anything that does not map to a preset is flagged for the site owner, never approximated.
