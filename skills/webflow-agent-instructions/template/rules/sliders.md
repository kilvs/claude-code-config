# Sliders

- **Every slider is Swiper 14 through the slider kit** (the `swiper-slider` skill). Never the native Webflow Slider element, Splide, Slick, Owl, a second slider library or a second copy of Swiper.
- **Roles, not library classes.** Parts are marked with `data-swiper-element` = `component` · `swiper` · `swiper-wrapper` · `slide` · `pagination` · `swiper-prev` · `swiper-next`. Never put `swiper`, `swiper-wrapper` or `swiper-slide` classes on elements in the Designer; the kit script adds them at runtime.
- **The Designer owns layout.** The track class sets `display: flex` and a `column-gap`; the slide class sets width per breakpoint. Swiper runs with `slidesPerView: 'auto'`; never set `slidesPerView` to a number.
- **Slides are direct children of the track.** A component slot is the one allowed wrapper in between. No padding on the track.
- **Grid-to-slider is a class change**: the track is grid at the breakpoints that show a grid and flex where it slides. Never a second script.
- **Loading:** Swiper only on pages that have a slider, in page footer code, pinned version with SRI. Never load Swiper's CSS file. The kit CSS lives in Global Styles, the kit script in Global Scripts.
- **Settings:** `data-swiper-*` attributes for a few switches; `data-swiper-config="name"` plus `window.SliderConfig.name` in the section's `section-script-js` embed for everything else. Breakpoint keys `0` / `480` / `768` / `992` match the Webflow breakpoints.
- **Every slider** has arrows that are real `button` elements (`type="button"`, `aria-label`), never divs, keyboard-reachable arrows and dots, honours reduced motion (the kit stops autoplay and animated moves) and is checked at 991, 767 and 479 before it is called done.
