---
name: swiper-slider
description: How every slider on this site is built. Swiper 14 driven by data-swiper-element role attributes, styled with Designer classes and started by one script in the Global Scripts component. Reference this skill whenever creating, editing, converting, reviewing or debugging a slider, carousel, testimonial row, card row, CMS slider, or a grid that becomes a slider on smaller screens, and before adding any slider library.
---

# Swiper slider kit

Every slider on this site runs on one setup, decided by the user on 29 Sep 2026 and tested on staging (Sample Slider Test 51). The `sliders` rule is the law; this skill is the manual. A live demo and a copyable docs page exist on that test site at `/slider-docs`.

## 1. How it works (plain words)

The kit turns a row of divs into a slider that visitors can swipe, drag or click through.

1. **Mark the parts.** The wrapper, the row and each slide get one attribute, `data-swiper-element`. That is how the script knows which element is which.
2. **Style with classes.** Slide width, the gap between slides and the arrows are normal Webflow classes, so the Designer canvas shows what visitors get.
3. **One script runs it all.** A single script in the Global Scripts component starts every slider on every page. A new slider needs no new code.

| Word | Meaning |
|---|---|
| Mask | The window you look through. It hides the slides off to the side. |
| Track | The long row that holds every slide. Swiper moves it left and right inside the mask. |
| Slide | One item in the row: a card, an image, a testimonial. |
| Setting | A switch that changes behaviour: loop, autoplay, free drag. |
| Named config | A list of settings written in JavaScript and given a name, for sliders that need more than a few switches. |

## 2. Prerequisites

| Need | Why |
|---|---|
| A plan that allows custom code | Code Embeds and page custom code need a paid Site plan or a paid Workspace. |
| A `page-wrapper` div on every page | The two global components sit inside it (builder section 9). |
| The Global Styles component | One Code Embed with the site CSS, first child of `page-wrapper`. |
| The Global Scripts component | One Code Embed with our scripts, last child of `page-wrapper`, class `global-scripts`. |
| Nothing to install | Swiper loads from cdnjs with one script tag. No account, npm, build step or Swiper CSS file. |

## 3. Installation (once per site)

### Step 1: load Swiper on pages that have a slider

Page settings, Custom code, **Before body tag**, only on pages with a slider (performance rule: page-only libraries never load site-wide). Add one script tag with these attributes:

| Attribute | Value |
|---|---|
| `src` | `https://cdnjs.cloudflare.com/ajax/libs/Swiper/14.2.0/swiper-bundle.min.js` |
| `integrity` | `sha512-nM1ZmLe8KJ0bEkxcoG3D09bO8YvrITjvqMRPqEj14rYoNH/Hdg+ZR3hC+ez1S08A5NxEkRDgyBWVTZZgLQLhaQ==` |
| `crossorigin` | `anonymous` |
| `referrerpolicy` | `no-referrer` |

No `async` or `defer` is needed: the kit script waits for it through the ready gate. Never load `swiper-bundle.min.css`; step 2 replaces it and the two clash.

### Step 2: slider CSS in the Global Styles embed

Paste inside the embed's style tag, under these banners. It renders on the canvas too.

