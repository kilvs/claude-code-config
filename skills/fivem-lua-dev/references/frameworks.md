# Frameworks: ESX, QBCore & Qbox

The RP frameworks provide players, money, jobs, and inventory so you don't rebuild them. They share concepts; APIs differ. Confirm current API details against each framework's own docs/GitHub, since these evolve. For why-pick-which at a glance, see SKILL.md "Choosing a framework."

## Contents
1. How they relate
2. Getting a player (server-side)
3. Money
4. Jobs
5. Items / inventory
6. Client-side player data
7. Writing framework-targeted code cleanly

---

## 1. How they relate

- **ESX Legacy** — long-standing, huge back-catalogue of `esx_*` scripts. APIs via the `ESX` shared object and exports/events.
- **QBCore** — widely used fork-era framework with a large `qb-*` ecosystem; APIs via the `QBCore` object (`exports['qb-core']:GetCoreObject()`).
- **Qbox** — a modern, optimized continuation of the QBCore lineage, restructured around the `ox_*` libraries; core resource commonly `qbx_core`. **Recommended for new servers.** Much QBCore knowledge transfers, but prefer Qbox-native exports and `ox_lib`/`ox_inventory` patterns over legacy `qb-*` ones.

Because Qbox descends from QBCore, tutorials/scripts for QBCore are often adaptable, but don't assume drop-in compatibility — match the script to the framework and version.

## 2. Getting a player (server-side)

The first thing most server logic does is resolve the calling player into a framework player object.

ESX:
```lua
ESX = exports['es_extended']:getSharedObject()
local xPlayer = ESX.GetPlayerFromId(source)
```

QBCore:
```lua
local QBCore = exports['qb-core']:GetCoreObject()
local Player = QBCore.Functions.GetPlayer(source)
```

Qbox (QBCore-compatible exports, ox-based under the hood):
```lua
local player = exports.qbx_core:GetPlayer(source)
```

In all three, `source` is the server ID of the player who triggered the event — captured server-side, never supplied by the client.

## 3. Money

Always mutate money **server-side** through the framework (so it persists and can't be forged client-side).

ESX: `xPlayer.addMoney(amount)` / `xPlayer.removeMoney(amount)` / `xPlayer.getMoney()` (and accounts like `bank`, `black_money`).
QBCore: `Player.Functions.AddMoney('cash', amount)` / `RemoveMoney('bank', amount)` / `Player.PlayerData.money['cash']`.
Qbox: same shape as QBCore via the `qbx_core` player object / exports.

A purchase flow is always: client *requests* → server resolves player → server checks they can afford it → server removes money and grants item → server tells client the result. The client never tells the server the new balance.

## 4. Jobs

ESX: `xPlayer.setJob(name, grade)`, read `xPlayer.job.name` / `.grade`.
QBCore: `Player.Functions.SetJob(name, grade)`, read `Player.PlayerData.job`.
Qbox: QBCore-style job API via `qbx_core`.

Job checks for restricted actions (who can open the police armory) must be **server-verified** — a client claiming to be a cop is not proof.

## 5. Items / inventory

Inventory is where frameworks diverge most. Modern servers across all three increasingly standardize on **`ox_inventory`**, which exposes its own exports regardless of framework:

```lua
-- ox_inventory (server)
local count = exports.ox_inventory:GetItemCount(source, 'water')
exports.ox_inventory:AddItem(source, 'water', 1)
exports.ox_inventory:RemoveItem(source, 'water', 1)
```

ESX (legacy) uses `xPlayer.addInventoryItem`; QBCore uses `Player.Functions.AddItem`. If you're on Qbox or a modern QBCore/ESX setup, you're likely using `ox_inventory` — check which inventory the server runs before writing item code, because the API differs entirely.

## 6. Client-side player data

Client code often needs read-only player info (job, name) for UI. Frameworks expose a client getter:
- ESX: `ESX.GetPlayerData()`
- QBCore: `QBCore.Functions.GetPlayerData()`
- Qbox: QBCore-style client export.

Treat this as **display only** — it's client-side and not authoritative. Any action gated on it must be re-checked server-side.

## 7. Writing framework-targeted code cleanly

- Resolve the core object/exports once, near the top, not repeatedly.
- Put framework name/version assumptions in `config.lua` and depend on the core resource in `fxmanifest.lua` (`dependencies`).
- For a script meant to support multiple frameworks, isolate the framework calls behind a small bridge file per framework (a common pattern in released scripts) rather than scattering `if QBCore then ... elseif ESX then ...` everywhere.
- Prefer the `ox_*` libraries (`ox_lib`, `ox_inventory`, `ox_target`) for new code — they're framework-agnostic and where the ecosystem is heading, especially on Qbox.
- When in doubt about an export name or event signature, check the framework's GitHub for the current source rather than trusting an old tutorial.
