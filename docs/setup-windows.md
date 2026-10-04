# AI Agent Config (Windows)

One folder that every Claude Code profile on your PC reads: your rules, one playbook per
stack, custom skills, Claude's auto-memory and your settings. Your Claude profiles
(`%USERPROFILE%\.claude`, and any extra ones) only keep logins, caches and sessions;
everything else is a link into this folder, so a change here reaches every profile at once.

Shared from a working setup, with the stack playbooks and skills kept and every client and
personal detail left out. Keep what fits, move out what doesn't.

## Layout

| Path | What lives here | Loaded when |
|---|---|---|
| `CLAUDE.md` | Your user-level instructions. Linked as `<profile>\CLAUDE.md`. | Every session |
| `general\how-i-work.md` | Your rules, whatever the client or stack. Starts as a prompt list. | Every session |
| `stacks\<stack>\` | One playbook per platform or language: Webflow, WordPress, PHP, Go, GSAP, Shopify, FiveM. | Before building on that stack |
| `skills\` | Custom skills, one folder each. Index in `skills\README.md`. | Claude Code discovers them |
| `work\<org>\` | One folder per org you work for: org card, client cards, a `KICKOFF.md` prompt. Start from `work\_template\`. | When working for that org |
| `memory\` | Claude's auto-memory, shared by every profile. `MEMORY.md` is the index. | Every session |
| `settings\` | `settings.json` and `mcp-servers.json`. | Every session |
| `bin\link-profile.ps1` | Wires a profile to this folder. Safe to rerun. | Setup |

Layers, most specific wins: **general** (always), **stack** (how the tool works), **org and
client** (who is asking), then the project's own `CLAUDE.md`.

Paths inside the stack playbooks and skills are written Mac style (`~/Documents/...`). On
Windows, read `~` as `%USERPROFILE%`. Shell snippets in the skills assume bash, which Claude
Code runs through Git Bash on Windows.

## Set up (Windows 10 or 11, PowerShell)

1. **Before you start.** Install Git for Windows (Claude Code uses its Git Bash) and Claude
   Code. Turn on **Developer Mode** (Settings > System > For developers) so the setup script
   can create file links without admin rights.

2. **Put the folder in place.** Unzip it and move it to `Documents\AI Agent Config`:
   ```powershell
   Move-Item "$HOME\Downloads\AI Agent Config" "$HOME\Documents\"
   cd "$HOME\Documents\AI Agent Config"
   ```
   Another location works too; the setup script points the memory folder at wherever it is.

3. **Put your name in.** Replace `{{NAME}}` (swap `Sam` for your name):
   ```powershell
   Get-ChildItem -Recurse -File -Include *.md | Where-Object { (Get-Content -Raw $_) -match '\{\{NAME\}\}' } |
     ForEach-Object { (Get-Content -Raw $_) -replace '\{\{NAME\}\}', 'Sam' | Set-Content -NoNewline $_ }
   ```

4. **Wire your profile.** Links `CLAUDE.md`, `settings.json` and every skill into
   `%USERPROFILE%\.claude`, and adds the MCP servers:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\bin\link-profile.ps1
   ```
   For a second profile, pass its folder: `... -File .\bin\link-profile.ps1 $HOME\.claude-work`,
   then start it with `$env:CLAUDE_CONFIG_DIR="$HOME\.claude-work"; claude`.
   An existing `CLAUDE.md` or `settings.json` in the profile is moved into
   `settings\superseded\`, never deleted. Copy anything you want to keep back into the new files.

5. **Log in to the MCP servers.** Start `claude`, run `/mcp`, and authenticate `webflow`,
   `figma` and `relume`. Remove the ones you don't use from `settings\mcp-servers.json` and
   from `%USERPROFILE%\.claude.json`.

6. **Make it yours.**
   - Write your rules into `general\how-i-work.md` and fill its accounts table.
   - Copy `work\_template\` to `work\<org>\` for each agency, employer or studio, fill the
     cards, and add the org to the table in `CLAUDE.md`.
   - Move out any stack or skill you never use, so Claude doesn't read rules that don't apply.
   - Turn the folder into a private git repo and commit after each change.

## How it grows

- When Claude gets something wrong and you correct it, add a row to the stack's "Gotchas that
  became rules" table, or a line to `general\how-i-work.md` if it applies everywhere.
- Claude writes its own memories into `memory\`. Read `MEMORY.md` now and then.
- Edit files here, never through a profile path. The profile paths are links.