```css
/* ===== SLIDER (SWIPER): STRUCTURE ===== */
/* Defaults have zero specificity, so classes win. Track is flex = slider; set it to grid at a breakpoint = no slider there. */
[data-swiper-element="swiper"] { position: relative; overflow: hidden; }
:where([data-swiper-element="swiper-wrapper"]),
:where([data-swiper-element="swiper"] :has(> [data-swiper-element="slide"])) {
  position: relative; z-index: 1; display: flex; width: 100%;
  box-sizing: content-box; transition-property: transform;
}
/* A slot between the track and the slides takes the track's layout */
[data-swiper-element="swiper-wrapper"] > :has(> [data-swiper-element="slide"]) {
  display: inherit; grid-template-columns: inherit; gap: inherit; width: 100%;
}
[data-swiper-element="slide"] { position: relative; flex-shrink: 0; transition-property: transform; }
:where([data-swiper-element="slide"]) { width: 100%; }
:where([data-swiper-element="pagination"]) { display: flex; align-items: center; gap: 0.375rem; min-height: 1.5rem; }

/* ===== CANVAS HOOKS ===== */
.wf-design-mode [data-swiper-element="swiper"] { overflow-x: auto; }
/* The canvas draws empty divs as tall placeholder boxes; keep the preview dots at their real height */
.wf-design-mode [data-swiper-element="pagination"]:empty { height: 1.5rem !important; min-height: 0 !important; padding: 0 !important; align-items: center; }
.wf-design-mode [data-swiper-element="pagination"]:empty::before {
  content: ""; width: 1.5rem; height: 0.5rem; border-radius: 999px; background-color: currentColor;
}
.wf-design-mode [data-swiper-element="pagination"]:empty::after {
  content: ""; width: 2.75rem; height: 0.5rem; opacity: 0.25;
  background: radial-gradient(circle, currentColor 0 0.25rem, transparent 0.26rem) -0.3125rem 0 / 1.125rem 0.5rem repeat-x;
}

/* ===== SLIDER (SWIPER): RUNTIME CLASSES ===== */
/* Classes Swiper adds while it runs; library classes, not Designer state classes */
[data-swiper-element="component"] .swiper-horizontal { touch-action: pan-y; }
[data-swiper-element="component"] .swiper-notification { position: absolute; top: 0; left: 0; opacity: 0; pointer-events: none; z-index: -1000; }
.swiper-fade [data-swiper-element="slide"] { pointer-events: none; transition-property: opacity; }
.swiper-fade .swiper-slide-active { pointer-events: auto; }
[data-swiper-element="pagination"] .swiper-pagination-bullet {
  display: flex; align-items: center; justify-content: center; height: 1.5rem; padding: 0 0.125rem;
  border: 0; background: none; color: inherit; cursor: pointer;
}
[data-swiper-element="pagination"] .swiper-pagination-bullet::before {
  content: ""; width: 0.5rem; height: 0.5rem; border-radius: 999px; background-color: currentColor;
  opacity: 0.25; transition: width 0.3s ease, opacity 0.3s ease;
}
[data-swiper-element="pagination"] .swiper-pagination-bullet:hover::before { opacity: 0.5; }
[data-swiper-element="pagination"] .swiper-pagination-bullet-active::before { width: 1.5rem; opacity: 1; }
[data-swiper-element="pagination"] .swiper-pagination-bullet:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; border-radius: 999px; }
[data-swiper-element="swiper-prev"].swiper-button-disabled,
[data-swiper-element="swiper-next"].swiper-button-disabled { opacity: 0.35; pointer-events: none; }
[data-swiper-element="component"] .swiper-button-lock,
[data-swiper-element="component"] .swiper-pagination-lock { display: none; }
```

### Step 3: the kit script in the Global Scripts embed

Paste inside a script tag in the Global Scripts embed, under its own banner.

