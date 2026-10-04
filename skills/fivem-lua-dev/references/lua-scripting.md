# FiveM Lua Scripting

The scripting core. Assumes you can already program; this covers what's *different* about FiveM Lua. For resource structure see `resource-anatomy.md`; for the security mindset see `security.md`.

## Contents
1. The three realms (client / server / shared)
2. Events: the nervous system
3. Server callbacks (request→response)
4. Natives
5. Threads, Wait, and not freezing the server
6. State bags (modern shared state)
7. oxmysql (database)
8. ox_lib (the modern utility library)
9. Common gotchas

---

## 1. The three realms (client / server / shared)

Every line of FiveM Lua runs in one of three contexts, declared in `fxmanifest.lua`:

- **client** — runs on each player's game. Has access to the game world, the player's ped/vehicle, UI/NUI, and **client natives**. Untrusted (the player can tamper with it).
- **server** — runs once, on the server. Authoritative. Handles DB, money, items, permissions, validation. Has **server natives** (a different set). Cannot call client/game-world natives.
- **shared** — code loaded into *both* realms (constants, config, helper functions with no realm-specific calls). Great for a `config.lua` both sides read.

The mental model: client *sees and requests*, server *decides and persists*, shared *is common knowledge*. Most bugs labeled "the native doesn't work" are a native being called in the wrong realm. Check the native's realm on the FiveM natives reference.

## 2. Events: the nervous system

Realms talk to each other through events. There is no shared memory across the client/server boundary — only messages.

Client → server:
```lua
-- client
TriggerServerEvent('myres:buyItem', 'water', 2)

-- server
RegisterNetEvent('myres:buyItem', function(item, amount)
    local src = source            -- the player who triggered it (server sets this)
    -- VALIDATE: never trust item/amount blindly (see security.md)
end)
```

Server → one client / all clients:
```lua
-- server
TriggerClientEvent('myres:notify', targetServerId, 'Purchase complete')
TriggerClientEvent('myres:notify', -1, 'Server restarting')  -- -1 = everyone
```

Local (same realm, no network):
```lua
AddEventHandler('myres:localThing', function() end)  -- not networked
TriggerEvent('myres:localThing')
```

Key distinctions that trip people up:
- **`RegisterNetEvent`** marks an event as receivable across the network; plain `AddEventHandler` is local-only. A client→server event must be registered with `RegisterNetEvent` on the server.
- **`source`** server-side inside a net event is the player's server ID — reliable, set by the core, not by the client. Capture it immediately (`local src = source`) before any `Wait()`, since it can change.
- Don't register a net event you don't intend clients to call — every `RegisterNetEvent` is an entry point a cheater can hit with arbitrary arguments.

## 3. Server callbacks (request→response)

Events are fire-and-forget. When the client needs a *value back* from the server (e.g. "how much money do I have?"), use a callback. Frameworks and `ox_lib` provide these; the pattern:

```lua
-- ox_lib style
-- server
lib.callback.register('myres:getBalance', function(source)
    return GetPlayerMoney(source)   -- computed server-side
end)

-- client
local balance = lib.callback.await('myres:getBalance', false)
```

The value is computed server-side and returned — the client never decides it. (QBCore/ESX have their own callback APIs; same idea, see `frameworks.md`.)

## 4. Natives

**Natives** are the built-in game/server functions FiveM exposes (e.g. `GetEntityCoords`, `RegisterCommand`, `GiveWeaponToPed`). They're realm-specific and numerous.

- Look them up at the FiveM natives reference (`docs.fivem.net` natives DB). Each entry shows the realm (client/server), parameters, and return.
- Lua calls them by name: `local coords = GetEntityCoords(PlayerPedId())`.
- Some have both a hashed and a named form; use the named form.
- A native called in the wrong realm returns nil/0 or errors — if a native "does nothing," check its realm first.

## 5. Threads, Wait, and not freezing the server

Lua resources are cooperatively scheduled. Code must **yield** or it blocks everything in that resource.

```lua
CreateThread(function()
    while true do
        -- do work
        Wait(1000)   -- yield for 1s; NEVER omit this in a loop
    end
end)
```

- `Wait(0)` runs every frame — only when you truly need per-frame work (e.g. drawing). It's expensive; minimize.
- A loop with no `Wait()` hard-freezes the resource and can hitch the whole server.
- Prefer **event-driven** code and longer waits. Pattern: poll cheaply with a long `Wait`, drop to `Wait(0)` only while actively doing something (e.g. player is in a menu), then back off.
- `SetTimeout(ms, fn)` schedules a one-shot.

## 6. State bags (modern shared state)

State bags replicate state from server to clients (and between resources) without manual event plumbing — good for entity/player state everyone should see (e.g. a vehicle's "locked" status).

```lua
-- server: set state on an entity, replicated to clients
Entity(vehicle).state:set('locked', true, true)  -- last arg = replicated

-- client: read it
local locked = Entity(vehicle).state.locked
```

Prefer state bags over a `while` loop that polls and re-broadcasts; they're cheaper and synced by the engine.

## 7. oxmysql (database)

`oxmysql` is the standard DB layer. Server-side only (the client never touches the DB — that would be a trust-boundary violation).

```lua
-- async/await style (inside a thread or callback)
local rows = MySQL.query.await('SELECT * FROM users WHERE identifier = ?', { identifier })
local money = MySQL.scalar.await('SELECT money FROM users WHERE id = ?', { id })
MySQL.update.await('UPDATE users SET money = ? WHERE id = ?', { newMoney, id })
local insertId = MySQL.insert.await('INSERT INTO logs (msg) VALUES (?)', { msg })
```

Always use **parameterized queries** (`?` placeholders) — never string-concatenate user input into SQL (injection). This is the SQL equivalent of the trust-boundary rule.

## 8. ox_lib (the modern utility library)

`ox_lib` is a shared library most modern resources (especially Qbox) depend on: UI (notifications, context menus, input dialogs, progress bars), callbacks (above), caching, math/table helpers, and zones. Add `'@ox_lib/init.lua'` per its docs and `ensure ox_lib` before your resource.

```lua
-- client notification
lib.notify({ title = 'Shop', description = 'Purchased', type = 'success' })
-- progress bar that the player can't skip client-side (still validate server-side)
if lib.progressBar({ duration = 3000, label = 'Working...' }) then end
```

Leaning on `ox_lib` instead of hand-rolling NUI/menus saves enormous time and gives a consistent UX. Check its docs for the current API.

## 9. Common gotchas

- **Wrong realm** — the #1 issue; verify the native/event realm.
- **Trusting the client** — see `security.md`; covered everywhere for good reason.
- **`source` lost after `Wait()`** — capture `local src = source` first.
- **No `Wait()` in a loop** — freezes the resource.
- **Forgot `RegisterNetEvent`** — a server event clients call must be registered as a net event.
- **Manifest realm mismatch** — a file in `client_scripts` calling server natives will error; put it in the right list (`resource-anatomy.md`).
- **String-concatenated SQL** — use `?` parameters.
- **Per-frame loops left running** — back off `Wait` when idle; watch `resmon`.
