# Webflow + Shopify through Smootify: general setup

How to turn a Shopify store into a Webflow storefront with Smootify. Written from one full
test build (October 2026). It covers the baseline every project gets. Anything past the
baseline is listed under "Discuss per project" so the complexity talk happens at kickoff.

Each item is marked **Proven** (built and tested in a browser) or **From docs** (read in
Smootify's docs or code, not yet built by us).

## 1. How the pieces fit

| Piece | Job |
|---|---|
| Shopify | Owns products, prices, stock, discounts, customers and the checkout |
| Webflow | Owns every page the shopper sees before checkout |
| Smootify | A script on the Webflow site. It reads Shopify live and fills the page |
| Shopify Headless channel | Gives the public token Smootify uses to read the store |

Three facts shape every decision:

- Price, images, variants, stock and metafields are never stored in Webflow. Smootify fetches
  them live on each page view.
- The Webflow CMS only holds one item per product and collection, so Webflow can create the
  pages. Each item carries its Shopify ID.
- Checkout always happens on Shopify. Webflow hands the cart over.

Smootify output only shows on a published site. The Designer canvas and Preview show the
placeholder template.

## 2. What the general setup includes

**Baseline (every project):**

| Piece | Status |
|---|---|
| Product page: title, description, price, gallery | Proven |
| Variants: swatches or buttons, image swap, sold-out options disabled | Proven |
| Simple products (no variants) | From docs. Same markup without the variant block |
| Quantity and add to cart | Proven |
| Buy now (quick buy, straight to checkout) | Proven |
| Collection listing: grid, product cards, load more, empty state, count | Proven |
| Cart as a dropdown that opens on add: lines, quantity, remove, total | Proven |
| Cart as a slide-in drawer | From docs. Same cart, different wrapper |
| Quick add to cart on product cards | From docs. Simple products add in one click; products with variants show "Choose options" |
| Checkout handoff to Shopify | Proven |
| Automatic discounts shown in the cart | Proven |

**Discuss per project** (each one adds work or has a catch):

| Piece | Size | Catch |
|---|---|---|
| Filters (size, colour, availability, price) and sort | Small | Needs Shopify's free Search & Discovery app. Price filter breaks with `hide-empty` (see gotchas) |
| Search page | Small | None |
| Type-ahead search in the navbar | Medium | Needs a small state stylesheet |
| Discount code field in the cart | Small | Invalid or non-combining codes fail silently |
| Free shipping progress bar | Small | None |
| Shop Pay button | Small | The only express wallet available outside checkout |
| Cart upsells or related products | Small | Shopify decides the suggestions |
| Product video in the gallery | Small | None |
| Metafield content (FAQs, specs, materials) | Small per field | Rich text metafields are not on Smootify's supported list. Use multi-line text or metaobjects |
| Structured data (JSON-LD) | Medium | Not automatic. Needs a script or Designer bindings |
| Customer account link | Small | Links to Shopify's own account pages |
| Customer account pages inside Webflow | Large | Needs the Customer Account API client id |
| Tracking (GA4, Meta) | Medium | Scripts added by hand. Smootify only auto-tracks add to cart and product view, and only with Shopify's cookie consent on |
| Reviews | Medium | Depends on the app. Judge.me only works headless on its paid Awesome plan |
| Wishlist, subscriptions, multi-currency, gift cards, bundles | Ask first | Smootify supports them. We have not built them |
| Any Shopify app that draws on the storefront | Ask first | Many do not work headless. Check Smootify's integrations list before promising |

## 3. Before starting

- Shopify admin access to the store, or a development store for testing.
- A Webflow site on a plan with CMS and custom code.
- A Smootify account. The free plan is enough to build and test.
- A browser session for the Shopify and Smootify dashboards. Tokens are pasted by a person,
  not by Claude.

## 4. Setup steps

1. **Prepare the store.** Products, variants, collections and discounts live in Shopify. For a
   test store, import the products by CSV. Leave a few variants at zero stock to test the
   sold-out state.
2. **Install the Shopify apps.** Smootify, Headless, and Search & Discovery (only if the site
   needs filters). In Search & Discovery, add one filter per thing shoppers filter by.
3. **Open the Headless channel.** Create a storefront, turn on the Storefront API permissions,
   and publish the products and collections to the Headless channel. Copy the public token.
4. **Create the Smootify project.** Connect it to the Webflow site (grant access to that one
   site). In Site settings, paste the store URL, the public token and the domain.
5. **Add Smootify to Webflow.** Paste the stylesheet and script tags from the Smootify
   dashboard into Site settings > Custom code > Head.
6. **Create the CMS collections.** Vendors (slug `vendor`), Collections (slug `collection`),
   Products (slug `product`), with the fields in Smootify's "Create CMS Collections" doc.
   Smootify's starter project ships them ready. On our own kit, create them through the API.
7. **Fill the CMS.** One item per vendor, collection and product, each with its Shopify ID
   (`gid://shopify/Product/<id>`). Three ways: the free Smootify Desktop app, Server Sync on
   Smootify's paid Server plan, or the Webflow API. A sync is only needed again when a product
   or collection is added.
8. **Build the pages.** Product template, collection template, and the cart inside the Navbar
   component. Markup is in section 5.
9. **Publish to the `webflow.io` staging domain and test.** Use the checklist in section 7.

## 5. Baseline markup

Smootify works through custom element tags and custom attributes. Classes are ours, so the
site keeps its own naming. Three rules apply everywhere:

- Add to cart, the cart, filters and sort must each wrap a **native Webflow form**. Smootify
  removes them at runtime if the form is missing.
- Buttons are real `<button>` elements.
- A template element (a cart line, a product card, a discount row) is written once. Smootify
  repeats it.

**Product page**

```
smootify-product[data-id = CMS Shopify ID]
  [product="title"]            [product="description"]
  smootify-price > span[data-prop="price"] + span[data-prop="compareAtPrice"]
  img[variant="image"]                          main image, follows the chosen variant
  a (Lightbox link)[product="media"] > img      thumbnails, images and video
  smootify-add-to-cart > Webflow form
    variant-swatches[data-option="1"]           one per option set, up to 3
      label + div > three button templates: base, is-active, is-disabled,
                    each holding div[option="title"]
    quantity-input > button[data-action="minus"] + input + button[data-action="plus"]
    button[type="submit"]                       add to cart
    button[type="submit"][name="buy-now"]       buy now, straight to checkout
      each button: div[data-state="default"] + div[data-state="loading"].is-hidden
  smootify-shop-pay                             empty; Smootify fills it
```

A simple product uses the same markup without the `variant-swatches` block.

**Collection listing**

```
smootify-search-discovery[limit="24"][sync-query-params="true"]
  span[filter="count"]
  filter-swatches[label = filter name in Shopify] > Webflow form > button templates
  filter-price > Webflow form > 2 x input[type=number] (filter-price="from" | "to")
                              + 2 x input[type=range] + div[filter-price="progress"]
  sort-dropdown > Webflow form
  button[filter="active"] > div[filter="active-label"]      active filter tags
  smootify-product[data-id="filter"]                        the product card template
    a[product="url"] > img[variant="image"]
    [product="title"]      smootify-price > span[data-prop="price"]
  button[data-action="load"]                                or next / prev
  [filter="empty-state"]
```

Without filters, the same element with only the card, the load button and the empty state is
the simple listing. On a collection template, the collection comes from the CMS item.

**Quick add on a card** (From docs)

```
inside the smootify-product card:
  smootify-add-to-cart[condition="is-not-variable"] > Webflow form > button[type="submit"]
  a[product="url"][condition="is-variable"]     "Choose options"
```

Products without variants get a one-click add. Products with variants get a link to the
product page. A variant picker inside the card is per-project work and untested.

**Cart**

```
smootify-cart[data-open="on-add"]
  Webflow Dropdown                              the dropdown version (Proven)
    toggle: span[cart="count"]
    list:   Webflow form
      cart-item                                 template, repeated per line
        img[cart-item="image"]   [cart-item="title"]   [cart-item="total"]
        [cart-item="options"] > [option="name"] + [option="value"]
        [cart-item="discount"] > [discount="title"] + [discount="amount"]
        quantity-input           button[data-action="remove"]
      [cart="total"]
      button[type="submit"]                     checkout
      the form's success state                  the empty cart message
```

For a **drawer** (From docs), swap the Webflow Dropdown for
`button[data-action="open-cart"]` + `dialog` holding the same form, with
`button[data-action="close-cart"]` inside. Smootify picks the mode from what it finds:
a Webflow Dropdown, a `dialog`, or a `details` element.

## 6. Limits to tell the client early

- Checkout is Shopify's. Its design is set in Shopify, not Webflow.
- Shop Pay is the only express button outside checkout. Apple Pay and Google Pay appear inside
  checkout only.
- Apps that inject widgets into a Shopify theme may not work. Check each one.
- At launch, the main domain points to Webflow only. Shopify's checkout needs its own
  subdomain. (From docs. We have not launched a Smootify site yet.)
- URLs change: Smootify's defaults are `/product/...` and `/collection/...`, not Shopify's
  `/products/...` and `/collections/...`. Plan redirects.
- Smootify adds no structured data and no tracking by itself.

## 7. Test checklist

Run on the published staging site, in a visible browser tab, at desktop, tablet and mobile.

- Product page loads title, price, images. Choosing a colour swaps the image.
- Sold-out variants are disabled.
- Add to cart opens the cart with the right line, options and price.
- Quantity up and down changes the total. Remove empties the cart and shows the empty state.
- Automatic discounts and discount codes show with their names and amounts.
- Buy now and Checkout both land on the Shopify checkout with the right items.
- Collection page shows every product. Each filter narrows the grid. Sort works.
- Load more and the empty state both work.
- Nothing overflows sideways at 991, 768 and 390.

## 8. Gotchas

| What happened | Rule |
|---|---|
| The price filter never appeared | `hide-empty` on the listing hides it for good: Shopify reports the price filter with a count of zero. Leave `hide-empty` off when using a price filter |
| Cards stayed in a loading state during tests | Smootify writes inside `requestAnimationFrame`, which never fires in a hidden browser tab. Test in a visible tab |
| A new metafield block stayed hidden on first view | Smootify caches product data in the browser. Reload before judging |
| "N products" lost its word | `[filter="count"]` and `[cart="count"]` have their whole text replaced. Put the attribute on an inner span |
| A discount code did nothing | Shopify refused to combine it with an automatic discount, and Smootify shows no message. Decide combination rules in Shopify |
| The cart stepper misbehaved | The cart's quantity input must carry no `value`, `min` or `name` of its own |
| Type-ahead search showed every state at once | Smootify only adds `has-query`, `is-empty` and `has-products` to the search element. The show and hide rules are ours to write |

## 9. Where to look things up

- Docs index: `https://docs.smootify.io/llms.txt`
- Every "Copy Element" button in the docs loads
  `https://docs.smootify.io/components-v2/data/<slug>.json`. That file holds the exact element
  tree, with custom tags in `data.tag` and attributes in `data.attributes`.
- Script source, for behaviour the docs do not cover:
  `https://cdn.smootify.io/assets/latest/js/index.js` and the chunks it imports.
