# {{NAME}}: user-level instructions

This file lives in your `AI Agent Config` folder and each Claude Code profile's `CLAUDE.md` is
a link to it (`bin/link-profile` makes the link). Edit it here. `README.md` beside it explains
the folder.

## Always

@general/how-i-work.md

## Read on demand

Before building on a platform or in a language, read its playbook in
`stacks/<stack>/README.md` (Webflow, WordPress, PHP, Go, GSAP, Shopify, FiveM). The skills in
`skills/` load on their own when a task matches them.

Before working under an org or on a client, read its folder in `work/<org>/`: the `README.md`
is the org card, one file per client beside it.

| Org | Folder | Clients |
|---|---|---|
| <Org name> | `work/<org>/` | `<client>.md` |

Org rules override stack rules; the project's own `CLAUDE.md` overrides both.
