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

## 10. Smootify 2.0 product page (Proven, 19 Nov 2026)

Built on two test sites with the 2.0 loader (`assets/v2/loader.js`, served 2.0.0-beta.14), CMS
slugs `products` / `collections` / `vendors`, and tested on `.webflow.io`. This replaces the
product page markup in section 5 for 2.0 sites.

```
smootify-product[data-id = CMS Shopify ID]
  a[product="first-collection"][exclude="Home page"]   breadcrumb collection
  div[product="gallery"][include-media]
    Webflow Slider[gallery="slider"]   keep ONE slide with an Image; Smootify copies it per media
    a[gallery="thumbnails"] > img      one template; current one gets is-active
  [product="title"]   smootify-price > [data-prop="price"] + [data-prop="compareAtPrice"]
  [product="description"]  (on a text-rich-text div)
  div[has-option="0"] > [variant="option1-name"] + variant-selector[data-option="1"] > select
                                                          (a dropdown picker; works outside the form)
  smootify-add-to-cart > Webflow form
    div[has-option="1|2"] > [variant="option2-name"] + variant-swatches[data-option="2|3"]
      > ONE button template > span[option="title"]       is-active / is-disabled classes
    quantity-input > button[data-action=minus] + input[name=quantity] + button[data-action=plus]
    button[type=submit] > [data-state=default] + [data-state=loading]
    button[type=submit][name=buy-now]
  div[if-metafield="rating_count"][namespace="reviews"]  stars: [metafield="rating"] sets
    --metafield-rating; fill width var(--metafield-rating) in the section CSS embed
Other sections: smootify-product[data-id = CMS Shopify ID] > button[data-is="direct-add-to-cart"]
Recommendations: smootify-product[data-id="related"][data-parent-id = CMS Shopify ID][limit]
  card template, repeated by Smootify; variant-swatches inside the card picks the size for quick add.
```

### Gotchas found
| What happened | Rule |
|---|---|
| A sold-out value still gets clicked | 2.0 marks it `is-disabled` but keeps it clickable; both submit buttons get `disabled` + `is-disabled`. Style the combo classes |
| Loading labels both vanished | Smootify toggles `[data-state]` with inline styles. Add no CSS for them |
| The breadcrumb said "Home page" | Dev stores have Shopify's default "Home page" collection. `exclude="Home page"` on `product="first-collection"` |
| Buy now opened `/password` | A dev store's storefront password blocks checkout. On a dev or client-transfer store Private mode is locked on, so it can't be removed: enter the password from Online Store > Preferences > Store access once in the browser. It goes away when the store gets a paid plan (after transfer) |
| "Project ... is not connected" in the console | The Smootify dashboard connection is not made yet. The loader still loads; nothing renders |
| `reviews.rating` definition refused | Shopify reserves the `reviews` namespace for its standard definitions, and the admin's suggestion list may not offer them. A reviews app fills them; plan for it |
| One template, two designs (e.g. drinks vs merch) | Visibility can only bind to component props over MCP. Bind a `data-template` attribute to a CMS text field and hide sections with attribute selectors in the section CSS embed |
| `related` on a tiny catalogue | Worked with 4 products (3 returned). No fallback needed for tests |
| Shopify CSV import by script | The file input sits in a shadow root (`s-internal-drop-zone`). Set it with a DataTransfer and fire `change` only. "Publish to all sales channels" includes the Headless channel |

### Webflow MCP gotchas (same build)
| What happened | Rule |
|---|---|
| `row-gap` refused `variable_as_value` ("does not support a variable of type length") | Pass `property_value: "var(--css-name)"`; it binds the token. `column-gap` takes the id fine |
| Removing one SliderArrow deleted the whole Slider | Leave arrows and nav; remove only the extra slide |
| A combo named `w--current` became `._w--current` | Runtime states like the tab current state go in the section CSS embed |
| CMS Number fields came out integer | The API cannot set Decimal 0.00. Set it in the Designer, or let Smootify Studio create the collections |
| Element builder silently skips a class that does not exist yet | Create every class first; check `partial_success` child results |

