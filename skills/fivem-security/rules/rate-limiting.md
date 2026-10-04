# Golden Rule 4 — Rate Limiting

> Prevent event spamming by implementing server-side cooldowns or debouncing for critical actions.

A handler can be perfectly validated — right job, right place, real item, server-computed price — and still be exploited by simply calling it *fast*, or *out of order*, or *replaying* it. Rate limiting is the cadence guard that closes that gap. Read this for any sensitive or repeatable action.

## Why validated actions still need this

Imagine a fully-validated "sell one item for $100" handler. A cheater scripts it to fire 1000 times a second. Each call individually passes every check — they do hold an item, they are at the dealer — but the aggregate is a money printer at machine speed, or it races your inventory checks (call it twice before the first `RemoveItem` lands, sell the same item twice). Cadence and sequence guards, **on the server**, are what stop this. A client-side cooldown is meaningless — the cheater isn't using your client.

## Per-player cooldown (debounce)

Track the last time each player did the action, reject if too soon:

```lua
local lastAction = {}   -- [src] = GetGameTimer() ms
local COOLDOWN = 3000   -- ms

RegisterNetEvent('shop:sell', function(...)
    local src = source
    local now = GetGameTimer()
    if lastAction[src] and now - lastAction[src] < COOLDOWN then return end
    lastAction[src] = now
    -- ... validated action ...
end)

AddEventHandler('playerDropped', function() lastAction[source] = nil end)
```

`GetGameTimer()` is server uptime in ms — a reliable server clock. Set the cooldown to the fastest a *legitimate* player could repeat the action; anything faster is abuse.

## Guard the race, not just the rate

A cooldown set after the work prevents rapid *repeats*, but two calls can arrive before the first finishes (especially across an `await`). For actions that consume a resource, set the guard **before** the slow work and verify state atomically:

```lua
RegisterNetEvent('stash:take', function(item, qty)
    local src = source
    local now = GetGameTimer()
    if lastAction[src] and now - lastAction[src] < 500 then return end
    lastAction[src] = now                         -- claim the slot BEFORE the work
    -- re-check inventory/state right before mutating, so a racing call can't double-spend
    if exports.ox_inventory:GetItemCount(src, item) < qty then return end
    exports.ox_inventory:RemoveItem(src, item, qty)
end)
```

This prevents the "fire twice before the first deduct lands" dupe.

## Sequence gating

Multi-step actions must enforce order server-side: you can't claim step 3 without having done steps 1 and 2. Keep per-player step state on the server:

```lua
local step = {}   -- [src] = 'idle' | 'collected' | 'processed'

RegisterNetEvent('job:collect', function()
    local src = source
    -- ... validate ...
    step[src] = 'collected'
end)

RegisterNetEvent('job:deliver', function()
    local src = source
    if step[src] ~= 'collected' then return end   -- can't deliver what you never collected
    -- ... validate distance, pay ...
    step[src] = 'idle'
end)
```

Without this, a cheater fires `job:deliver` directly and gets paid for a delivery that never happened. The server's step state is the truth.

## Diminishing returns (soft anti-farm)

For repeatable economy actions (selling drugs, mining), a flat cooldown still allows steady grinding. Reduce the payout for consecutive actions in a window, recovering over time:

```lua
local runs = {}   -- [src] = { count = n, last = ms }

local function payoutMultiplier(src)
    local r = runs[src] or { count = 0 }
    return math.max(0.3, 1.0 - r.count * 0.1)     -- floor at 30%
end
-- bump r.count on each sale; a slow thread decrements it over time
```

This bounds how lucrative an unattended grind can be without punishing normal play.

## Always clean up per-player state

Every per-player table (`lastAction`, `step`, `runs`) leaks memory and can misattribute across reconnects if you don't clear it:

```lua
AddEventHandler('playerDropped', function()
    local src = source
    lastAction[src] = nil; step[src] = nil; runs[src] = nil
end)
```

## The exploits this rule prevents

- **Spam-farm**: a validated action fired at machine speed. Stopped by the per-player cooldown.
- **Double-spend / dupe race**: two calls before the first mutation lands. Stopped by claiming the guard before the work and re-checking state atomically.
- **Skip-the-work payout**: firing a later step directly. Stopped by server-side sequence gating.
- **Unattended grind**: steady farming within the cooldown. Bounded by diminishing returns.

Rate limiting pairs with distance (`rules/distance.md`): distance stops *remote* abuse, cadence stops *rapid* abuse. Together with server authority (`rules/events.md`) and parameter validation (`rules/parameters.md`), they close the four main ways a handler gets exploited.
