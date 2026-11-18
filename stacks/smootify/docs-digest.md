# Smootify docs digest

Read 19 Nov 2026. Companion to `README.md` and `general-setup.md` in this folder.

**Two doc sets exist.** `docs.smootify.io` now carries a banner: "These docs are for Smootify 1.x". The current docs are
for **Smootify 2.0 (public beta)** at `www.smootify.io/docs`, with their own `llms.txt` and `llms-full.txt`. Our
October test build loaded `assets/latest/`, which is 1.x. New projects should start on 2.0.

Link shorthand: `v1:` = `https://docs.smootify.io/docs/`, `v2:` = `https://www.smootify.io/`.

## 1. Setup and prerequisites

| Need | Detail | Source |
|---|---|---|
| Shopify plan | Basic or higher. Starter cannot use the Headless channel | v2:docs/start/shopify-store |
| Webflow plan | Any workspace to build. Site plan with CMS to publish. No Ecommerce plan | v2:faq |
| Dev store | Partner account, "Create a store for a client". No time limit, no real payments | v1:getting-started/quick-start/shopify-store |
| Connect | Install the Shopify app (or the Webflow Marketplace app), open the dashboard, authorize one Webflow site. One project = one store + one site | v2:docs/start/webflow-project |
| Token | The app makes a test token. Before real orders, paste the Headless storefront's public token (all Storefront permissions). Test-token orders send no confirmation email. Private tokens are refused | v2:docs/start/shopify-store |
| Catalogue | Products and collections must be on the Headless sales channel and in your markets, or they neither load nor sync | v2:docs/start/shopify-store |
| Script (2.0) | One line in site Head code: `<script src="https://cdn.smootify.io/assets/v2/loader.js" data-channel="latest" data-css="true"></script>`. `data-channel="2.0.3"` pins a release. One `SmootifyUserOptions` script, placed before it | v2:docs/start/install |
| Locale | Webflow default locale must be set, or the sync imports nothing | v2:docs/start/cms |
| Debugger | Alt+Shift+D, or `?smootify-debug`, on `.webflow.io` only | v2:docs/start/debugger |
| Shopify identity verification | Not mentioned in either doc set | n/a |

## 2. Accounts, plans and pricing

Billed on the store's Shopify invoice, not to a card. "Whoever pays the Shopify bill pays Smootify." One subscription
covers one store and one project. Plans can be switched any time. (v2:pricing, v2:faq)

| Plan | Price | Unlocks |
|---|---|---|
| Free | $0 | Whole store on `.webflow.io` with a "Made with Smootify" badge, every Webflow app component, 10 client add-ons, CMS sync with Smootify Studio, Discord support |
| Lite | $19/mo ($15 yearly) | Custom domain, ticket support |
| Server | $49/mo ($39 yearly) | Lite + automatic CMS sync on Smootify's server + 7 server add-ons |

- Free works on a Partner dev store and on `.webflow.io`: "build against a free Shopify development store". (v2:faq)
- Purchase rules (min, max, multiple per variant, minimum order), delivery rules and "free gift above a threshold" come with the Shopify app on every plan. (v2:faq)
- A custom domain needs a paid plan **and** the domain in project settings, written exactly as published (`www` included). (v2:docs/start/webflow-project)

## 3. Hand-off between agency and client

Build in the agency's Smootify account on Free. Ownership of the Smootify project does not decide who pays: the plan
rides on the store's Shopify bill. Order (v2:docs/start/hand-off, v1:getting-started/publish/project-hand-off):

1. **Shopify.** Partner Dashboard, log in to the store, Settings > Users and permissions > Transfer ownership. Client accepts and picks a Shopify plan. Irreversible: if the client never accepts and pays, the store is lost. 1.x adds: the store freezes once the invite is sent, and the email cannot be changed. The Headless storefront and token move with the store.
2. **Webflow.** Transfer the **original** site, never a copy (a copy shows "Project not Connected" and needs a new integration). Client adds a site plan, connects the domain, publishes.
3. **Smootify.** Client signs in to the dashboard once (sharing to an email with no account is refused). Then **Share** (both keep access) or **Transfer** (it leaves the agency account). Client picks Lite or Server in the dashboard. Check the live domain in project settings.
4. **Reconnect Webflow.** The transfer revokes Smootify's Webflow access and stops the CMS sync. The client clicks Reconnect Webflow and picks the same site. If server sync was on, click Restart the sync. The plan is kept.

Also re-check after hand-off: Customer Account API JavaScript origins and callback URIs include the live domain; Studio users re-authorize (v1:ecommerce/faqs, "Invalid Webflow Token").

## 4. MCP and Webflow app