```js
// ===== SLIDER (SWIPER) =====
// Roles:    data-swiper-element = component | swiper | swiper-wrapper | slide | pagination | swiper-prev | swiper-next
// Quick:    data-swiper-* attributes, e.g. data-swiper-loop="true" -> { loop: true }
// Full:     data-swiper-config="name" + window.SliderConfig.name = { any Swiper params, breakpoints, on }
// Layout:   the Designer decides. Track is flex = slider; track set to grid at a breakpoint = no slider there.
// API:      Slider.get('name') returns the Swiper instance; Slider.init(element) starts sliders added later.
// Globals:  window.Slider and window.SliderConfig are the kit's public API, the only globals the kit rules allow.
window.SliderConfig ||= {};
window.Webflow ||= [];
window.Webflow.push(() => {
  if (!window.Swiper) return;

  const ROLE = 'data-swiper-element';
  const find = (scope, role) => scope.querySelector(`[${ROLE}="${role}"]`);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const breakpoints = ['(max-width: 991px)', '(max-width: 767px)', '(max-width: 479px)'].map(q => matchMedia(q));

  const DEFAULTS = {
    slidesPerView: 'auto', // widths come from the Designer, not from Swiper
    speed: 600,
    grabCursor: true,
    watchOverflow: true,
    observer: true,
    observeParents: true,
  };

  // "true" -> true, "600" -> 600, '{"delay":4000}' -> object, anything else stays text
  const parse = raw => {
    if (raw === 'true') return true;
    if (raw === 'false') return false;
    if (/^-?\d+(\.\d+)?$/.test(raw)) return Number(raw);
    if (/^[{[]/.test(raw)) {
      try { return JSON.parse(raw); } catch (e) { console.warn('[slider] invalid JSON:', raw); }
    }
    return raw;
  };

  // Empty values are skipped, so an empty component prop means "use the default"
  const readOptions = node => {
    const options = {};
    for (const [key, raw] of Object.entries(node.dataset)) {
      if (!key.startsWith('swiper') || ['swiperElement', 'swiperConfig'].includes(key) || raw.trim() === '') continue;
      options[key.charAt(6).toLowerCase() + key.slice(7)] = parse(raw.trim());
    }
    return options;
  };

  const setup = mask => {
    const firstSlide = find(mask, 'slide');
    if (!firstSlide || mask.dataset.sliderReady) return;
    if (!mask.getClientRects().length) return; // hidden by a variant (Static / Slotted)
    mask.dataset.sliderReady = 'true';

    const wrapper = firstSlide.parentElement; // the track, or a slot inside it
    const container = wrapper.parentElement;
    const scope = mask.closest(`[${ROLE}="component"]`) || mask.parentElement;
    const next = find(scope, 'swiper-next');
    const prev = find(scope, 'swiper-prev');
    const pagination = find(scope, 'pagination');
    const name = scope.dataset.swiperConfig || mask.dataset.swiperConfig;

    const options = { ...DEFAULTS, ...window.SliderConfig[name], ...readOptions(scope), ...readOptions(mask) };
    if (typeof options.autoplay === 'number') {
      options.autoplay = { delay: options.autoplay, pauseOnMouseEnter: true, disableOnInteraction: false };
    }
    if (reduceMotion) Object.assign(options, { speed: 0, autoplay: false });

    const slides = () => [...wrapper.children].filter(el => el.matches(`[${ROLE}="slide"]`));
    const isSlider = () => getComputedStyle(wrapper).display.includes('flex');

    // The gap is designed on the track; hand it to Swiper instead
    const readGap = () => {
      wrapper.style.gap = '';
      const gap = parseFloat(getComputedStyle(wrapper).columnGap) || 0;
      wrapper.style.gap = '0px';
      return gap;
    };

    const mount = () => {
      // Swiper looks for these classes internally; added here so the Designer stays clean
      wrapper.classList.add('swiper-wrapper');
      slides().forEach(el => el.classList.add('swiper-slide'));
      const swiper = new Swiper(container, {
        ...options,
        spaceBetween: readGap(),
        navigation: next || prev ? { nextEl: next, prevEl: prev } : false,
        pagination: pagination ? { el: pagination, clickable: true, bulletElement: 'button' } : false,
      });
      scope.dispatchEvent(new CustomEvent('slider:ready', { bubbles: true, detail: { swiper, name } }));
    };

    const unmount = () => {
      container.swiper.destroy(true, true);
      wrapper.classList.remove('swiper-wrapper');
      slides().forEach(el => el.classList.remove('swiper-slide'));
      pagination?.replaceChildren();
      scope.dispatchEvent(new CustomEvent('slider:destroy', { bubbles: true, detail: { name } }));
    };

    const sync = () => {
      const running = Boolean(container.swiper);
      if (isSlider() && !running) mount();
      else if (!isSlider() && running) unmount();
      else if (running) {
        container.swiper.params.spaceBetween = readGap();
        container.swiper.update();
      }
    };

    sync();
    breakpoints.forEach(mq => mq.addEventListener('change', sync));
  };

  const all = root => (root.matches?.(`[${ROLE}="swiper"]`) ? [root] : [...root.querySelectorAll(`[${ROLE}="swiper"]`)]);

  window.Slider = {
    init: (root = document) => all(root).forEach(setup),
    get: name => {
      const scope = document.querySelector(`[data-swiper-config="${name}"]`);
      return scope ? all(scope).map(mask => find(mask, 'slide')?.parentElement.parentElement.swiper).find(Boolean) ?? null : null;
    },
  };

  window.Slider.init();
});
```

