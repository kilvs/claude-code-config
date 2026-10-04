# Mission Engine — missions as data, server-owned state machine

The core of the skill. Write the engine once; every mission is a data table the engine runs. Read this first for any mission work. The two modes (`directed-missions.md`, `random-events.md`) are just different ways to *start* a mission that this engine then drives.

## Contents
1. Missions as data (the schema)
2. The objective-type vocabulary
3. The server-side state machine
4. The reward hook (swappable per framework / standalone)
5. Sync with state bags
6. The single cleanup pattern
7. The trust boundary (restated, because missions have many steps)

---

## 1. Missions as data

A mission is a config table, not bespoke code. The engine reads the table and runs it. This is what makes the skill "flexible" — new content is new data, not new engine.

```lua
-- shared/missions.lua  (server reads this; client gets a sanitized view)
Missions['warehouse_raid'] = {
    id = 'warehouse_raid',
    label = 'Warehouse Raid',
    coop = { min = 1, max = 4, progress = 'shared' },   -- 'shared' or 'perPlayer'
    cooldownMs = 600000,                                  -- per starter; events use their own scheduler
    objectives = {
        {
            id = 'goto_warehouse', type = 'goto',
            coords = vec3(0,0,0), radius = 20.0,          -- TODO coords
            text = 'Get to the warehouse',
        },
        {
            id = 'clear_guards', type = 'kill',
            count = 5,                                     -- server-credited kills
            spawn = 'guards',                              -- key into a spawn table (see §3)
            text = 'Eliminate the guards (0/5)',
            failOnPlayerDeath = false,
        },
        {
            id = 'grab_loot', type = 'collect',
            item = 'stolen_goods', count = 3,             -- verified via ox_inventory server-side
            coords = vec3(0,0,0), radius = 3.0,
            text = 'Grab the goods (0/3)',
            timerMs = 120000,                              -- optional fail timer for THIS objective
        },
        {
            id = 'escape', type = 'goto',
            coords = vec3(0,0,0), radius = 30.0,
            text = 'Escape the area',
        },
    },
    reward = { money = { account = 'cash', amount = 5000 }, items = { { name='cash_roll', count=1 } } },
    onFail = 'cleanup',   -- engine always cleans up; this is for any extra fail behaviour
}
```

The client receives only what it needs to render (labels, objective coords/text) — never the completion logic or reward amounts. The server keeps the authoritative copy.

## 2. The objective-type vocabulary

A small set of reusable types covers most missions. Each type defines a server-side completion check. Build these once in the engine:

