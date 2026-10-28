# claude-code-config

A folder that every Claude Code profile on your machine reads: one playbook per stack, a set
of custom skills, your own rules, Claude's auto-memory and your settings. Your Claude
profiles (`~/.claude`, and any extra ones) only keep logins, caches and sessions; everything
else is a link into this folder, so a change here reaches every profile at once.

It grew out of a working setup for building client websites (Webflow first, then WordPress,
Shopify, PHP, Go, GSAP and FiveM). The stack playbooks and skills are shared here; the
client and personal parts are not.

## What is inside

| Path | What lives here | Loaded when |
|---|---|---|
| `CLAUDE.md` | Your user-level instructions. Linked as `<profile>/CLAUDE.md`. | Every session |
| `general/how-i-work.md` | Your rules, whatever the client or stack. Starts as a prompt list. | Every session |
| `stacks/<stack>/` | One playbook per platform or language, with dated "gotchas that became rules". | Before building on that stack |
| `skills/` | Custom skills, one folder each. Index in `skills/README.md`. | Claude Code discovers them |
| `work/<org>/` | One folder per org you work for: org card, client cards, a kickoff prompt. Start from `work/_template/`. | When working for that org |
| `memory/` | Claude's auto-memory, shared by every profile. Starts empty. | Every session |
| `settings/` | `settings.json` and `mcp-servers.json` (Webflow, Figma, Relume). | Every session |
| `bin/` | `link-profile.sh` (macOS) and `link-profile.ps1` (Windows) wire a profile to this folder; `claude-list` (macOS) lists, launches or adds profiles. | Setup |

Layers, most specific wins: **general** (always), **stack** (how the tool works), **org and
client** (who is asking), then the project's own `CLAUDE.md`. Only `CLAUDE.md`, the general
rules and the memory index load every session; stacks, cards and skills load when a task
needs them, which keeps the context small.

## Install

Clone it to `~/Documents/AI Agent Config` (any location works; the setup script points the
memory folder at wherever it is), then follow the guide for your OS:

```sh
git clone https://github.com/<owner>/claude-code-config.git ~/Documents/"AI Agent Config"
```

- macOS: [`docs/setup-mac.md`](docs/setup-mac.md)
- Windows: [`docs/setup-windows.md`](docs/setup-windows.md)

Fork it rather than working on a clone of this repo: your `general/`, `work/` and `memory/`
will hold your own details, so keep your fork private.

## Credits

Several skills are adapted from other projects and keep their own licence file in the skill
folder: Webflow's official skills (`webflow-official-*`), Vercel's React skills, Neon's
skills, GreenSock's GSAP skill, samber's Go skills, Jezweb's WordPress skills and Anthropic's
`frontend-design`. See each `SKILL.md` for the source.

## Licence

MIT for this repo's own files (`LICENSE`). Skills adapted from other projects keep their own
licence file inside the skill folder, and that licence applies to that skill.

## Staying up to date

This repo is rebuilt automatically from a private working setup whenever a stack playbook or
skill changes. Pull it now and then (`git pull`), or watch the repo on GitHub. If you forked
it, merge upstream into your fork: your own `general/`, `work/` and `memory/` files are not
touched by upstream changes, since upstream ships them blank.
