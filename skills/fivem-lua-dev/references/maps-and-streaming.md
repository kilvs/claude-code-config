# Maps, MLOs & Asset Streaming

How custom level content and assets actually enter a FiveM server. The honest framing up front: in FiveM you mostly **integrate and stream** assets that were authored in external tools — you don't build geometry in Lua. This file covers the integration side thoroughly and **signposts** the authoring tools without trying to teach 3D modeling (that's a separate craft). For the resource manifest basics see `resource-anatomy.md`. Confirm current file types and limits at the Cfx.re asset docs (`docs.fivem.net/docs/assets-manual/`), since the toolchain evolves.

## Contents
1. The core idea: the stream/ folder
2. Map mods (ymap placements)
3. MLOs (custom interiors)
4. Custom vehicles
5. Custom clothing / peds
6. Performance & crash limits (read this)
7. IPLs (toggling built-in GTA interiors)
8. Where the authoring tools fit (signposts)

---

## 1. The core idea: the stream/ folder

Custom assets live inside a normal resource, in a folder named **`stream/`**. FiveM auto-scans `stream/` and loads anything there by file extension — you do **not** list those files in `fxmanifest.lua`. The file types you'll meet:

- `.ymap` — placement data (where props/objects sit in the world)
- `.ytyp` — type/archetype definitions (what an object *is*); needs a `data_file` declaration (below)
- `.ydr` / `.yft` — models (drawable / fragment)
- `.ytd` — texture dictionary
- `.ybn` — collision (bounds)
- `.ydd` — clothing/component drawables

Minimal map resource:
```
my_map/
├── fxmanifest.lua
└── stream/
    ├── placement.ymap
    └── interior.ytyp
```
```lua
-- fxmanifest.lua
fx_version 'cerulean'
game 'gta5'
this_is_a_map 'yes'
```
`this_is_a_map 'yes'` tells FiveM to treat the resource as mapping and load the `stream/` content efficiently. Then `ensure my_map` in `server.cfg`.

## 2. Map mods (ymap placements)

A "map mod" that only *places existing game props* (barriers, furniture, decoration) is the simplest case: just `.ymap` files in `stream/` with the manifest above. Players auto-download on join.

Gotcha: if two map resources place data at the same coordinates you get **texture flickering / z-fighting**. Don't run overlapping maps; remove the duplicate. A `.ymap` only contains placement — if it references custom models/textures, those `.ydr`/`.ytd`/`.ytyp` files must also be present.

## 3. MLOs (custom interiors)

An **MLO** is more than placement — it modifies the building's interior data, "punching" new rooms/holes into existing shells (a custom police station, club, apartment). Structure:
```
custom_mlo/
├── fxmanifest.lua
└── stream/
    ├── interior.ymap
    ├── interior.ytyp
    ├── interior_shell.ybn
    └── textures.ytd
```
MLOs usually need `data_file` declarations so the interior/type data registers. The common ones:
```lua
fx_version 'cerulean'
game 'gta5'
this_is_a_map 'yes'

files { 'stream/*.ytyp' }                       -- or a data/ folder
data_file 'DLC_ITYP_REQUEST' 'stream/*.ytyp'    -- register the .ytyp archetypes
```
Some MLOs ship interior-proxy meta files and want those declared too:
```lua
files { 'interiorproxies.meta' }
data_file 'INTERIOR_PROXY_ORDER_FILE' 'interiorproxies.meta'
```
Follow the **specific MLO's included instructions** — they vary, and the readme tells you which meta files and data_file lines that MLO needs. Many MLOs also require a small script to define teleport/entry points or door locks; install those as provided.

Most install failures are **folder-structure mistakes** (files outside `stream/`, wrong resource name) or missing `data_file` lines — not the model itself. "Invisible walls" / no-collision usually means the `.ybn` collision file didn't load.

## 4. Custom vehicles

A car needs models + data:
```
my_car/
├── fxmanifest.lua
├── stream/
│   ├── adder.yft        -- model
│   └── adder.ytd        -- textures
└── data/
    ├── vehicles.meta     -- registers the vehicle to the game
    ├── handling.meta     -- physics/handling
    └── carvariations.meta / carcols.meta (colors, variations)
```
```lua
fx_version 'cerulean'
game 'gta5'
files {
    'data/vehicles.meta',
    'data/handling.meta',
    'data/carvariations.meta',
    'data/carcols.meta',
}
data_file 'VEHICLE_METADATA_FILE' 'data/vehicles.meta'
data_file 'HANDLING_FILE' 'data/handling.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/carvariations.meta'
data_file 'CARCOLS_FILE' 'data/carcols.meta'
```
The `.meta` files are what make the model a usable, spawnable vehicle (the model alone won't work). Match the spawn name in `vehicles.meta` to what you spawn in script.

## 5. Custom clothing / peds

Clothing uses ped component data (`.ydd` drawables, `.ytd` textures) in `stream/`, often under a ped-model subfolder (e.g. `stream/mp_m_freemode_01/...`). Clothing/EUP packs get large fast — mind the limits below. Adding clothing to the player wardrobe also typically involves a clothing/appearance resource (e.g. `illenium-appearance`, `fivem-appearance`) that knows about the added components; pure streaming alone may not surface them in a menu.

## 6. Performance & crash limits (read this)

Custom assets are the top cause of client crashes and "city blinking." Hard realities:
- **Single file ~16MB physical limit** — exceeding it crashes players. Split oversized dictionaries.
- **Textures >2048×2048** cause texture loss (the world blinking/disappearing) on lower-VRAM clients. Compress textures; drop unused alpha channels.
- **A `.ytd` over ~10MB** should be split or quality-reduced.
- **High-poly models (>~200k polys)** cause instability and FPS drops.
- More streamed assets = longer join download and more client memory. Audit what you actually need.

When players report crashes near a custom area or random "texture loss," suspect an oversized/uncompressed asset before anything else.

## 7. IPLs (toggling built-in GTA interiors)

GTA V already contains many interiors that are disabled by default (some DLC buildings, the destroyed/alternate versions of areas). You enable them in script with **IPLs** — no streaming needed, it's built-in content:
```lua
RequestIpl('ex_dt1_02_office_02b')   -- load an interior
-- RemoveIpl(...) to unload
```
Useful when the interior you want already exists in the game and you just need it on. Finding the right IPL name is the work — they're catalogued in community references and CodeWalker.

## 8. Where the authoring tools fit (signposts)

Creating the assets above — modeling an MLO, building a `.ymap`, making a car — happens in **external tools**, and is its own discipline this skill does not teach. Pointers so you know what to learn or commission:

- **CodeWalker** — the community world editor: explore the GTA map, place props and build `.ymap` files, find coordinates/IPL names, inspect archetypes. The standard tool for placement-style map mods and for figuring out where things are. Cfx.re's own beginner asset series uses it.
- **Sollumz (Blender add-on)** — import/export GTA formats in Blender for modeling MLOs and assets; the modern open path for interior/model authoring.
- **OpenIV** — browse/extract the game's archives (find original models, textures, IPL names) and install/inspect assets. More a research/extraction tool now than the primary authoring path.
- **3ds Max + tools / ZModeler** — older/commercial vehicle and model pipelines you'll see referenced.

Recommended division of labour for a server dev: integrate and place with **CodeWalker**, buy or commission complex **MLOs/vehicles** rather than modeling them yourself early on, and keep your effort on the scripting and server side where this skill is strong. When you do bring in custom assets, the integration rules in §1–6 are what keep them from crashing your players. The official, current authoring walkthroughs live at `docs.fivem.net/docs/assets-manual/` — follow those for tool specifics, since versions change.