- **goto** — player within `radius` of `coords`. Server checks the player's server-known ped coords.
- **kill** — `count` of a tagged enemy set killed. **The server credits kills** (from the spawned peds' death events it owns), not a client tally.
- **collect** — hold `count` of `item` (verify with `exports.ox_inventory:GetItemCount`), optionally within a pickup zone.
- **interact** — use an `ox_target`/zone option at `coords` (e.g. hack, plant, lockpick), usually gated behind a `lib.progressBar` / `lib.skillCheck` whose *completion* the server validates by location + state.
- **escort** — keep an NPC/vehicle alive and move it to a destination; server tracks the entity it spawned.
- **defend** — keep an entity/zone intact for a duration or against waves; server owns the timer and the waves.
- **capture** — hold a zone (no hostiles inside / presence for N seconds); server owns the zone timer.
- **survive / wait** — stay alive / present for `timerMs`; server owns the clock.

Anything exotic is usually a combination of these plus a custom check. Keep custom checks server-side.

## 3. The server-side state machine

The server holds one record per *active mission instance* (an instance can have one player or a group). The record tracks current objective, per-objective progress, all spawned handles, timers, and participants.

```lua
-- server
local active = {}   -- [instanceId] = stateRecord
local cooldowns = {} -- [citizenid or location] = expiryMs

local function startMission(missionId, starterSrc, party)
    local def = Missions[missionId]
    if not def then return end                              -- bound the input
    -- eligibility (cooldown, party size, not already in one) — gate server-side
    local instId = ('%s:%d'):format(missionId, GetGameTimer())
    active[instId] = {
        def = def, objIndex = 1,
        progress = {}, handles = { peds = {}, vehicles = {}, objects = {}, blips = {}, zones = {} },
        participants = party or { starterSrc },
        timers = {},
    }
    spawnForObjective(instId, 1)                            -- spawn what objective 1 needs
    syncMission(instId)                                     -- push to participants
    return instId
end
```

**Advancing** is a server function called only after a server-validated completion check passes:

```lua
local function tryComplete(instId, src, objId, payload)
    local inst = active[instId]; if not inst then return false end
    local obj = inst.def.objectives[inst.objIndex]
    if not obj or obj.id ~= objId then return false end     -- must be on THIS step
    if not isParticipant(inst, src) then return false end

    -- server-side completion check by type (the client cannot assert completion)
    if obj.type == 'goto' then
        if #(GetEntityCoords(GetPlayerPed(src)) - obj.coords) > (obj.radius or 5.0) then return false end
    elseif obj.type == 'collect' then
        if exports.ox_inventory:GetItemCount(src, obj.item) < obj.count then return false end
    elseif obj.type == 'kill' then
        if (inst.progress[objId] or 0) < obj.count then return false end  -- server-credited count
    -- ...other types...
    end

    advance(instId)                                          -- next objective or finish
    return true
end
```

**Kill crediting** (the part clients try to fake): when the engine spawns enemies for a `kill` objective, it tags them and listens for *their* death server-side, incrementing `inst.progress[objId]`. The client never sends "I killed one."

```lua
-- when spawning the guard peds (spawn delegated to fivem-lua-dev), record handles and watch deaths
-- on a ped death the server controls: inst.progress['clear_guards'] = (inst.progress['clear_guards'] or 0) + 1
-- then syncMission(instId) so clients see (3/5)
```

**Finish**:
```lua
local function advance(instId)
    local inst = active[instId]
    cleanupObjective(instId, inst.objIndex)                  -- tear down the finished step's spawns/timers
    inst.objIndex = inst.objIndex + 1
    if inst.objIndex > #inst.def.objectives then
        giveReward(instId)                                   -- §4, server-authoritative
        cleanupMission(instId)                               -- §6
    else
        spawnForObjective(instId, inst.objIndex)
        syncMission(instId)
    end
end
```

## 4. The reward hook (swappable)

Rewards use the `fivem-job-builder` server-authoritative pattern: amounts come from the mission def (server config), never a client. Isolate the framework touch in one function so standalone/QBCore/ESX swap cleanly.

```lua
-- Qbox default
local function rewardPlayer(src, reward)
    local player = exports.qbx_core:GetPlayer(src)
    if not player then return end
    if reward.money then player.Functions.AddMoney(reward.money.account, reward.money.amount, 'mission') end
    if reward.items then
        for _, it in ipairs(reward.items) do exports.ox_inventory:AddItem(src, it.name, it.count) end
    end
end
```

For **standalone**, replace the body with your server's own payout (or make rewards item-only via ox_inventory if present, or cosmetic). For QBCore/ESX, swap the player-get and money calls per `fivem-job-builder/references/frameworks-jobs.md`. `giveReward(instId)` calls this for each participant, splitting per `references/coop-and-state.md` if you want split rather than full rewards.

## 5. Sync with state bags

Push mission state to participants; don't make clients poll. State bags are the Qbox-idiomatic way and survive relevancy.

```lua
-- server: publish a sanitized view (no reward amounts, no completion logic)
local function syncMission(instId)
    local inst = active[instId]
    local view = {
        label = inst.def.label,
        objIndex = inst.objIndex,
        objective = inst.def.objectives[inst.objIndex] and {
            text = renderText(inst, inst.objIndex),          -- e.g. 'Eliminate the guards (3/5)'
            coords = inst.def.objectives[inst.objIndex].coords,
        } or nil,
    }
    for _, src in ipairs(inst.participants) do
        TriggerClientEvent('mission:sync', src, instId, view)
    end
end
```

Client uses the view to draw the current objective blip/marker and the text UI (`lib.showTextUI`). The blip/marker is created and removed client-side as the objective changes — and the engine cleanup also tells clients to clear them.

## 6. The single cleanup pattern

Every mission outcome routes through one cleanup. This is non-negotiable — orphaned spawns are the signature mission bug.

```lua
local function cleanupMission(instId)
    local inst = active[instId]; if not inst then return end
    -- delete every spawned entity the server owns
    for _, h in ipairs(inst.handles.peds)     do if DoesEntityExist(h) then DeleteEntity(h) end end
    for _, h in ipairs(inst.handles.vehicles) do if DoesEntityExist(h) then DeleteEntity(h) end end
    for _, h in ipairs(inst.handles.objects)  do if DoesEntityExist(h) then DeleteEntity(h) end end
    -- stop timers
    for _, t in pairs(inst.timers) do if t then t = nil end end
    -- tell participants to clear client-side blips/markers/textui/zones for this instance
    for _, src in ipairs(inst.participants) do TriggerClientEvent('mission:cleanup', src, instId) end
    active[instId] = nil
end
```

Also call cleanup on `onResourceStop` (loop all `active` instances) and remove a dropping player from `participants` on `playerDropped` (and fail/cleanup the instance if it empties or your join/leave policy says so — `coop-and-state.md`).

## 7. The trust boundary (restated)

Missions have *more steps* than jobs, so more places a cheater can poke. The rule is unchanged: the client may **request** an advance and **render** state; the server **validates and decides**. Concretely, the server never trusts the client for: which objective is active, whether a `goto`/`collect`/`kill` condition is met, kill counts, timer expiry, eligibility to start, or reward amounts. If you find yourself reading a completion or a count out of a client event payload and acting on it, that is the bug — re-derive it from server state instead. Bound every id/index the client sends against server config.
