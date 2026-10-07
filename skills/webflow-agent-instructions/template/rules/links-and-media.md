# Links and media

- External links (any href leaving this site's domain) always open in a new tab: enable "Open in new tab" (`target="_blank"`) and add `rel="noopener"` via custom attributes.
- Internal links never open in a new tab.
- Every image element carries **explicit `width` and `height` attributes** (its intrinsic dimensions) so the browser reserves the space and layout never shifts (CLS).
- Hero / first-viewport large images: set Load to **Eager** (`loading="eager"`) and add the custom attribute `fetchpriority="high"`. Only the true above-the-fold hero image gets `fetchpriority="high"` — never more than one or two per page.
- All other below-the-fold images: Load = **Lazy**.
- **Image classes use `object-fit: contain`, never `cover`** (29 Sep 2026; the template's default from 30 Sep 2026), including the `aspect-ratio-*` utilities, so SVG art is never cropped. A photo that must fill its box gets an `is-cover` combo.
- Alt text is managed on the **asset** in the Assets panel — set once at upload, applied everywhere the image is used. Never set alt per element or per component instance. Override on an element only when a specific placement genuinely needs different context; mark purely decorative placements as decorative (empty alt).
- **Format:** every raster image ships as compressed **WebP** — static assets converted in the Assets panel or pre-export, and **CMS images compressed to WebP before upload** (CMS uploads are not auto-converted). Logos and icons stay SVG.
- **Graphics** (mock UIs, diagrams, illustrations): a **static** graphic is exported as **one SVG** (text outlined from the brand fonts, no embedded bitmaps, svgo-optimised, checked side by side against its source) and uploaded as an Image asset. Never WebP or PNG for a graphic that can be SVG. A graphic with any part that animates is **never** an image: see the animation rule.
- Export images at no more than 2× their largest displayed size. No multi-thousand-pixel originals behind card thumbnails.
