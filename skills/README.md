# Custom skills

One folder per skill with a `SKILL.md` inside. `bin/link-profile.sh` links each folder into
`<profile>/skills/<name>` so every profile sees it.

## Editable masters vs synced copies

The `anthropic-skills:*` set is synced from claude.ai into `<profile>/skills/synced/` and is
read-only there; it follows the claude.ai login of each profile. Every skill the user wrote was
migrated here on 22 Sep 2026 as the editable master. Both versions load; the local one appears
without the `anthropic-skills:` prefix and wins when they disagree.

| Group | Skill here | Synced twin |
|---|---|---|
| Webflow | `webflow-ui-design/` | `anthropic-skills:webflow-ui-design` |
| Webflow | `webflow-agent-instructions/` | `anthropic-skills:webflow-agent-instructions` |
| Webflow | `design-compilation/` | `anthropic-skills:design-compilation` |
| Design | `design-craft-check/` | `anthropic-skills:design-craft-check` (uploaded 29 Sep 2026; adapted from Anthropic's frontend-design and pbakaus/impeccable, Apache 2.0, 29 Sep 2026) |
| Webflow | `pre-launch-checklist/` | `anthropic-skills:pre-launch-checklist` |
| Webflow | `page-quality-auditor/` | `anthropic-skills:page-quality-auditor` |
| WordPress | `wordpress-theme-dev/` | `anthropic-skills:wordpress-theme-dev` |
| WordPress | `wordpress-elementor/` | `anthropic-skills:wordpress-elementor` (uploaded 29 Sep 2026; adapted from Jezweb's MIT skill, 29 Sep 2026) |
| Motion | `gsap/` | `anthropic-skills:gsap` (uploaded 29 Sep 2026; adapted from GreenSock's MIT skills, 29 Sep 2026) |
| Web apps | `env-files/` | `anthropic-skills:env-files` |
| Go | `go-idioms/` | `anthropic-skills:go-idioms` (uploaded 29 Sep 2026; merged from samber/cc-skills-golang, MIT, 29 Sep 2026; review-first) |
| React / Next.js | `vercel-react-best-practices/` | `anthropic-skills:vercel-react-best-practices` (uploaded 29 Sep 2026; Vercel, MIT, imported as is 29 Sep 2026) |
| React / Next.js | `vercel-composition-patterns/` | `anthropic-skills:vercel-composition-patterns` (uploaded 29 Sep 2026; Vercel, MIT, imported as is 29 Sep 2026) |
| Postgres (Neon) | `neon/` | `anthropic-skills:neon` (uploaded 29 Sep 2026; Neon, Apache 2.0, imported as is 29 Sep 2026) |
| Postgres (Neon) | `neon-postgres/` | `anthropic-skills:neon-postgres` (uploaded 29 Sep 2026; Neon, Apache 2.0, imported as is 29 Sep 2026) |
| FiveM (game dev) | `fivem-lua-dev/` | `anthropic-skills:fivem-lua-dev` |
| FiveM (game dev) | `fivem-job-builder/` | `anthropic-skills:fivem-job-builder` |
| FiveM (game dev) | `fivem-mission-builder/` | `anthropic-skills:fivem-mission-builder` |
| FiveM (game dev) | `fivem-nui-dev/` | `anthropic-skills:fivem-nui-dev` |
| FiveM (game dev) | `fivem-security/` | `anthropic-skills:fivem-security` |

## Webflow official skills (vendored 29 Sep 2026)

Nine skills copied from Webflow's official repo (github.com/webflow/webflow-skills, MIT, main at
c8a1650d, 21 Sep 2026), renamed `webflow-official-*`, each with a house note that the user's
standards win. The user: "Only Install Skills that do not contradict the standards specially the
client first standards" and "I stick to my own standards."

| Installed | For |
|---|---|
| `webflow-official-interactions` (+ 16 references) | IX3 API mechanics |
| `webflow-official-designer-tools` | headless element, style, component work |
| `webflow-official-site-audit` | read-only site inventory and health report |
| `webflow-official-cms-collection-setup` | creating collections and fields |
| `webflow-official-new-cms-plan`, `webflow-official-migrate-cms` | CMS planning and migration (never publish) |
| `webflow-official-cloud-apps`, `webflow-official-cloud-cli`, `webflow-official-cli-troubleshooter` | Webflow Cloud |

Left out because they contradict the standards: `flowkit-naming` and `figma-to-webflow` (Flowkit
`fk-` naming, px, inline SVG embeds, no `::before`/`clamp`), `accessibility-audit` (`role="button"`
on divs), `asset-audit` (writes alt text), `review-comments` (posts replies), `safe-publish`,
`bulk-cms-update`, `webflow-compress-cms-image`, `link-checker`, `site-activity` (publish),
`custom-code-management` (publish reminders, scripts outside Global Scripts), `cms-best-practices`
(publish step, alt-text writing), and the code-component / DevLink / designer-extension set
(Tailwind and CSS Modules, site classes treated as a fault). `wfu-mcp-getting-started` left out
as not needed. The whole plugin is never installed: it would also register a generic `webflow`
MCP server that mixes up the per-workspace accounts. Update by re-copying from the repo and
re-applying the house note.

Stays synced-only: docs, docx, pdf, pptx, xlsx,
skill-creator, import-memory.

**Workflow.** Edit here, commit, test in a session. When a version is worth sharing, zip the
folder and upload it in claude.ai (Settings, Skills) to replace the synced twin, so the team
and other devices get it. Log what changed and why at the top of the skill's `SKILL.md`
under the "Changes" heading, newest first, dated. A skill's stack playbook
(`stacks/<stack>/README.md`) points at it.
