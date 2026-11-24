# Storepoint playbook

**Status:** occasional. Since 25th Nov 2026 (first full test: a Singapore store locator on a Webflow test site).

Storepoint (storepoint.co) is a hosted store locator. You add locations in its dashboard, it gives you
one embed snippet, and the widget draws a searchable map and list on any site. The map itself comes
from Mapbox or Google Maps on **our own key**, not Storepoint's.

The client-ready version of this ("here is what you need, here is what it costs") is
`client-setup-guide.md` beside this file. The store list template is `store-list-template.csv`.

## What it is used for
Store or stockist locators on brand sites ("where to buy"). Fits Webflow, WordPress, Shopify and plain HTML.

## What a project needs (checklist)
1. **Storepoint account** on the client's or the agency's email. 7-day free trial, card required.
2. **A plan** (prices checked 25th Nov 2026, USD per month):

   | Plan | Price | Locations | Worth knowing |
   |---|---|---|---|
   | Starter | 25 | up to 200 | Spreadsheet bulk import. No Google Sheets sync, no analytics. 2 team members |
   | Pro | 49 | up to 2,000 | Google Sheets sync daily, Webflow CMS sync, analytics, featured locations, more languages. 5 team members |
   | Business | 99 | unlimited | Sheets sync every 5 min, hides the Storepoint logo, service areas, own-system sync. 20 team members |

   Every plan has filters, keyword search, open hours, images, directions, custom CSS and the APIs.
   The "Store Locator Software" credit link only goes away on Business.
3. **Mapbox account and public token** (or a Google Maps API key). Without it the map is blank.
   Mapbox free tier, checked 25th Nov 2026: 50,000 map loads a month free, then USD 5 per 1,000
   (cheaper at volume); 100,000 search (geocoding) requests a month free, then USD 0.75 per 1,000.
   With no card on the Mapbox account it is capped at the free tier and is never charged.
4. **The store list**: name, street address, suburb or city, state or region, postcode, country,
   plus optional phone, website and store type. Use `store-list-template.csv`.
5. **Where it goes**: the page and the domains (staging and live) the locator will run on.

## Setup steps
1. Storepoint: create the account and the locator. Note the locator (map) ID from Embed & Preview > Embed Locator.
2. Locations: bulk import the CSV, or Manage Locations > Add a Location one by one.
   Check each pin landed in the right place (the edit page shows coordinates).
3. Mapbox: sign up at account.mapbox.com, copy a public token from Access tokens
   (account.mapbox.com/access-tokens). Paste it in Storepoint: Embed & Preview > Map Provider Settings >
   Use Mapbox > Save Settings. The client or the user does the pasting; Claude never enters keys.
4. Settings: Widget Settings > Search & Map Functionality.
   - Restrict search suggestions to the countries the stores are in.
   - Distance unit: Kilometers (outside the US).
   - Default radius, radius options, "Use my current location", filters.
5. Embed: put the snippet in a Code Embed (Webflow), a Custom HTML block (WordPress) or the page HTML:

   ```html
   <div id="storepoint-container" data-map-id="MAP_ID"></div><script>(function(){var a=document.createElement("script");a.type="text/javascript";a.async=!0;a.src="https://cdn.storepoint.co/api/v1/js/MAP_ID.js";var b=document.getElementsByTagName("script")[0];b.parentNode.insertBefore(a,b);})();</script>
   ```
   Give the embed its own class (Client-First: `store-locator_embed`) so it can be sized.
6. Test on staging: search a suburb, a postcode, the country name on its own, and a place name
   that also exists in another country. Check desktop, tablet (768) and mobile (390).
7. Before launch: swap to a Mapbox token restricted to the live and staging domains (needs a card
   on Mapbox, see gotchas), and pick the plan.

## Updating the store list (checked in Storepoint's docs, 25th Nov 2026)
Every location belongs to the "source" it came from (Imports & Syncs). Three ways to keep it current:

| Way | Plan | How it updates |
|---|---|---|
| Dashboard by hand | All | Add, edit or delete one location at a time. Fine for a handful of changes |
| Spreadsheet re-upload | All (Starter's only bulk option) | Upload the new CSV to the same source. Only that source's locations are replaced; others stay |
| Google Sheets sync | Pro daily, Business every 5 min | Storepoint reads the sheet on schedule. New row adds a store, edited cell updates it, deleted row removes it |

Sheets sync rules:
- Headings in row 1, one store per row, one tab (the first tab unless the link points to another).
- Name and full address are required. Address parts can sit in separate columns. Coordinates optional.
- Stores are matched by name and address, so renaming or moving a store counts as remove plus add.
  Duplicate rows are merged.
- Share the sheet as "Anyone with the link: Viewer", or ask Storepoint for their sync account email to keep
  it private. Keep nothing confidential in a link-shared sheet.
- Filterable data (store type, products) maps to Tags; extra text or buttons need Custom Fields set up first.
- Export a backup before connecting an existing list, and use one source per list to avoid duplicates.
- Docs: storepoint.co/docs/features/google-sheets-sync

## Accounts and tools
- Dashboard: app.storepoint.co/dashboard. Sign-in is the account owner's job (password or Google).
- Public read API, handy for checks without the browser:
  `https://api.storepoint.co/v1/MAP_ID/locations` (all) and
  `...?lat=LAT&long=LONG&radius=25` (nearest first; `distance` in the response is in miles).
- Widget script: `https://cdn.storepoint.co/api/v1/js/MAP_ID.js`. Storepoint rebuilds it a minute
  after any settings or location change.

## Gotchas that became rules
| Date | What happened | Rule |
|---|---|---|
| 25th Nov 2026 | Map blank on localhost and staging; Mapbox answered 401 and the dashboard showed "Mapbox Token Error", while the dashboard checklist still said "Storepoint managed maps, set up" | A Mapbox (or Google) key is required. Blank map plus "1 map error needs fixing" means no or bad key |
| 25th Nov 2026 | After the key was saved the page stayed blank | The widget script is cached by browsers for up to 30 minutes. Hard refresh (Cmd+Shift+R) before deciding it failed |
| 25th Nov 2026 | Km was saved but the widget showed "25 mi" | The widget only applies its settings once the map loads. Fix the map first, then check units |
| 25th Nov 2026 | Mapbox would not add URL restrictions on the free token | URL-restricted tokens need a payment method on Mapbox. Default token is fine for a test; restrict before launch |
| 24th Nov 2026 | Searching a bare place name ("Bondi") landed abroad on the dashboard preview | Set the country restriction, and test on the real embed with a key, not the preview |
| 24th Nov 2026 | Cancelling the trial | Cancel turns the locator off at once, not at the end of the trial. Decide keep or cancel before the trial date |
| 25th Nov 2026 | The add-location address suggestion was a different street | Keep the typed address unless the suggestion is the same place; check the pin |

## Pointers
- Client-ready requirements and pricing: `client-setup-guide.md`.
- Store list template: `store-list-template.csv`.
- Storepoint pricing: storepoint.co/pricing. Mapbox pricing: mapbox.com/pricing.
- Mapbox token guide: docs.mapbox.com/help/getting-started/access-tokens/