### Step 4: markup and classes

Any class names work; the roles do the wiring. Slides sit directly inside the track.

```html
<div class="slider_component" data-swiper-element="component">
  <div class="slider_mask" data-swiper-element="swiper">
    <div class="slider_track" data-swiper-element="swiper-wrapper">
      <div class="slider_slide" data-swiper-element="slide">Slide 1</div>
      <div class="slider_slide" data-swiper-element="slide">Slide 2</div>
      <div class="slider_slide" data-swiper-element="slide">Slide 3</div>
      <div class="slider_slide" data-swiper-element="slide">Slide 4</div>
    </div>
  </div>
  <div class="slider_controls">
    <button type="button" class="slider_arrow" data-swiper-element="swiper-prev" aria-label="Previous slide">&larr;</button>
    <div class="slider_pagination" data-swiper-element="pagination"></div>
    <button type="button" class="slider_arrow" data-swiper-element="swiper-next" aria-label="Next slide">&rarr;</button>
  </div>
</div>
```

The only thing the slider needs from the Designer: the track is `display: flex` with a `column-gap`. Everything else is the design.

```css
/* Style these as classes in the Designer, every colour and size bound to a token.
   The embed never names a class. var(--…) names here stand for the token to bind. */
.slider_track { display: flex; column-gap: 1.5rem; }             /* flex = slider */
.slider_slide { width: calc((100% - 3rem) / 3); }                /* 3 across */
.slider_controls { display: flex; align-items: center; column-gap: 0.75rem; margin-top: 2rem; }
.slider_pagination { flex: 1; order: -1; color: var(--text-primary); } /* dots left, arrows right; bind Theme text/primary */
.slider_arrow { display: flex; justify-content: center; align-items: center;
  width: 2.75rem; height: 2.75rem; padding: 0; border: 0; border-radius: 999px;
  background: none; color: inherit; font: inherit; cursor: pointer; } /* button reset */

@media screen and (max-width: 991px) {
  .slider_slide { width: calc((100% - 1.5rem) / 2); }            /* 2 across */
}
@media screen and (max-width: 767px) {
  .slider_slide { width: 85%; }                                  /* 1 plus a peek */
}
```

## 4. Roles

| `data-swiper-element` | Put it on | Needed |
|---|---|---|
| `component` | The outer wrapper. Scopes the controls and holds the settings. | Yes |
| `swiper` | The mask. Clips the row with `overflow: hidden`. | Yes |
| `swiper-wrapper` | The track. Its column gap becomes the space between slides. | Yes |
| `slide` | Each slide. | Yes |
| `pagination` | An empty div. The script fills it with dot buttons. | Optional |
| `swiper-prev` / `swiper-next` | The arrows: real `button` elements with `type="button"` and an `aria-label` ("Previous slide", "Next slide"), never divs (accessibility rule). In Webflow: a Custom Element with the tag `button` (element builder `DOM`, `dom_tag: "button"`); read the element type back after building. | Optional |

Each slider only looks for controls inside its own `component`, so a page can hold any number. CMS: `swiper` on the Collection List Wrapper, `swiper-wrapper` on the Collection List, `slide` on the Collection Item. Component: a slot may sit inside the track; it publishes as a bare `div` and the CSS passes the track's layout and gap to it.

## 5. Settings

Merge order, later wins: kit defaults, named config, attributes on `component`, attributes on `swiper`.

**Quick: attributes.** `data-swiper-` plus the Swiper setting in kebab-case. `true`/`false` become booleans, digits become numbers, `{...}` is read as JSON, empty values are ignored (so an empty component prop means "use the default"). No code change is ever needed for a new setting.

