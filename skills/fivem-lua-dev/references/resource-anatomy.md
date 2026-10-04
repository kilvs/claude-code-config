# Resource Anatomy

How a FiveM resource is structured and why it starts (or doesn't). For scripting see `lua-scripting.md`; for server.cfg `ensure` lines see `server-setup.md`.

## Contents
1. What a resource is
2. fxmanifest.lua
3. Folder layout & the [category] convention
4. Realm script lists
5. Dependencies & load order
6. Wiring ox_lib / oxmysql
7. "My resource won't start" checklist

---

## 1. What a resource is

A **resource** is a folder the server can start/stop independently, containing an `fxmanifest.lua` plus its scripts/assets. Resources are the unit of everything in FiveM — the framework core is a resource, each script is a resource, maps and cars are resources. The server loads a resource when `server.cfg` says `ensure <name>` (or via txAdmin).

## 2. fxmanifest.lua

The manifest declares what the resource is and what runs where. Minimal modern manifest:

```lua
fx_version 'cerulean'      -- manifest format version (use the current one)
game 'gta5'                -- target game
lua54 'yes'                -- opt into Lua 5.4 (recommended for new resources)

author 'You'
description 'My resource'
version '1.0.0'

shared_scripts {
    '@ox_lib/init.lua',    -- pull ox_lib into both realms (if used)
    'config.lua',
}

client_scripts {
    'client.lua',
}

server_scripts {
    '@oxmysql/lib/MySQL.lua',  -- pull in oxmysql server-side (if used)
    'server.lua',
}

dependencies {
    'ox_lib',
    'oxmysql',
}
```

Field notes:
- `fx_version` — the manifest schema name (e.g. `cerulean`); use the current one from the docs, an old value can refuse to load.
- `lua54 'yes'` — opt into Lua 5.4; worth it for new code.
- The `@resource/file.lua` syntax loads a file *from another resource* (how `ox_lib`/`oxmysql` are pulled in).
- `escrow_ignore` / `dependency`/`provide` and many `data_file` types exist for advanced cases — check the docs when needed.

## 3. Folder layout & the [category] convention

A resource folder:
```
my_resource/
├── fxmanifest.lua
├── config.lua          (shared)
├── client.lua
├── server.lua
├── client/             (optional split into multiple files)
├── server/
└── html/               (NUI: index.html, app.js, style.css)
```

Resources are grouped on disk in **`[category]`** folders (the square brackets are literal) — e.g. `resources/[qbx]/qbx_core`, `resources/[standalone]/my_resource`. A `[bracketed]` folder is a grouping the server recurses into; you don't `ensure` the folder, you `ensure` the resources inside it. Keep third-party packs in their own `[category]` so updates don't clobber your work.

## 4. Realm script lists

The manifest routes files to realms (this is how the realms from `lua-scripting.md` are assigned):
- `client_scripts { ... }` → client realm
- `server_scripts { ... }` → server realm
- `shared_scripts { ... }` → both

A file in the wrong list runs in the wrong realm and its realm-specific natives fail. If a "client" script needs to talk to the server, it doesn't move realms — it sends an **event** (`lua-scripting.md` §2).

NUI (HTML/CSS/JS UI) is declared with `ui_page 'html/index.html'` and the files listed under `files { 'html/index.html', 'html/app.js', ... }`.

## 5. Dependencies & load order

Two mechanisms, both matter:
- **`dependencies { 'ox_lib', 'oxmysql' }`** in the manifest tells the server this resource needs those; it won't start cleanly without them and the error names the missing one.
- **`ensure` order in `server.cfg`** controls actual start sequence. Put libraries and the framework core *before* dependents:
  ```
  ensure oxmysql
  ensure ox_lib
  ensure qbx_core
  ensure my_resource
  ```
A resource that starts before its dependency throws "failed to load / could not find dependency." When in doubt, ensure libraries → framework → your resources.

## 6. Wiring ox_lib / oxmysql

Most modern resources use both:
- **ox_lib**: add `'@ox_lib/init.lua'` to `shared_scripts` (usually first), declare it in `dependencies`, and `ensure ox_lib` before your resource.
- **oxmysql**: add `'@oxmysql/lib/MySQL.lua'` to `server_scripts`, declare the dependency, `ensure oxmysql` first of all.

Install both as resources (their own folders) from their official releases; keep them updated since scripts track their current APIs.

## 7. "My resource won't start" checklist

When a resource fails to load, walk these in order:
- [ ] `fxmanifest.lua` present, named exactly that, and `fx_version`/`game` set to current valid values.
- [ ] No Lua syntax error in a listed file (the console prints the file + line).
- [ ] File is in the correct realm list (client vs server vs shared).
- [ ] Dependencies installed and `ensure`d **before** this resource in `server.cfg`.
- [ ] Resource folder name matches the `ensure` name and any manifest references (renaming a resource breaks scripts that reference it by name).
- [ ] It's actually inside a path the server scans (a `[category]` folder under `resources/`).
- [ ] `refresh` then `ensure <name>` in the txAdmin/server console after adding it.
