# Repeatable Random Events — ambient, server-spawned, opt-in

An event the *server* spawns on a cooldown somewhere on the map, announces, and any eligible player can join until it resolves or times out — then it re-arms. Roaming heists, gang attacks, supply drops, bounties, hostage situations. Runs on the same engine (`mission-engine.md` — read first); this file is the *scheduler*, the *opt-in*, and the *re-arm/anti-farm*.

## How it differs from a directed mission

| | Directed mission | Random event |
|---|---|---|
| Who starts it | a player (trigger) | the **server scheduler** |
| Who joins | a fixed party at start | any eligible player, often mid-event |
| Location | fixed in the mission def | picked from a **location pool** |
| Lifecycle | start → finish → cooldown per player | spawn → open window → resolve/timeout → **global cooldown** → re-arm |
| Progress | usually shared in a small party | shared across whoever opted in |

The engine, objectives, server-authoritative completion, and cleanup are identical. Only the launcher and the participation model change.

## The server scheduler

A server loop arms events on a cooldown, respecting a max-concurrent cap. Keep it cheap — it ticks slowly.

```lua
-- server
local EventDef = Events['gang_attack']
local lastSpawn = 0
local activeEvents = 0

CreateThread(function()
    while true do
        Wait(60000)                                          -- check once a minute; cheap
        local now = GetGameTimer()
        if activeEvents < EventDef.maxConcurrent
           and now - lastSpawn >= EventDef.cooldownMs
           and #GetPlayers() >= EventDef.minPlayersOnline then
            if math.random() < EventDef.spawnChance then      -- some randomness so it's not clockwork
                spawnEvent(EventDef)
                lastSpawn = now
            end
        end
    end
end)
```

`Events['gang_attack']` is a mission def (same schema, `mission-engine.md` §1) plus event fields:
```lua
Events['gang_attack'] = {
    id='gang_attack', label='Gang Attack',
    coop = { min=1, max=12, progress='shared' },             -- many can join
    cooldownMs = 1800000,                                    -- 30 min global re-arm
    maxConcurrent = 1,
    minPlayersOnline = 2,
    spawnChance = 0.5,
    locationPool = { vec3(1,2,3), vec3(4,5,6), vec3(7,8,9) }, -- server picks one
    joinRadius = 150.0,                                       -- how close to opt in
    timeoutMs = 900000,                                       -- 15 min to resolve or it despawns
    objectives = { --[[ kill/defend/capture etc. ]] },
    reward = { money = { account='cash', amount=3000 } },
}
```

## Spawn, announce, open the join window

```lua
local function spawnEvent(def)
    local loc = def.locationPool[math.random(#def.locationPool)]
    local instId = startMission(def.id, nil, {})             -- no starter, empty party to begin
    active[instId].eventLoc = loc
    active[instId].open = true
    -- announce to everyone (or to players within a region) with a map blip
    for _, pid in ipairs(GetPlayers()) do
        TriggerClientEvent('event:announce', tonumber(pid), instId, def.label, loc)
    end
    activeEvents = activeEvents + 1
    -- timeout: if not resolved, despawn and re-arm
    active[instId].timers.timeout = SetTimeout(def.timeoutMs, function()
        if active[instId] then failEvent(instId, 'timeout') end
    end)
end
```

Client `event:announce` draws a map blip at `loc` and shows a notification ("Gang activity reported in the area"). Blur the blip a little if you want players to search.

## Opt-in and eligibility

Players join by approaching and confirming — the server checks they're actually near and eligible, then adds them to `participants`.

```lua
RegisterNetEvent('event:join', function(instId)
    local src = source
    local inst = active[instId]
    if not inst or not inst.open then return end             -- event over or unknown
    if #(GetEntityCoords(GetPlayerPed(src)) - inst.eventLoc) > inst.def.joinRadius then return end
    if #inst.participants >= inst.def.coop.max then
        return lib.notify(src, { type='error', description='Too many people on this already.' })
    end
    if isParticipant(inst, src) then return end
    inst.participants[#inst.participants+1] = src
    syncMission(instId)                                       -- newcomer now sees objective state
    lib.notify(src, { type='success', description='You joined the event.' })
end)
```

Joining mid-event is the norm here (unlike directed missions). Because progress is `shared` and server-owned, a late joiner just picks up the current objective — no backfill problem.

## Resolve, re-arm, despawn

- **Resolve (success)**: last objective completes → reward participants (split or full, `coop-and-state.md`) → `cleanupMission` → `activeEvents -= 1`. The global `cooldownMs` is enforced by the scheduler (`lastSpawn`), so it won't immediately respawn.
- **Timeout / fail**: `failEvent` notifies, cleans up, decrements `activeEvents`. Re-arm waits the cooldown.
- **No participants**: if the join window passes with nobody in range, you can despawn early to save resources (optional grace period).

## Difficulty / reward scaling and anti-farm

Random events get farmed if reward is flat and the loop is tight. Scale server-side:

- **Scale to participant count**: more players → more/stronger enemies (spawn waves keyed to `#participants`), so it's not trivially soloable when busy nor impossible when empty.
- **Scale reward to contribution**, not just presence: credit players who actually did damage / completed steps (server-tracked), so AFK leeching pays little. See reward splitting in `coop-and-state.md`.
- **Global cooldown** (already in the scheduler) bounds how often the server economy absorbs the payout.
- **Cap concurrency** (`maxConcurrent`) so the map isn't blanketed in events.
- Re-test the exploit path: confirm a client can't fire `event:join` from across the map, can't trigger `spawnEvent`, and can't claim objective completion (the engine's server checks cover this).

## Worked example — roaming heist (flow)

1. Scheduler arms `armored_truck` heist every ~25 min, 1 concurrent, picks a route point from the pool, needs 2+ players online.
2. Spawns the truck + guard peds (delegated to `fivem-lua-dev`), announces a blip region.
3. Players approach and `event:join` (server distance-checks). Objective 1 (`kill` guards, count scaled to participants) — kills server-credited. Objective 2 (`interact` to crack the truck, `lib.skillCheck`, server-validated by location). Objective 3 (`collect` the cash items into inventory).
4. Police get alerted on the crack (reuse the dispatch pattern from `fivem-job-builder/illegal-jobs.md` if it's a crime).
5. Resolve → split reward by contribution → cleanup → 25-min cooldown before the scheduler can arm it again.

Same engine as a directed mission; the scheduler and opt-in are the only new parts.