```html
<!-- data-swiper- plus the Swiper setting in kebab-case. No code change needed. -->
<div data-swiper-element="component"
     data-swiper-free-mode="true"
     data-swiper-autoplay="5000"
     data-swiper-speed="800"
     data-swiper-breakpoints='{"768":{"slidesPerGroup":2}}'>
```

| Attribute | What it does | Example |
|---|---|---|
| `data-swiper-loop` | After the last slide, go back to the first. | `true` |
| `data-swiper-free-mode` | Drag freely instead of snapping. | `true` |
| `data-swiper-autoplay` | Move on its own; the number is the pause in ms. | `5000` |
| `data-swiper-speed` | How long one move takes, in ms. | `800` |
| `data-swiper-centered-slides` | Keep the active slide in the middle. | `true` |
| `data-swiper-slides-per-group` | How many slides one click moves. | `2` |
| `data-swiper-effect` | Fade instead of slide. | `fade` |

**Full: a named config.** Name the slider, then describe it in the section's `section-script-js` embed so it travels with the section. Any Swiper parameter works, including `breakpoints` and `on` handlers.

```html
<div class="slider_component" data-swiper-element="component" data-swiper-config="team">
```

```js
// ===== TEAM SLIDER CONFIG =====
// In the section's section-script-js embed. The section sits above Global Scripts,
// so this callback is queued first and the config exists before the kit starts.
window.Webflow ||= [];
window.Webflow.push(() => {
  window.SliderConfig ||= {};
  window.SliderConfig.team = {
    speed: 800,
    loop: true,
    autoplay: { delay: 5000, pauseOnMouseEnter: true, disableOnInteraction: false },
    breakpoints: {
      0: { slidesPerGroup: 1, freeMode: true },    // mobile portrait and up
      768: { slidesPerGroup: 2, freeMode: false }, // tablet and up
      992: { slidesPerGroup: 3 },                  // desktop and up
    },
    on: {
      // State only: expose the current slide for styling or a counter
      slideChange(swiper) {
        const component = swiper.el.closest('[data-swiper-element="component"]');
        if (component) component.dataset.activeSlide = String(swiper.realIndex + 1);
      },
    },
  };
});
```

Never set `slidesPerView` to a number: Swiper then writes widths inline and the canvas stops matching the live page. The kit runs `slidesPerView: 'auto'` so the slide class owns width.

## 6. Breakpoints

Swiper counts min-widths from mobile up; Webflow counts max-widths from desktop down. Use these keys so they line up. Behaviour goes in `breakpoints`; widths and gaps stay in classes (the script re-reads the gap at 991, 767 and 479).

| Swiper key | Webflow breakpoint | Width |
|---|---|---|
| `0` | Mobile portrait | 0 to 479px |
| `480` | Mobile landscape | 480 to 767px |
| `768` | Tablet | 768 to 991px |
| `992` | Desktop | 992px and up |

## 7. Grid on desktop, slider below

No code. The script checks the track at every Webflow breakpoint: flex means slider, grid means no slider. When it stops, Swiper removes every inline style it wrote and the grid comes back clean (`slider:destroy` fires).

| Class | Desktop | Tablet and below |
|---|---|---|
| Track | `display: grid`, 3 columns, gap | `display: flex` |
| Slide | no width | half on tablet, `85%` on mobile |
| Controls | hidden with an `is-hide-desktop` combo | visible |

## 8. Control a slider with code

```js
// At page load: wait for the slider to start, then use it.
window.Webflow ||= [];
window.Webflow.push(() => {
  document.addEventListener('slider:ready', (event) => {
    const { swiper, name } = event.detail;
    if (name !== 'team') return;
    swiper.slideTo(2);
  });
});
```

```js
// Any time after load, for example in a click handler:
const team = Slider.get('team'); // the Swiper instance, or null
team?.slideNext();
team?.autoplay.stop();

// Without a name, the instance also sits on the element Swiper runs on:
const swiper = document.querySelector('.swiper-initialized')?.swiper;
```

```js
// Slider markup added after load (a modal, a tab, fetched HTML):
Slider.init(document.querySelector('.modal'));

// Slides added to a running slider (for example a CMS "load more"):
const cms = Slider.get('news');
newItems.forEach((item) => item.classList.add('swiper-slide'));
cms.update();
```

