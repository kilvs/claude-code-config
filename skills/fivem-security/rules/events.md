# Golden Rule 1 — Server Authority: validating events

> The server dictates the truth. The client only requests actions.

Every `RegisterNetEvent` server handler and every `lib.callback.register` is a **public, hostile-facing endpoint** — anyone on the server can call it with any arguments, in any order, as fast as they like. This file is how you structure them so unauthorized execution gets nothing. Read it first for any event work.

## The shape of a safe handler

Every server handler that does something meaningful follows the same five-step order. The order matters: cheap rejections first, the action last.

```lua
RegisterNetEvent('shop:buy', function(itemName, amount)
    local src = source                          -- 1. capture source FIRST
    local player = exports.qbx_core:GetPlayer(src)
    if not player then return end               -- 2. resolve + authorize
    if not isAllowedToBuy(player) then return end

    amount = tonumber(amount)                    -- 3. distrust parameters
    if type(itemName) ~= 'string' then return end
    if not amount or amount < 1 or amount > 100 then return end
    local def = Config.Items[itemName]           --    whitelist, not the client's word
    if not def then return end

    local price = def.price * amount             -- 4. verify against server state
    if player.PlayerData.money.cash < price then return end
    -- (distance / rate-limit here too — rules/distance.md, rules/rate-limiting.md)

    player.Functions.RemoveMoney('cash', price, 'shop')   -- 5. act, amount from SERVER
    exports.ox_inventory:AddItem(src, itemName, amount)
    lib.notify(src, { type = 'success', description = ('Bought %dx %s'):format(amount, itemName) })
end)
```

Notice what the client never supplied: the price, the new balance, or proof the item is real. All of that is server-derived.

## Step 1: capture `source` first, before any `Wait()`

`source` is set by the server for the duration of the event handler and **cannot be spoofed** by the client — this is your one trustworthy input. But it is only valid synchronously: if the handler yields (`Wait`, an `await` callback, a DB call without care), `source` may have changed to another event in flight. So:

```lua
RegisterNetEvent('thing:do', function(arg)
    local src = source          -- FIRST line. Now `src` is safe across yields.
    -- ... Wait(100) or MySQL.query.await(...) is fine now; use `src`, never `source`, after this.
end)
```

The bug this prevents: reading `source` after a `Wait()` and acting on the wrong player — a subtle, intermittent vulnerability.

## Step 2: resolve and authorize

Turn `src` into a framework player and confirm they're allowed to do this *specific* action:

```lua
local player = exports.qbx_core:GetPlayer(src)
if not player then return end                              -- not a valid player
if player.PlayerData.job.name ~= 'mechanic' then return end -- job gate
if player.PlayerData.job.grade.level < 2 then return end    -- grade gate
```

Authorization is **per-action**. A player allowed to open a menu is not thereby allowed to fire every callback the menu can send — re-check on each consequential handler, not once at the menu.

## Steps 3–5: parameters, state, act

Parameter validation is Golden Rule 2 (`rules/parameters.md`); state verification and distance are Rules 3 (`rules/distance.md`); cadence is Rule 4 (`rules/rate-limiting.md`). The point of *this* file is that they happen **in the handler, on the server**, before the action — and the action uses server-owned values.

## `lib.callback` specifics

Callbacks are the same rules plus a return value. Validate identically; return a result the client can react to. Always return something (even `false`) so the client's `await` resolves.

```lua
lib.callback.register('shop:tryBuy', function(src, itemName, amount)
    local player = exports.qbx_core:GetPlayer(src)
    if not player then return false end
    -- ... same validation as above ...
    return true            -- client shows success UI; the actual money/item already moved server-side
end)
```

The return is **feedback, not authority** — the client learning "true" doesn't grant anything; the server already did (or refused) the work. Never structure it as "client asks, server returns the price, client confirms" — that round-trips authority back to the client.

## Minimize the event surface

Every networked event is an attack entry point. Reduce them:

- Don't `RegisterNetEvent` for things that don't need to cross the network. A purely client-side helper should be a local function, not a net event.
- Don't expose internal/admin operations as plain net events without an ACE check (see SKILL.md hard rules).
- One well-validated event beats five loosely-scoped ones. Fewer endpoints, each fully guarded.

## The exploit this rule prevents

A handler that skips server authority:
```lua
-- DANGEROUS
RegisterNetEvent('shop:buy', function(item, price)
    removeMoney(source, price)   -- client chose the price
    giveItem(source, item)       -- and the item
end)
```
`TriggerServerEvent('shop:buy', 'goldbar', -100000)` makes the cheater infinitely rich. The safe handler is immune because price and item validity are server-derived, not client-supplied. Server authority is the difference.