### More gotchas (QA round, 19 Nov 2026)
| What happened | Rule |
|---|---|
| Collection and vendor links 404 | Build the Collections and Vendors template pages too, even for a product-page test. `smootify-search-discovery[data-collection]` needs no app; `data-vendor` and vendor or brand filters need Shopify's Search & Discovery app |
| Vendor page without Search & Discovery | `smootify-product[data-id="custom-query"]` with `data-query` bound to a CMS text field holding `vendor:"Name"` lists that vendor's products |
| Native Webflow Slider stuck at two slides over MCP | The builder ignores slide children and WHTML refuses slides in a mask. Product sliders still work (Smootify adds a slide per product); a static image slider needs the Designer or a CSS scroll-snap row |
| A product list slider showed no arrows | When every card fits, Smootify adds `is-disabled` to both arrows. Style the combo |
| `details` did not start open | An empty `open` attribute set over MCP did not survive publish. Use `open="open"` |
| A Paragraph built with child spans showed Lorem ipsum | The builder keeps the default text node. Use a Div block for inline wrappers, or remove the String node |
| A calc() value bound the wrong token | `calc(-1 * var(--x))` was stored as the plain variable. Avoid calc with tokens in the style API |
| CMS Number fields to Decimal | Designer > CMS > collection Settings > field > Format Decimal, Precision 1.00, Save Field, Save Collection. API then reports `format: decimal, precision: 2` |
| Filters before Search & Discovery is installed | Shopify still returns its default Availability (and Price) filters, so those render; vendor, option and tag filters stay hidden until the app defines them. The filter `label` must match the app's label exactly |
| "1 products" | `filter="count"` writes only the number, with no plural rule. Put the label before it ("Results: 1") |
| Predictive search in a navbar dropdown (2.0, Proven) | `details` > `summary` (icon) > `smootify-search[limit]` holding a Form with a text field named `query`, `button[data-action="close"]`, `search-no-query`, `search-with-query` > one `search-result` (`search="url|image|title|vendor|price"`), `search-empty`. The close button closes the parent `details`. A brand name matches its products. Smootify shows and hides the regions itself |
| Cart drawer (2.0, Proven) | `smootify-cart[data-open="on-add"]` > `button[data-action="open-cart"]` + `dialog` > panel > `button[data-action="close-cart"]` and a Form Block whose form holds one `cart-item` template, `[cart="subtotal"]` and the Form Button (checkout). Success message = empty cart. `quantity-input` with buttons `data-action="minus|plus"` and an input named `quantity` |
| Two navbar `details` panels open at once | Give both the same `name` attribute (exclusive accordion). Opening one closes the other |
| Webflow MCP refused `placeholder` | It is a reserved attribute name on form inputs. Set placeholder text in the Designer |
| Chrome window would not resize for breakpoint checks | Load the page in a same-origin iframe at 768 and 390 px and measure inside it |
| Mobile menu with no script (2.0, Proven) | Make the links `nav` a popover: `popover="auto"`, an ID, `data-overflow-body`, opened by `button[popovertarget=<id>]`. Smootify hides closed popovers with `display: var(--smootify-closed-display, none) !important`, so set `--smootify-closed-display: flex` on the class at desktop and `none` below 992px. At desktop also reset the browser popover box (position static, inset auto, margin 0, width and height auto, transparent background). Escape, click outside and scroll lock come free |
| Escape did not close a `details` dropdown | `details` has no Escape. Use a popover (`popover="auto"` panel plus a `popovertarget` button): Escape and click outside close it, and focus goes back to the button |
| Webflow MCP style API refused a CSS custom property | `--name` properties are rejected. Put them in the site's global embed, or set them in the Designer style panel |
| A popover panel landed in the middle of the window | Popovers sit in the top layer, so `absolute` inside the navbar no longer works. Give the panel `position: fixed` with its own top, right, margin 0 and bottom auto |
| Focus the search field when its popover opens | The Webflow API reserves `autofocus`. Add a capture-phase `toggle` listener on `document` (outside the ready gate) that focuses `input[name="query"]` when the panel's `newState` is `open` |

## 11. Launch standard: domains, checkout and static pages (agreed 19 Nov 2026)

Not yet proven on a live launch. Written from Smootify's 2.0 domains docs and our dev-store tests.

- **Domains.** Root and `www` point to Webflow. Checkout gets a sub-domain such as `shop.example.com`,
  connected in Shopify (Settings > Domains) and set as the **primary** domain. Remove the main
  domain from Shopify, or checkout breaks. Custom domains need a paid Shopify plan, so a dev store
  checks out on `.myshopify.com` until hand-off.
- **No reverse proxy.** Proxying Shopify checkout behind the main domain is unsupported and puts
  payments (Shop Pay, wallets, 3-D Secure, fraud checks) at risk. Webflow only supports a proxy on
  Enterprise. Checkout pages aren't indexed, so there is no SEO gain.
- **Lock the Shopify storefront with Smootify's Redirect Theme** (free zip from Smootify's domains
  page). Upload it in Online Store > Themes, set Hostname (with `www`), Products Base `products`,
  Collections Base `collections`, publish. It sends every storefront page except the cart to the
  same Webflow page. Checkout, order status and discount links keep working. Do not use the store
  password for this: it blocks checkout too.
- **Static pages** (about, contact, stockists, blog) live only in Webflow. Leave Shopify Pages empty.
  Add a Webflow redirect `/pages/(.*)` to `/%1` so Shopify-style page links land.
- **Policies** go in Shopify Settings > Policies (checkout shows them in pop-ups) **and** on Webflow
  pages for the footer.
- **Checkout links back.** Point the checkout logo and "continue shopping" to the Webflow domain.
- **Replacing an existing site.** Crawl the old site and add a permanent redirect for every old URL
  in Webflow before switching DNS.
- **Search engines.** Check whether the Redirect Theme sends a server redirect or a script redirect.
  If it is a script, keep the checkout sub-domain out of the index.
- **Redirect Theme tested on a dev store (19 Nov 2026, v1.1.1, Proven).** Settings: Hostname = the
  Webflow domain, Products Base `products`, Collections Base `collections`, Custom redirects
  `/pages/>/`. Results: `/products/<handle>`, `/collections/<handle>` and `/` land on the matching
  Webflow URL; `/pages/contact` lands on `/contact`; `/search?q=` lands on `/search?q=` (so the
  Webflow site needs a search page); query strings are kept. `/cart` is not redirected and shows
  the theme's own cart page with a Shopify header and featured products: the one storefront page a
  visitor can still see. Buy now and checkout keep working with the theme published. The redirect
  is a script plus a canonical tag to the Webflow URL, not a server redirect. Theme settings are in
  the theme editor: Theme settings > Storefront.
