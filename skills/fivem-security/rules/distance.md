# Golden Rule 3 — Distance Checks

> Always check distance on the server side before allowing an interaction.

Looting a body, selling to a dealer, opening a stash, using a target, entering a zone — every in-world interaction has a *place* it's supposed to happen. A cheater can fire the event from anywhere on the map. The server must confirm the player is actually there, using coordinates the server knows, not coordinates the client claims. Read this for any in-world interaction.

## Why client position is untrustworthy

The client can tell the server "I'm standing at the dealer" while their character is across the map (or nowhere). If your handler trusts a position the client *sends*, a cheater sells, loots, or interacts remotely — repeatedly, safely, from a hidden corner. The fix is to read the player's position from the **server's** knowledge of their ped, and compare it to the interaction point stored in **server** config.

## The pattern

```lua
-- the real interaction point lives in SERVER config
Config.Dealer = vec3(123.4, 567.8, 90.1)
Config.InteractRadius = 5.0

RegisterNetEvent('drugs:sell', function()
    local src = source
    local player = exports.qbx_core:GetPlayer(src)
    if not player then return end

    -- server-known ped coords — NOT a position the client sent
    local pcoords = GetEntityCoords(GetPlayerPed(src))
    if #(pcoords - Config.Dealer) > Config.InteractRadius then return end   -- too far: reject

    -- ... now safe to proceed (still validate items, rate-limit, etc.)
end)
```

Two things make this trustworthy:
- `GetPlayerPed(src)` + `GetEntityCoords` reads the position the **server** has for that player, derived from normal game sync — the client isn't handing you a number.
- `Config.Dealer` is server-side; the client can't relocate the dealer.

`#(a - b)` is the vector distance (magnitude of the difference) — the idiomatic FiveM way to measure distance between two `vec3`s.

## Choosing a radius

- Match it to the real interaction footprint plus a little slack for sync jitter — typically **2.0–5.0** for a point interaction, larger for a building or zone.
- Too tight and legitimate players get rejected by normal position desync; too loose and you've reopened the remote-interaction hole. 5.0m is a sane default for most ground interactions.
- For interactions tied to an `ox_target` option, the target's own range handles the *client* UX, but the **server still re-checks distance** — the target range is presentation, not security.

## Server-validated zones

For area-based gameplay (a turf, a safe zone, a job site), validate zone membership server-side rather than trusting a client "I'm in the zone" event. Compute it from server-known coords against a server-defined zone (a radius, or a polygon test). The principle is identical: the server decides whether the player is in the zone from data it owns.

## Distance to another entity or player

When an interaction targets another entity (reviving a downed player, robbing someone, hotwiring a car), check distance between the two server-known positions, and validate the target exists and is a plausible target:

```lua
RegisterNetEvent('ems:revive', function(targetServerId)
    local src = source
    targetServerId = tonumber(targetServerId)
    if not targetServerId then return end
    local target = exports.qbx_core:GetPlayer(targetServerId)
    if not target then return end
    local a = GetEntityCoords(GetPlayerPed(src))
    local b = GetEntityCoords(GetPlayerPed(targetServerId))
    if #(a - b) > 3.0 then return end          -- must be next to the patient
    -- ... authorize (is src EMS?), then revive
end)
```

Note `targetServerId` is a client-supplied parameter too — validate it (Golden Rule 2) and confirm the target is real before measuring distance to it.

## The exploits this rule prevents

- **Teleport-loot / remote-sell**: firing an interaction event from across the map. Stopped because server-known coords aren't near the point.
- **Spoofed-position interaction**: trusting a client-sent position. Stopped by never accepting a client position — always reading the server's.
- **Action on an absent target**: reviving/robbing someone who isn't there. Stopped by validating the target exists and measuring server-known distance to it.

Combine with rate-limiting (`rules/rate-limiting.md`) — distance stops *remote* abuse; cadence stops *rapid* abuse. Sensitive interactions usually need both.
