# Legal Loop Jobs — go here, do this, get paid, repeat

The default archetype: delivery, mechanic, garbage, fishing, lumberjack, taxi. Low risk, steady pay, usually no whitelist. The structure is a loop between interaction points, with the server validating each payout (see `job-economy.md` — that's where the money rules live; this file is the loop and the world-building).

## The shape

1. Player goes on duty (or just has the job).
2. Script directs them to a **start point** (pickup, job-board, task source) via blip + `ox_target`.
3. They do the task (drive a package, repair a part, catch a fish) — often a `lib.progressBar`.
4. Script directs them to a **finish point** (dropoff, job-board) — another `ox_target`.
5. Server validates and pays; loop resets.

Keep the per-player step state **on the server** (`job-economy.md` §6) so a dropoff can't be claimed without a real pickup.

## Interaction points with ox_target

`ox_target` attaches interaction options to zones, models, or entities. Gate the option's `canInteract`/`groups` on the job client-side for clean UX — but remember that's only UX; the server re-checks.

**Box zone** (a spot in the world):
```lua
exports.ox_target:addBoxZone({
    coords = vec3(123.4, 567.8, 90.1),
    size = vec3(2, 2, 2),
    rotation = 0,
    options = {
        {
            name = 'trucker_pickup',
            label = 'Grab package',
            icon = 'fa-solid fa-box',
            groups = { trucker = 0 },     -- only shows for the trucker job (UX gate)
            onSelect = function()
                TriggerServerEvent('trucker:pickup')   -- server validates & sets state
            end,
        },
    },
})
```

**Model target** (every prop/ped of a model — e.g. a dumpster for garbage job):
```lua
exports.ox_target:addModel({ `prop_dumpster_01a`, `prop_dumpster_02a` }, {
    { name = 'garbage_collect', label = 'Empty bin', groups = { garbage = 0 },
      onSelect = function() TriggerServerEvent('garbage:collect') end },
})
```

## Blips

Show the player where to go. Create on the client; update as the loop advances.

```lua
local blip = AddBlipForCoord(123.4, 567.8, 90.1)
SetBlipSprite(blip, 478)
SetBlipColour(blip, 5)
SetBlipRoute(blip, true)              -- draw GPS route
BeginTextCommandSetBlipName('STRING')
AddTextComponentSubstringPlayerName('Package Dropoff')
EndTextCommandSetBlipName(blip)
```

Remove with `RemoveBlip(blip)` when the step changes so the map doesn't litter.

## Task feedback — progress bar

```lua
if lib.progressBar({
    duration = 5000,
    label = 'Loading package...',
    useWhileDead = false,
    canCancel = true,
    disable = { move = true, car = true, combat = true },
    anim = { dict = 'anim@heists@box_carry@', clip = 'idle' },
}) then
    TriggerServerEvent('trucker:pickup')   -- only fire the server step if it completed
end
```

The progress bar is client-side flavour; it does **not** authorize anything. The server step it fires must still validate.

## Optional: a job vehicle

Many legal jobs hand out a work vehicle on duty. Spawn it client-side near a depot, set it owned/keyed per your framework, and despawn/return it off duty. Validate that the player has the job before honouring any "return vehicle for deposit" payout server-side. Detailed vehicle spawning/control is in the broader `fivem-lua-dev` skill's `world-entities.md`.

## End-to-end: a minimal delivery loop

**client.lua**
```lua
local hasPackage = false  -- local UX flag only; server is the source of truth

CreateThread(function()
    exports.ox_target:addBoxZone({
        coords = Config.Pickup, size = vec3(2,2,2),
        options = {{ name='pk', label='Grab package', groups={trucker=0},
            onSelect = function()
                if hasPackage then return lib.notify({type='error',description='Already carrying'}) end
                if lib.progressBar({duration=3000,label='Loading...',disable={move=true}}) then
                    local ok = lib.callback.await('trucker:pickup', false)
                    if ok then hasPackage = true; lib.notify({type='success',description='Got it. Deliver it.'}) end
                end
            end }}
    })
    exports.ox_target:addBoxZone({
        coords = Config.Dropoff, size = vec3(2,2,2),
        options = {{ name='dr', label='Deliver package', groups={trucker=0},
            onSelect = function()
                local ok = lib.callback.await('trucker:deliver', false)
                if ok then hasPackage = false end
            end }}
    })
end)
```

**server.lua**
```lua
local carrying = {}   -- [src] = true, server-owned step state
local lastPay  = {}

lib.callback.register('trucker:pickup', function(src)
    local p = exports.qbx_core:GetPlayer(src)
    if not p or p.PlayerData.job.name ~= 'trucker' then return false end
    if #(GetEntityCoords(GetPlayerPed(src)) - Config.Pickup) > 5.0 then return false end
    carrying[src] = true
    return true
end)

lib.callback.register('trucker:deliver', function(src)
    local p = exports.qbx_core:GetPlayer(src)
    if not p or p.PlayerData.job.name ~= 'trucker' then return false end
    if not carrying[src] then return false end                        -- sequence gate
    if #(GetEntityCoords(GetPlayerPed(src)) - Config.Dropoff) > 5.0 then return false end
    local now = GetGameTimer()
    if lastPay[src] and now - lastPay[src] < 3000 then return false end -- cadence
    lastPay[src], carrying[src] = now, nil
    p.Functions.AddMoney('cash', Config.Pay, 'trucker-delivery')        -- pay from server config
    lib.notify(src, { type='success', description=('Delivered. +$%d'):format(Config.Pay) })
    return true
end)

AddEventHandler('playerDropped', function() carrying[source]=nil; lastPay[source]=nil end)
```

Note there is **no amount, no item, no position** the client can supply to cheat: it sends only "I'm trying to pickup/deliver," and the server checks job, location, sequence, and cadence before paying its own configured amount. This is the whole archetype — everything else (fishing, mechanic, garbage) is the same skeleton with different points, props, items, and pay.

## Variations on the skeleton
- **Fishing/lumberjack**: pickup step = `lib.progressBar` at a water/tree zone that grants an item (`ox_inventory:AddItem`) instead of a flag; dropoff = sell the item to a buyer (validate `GetItemCount` server-side, see `job-economy.md`).
- **Mechanic**: "pickup" = repair target on a damaged vehicle near the player; pay scales with repair type. Validate the vehicle is real and nearby server-side.
- **Taxi**: start = accept a fare (server picks a dropoff), finish = arrive within range of that server-chosen dropoff. The dropoff must be server-chosen so the client can't claim arrival at a fake one.
