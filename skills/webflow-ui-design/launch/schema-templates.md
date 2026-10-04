# Schema / JSON-LD templates

Copy-paste JSON-LD blocks for the schema types that still earn rich results or feed entity/AI understanding in 2026. Google recommends JSON-LD (over Microdata/RDFa). Each block goes in `<head>` as `<script type="application/ld+json">`. In Webflow: Page settings → Custom code (per-page types) or Site settings → Custom code head (site-wide types). Webflow adds no schema automatically.

**Replace every `{{PLACEHOLDER}}`.** Rules: URLs absolute, dates ISO 8601 (`2026-01-15`), schema reflects only visible content, validate in Google Rich Results Test + validator.schema.org before shipping.

## Priority matrix — which page gets what

| Page type | Schema to include |
|---|---|
| Every page (site-wide) | `Organization` (or `LocalBusiness`) + `WebSite` |
| Every page with a breadcrumb trail | `BreadcrumbList` |
| Home | Organization/LocalBusiness + WebSite |
| Blog / article detail | `Article` (or `BlogPosting`) + BreadcrumbList |
| Product detail | `Product` + `Offer` + BreadcrumbList |
| Local/contact/location | `LocalBusiness` (with NAP, hours, geo) |

Most sites need 4–6 types total. Start with the foundation (Organization + WebSite + BreadcrumbList), add page-specific types only where the content genuinely matches. Partial implementations earn zero rich-result lift — fill required fields completely.

**Deprecated — don't rely on:** FAQPage rich results were removed from Google Search in May 2026 (keep FAQ content for users if useful, but no rich result). HowTo rich results deprecated since Sept 2023. Don't invest implementation time in either for rich results.

---

## Organization (site-wide, in head)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{{BUSINESS_NAME}}",
  "url": "https://{{DOMAIN}}",
  "logo": "https://{{DOMAIN}}/{{LOGO_PATH}}.png",
  "description": "{{ONE_LINE_DESCRIPTION}}",
  "sameAs": [
    "https://www.facebook.com/{{HANDLE}}",
    "https://www.instagram.com/{{HANDLE}}",
    "https://www.linkedin.com/company/{{HANDLE}}"
  ]
}
</script>
```

## WebSite (site-wide, in head)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{{SITE_NAME}}",
  "url": "https://{{DOMAIN}}"
}
</script>
```

## LocalBusiness (use instead of Organization for a physical/service business)

Pick the most specific subtype where one fits (`Restaurant`, `CafeOrCoffeeShop`, `Dentist`, `AutoRepair`, etc.); otherwise `LocalBusiness`. Keep NAP identical to Google Business Profile and directory citations.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "{{LOCALBUSINESS_SUBTYPE}}",
  "name": "{{BUSINESS_NAME}}",
  "url": "https://{{DOMAIN}}",
  "image": "https://{{DOMAIN}}/{{IMAGE_PATH}}.jpg",
  "telephone": "{{+CC_PHONE}}",
  "priceRange": "{{$$}}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{{STREET}}",
    "addressLocality": "{{CITY}}",
    "addressRegion": "{{REGION}}",
    "postalCode": "{{POSTCODE}}",
    "addressCountry": "{{COUNTRY_CODE}}"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "{{LAT}}",
    "longitude": "{{LNG}}"
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
      "opens": "{{09:00}}",
      "closes": "{{17:00}}"
    }
  ],
  "sameAs": [
    "https://www.facebook.com/{{HANDLE}}",
    "https://www.instagram.com/{{HANDLE}}"
  ]
}
</script>
```

## BreadcrumbList (per page with a trail — `item` URLs must be absolute)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://{{DOMAIN}}/" },
    { "@type": "ListItem", "position": 2, "name": "{{PARENT_NAME}}", "item": "https://{{DOMAIN}}/{{PARENT_SLUG}}" },
    { "@type": "ListItem", "position": 3, "name": "{{CURRENT_PAGE_NAME}}" }
  ]
}
</script>
```
(The last item has no `item` URL — it's the current page.)

## Article / BlogPosting (blog detail)

Use `headline` matching the visible `<h1>`. Include `author` (Person) and `publisher` (Organization with logo) for author display and Top-Stories formatting.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ARTICLE_TITLE}}",
  "description": "{{ARTICLE_SUMMARY}}",
  "image": "https://{{DOMAIN}}/{{FEATURED_IMAGE}}.jpg",
  "datePublished": "{{2026-01-15}}",
  "dateModified": "{{2026-01-20}}",
  "author": {
    "@type": "Person",
    "name": "{{AUTHOR_NAME}}",
    "url": "https://{{DOMAIN}}/author/{{AUTHOR_SLUG}}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "{{BUSINESS_NAME}}",
    "logo": {
      "@type": "ImageObject",
      "url": "https://{{DOMAIN}}/{{LOGO_PATH}}.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://{{DOMAIN}}/{{ARTICLE_SLUG}}"
  }
}
</script>
```

In Webflow CMS templates, bind the placeholders to Collection fields via the page's custom code (or a field-bound embed) so each item outputs its own values.

## Product + Offer (product detail)

Required for product rich snippets: `name`, `image`, `offers` (with `priceCurrency`, `price`, `availability`). Add `aggregateRating`/`review` only if ratings are genuinely shown on the page. `price` is a plain number; `availability` uses the schema.org enum.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{PRODUCT_NAME}}",
  "image": "https://{{DOMAIN}}/{{PRODUCT_IMAGE}}.jpg",
  "description": "{{PRODUCT_DESCRIPTION}}",
  "sku": "{{SKU}}",
  "brand": { "@type": "Brand", "name": "{{BRAND}}" },
  "offers": {
    "@type": "Offer",
    "url": "https://{{DOMAIN}}/{{PRODUCT_SLUG}}",
    "priceCurrency": "{{PHP}}",
    "price": "{{199.00}}",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  }
}
</script>
```
(`availability` options: `InStock`, `OutOfStock`, `PreOrder`, `Discontinued`, `BackOrder`.)

## FAQPage (optional — no rich result since May 2026, but valid for users/LLMs)

Only mark up questions that are visibly on the page. Don't add FAQs just for the markup.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{{QUESTION_1}}",
      "acceptedAnswer": { "@type": "Answer", "text": "{{ANSWER_1}}" }
    },
    {
      "@type": "Question",
      "name": "{{QUESTION_2}}",
      "acceptedAnswer": { "@type": "Answer", "text": "{{ANSWER_2}}" }
    }
  ]
}
</script>
```

---

## Webflow placement summary

- **Site-wide** (Organization/LocalBusiness, WebSite) → Site settings → Custom code → Head code.
- **Per-page** (BreadcrumbList, Article, Product, FAQ) → Page settings → Custom code → Inside `<head>` tag.
- **CMS template** (Article/Product on a Collection page) → put the block in the Collection page's custom code and bind placeholders to Collection fields.
- Validate each block (Rich Results Test + schema.org validator) before publishing; re-check Search Console Enhancements after the first crawl.
