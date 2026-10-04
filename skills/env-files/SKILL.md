---
name: env-files
description: "Set up and maintain environment variables in a web app repo: a committed .env.example template listing every variable with where to get its value, and a gitignored .env / .env.local holding the real values, so setting up a machine is copy the template, paste the values. Covers the .gitignore block, public vs secret prefixes (NEXT_PUBLIC_, VITE_, PUBLIC_), per-stack loading (Next.js, Astro, Vite, Node, Go, PHP), startup validation, host dashboards (Vercel, Webflow Cloud), GitHub Actions secrets, and what to do if a key leaks. Use when starting a web app repo, adding or renaming an env var, adding an API or secret key, onboarding a machine, or when a build fails on a missing variable."
---

## Changes

- 29 Sep 2026 (the user: "a skill for web app to have an env file and a .env template file on
  the github repo so I can just copy and paste the env values or even api and secret keys"):
  new.

# Env files

## The rule

- **`.env.example` is committed.** Every variable the app reads, with an empty value (or a
  harmless local default), a comment saying what it is, whether it is secret, and exactly
  where to get the value.
- **The real values file is never committed**, not even in a private repo. Git history keeps
  a key forever, forks and clones copy it, and GitHub secret scanning flags it.
- **Setup on any machine:** `cp .env.example .env.local` (or `.env`), then paste each value from
  the place its comment names.

The template is the copy-paste checklist; the values come from the provider dashboards, the
host's env settings or the user's password manager.

## The template

```dotenv
# .env.example: copy to .env.local and fill in. Never commit the copy.
# Each variable: a comment line above it (what | secret or public | where to get it).

# ---- App ----
# Base URL | public | localhost here, the real domain in the host's settings
APP_URL=http://localhost:3000

# ---- Database (Neon) ----
# Pooled connection string | SECRET | Neon console > Connect > Pooled connection
DATABASE_URL=
# Direct connection, for migrations | SECRET | Neon console > Connect > pooling off
DATABASE_URL_UNPOOLED=

# ---- Payments (Stripe) ----
# Secret key | SECRET | dashboard.stripe.com/test/apikeys (test key locally, live key only in the host)
STRIPE_SECRET_KEY=
# Publishable key | public, shipped to the browser | same page
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

- Group by service, in the order a new developer would set them up.
- Name the exact dashboard path or URL. "Get it from Stripe" is not enough.
- Mark local-only vs production differences (test keys locally, live keys only in the host).
- Comments go on their own line, never after a value.
- **Quote pasted values that contain `#`, spaces or quotes:** `DATABASE_URL="postgres://u:p#ss@h/db"`.
  Unquoted, the parser treats `#` as a comment and silently cuts the value (tested with Node's
  `--env-file`, 29 Sep 2026). Quoting every secret is the safe habit.
- Keep it in sync: **a new variable and its
  `.env.example` line land in the same commit.** A variable missing from the template is a bug.

## .gitignore

```gitignore
# env: real values stay local
.env
.env.*
!.env.example
```

Check before the first commit and whenever env files change:
`git ls-files | grep -i env` must list only `.env.example`.

## Public vs secret

Anything with a public prefix is compiled into the browser bundle, where anyone can read it.

| Stack | Browser-visible prefix | Loads |
|---|---|---|
| Next.js | `NEXT_PUBLIC_` | `.env`, `.env.local` (local overrides), `.env.development`, `.env.production` |
| Vite | `VITE_` | `.env`, `.env.local`, `.env.[mode]` |
| Astro | `PUBLIC_` (or `astro:env` with `access: "public"`) | `.env` files via Vite; prefer `astro:env` schemas |
| Node scripts | none | `node --env-file=.env.local app.js` (Node 20.6+) |
| Go | none | not automatic; `os.Getenv` / `os.LookupEnv`, export vars in the shell or load a file in dev only |
| PHP / WordPress | none | `getenv()`; `wp-config.php` reads from the server env, never a committed file |

Never put a secret behind a public prefix. Publishable keys (Stripe `pk_`, a Supabase anon key,
Google Maps with referrer limits) are designed to be public; everything else is not.

## Validate at startup

Fail fast, naming the missing variables, never printing values.

```ts
// env.ts (Node / Next.js server code)
const required = ["DATABASE_URL", "STRIPE_SECRET_KEY"] as const;
const missing = required.filter((k) => !process.env[k]);
if (missing.length) throw new Error(`Missing env: ${missing.join(", ")} (see .env.example)`);
```

```go
// Go
for _, k := range []string{"DATABASE_URL"} {
	if _, ok := os.LookupEnv(k); !ok {
		log.Fatalf("missing env %s (see .env.example)", k)
	}
}
```

With a schema library already in the project (zod, t3-env, `astro:env`), use it instead.

## Where the real values live

- **Deployed:** the host's env settings (Vercel: Project > Settings > Environment Variables,
  per environment; Webflow Cloud: the app's environment variables). Set them there by hand
  from the same template.
- **CI:** GitHub Actions secrets. `gh secret set -f .env.production` loads a dotenv file into
  the repo's secrets. They are write-only: GitHub never shows them again, so they are not a
  place to copy values back from.
- **The user's machines:** `.env.local`, filled from the provider dashboards or a password
  manager entry per project.

## How Claude handles secrets

- Read `.env.example`, not `.env.local`, to learn what a project needs.
- Never echo a secret value into chat, logs, commit messages, `CLAUDE.md`, memory, docs or
  screenshots. Refer to it by name.
- When the user pastes a key into chat, write it into the gitignored file and don't repeat it.
- Before any commit, run `git status` and `git diff --cached --name-only`, and stop if an env
  file other than `.env.example` is staged.
- Tests and CI get dummy values, never real keys.

## If a key is committed or pasted somewhere public

1. **Rotate the key first** at the provider. Deleting the file or rewriting history does not
   un-leak it.
2. Put the new key in `.env.local` and the host, redeploy.
3. Remove the file from git (`git rm --cached .env.local`), fix `.gitignore`, commit.
4. Tell the user which key, where it was exposed, and that it is rotated. Log it in the project
   `CLAUDE.md` by name only.

## New repo checklist

1. `.gitignore` block above.
2. `.env.example` with every variable, grouped and commented.
3. Startup validation.
4. README "Setup" section: `cp .env.example .env.local`, then fill in each value.
5. Host env vars set per environment; CI secrets if Actions need them.
6. `git ls-files | grep -i env` shows only `.env.example`.
