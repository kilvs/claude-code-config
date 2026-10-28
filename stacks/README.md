# Stacks

One folder per platform or language. A stack playbook is org-agnostic: it says how the tool
works and how you use it, never who the client is. Org rules (`work/<org>/`) override a stack;
the project's `CLAUDE.md` overrides both.

| Stack | What it covers |
|---|---|
| `webflow/` | Client-First builds through the Designer and the Webflow MCP. The longest playbook. |
| `shopify/` | Liquid themes; to be filled from the first build. |
| `smootify/` | Shopify storefronts in Webflow; `general-setup.md` is the conversion guide. |
| `wordpress/` | Themes and Elementor. Skills: `wordpress-theme-dev`, `wordpress-elementor`. |
| `gsap/` | Custom-code motion; skill `gsap`. Webflow motion stays IX3. |
| `php/` | Modern PHP before the WordPress dialect. |
| `go/` | Go services and tools. Skill `go-idioms` (review-first). |
| `fivem/` | FiveM roleplay servers in Lua. Five skills in `skills/fivem-*`. |

Every stack folder has a `README.md`, the playbook. Sections: What it is used for,
Conventions, Accounts and tools, Gotchas that became rules (dated), Pointers (skills, docs).
Keep it short. While you are learning a stack, add a `learning.md` beside it (see
`_template/learning.md`): where you are on the roadmap, what you understand, what to learn
next. Claude updates it at the end of a learning session.

Skills here for stacks without a folder yet: `vercel-react-best-practices` and
`vercel-composition-patterns` (React / Next.js), `neon` and `neon-postgres` (Postgres on Neon).
Give them a stack folder when a project uses them.

Add a stack by copying `_template/` to the new name and filling the sections.