`slider:ready` is dispatched on the component and bubbles, so listen on `document`. A section script's ready-gate callback is queued before the kit's (the section sits above Global Scripts), so at load it uses the event rather than `Slider.get`.

## 9. Building it through MCP

Order that works (checked 29 Sep 2026):

1. Load Swiper in the page footer with `data_scripts_tool` `set_page_freeform_code`. Put the CSS and script into the Global Styles and Global Scripts embeds with `data_element_settings_tool` `set_settings` key `code`.
2. Build static markup with `data_whtml_builder`; custom attributes survive. Give the CSS in the same call so the classes are created.
3. **Component version:** Slide Card (group Cards, props Heading, Text, Image, Alt text) inside Slider Slide (group Slots, root carries `slide`, holds `Slot: Content`, variants for width such as Three across and Full width) inside Slider (group Global, root carries `component`, track holds `Slot: Slides`, props Loop, Free drag, Autoplay, Show arrows, Show dots). Transform from the inside out with `transform_element_to_component`, add slots with the element builder type `ComponentSlot` and `scope_component_id`, name them with `set_display_name`.
4. Fill slots on the page instance with `data_component_builder` `insert_in_slot`; nested slots work in one call by display name (`Slot: Content`).
5. **CMS version:** element builder type `CMSCollection`, set `source` with `static_json`, add roles and classes to the wrapper, list and item, bind the card props with `binding_source_type: cms`. Sort by a Number `order` field.

Known limits of the API (do these by hand in the Designer and say so):

- Starter content cannot be placed in a slot inside a component definition.
- A custom attribute value cannot be bound to a prop (Loop, Free drag, Autoplay on the Slider root). Visibility bindings work.
- `set_dom_id` on new sections can fail with a component-map conflict.

## 10. Gotchas that became rules

| What happened | Rule |
|---|---|
| `display: grid` with no template drew as a 2x2 grid on the canvas and cards filled one cell | Single-column wrappers are flex columns |
| A Collection List kept stacking | Set `display: flex` on the track class; Webflow's list styles beat the kit's zero-specificity default |
| The component slides came out one gap narrow and would have shown text | Without Swiper's CSS, its a11y `.swiper-notification` span is a flex item; the kit CSS hides it |
| Collection List showed newest first | Add a Number `order` field and sort by it |
| Empty pagination drew as a tall placeholder on the canvas | The canvas hook pins its height and draws preview dots |
| The style panel saved `Menlo, Consolas` as `Menlo` | Font stacks go in an embed |
| A `data-swiper-free-mode` JSON value was refused: custom attribute values cannot contain double quotes | Object settings (freeMode, mousewheel, keyboard) go in a named config in the section's `section-script-js` embed |
| A per-frame script wrote CSS variables on the slider root and the slider froze on drag and wheel: `observeParents` saw each write and reset the position | Per-frame state goes on the wrapper (`swiper.wrapperEl`) or the slides, never on the mask's parents |
| With a slot between track and slides, Swiper runs on the track and the slot becomes the wrapper | Expected; the mask still clips. Test in the canvas by loading Swiper into the canvas frame and running the setup by hand, then reload |
| A section needed the same posts on every page and its own posts on some | Static / Slotted variants: two wrappers in the component, each with its own mask and track; Static (base) holds the cards in the definition, Slotted holds the slot; the variant sets `display: none` on the other wrapper. The kit skips a hidden mask (`getClientRects().length` guard), so only the visible one mounts |

## 11. Before calling a slider done

- Track flex with a gap, slide widths set at base, 991 and 767, controls inside `component`.
- Drag, arrows and dots work; the arrows are `button` elements with an `aria-label`; arrows disable at the ends unless it loops; arrows and dots are reachable by keyboard.
- With reduced motion on, there is no autoplay and no animated moves.
- Checked at 1440, 992, 768 and 390 on staging; no horizontal page overflow.
- CMS sliders sort by `order`; images have real alt text from a field, not the item name.