**Smootify MCP** (beta, read only, 20 tools). (v2:developers/mcp)
- Claude Code: `claude mcp add --transport http smootify https://mcp.smootify.io/mcp`, then `/mcp` and sign in with the Smootify account. Any plan, no key.
- Never writes to Shopify, never publishes. Knows 2.0 only.
- Useful tools: `check_markup` (HTML, Webflow clipboard or Designer tree), `scan_requirements`, `audit_site`, `check_license`, `probe_storefront`, `diagnose`.
- Skills: `github.com/smootify/skills` (5, including Figma to Webflow and site audit). (v2:skills)

**Webflow app (2.0).** 181 components inside the Designer. "Fits the selection" lists what can go inside the selected element. Each component goes in as a native Webflow component with props, **or as plain elements to restyle**. It also shows plan, domain and store. In 2.0 components live in the app, "not on a website to copy from". (v2:webflow-app)

**Smootify Studio** (desktop, beta). Creates the three CMS collections and fixes field settings the Webflow API cannot (decimal prices). Syncs by hand or every 5 minutes, logs each item. Runs your own Claude Code in `~/Smootify Studio/<site>` with a generated `CLAUDE.md`. (v2:docs/start/studio)

## 5. Components and attributes we have not used

- `button[data-is="direct-add-to-cart"]`: quick add on a card, no form. With `variant-swatches` in the card it adds the picked variant. (v2:docs/build/product-cards)
- `product="option-values"` with `option="bg-color"`: colour dots on cards. (same)
- `product="min-price"`, `min-available-price`, `min-compare-at-price` + `condition="variable-price"`: "From" prices. (same)
- `condition="is-new"`, `data-new-days`: New badge. (same)
- `smootify-product data-id="<numeric id>"`: a product anywhere, no CMS. (v2:docs/start/quick-start)
- `data-id` lists: `best-seller`, `created-at`, `related`, `complementary`, `metafields.custom.<key>`, `specific-collection`. (v1:ecommerce/products/listing)
- `smootify-search-discovery` with `data-vendor`, `data-collection`, `data-tag`. (v2:docs/build/filters)
- `data-action="page"` page numbers, `type="reset"` clear-all. (same)
- `variant="components"` and cart `box-item`: bundle contents. (v2:docs/features/fixed-bundles)
- `subscription-swatches` (Webflow Tabs + Radio Buttons). (v2:docs/features/subscriptions)
- `country-switcher`, `currency-code`, `location-switcher`. (v2:docs/features/markets)
- `metafield="rating" namespace="reviews"` sets `--metafield-rating` for CSS stars. (v2:docs/features/reviews)
- `smootify-consent`: cookie banner. (v2:docs/features/cookie-consent)
- `skeleton="text|image|..."`: loading shimmer. (v2:docs/start/changes)
- `data-free-gift` on the cart. (v2:faq)
- `data-format="table"` on a JSON metafield: size charts. (v2:docs/build/metafields)

## 6. Add-ons

| Add-on | Plan | Note |
|---|---|---|
| Wishlist, Last viewed | All | Turn on in dashboard |
| Magic Box (mix and match) | All | Turn on in dashboard. Cannot be a subscription |
| Magic add-ons | All | Needs Magic Box on |
| Cart upsell, Predictive search, Search & Discovery | All | Shopify's free features |
| Store locator | All | Mapbox token, stores from Shopify Locations |
| Dynamic properties, Customer metafield editor | All | Metafield access to set in Shopify |
| Booking, Product configurator, Name your price, Draft orders (quotes), Metaobject creator, Newsletter subscription, Product file upload | Server | Activate per project. Run only on the domain in settings |

Fixed bundles and multipacks come from the free Shopify Bundles app, nothing to turn on. (v2:docs/features/fixed-bundles)
Custom prices (configurator, name your price) go through a draft order invoice: discounts, Shop Pay and subscriptions behave differently. (v2:faq)

## 7. Customer accounts, wishlist, reviews, markets, subscriptions

