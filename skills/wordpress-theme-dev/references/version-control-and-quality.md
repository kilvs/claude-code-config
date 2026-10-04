# Version Control, Project Hygiene & Quality

How to keep a theme project clean in git, and where to hand off for performance/SEO/accessibility auditing.

## Contents
1. What belongs in the repo (and what doesn't)
2. .gitignore for a theme
3. Committing field definitions & generated assets
4. Quality / performance / a11y — use the page-quality-auditor skill

---

## 1. What belongs in the repo (and what doesn't)

The theme directory is usually the repo root (or the theme lives in a repo that's symlinked into `wp-content/themes/`). Commit the source of truth; ignore anything generated, installed, or environment-specific.

**Commit**: PHP templates, `functions.php` and `inc/`, `theme.json`, block templates/parts/patterns, SCSS *source*, the compiled CSS you ship, `style.css`, `package.json`/`composer.json` (and lockfiles), `acf-json/` (ACF field definitions), `.pot` translation template.

**Ignore**: `node_modules/`, `vendor/` (restore via `composer install`), compiled CSS *source maps* in production, OS cruft, editor folders, local env files, and any secrets.

A subtlety on compiled CSS: in a theme that ships to clients/hosts who run `composer install` / `npm install`, you generally **do** commit the compiled `assets/css/*.css` so the theme works without a build step on the server. If your deploy pipeline builds on deploy, you can ignore it instead. Decide per project and be consistent; don't commit both an ignored and tracked copy.

## 2. .gitignore for a theme

A sensible default (the scaffolds now drop this in):

```gitignore
# Dependencies
/node_modules/
/vendor/

# Build artifacts
*.css.map
.sass-cache/

# OS / editor
.DS_Store
Thumbs.db
.idea/
.vscode/
*.sublime-*

# WordPress / local env
wp-config.php
/wp-content/uploads/
*.log
debug.log

# Secrets / env
.env
.env.*
```

Note `wp-config.php` and `debug.log` are listed because people sometimes init a repo above the theme; inside a theme-only repo they're harmless to keep. Adjust to the repo root.

## 3. Committing field definitions & generated assets

- **ACF / SCF**: commit the `acf-json/` directory so field groups travel with the theme and sync across environments. If you register fields in PHP instead (`acf_add_local_field_group`), that PHP is committed like any other code. See `custom-fields.md` §6.
- **Carbon Fields**: field definitions are PHP, so they're version-controlled by nature; `vendor/` (where the library installs) is ignored and restored with `composer install`.
- **Translations**: commit the `.pot` template; committing compiled `.mo`/`.po` is optional and project-dependent.

## 4. Quality / performance / a11y — use the page-quality-auditor skill

This skill builds themes; it does not duplicate page-quality auditing. For Core Web Vitals (LCP/INP/CLS), Lighthouse scoring, SEO (meta tags, headings, structured data, crawlability), and accessibility (WCAG, contrast, alt text, screen-reader semantics), hand off to the **page-quality-auditor** skill, which is built for exactly that and is platform-aware (it knows WordPress).

Two ways they fit together:
- **At build time**: write the theme to a clean standard as you go (semantic HTML5, escaped output, properly enqueued/deferred assets, alt text on `the_post_thumbnail`), then run page-quality-auditor on the result to catch what slipped.
- **As an audit**: when the task is "make this theme faster / more accessible / rank better," that *is* the page-quality-auditor skill's job — reach for it directly rather than re-deriving the checks here.

The handoff is deliberate: keep theme-construction logic here, keep the prioritized audit-and-fix logic there, so neither drifts out of sync with the other.
