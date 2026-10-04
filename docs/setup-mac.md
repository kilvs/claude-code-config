# AI Agent Config (Mac)

One folder that every Claude Code profile on your Mac reads: your rules, one playbook per
stack, custom skills, Claude's auto-memory and your settings. Your Claude profiles
(`~/.claude`, and any extra ones) only keep logins, caches and sessions; everything else is a
link into this folder, so a change here reaches every profile at once.

Shared from a working setup, with the stack playbooks and skills kept and every client and
personal detail left out. Keep what fits, move out what doesn't.

## Layout

| Path | What lives here | Loaded when |
|---|---|---|
| `CLAUDE.md` | Your user-level instructions. Linked as `<profile>/CLAUDE.md`. | Every session |
| `general/how-i-work.md` | Your rules, whatever the client or stack. Starts as a prompt list. | Every session |
| `stacks/<stack>/` | One playbook per platform or language: Webflow, WordPress, PHP, Go, GSAP, Shopify, FiveM. | Before building on that stack |
| `skills/` | Custom skills, one folder each. Index in `skills/README.md`. | Claude Code discovers them |
| `work/<org>/` | One folder per org you work for: org card, client cards, a `KICKOFF.md` prompt. Start from `work/_template/`. | When working for that org |
| `memory/` | Claude's auto-memory, shared by every profile. `MEMORY.md` is the index. | Every session |
| `settings/` | `settings.json` and `mcp-servers.json`. | Every session |
| `bin/link-profile.sh` | Wires a profile to this folder. Safe to rerun. | Setup |
| `bin/claude-list` | Lists your profiles with a 7-day usage view, launches one, or adds a new one. | Any terminal |

Layers, most specific wins: **general** (always), **stack** (how the tool works), **org and
client** (who is asking), then the project's own `CLAUDE.md`.

## Set up (macOS, zsh)

1. **Put the folder in place.** Unzip it and move it to `~/Documents/AI Agent Config`:
   ```sh
   mv ~/Downloads/"AI Agent Config" ~/Documents/
   cd ~/Documents/"AI Agent Config"
   ```
   Another location works too; the setup script points the memory folder at wherever it is.

2. **Put your name in.** Replace `{{NAME}}` (swap `Sam` for your name):
   ```sh
   grep -rl '{{NAME}}' . | xargs sed -i '' 's/{{NAME}}/Sam/g'
   ```

3. **Wire your profile.** Links `CLAUDE.md`, `settings.json` and every skill into `~/.claude`,
   and adds the MCP servers:
   ```sh
   bin/link-profile.sh ~/.claude
   ```
   An existing `~/.claude/CLAUDE.md` or `settings.json` is moved into `settings/superseded/`,
   never deleted. Copy anything you want to keep back into the new files.

4. **Log in to the MCP servers.** Start `claude`, run `/mcp`, and authenticate `webflow`,
   `figma` and `relume`. Remove the ones you don't use from `settings/mcp-servers.json` and
   from `~/.claude.json`.

5. **Optional: the `claude-list` command.**
   ```sh
   mkdir -p ~/.local/bin && ln -s "$PWD/bin/claude-list" ~/.local/bin/claude-list
   ```
   `claude-list add` creates a second profile (for example one per employer, with its own
   GitHub login and commit email) and wires it with `link-profile.sh`.

6. **Make it yours.**
   - Write your rules into `general/how-i-work.md` and fill its accounts table.
   - Copy `work/_template/` to `work/<org>/` for each agency, employer or studio, fill the
     cards, and add the org to the table in `CLAUDE.md`.
   - Move out any stack or skill you never use, so Claude doesn't read rules that don't apply.
   - Turn the folder into a private git repo and commit after each change.

## How it grows

- When Claude gets something wrong and you correct it, add a row to the stack's "Gotchas that
  became rules" table, or a line to `general/how-i-work.md` if it applies everywhere.
- Claude writes its own memories into `memory/`. Read `MEMORY.md` now and then.
- Edit files here, never through a profile path. The profile paths are links.
