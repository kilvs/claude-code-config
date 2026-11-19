# Ecommerce project process: Webflow + Shopify through Smootify

The order of work for any project where a Webflow site sells through Shopify. Written 19 Nov 2026
from two test builds run side by side (a drinks brand and a multi-brand apparel store). Each step
says who does it: **The user** (account, money, identity and sign-in steps Claude never does),
**Claude** (main session), or an **agent** (`senior-web` builds, `qa` checks, read-only research
agents audit).

Read with: `general-setup.md` (markup, gotchas, launch standard in section 11), `docs-digest.md`
(plans, hand-off, 2.0 vs 1.x), `stacks/webflow/README.md` (build rules).

## 1. Discovery (before any build)

Answer these first. Ask the client through whoever owns the client relationship, after checking the
previous owner's handover notes.

| Question | Why it matters |
|---|---|
| Does the client already have a Shopify store? URL, plan, product count, installed apps | Existing store: we connect to it as collaborators. No store: we build a client-transfer store and hand it over |
| Which domain, and who controls its DNS? | Root and `www` go to Webflow, checkout to a `shop.` sub-domain. A domain bought through Shopify needs its DNS moved first |
| Is there a live site being replaced? | Every old URL needs a permanent redirect at launch |
| Reviews, subscriptions, multi-currency, wholesale, bundles, gift cards? | Each has a plan, app or extra-work catch (`general-setup.md` section 2, `docs-digest.md` section 7) |
| Rough product and variant count, how often products change | Decides Smootify Lite (manual sync) or Server (auto sync), and the Webflow CMS plan size |

Public checks Claude can do without asking anyone: curl the domain for `cdn.shopify.com` /
`myshopify.com` / `x-shopid` (a Shopify store) or `wp-content` (WordPress), `/products.json` for
the public product count, `dig NS` for the DNS host.

## 2. Design audit: does the connector cover the Hi-Fi?

An agent reads the Figma Hi-Fi (product, shop/collection, navbar, cart, account, search pages) and
returns a table per feature: Smootify yes/partial/no, StoreSynk yes/partial/no, extra app or code.
Default verdict: **Smootify**. A Shopify developer (Liquid theme) only wins when the catalogue
exceeds the Webflow CMS item cap or the store depends on apps that only work in a Liquid theme.

Design gaps to check every time (found missing in real Hi-Fis):
- **Cart entry point** in the navbar (icon or button). A shop with no cart icon is a design question.
- **Search state.** If there is a search icon, is the results dropdown or page designed? Pick one:
  predictive dropdown in the navbar (default), or a `/search` page reusing the shop grid.
- **Reviews.** Stars or a reviews panel need an app (Judge.me Awesome, Loox Convert or higher). The
  panel will not match a custom design exactly.
- **Filters.** Brand, size, colour filters need Shopify's free Search & Discovery app.
- **Empty, sold-out, loading and error states** for cards, variants and the cart.
- **Brands sold elsewhere.** If the client already sells a brand on another Shopify store, ask
  whether those products move.

Raise gaps with the designer before the build starts.

## 3. Test build (proves the design before the real build)

1. **Shopify store.** Partner Dev Dashboard > Create store > **Client transfer** (it can
   become the client's store later). Country = where the client sells. Store handles are permanent.
   First third-party app install asks for **partner identity verification** (Stripe ID check, once
   per person). Open each new store admin once so the account picker is done.
2. **Shopify apps.** Headless (create a storefront, turn on every Storefront
   API permission), Smootify, and Search & Discovery if filters are in the design. App install
   screens grant access: needs the user's word in the main chat; agents do not take relayed approval.
3. **Webflow test site (Claude).** Duplicate the org's Client-First starter, rename it
   `Smootify <Project> Test`, set a matching webflow.io sub-domain. Never touch the client's real
   build site.
4. **Smootify project.** Dashboard > Choose the site > Connect Webflow > Authorize: pick
   **one site only**. The OAuth window is a pop-up Claude cannot reach. The Smootify account should
   be the agency's shared work login, with each project shared to the developers.
5. **Build (senior-web agent).** Brief: functionality and section order must match Figma, looks do
   not. Smootify **2.0** with plural CMS slugs `products`, `collections`, `vendors`. Test products in
   the same data shape as the design (options, a sold-out value, two vendors if brands matter), all
   on the Headless channel. Build product template, collection and vendor templates, filters,
   navbar cart and search. Publish to webflow.io only.
6. **QA (qa agent, read-only).** Every page at 1440, 768, 390: data, variants, sold-out, quantity,
   add to cart (check lines with `Smootify.getCart()`), quick add, sliders, accordions, filters, no
   overflow, no console errors. Fix, then QA again.
7. **Checkout check.** Dev stores keep Private mode on (it cannot be turned off before hand-off).
   The user enters the store password once in the browser (Online Store > Preferences > Store
   access), then buy now must reach Shopify checkout. Never pay.
8. **Redirect Theme check (optional on a dev store).** See `general-setup.md` section 11.

Log everything in the project's build log, newest first. New gotchas go in `general-setup.md`.

## 4. Real build

- Copy the proven Smootify parts from the test site into the real Webflow site. If an outside
  developer builds the real site, brief them early on Smootify markup and the plural slugs so they
  don't build static product pages.
- Load real products into the client-transfer store (or the client's own store as a collaborator).
- Static pages (about, contact, stockists, blog, policies) are plain Webflow pages.

## 5. Launch

Follow `general-setup.md` section 11. In short: client on a paid Shopify plan (Basic or higher), a
Smootify paid plan (Lite or Server) and a Webflow site plan with CMS; `shop.` sub-domain as Shopify's
primary domain; Redirect Theme published with Hostname, bases and custom redirects (`/pages/>/`,
plus `/search>/collections/<all>` when the site has no search page); live domain in Smootify
settings and in the Customer Account API origins; publish webflow.io and the custom domain together;
old-site redirects; one real order, then refund.

## 6. Hand-off (order matters)

1. Shopify store transfer to the client's email. Irreversible; the email cannot be changed; the
   client must accept and pick a plan within 7 days or a dev store is deleted. Shopify Balance,
   Credit or Capital must be off first.
2. Transfer the original Webflow site (never a copy).
3. Share (or transfer) the Smootify project; the client picks Lite or Server.
4. Client reconnects the same Webflow site in Smootify; restart Server sync if used.

Commission: a client-transfer store that becomes a paying store earns the partner referral
commission, so building the store on the agency's partner account has a revenue upside.
