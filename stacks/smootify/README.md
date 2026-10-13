# Smootify playbook (Shopify storefronts in Webflow)

**Status:** occasional. Since 12 Oct 2026, from one full test build.

## What it is used for
Turning a Shopify store into a Webflow storefront: Shopify keeps products, stock, discounts
and checkout, Webflow owns the pages, Smootify's script joins them. The step-by-step setup,
the baseline scope and the per-project extras are in `general-setup.md` beside this file.
Read that first on any new conversion.

## Conventions
- **Baseline first.** Every project gets the baseline in `general-setup.md` section 2
  (product page with variants, collection listing, cart, quick add, buy now, checkout
  handoff). Everything under "Discuss per project" is scoped with the user at kickoff, not
  assumed.
- **Webflow rules still apply.** Classes follow the site's own naming (`stacks/webflow/`),
  never Smootify's `sm-*` names. Take the structure from Smootify's component, rename the
  classes, bind tokens.
- **Get the markup from the source, not from memory.** Each docs "Copy Element" button loads
  `docs.smootify.io/components-v2/data/<slug>.json`; read the tree from there. For behaviour
  the docs skip, read the script chunks under `cdn.smootify.io/assets/latest/js/`.
- **Native Webflow form inside** add to cart, the cart, every filter and sort, or Smootify
  removes the element at runtime.
- **Real buttons and inputs** are DOM elements (`dom_tag: button` / `input`). Custom tags
  (`smootify-product`, `cart-item`, `filter-price`) are DOM elements too.
- **State CSS Smootify leaves to us** (search states, anything keyed on a runtime class or a
  custom tag) goes in a `section-script-css` embed beside the element, with a banner saying
  why the style panel cannot do it.
- **Tokens and keys are pasted by a person.** Claude builds the markup and leaves the
  Storefront token, Customer Account client id and tracking IDs to the user.
- **Never put a live store's tracking IDs on a test site.**
- **Verify on the published staging site in a visible tab.** The canvas and Preview never run
  Smootify.

## Accounts and tools
- Shopify admin and the Smootify dashboard through Claude in Chrome, in the org's Chrome
  profile (`general/how-i-work.md` has the table). Shopify admin steps need the user's go-ahead
  each session.
- Webflow through the org's Webflow MCP.
- Shopify apps: Smootify, Headless (the public token), Search & Discovery (filters).
- Smootify's free plan is enough to build and test. The CMS can be filled by the free Desktop
  app, by Server Sync on the paid Server plan, or through the Webflow API.

## Gotchas that became rules
| Date | What happened | Rule |
|---|---|---|
| 12 Oct 2026 | Filters and sort vanished on the published page | They need a native Webflow form inside. Same for add to cart and the cart |
| 12 Oct 2026 | "N products" and the cart count lost their label | `[filter="count"]` and `[cart="count"]` replace their whole text: put the attribute on an inner span |
| 12 Oct 2026 | Cards stuck loading, cart stepper stuck at 1, only in tests | `requestAnimationFrame` never fires in a hidden tab. Before testing run `window.requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16)` |
| 12 Oct 2026 | The WHTML builder dropped custom tags and every custom attribute | Build Smootify elements with the element builder (`type: DOM`), set attributes there or with `set_attributes` |
| 14 Oct 2026 | The price filter stayed hidden | `hide-empty` on `smootify-search-discovery` drops zero-count values, and Shopify's price filter always reports zero. Leave `hide-empty` off with a price filter |
| 14 Oct 2026 | `filter-price` needs a fixed shape | Its form must hold two `input[type=number]`, two `input[type=range]` and `[filter-price="progress"]`, or it removes itself. Hide the range pair with a class if the design uses number fields |
| 14 Oct 2026 | Type-ahead search showed all states together | Smootify only toggles `has-query`, `is-empty`, `has-products` on `smootify-search` and leaves a `[data-fake="true"]` row. Write the display rules in an embed |
| 14 Oct 2026 | A discount code was refused with no message | Shopify answered `DISCOUNT_CODE_NOT_HONOURED` because an automatic discount was active and the code did not combine. Smootify shows nothing. Set combination rules in Shopify |
| 14 Oct 2026 | A new metafield block stayed hidden on the first view | Smootify caches product data in the browser; `if-metafield` used the stale copy. Reload before judging |
| 14 Oct 2026 | Rich text metafield wanted for FAQs | Not on Smootify's supported list. Use multi-line text (`white-space: pre-line`) or a list of metaobjects |
| 14 Oct 2026 | Typing in Shopify admin opened a barcode dialog | The field had no caret. Click the field, confirm focus, then type. Metafield values save on the second Save click |
| 14 Oct 2026 | A product video uploaded twice | Setting a file input by script and firing both `input` and `change` uploads twice. Fire `change` only |
| 14 Oct 2026 | Product JSON-LD needed live price and stock | The product element exposes the Storefront data as `element.product` (`variants.nodes`, `media.nodes`, `descriptionHtml`). Build the schema from it in Global Scripts |

## Pointers
- `general-setup.md` (this folder): setup steps, baseline markup, per-project extras, client
  limits, test checklist.
- `stacks/webflow/README.md` for every Webflow build rule; `stacks/shopify/README.md`.
- Docs index `https://docs.smootify.io/llms.txt`; changelog `https://docs.smootify.io/changelog`.
