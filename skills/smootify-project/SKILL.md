---
name: smootify-project
description: Kick off or continue an ecommerce project where a Webflow site sells through Shopify (Smootify connector). Use whenever a project mentions Shopify plus Webflow, a store, products, cart, checkout, Smootify or StoreSynk, or the user says "new Smootify project", "ecommerce setup", "connect Shopify", "test the store" or "/smootify-project". Runs the discovery checks, the Figma design-gap audit, the test-store and test-site setup, the agent build and QA, and points to the launch and hand-off steps, stopping at every step that needs the user.
---

# Smootify project

The playbook is `~/Documents/AI Agent Config/stacks/smootify/project-process.md`. Read it first,
then `general-setup.md` (markup, gotchas, launch standard section 11) and `docs-digest.md` (plans,
hand-off, 2.0 vs 1.x) in the same folder. This skill is the run order; the playbook is the detail.

## 0. Orient (every time)
- Which project, which org, which client card (`work/<org>/`). Read the org's rules and the
  project's RESUME HERE if it exists. Accounts, Chrome profile and Webflow MCP come from the card.
- Is this a new project or a continuation? For a continuation, read the project's build log and
  pick up at the first open step below.
- Smootify 2.0 is beta: if `docs-digest.md` is more than a month old, refresh it from
  `https://www.smootify.io/docs` (llms.txt) before building, with a read-only research agent.
- If the `smootify` MCP is connected, use it to check markup and audit the site while building
  (read only). If it asks to sign in, the user runs `/mcp` and signs in.

## 1. Discovery (Claude, no permissions needed)
Public checks, then a short list of client questions for whoever owns the client relationship:
- curl the client domain: Shopify (`cdn.shopify.com`, `myshopify.com`, `powered-by: Shopify`),
  WordPress (`wp-content`) or other; `/products.json` for the public product count; `dig NS` for the
  DNS host. Check any sister brand the client already sells.
- Questions (only through the client owner, after the previous owner's handover): existing Shopify
  store, domain and DNS access, site being replaced, reviews / subscriptions / markets / wholesale,
  product count and how often it changes.

## 2. Design audit (read-only agent)
Spawn a research agent on the Figma Hi-Fi with the brief in `project-process.md` section 2. It
returns a feature table (Smootify / StoreSynk / extra app or code) and the design gaps: cart entry
point, search state, reviews, filters (need Search & Discovery), empty and sold-out states, brands
sold elsewhere. Report the verdict and the gaps to the user; draft the gap message to the designers.

## 3. Test build
| Step | Who |
|---|---|
| Create a **client-transfer** store in the Partner Dev Dashboard (country = where they sell) | Claude, on the user's go |
| Partner identity verification (first third-party app only, once per person) | **The user** |
| Open each new store admin once (account picker) | **The user** |
| Install Headless (storefront, all Storefront API permissions), Smootify, Search & Discovery if filters | Claude, after the user says yes in the main chat |
| Duplicate the org's Client-First starter as `Smootify <Project> Test`, set the webflow.io sub-domain | Claude |
| Smootify dashboard: Choose the site > Connect Webflow > Authorize **one site** (pop-up) | **The user** |
| Build: `senior-web` agent with the brief in `project-process.md` section 3.5 (2.0, plural slugs, test products shaped like the design, webflow.io only) | agent |
| QA: `qa` agent at 1440 / 768 / 390, then fix and QA again | agent |
| Enter the dev-store password once to test checkout (Online Store > Preferences > Store access) | **The user** |
| Redirect Theme test (optional): the user uploads the zip (file picker), Claude sets Hostname, bases, custom redirects and tests | both |

Rules: never pay; never publish to a custom domain; never touch the client's real build site;
agents don't take relayed approval for app installs or account steps, so do those in the main
session on the user's word. Log everything in the project's build log, newest first.

## 4. Real build, launch, hand-off
Follow `project-process.md` sections 4 to 6 and `general-setup.md` section 11. Launch steps that
touch DNS, custom domains, store transfers, plans or payments are the user's call each time.

## 5. Close out
- Run `records-keeper` at the end of a session that changed the project.
- New gotchas go in `general-setup.md` (client-free wording); process changes go in
  `project-process.md`. Keep both free of client names: they ship in the shareable build.
- Drafts to the team follow the org's message rules (clipboard, first person, no colon labels).

## Changes
- 19 Nov 2026: created from the first two-store Smootify test.
