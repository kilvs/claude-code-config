# Illegal / Criminal Jobs — risk, reward, and not getting farmed

Drug harvesting & selling, store robberies, vehicle theft, heists. The design difference from a legal job is **risk/reward**: pay is higher, but there's a chance of failure, police get alerted, items can be seized, and the loop must resist being ground 24/7. The server-authoritative rules from `job-economy.md` still apply in full — read that first. This file is the risk layer on top.

## What makes it "illegal" mechanically

Three ingredients, in roughly this order of importance:
1. **Police involvement** — the act creates a dispatch alert / blip for on-duty LEO, so it's risky in a populated server.
2. **Failure & loss** — a chance the run fails, the player is caught, or items/cash are seized. Expected value, not headline pay, is what you balance.
3. **Bounded farmability** — cooldowns, diminishing returns, and limited sell capacity so the loop can't be repeated infinitely for steady income.

A "drug job" that's just a legal delivery loop with a higher number and no alert isn't a criminal job — it's a money printer. The risk is the point.

## The harvest → process → sell loop

Most drug jobs are a three-stage chain, each stage server-validated:

- **Harvest**: at a field/zone, `lib.progressBar` then server grants raw item (`ox_inventory:AddItem(src, 'raw_leaf', n)`). Gate by job/zone server-side.
- **Process**: at a lab, server checks the player holds enough raw item, removes it, grants processed item. (`RemoveItem` raw, `AddItem` processed — both server-side.)
- **Sell**: to an NPC/ped or zone, server checks held processed item, removes it, pays. This is where the risk fires.

Each transition is its own validated server callback — never a single client event that claims "I did the whole chain, pay me."

## Police dispatch / alerts

When a risky action fires (selling, robbing), the server notifies on-duty police. The standard approach is integrating whatever dispatch resource the server runs (e.g. `ps-dispatch`, `cd_dispatch`, `qs-dispatch`) via its export/event — check which one the target server uses rather than assuming. The minimal framework-native version: the server iterates connected players, and for those whose job is LEO and who are on duty, sends a blip near the (server-known) location.

```lua
-- server: alert on-duty cops near the crime, with a chance the sale is 'noticed'
local function alertPolice(coords)
    if math.random() > Config.AlertChance then return end   -- not every sale is seen
    for _, pid in ipairs(GetPlayers()) do
        local cop = exports.qbx_core:GetPlayer(tonumber(pid))
        if cop and cop.PlayerData.job.type == 'leo' and cop.PlayerData.job.onduty then
            TriggerClientEvent('myjob:copBlip', tonumber(pid), coords)  -- approximate the coords client-side
        end
    end
end
```

Blur the reported location a little (offset by a random small radius) so it's "somewhere around here," not a pinpoint — that's the cat-and-mouse.

## Failure, seizure, and item loss

Bake the downside into the server handler:

```lua
-- on a sell attempt, server-side:
if math.random() < Config.BustChance then
    exports.ox_inventory:RemoveItem(src, 'processed', heldAmount)  -- lose the goods
    alertPolice(sellCoords)
    lib.notify(src, { type = 'error', description = 'Deal went bad — you got robbed!' })
    return
end
```

Tune `BustChance` and `AlertChance` (and how much is seized) — these are the real balancing levers, not the sale price. Expected value ≈ `pay × (1 − bustChance) − lossOnBust × bustChance`. Make sure that lands at your intended risk-adjusted $/hr (`job-economy.md` §8).

## Stopping the farm: cooldowns & diminishing returns

Without these, players park at one sell point and grind. Server-side, per player:

- **Per-action cooldown** between sales (e.g. 20–60s).
- **Diminishing price**: each consecutive sale to the same buyer/zone pays less, recovering over time. Track `salesThisWindow[src]` server-side and scale `pay = basePay * math.max(Config.MinMult, 1 - n*Config.Decay)`.
- **Buyer cooldown / saturation**: an NPC buyer "isn't interested" for a while after buying, pushing players to move around the map (and spread risk).
- **Reset on `playerDropped`** to avoid leaks.

## Selling to a ped (NPC buyer)

A common pattern: spawn a buyer ped, target it, server validates the sale. The ped is flavour — the sale is a server callback that checks held item, applies cooldown/diminishing return, rolls the bust chance, then removes item and pays. Ped spawning/wandering details are in `fivem-lua-dev`'s `world-entities.md`; the *transaction* lives here and obeys `job-economy.md`.

## Robbery / heist variant

Store/house robbery and heists are the same spine with a longer, multi-step sequence and a bigger alert:
- A **start** action (hack/lockpick via `lib.skillCheck` or `lib.progressBar`) that fires the police alert immediately.
- A **sequence** of server-gated steps (can't loot the safe before cracking it — enforce step order server-side).
- A **reward** pulled from server config, often with a cooldown on the *location* (the store can't be robbed again for N minutes — store that timestamp server-side, keyed by location, not by player).
- Heists usually require a minimum number of LEO online (`Config.MinCops`) — check it server-side at start and refuse otherwise.

## Balancing summary

- Headline pay is higher than legal jobs, but **expected** pay after bust/seizure and diminishing returns should be only moderately higher — risk is compensated, not free.
- The fun is the cat-and-mouse with police, not the number. Invest in the alert/escape loop.
- Re-run the exploit test: fire each stage's event directly, out of order, with junk args — confirm nothing pays and no items appear.
