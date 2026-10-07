# Core structure

- Every section follows this exact nesting, no skipped layers:
  `page-wrapper > main-wrapper > section-[page]_[element] > padding-section-[large|medium|small] > padding-global > container-[large|medium|small|semi-full|full] > [page]_[element]_content` (29 Sep 2026: vertical padding outermost, then the gutter, then the container). A site built before that date keeps its old `padding-global > container > padding-section` nest: match what the site already uses, never migrate it.
- `container-large` is the default. `container-semi-full` is edge to edge up to 1920px and capped beyond; `container-full` never caps. Both are for media, galleries and strips, never for text.
- Repeating items (grids, Collection Lists) use `[page]_[element]_list_wrap > _list > _item`. The grid/flex styling lives on `_list` — never on `_wrap`, never on `_item`.
- Images are wrapped: `[page]_[element]_image_wrap` (or `component_[name]_image-wrap`) around the image element.
- CTAs always sit inside `button-group`, even a single button.
- Semantic HTML: `header` / `nav` / `main` / `section` / `footer` tags; exactly one `h1` per page; no skipped heading levels. When visual size ≠ semantic level, keep the correct tag and style with `heading-style-h*` / `text-size-*` utilities.
- No classless divs that serve no purpose. If you can't say what a div is for, it shouldn't be there.