- **Accounts.** 2.0 supports only Shopify's new customer accounts: passwordless email code, no separate sign-up. Headless > Customer Account API: client type Public, all permissions, both addresses in JavaScript origins and callback URIs (no trailing slash). Client ID goes in `newCustomerAccountsPublicKey`. Pages in an `account` folder are login-only. Orders, buy again, returns, addresses and subscriptions are buildable, or link to Shopify's account pages. (v2:docs/build/account)
- **Wishlist.** Guests: browser only. Logged in: browser + customer metafield `custom.wishlist_data` (set Read and write). Lists are not merged on login; last changed wins. Share link snapshot, up to 100 items. (v2:docs/features/wishlist)
- **Reviews.** Judge.me: elements provided, paid Awesome plan for headless (v1:apps/judge-me-reviews). Loox: Convert plan and up (v2; 1.x said Scale). Klaviyo Reviews: embeds. Or stars from `reviews.rating` metafields with no app code, which also feed Google. Or own reviews as metaobjects (Server). (v2:docs/features/reviews)
- **Markets.** Shopify Markets + `country-switcher`. Languages via Webflow Localization or Weglot. Products not sold in a market leave an empty block (`w-dyn-bind-empty`); 2.0 no longer redirects. (v2:docs/features/markets)
- **Subscriptions.** Need a Shopify subscription app for selling plans. Pause, resume, cancel from the account. Add-ons sell only with one-time purchase. (v2:docs/features/subscriptions)
- **Gift cards.** Shopify gift card products, optional recipient fields in the add-to-cart form, cart field named `gift-card`, balance form in 2.0. (v2:docs/build/gift-cards, v1:cart/cart-page)
- **Analytics.** 2.0 loads Meta, GA4, Google Ads and TikTok itself after consent, from `SmootifyUserOptions.analytics`. Remove other copies, tag managers included. (v2:docs/features/analytics)

## 8. Limitations and gotchas

- Synced items count against the Webflow CMS cap for all collections together. Shopify allows 3 option sets per product. (v2:docs/start/quick-start, v1:ecommerce/faqs)
- Main domain on Webflow only; checkout on a Shopify sub-domain set as primary. Redirect theme 1.1.1 sends `.myshopify.com` visitors to the site. (v2:docs/start/domains)
- Apps that use the app proxy (`/apps/…`) do not work. Theme app scripts need `type="smootify-load"`. (v2:docs/features/theme-apps)
- Publishing `.webflow.io` and the custom domain at different times breaks the sync. (v2:docs/start/cms)
- Custom CMS fields must not be required. Price fields must be decimal `0.00` or Webflow rounds. (same)
- `seo.hidden` or `sync.hidden` metafield set to 1 keeps a product out of the CMS. (same)
- Predictive search shows 10 results max; Search & Discovery 250 per page; search inside a collection compares the first 2,000 products. (v2:docs/build/filters)
- Vendor and Tag filters need those filters on in Search & Discovery; their values are never translated. (same)
- iPhone in-app browsers get a compat build: no 3D, no `dynamic-swiper`. (same)
- Customer conditions only hide with CSS. Never hide private data with them. (v2:docs/build/account)

## 9. Corrections to our playbook

| `general-setup.md` says | Docs now say |
|---|---|
| Two script and stylesheet tags from the dashboard | One 2.0 loader line (section 1) |
| CMS slugs `product`, `collection`, `vendor`; URLs `/product/...` | 2.0 expects `products`, `collections`, `vendors`, matching Shopify. Singular needs `productsBase` etc. (v2:docs/start/cms) |
| Smootify adds no structured data | 2.0 adds Product JSON-LD on product pages and skips it if Product markup already exists. Drop our script or set `structuredData: false` (v2:docs/start/seo) |
| Auto-tracks only add to cart and product view, with Shopify's banner | 2.0 loads pixels itself after `smootify-consent`; Shopify's banner is no longer added (v2:docs/features/analytics) |
| Rich text metafields unsupported | 2.0 renders Rich text and syncs it to Rich text fields (v2:docs/build/metafields) |
| Markup from `docs.smootify.io/components-v2/data/<slug>.json` | That is 1.x. 2.0 markup comes from the Webflow app and the MCP |
| Card variant picker untested, variants get "Choose options" | `variant-swatches` + direct add button is documented |
| Wishlist "ask first" | Free on every plan, documented |
| Cards shimmer while loading | 2.0 has no automatic placeholders: add `skeleton` |
| Stale metafield cache | Products sit in the browser cache 10 minutes while `preload` is on (v2:docs/developers/options) |
| Sold-out swatch image via `variant="image"` | Inside swatches 2.0 uses `option-variant="image"` (v2:docs/start/changes) |

## 10. Not read

- 2.0 docs read in full: start (quick start, install, Shopify store, Webflow project, CMS, publish, domains, hand-off, SEO, changes, studio), product cards, filters, vendor page, account, wishlist, reviews, subscriptions, markets, fixed bundles, analytics, theme apps, plus the FAQ, pricing, MCP, Webflow app, agencies and 2.0 release notes pages. **Not read:** the 2.0 Reference section (about 280 pages), the Astro docs, and the other 2.0 build and feature pages (cart, product page, gallery, swatches, orders, booking, quotes, options in detail).
- 1.x: all 115 pages in `llms-full.txt` read; long attribute pages skimmed by heading and attribute. `/components` read as a list only. `docs.smootify.io/changelog` returned 404.
