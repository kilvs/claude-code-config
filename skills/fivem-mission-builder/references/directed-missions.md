# Directed / Narrated Missions — authored sequences with a start, beats, and an end

An authored experience the player deliberately starts and works through: story missions, quests, tutorials, scripted scenarios. Runs on the engine (`mission-engine.md` — read that first); this file is the *starting*, the *pacing beats*, and *branching*.

## The shape

1. A **start trigger** the player activates (NPC giver, item, command, zone).
2. Server checks **eligibility** (cooldown, not already in a mission, party size/job/level if required) and starts the instance.
3. The engine drives the **objective sequence**, with **dialogue/text beats**, optional **per-objective timers**, and **fail conditions** between or during objectives.
4. **Branching** (optional): a choice or outcome picks which objective runs next.
5. **End**: success → reward + cleanup; fail/abandon → cleanup.

## Start triggers

All of these end in a single server event (`mission:requestStart`) that validates eligibility before `startMission`. The trigger is just UX; the server decides.

**NPC giver** — spawn a giver ped (via `fivem-lua-dev` spawning), put an `ox_target` option on it:
```lua
exports.ox_target:addLocalEntity(giverPed, {
    { name = 'start_raid', label = 'Ask about work', icon = 'fa-solid fa-comment',
      onSelect = function() TriggerServerEvent('mission:requestStart', 'warehouse_raid') end },
})
```

**Item** — using a usable item (`ox_inventory` item with a server `use` callback) starts it. Validate the player holds it server-side; consume if it's a one-shot.

**Command** — `RegisterCommand('startraid', ...)` on the client that fires the request; or a server command for admin-run scenarios. Server still gates eligibility.

**Zone** — `lib.zones`/`ox_target` box at a location; entering or interacting fires the request.

Server side of every trigger:
```lua
RegisterNetEvent('mission:requestStart', function(missionId)
    local src = source
    if not Missions[missionId] then return end                 -- bound input
    local player = exports.qbx_core:GetPlayer(src)
    if not player then return end
    local cid = player.PlayerData.citizenid
    if cooldowns[cid] and GetGameTimer() < cooldowns[cid] then
        return lib.notify(src, { type='error', description='You can\'t do that yet.' })
    end
    if playerInMission(src) then return end                    -- one at a time
    -- party assembly for co-op happens here (coop-and-state.md)
    startMission(missionId, src, assembleParty(src, Missions[missionId].coop))
end)
```

## Dialogue / text beats

Narration between objectives. Keep it client-rendered, server-triggered (the server tells the client "show beat N" as part of sync or a dedicated event).

- **Persistent objective text**: `lib.showTextUI('~b~Get to the warehouse')` while an objective is active; `lib.hideTextUI()` when it changes.
- **A spoken/cutscene-ish beat**: a sequence of `lib.notify` lines on a timer, or an `lib.alertDialog` for a decision, or a subtitle via `BeginTextCommandPrint`/`EndTextCommandPrint`. Keep beats short; FiveM has no real cutscene system beyond camera natives.
- **Camera moments** (optional, advanced): `SetCamCoord`/`PointCamAtCoord` for a brief framed shot. This is presentation only — done client-side, it never authorizes anything.

A beat is flavour. It never advances the mission by itself — the *objective* completion (server-validated) does.

## Per-objective timers and fail conditions

Defined in the objective data (`mission-engine.md` §1). The **server owns the clock**:

```lua
-- when objective with timerMs starts, server sets a timer; on expiry it fails the instance
inst.timers[objId] = SetTimeout(obj.timerMs, function()
    if active[instId] and active[instId].objIndex == idx then
        failMission(instId, 'timeout')   -- routes to cleanup
    end
end)
```

Common fail conditions, all server-judged: timer expiry, escort target destroyed, all participants dead/down, player left the mission zone for too long, required NPC killed. `failMission` notifies participants, runs `onFail`, and calls `cleanupMission`.

## Branching

Branching = the next objective index depends on a choice or outcome. Keep the branch decision server-side.

```lua
-- objective of type 'interact' offering a choice via lib.alertDialog on the client,
-- whose RESULT is sent to the server, which validates and sets the branch:
objectives = {
    [3] = { id='choice', type='interact', coords=..., branches = { stealth='go_quiet', loud='go_loud' } },
}
-- server, on the validated interact:
local pick = payload.choice                       -- 'stealth' | 'loud' (bounded set)
local nextId = inst.def.objectives[inst.objIndex].branches[pick]
if not nextId then return false end               -- reject unknown choice
setNextObjectiveById(inst, nextId)
```

Branches converge by pointing different paths at the same later objective id. Keep the graph small; deep branching is hard to test and easy to leak state in.

## Solo vs fixed-party

- **Solo**: `participants = { src }`, progress is trivially per-player.
- **Fixed co-op party**: assembled at start (invite/accept, or "everyone in the zone"), `participants` is the group, progress is usually `shared`. Join/leave policy and reward split in `coop-and-state.md`. Directed missions typically *lock* the party at start (no mid-mission joins) — simpler and avoids backfill complexity.

## Worked example — a small 3-step mission (server, abridged)

```lua
Missions['repo_car'] = {
    id='repo_car', label='Repossess the Car',
    coop = { min=1, max=2, progress='shared' }, cooldownMs=300000,
    objectives = {
        { id='goto_car', type='goto', coords=vec3(1,2,3), radius=15.0, text='Find the car' },
        { id='hotwire',  type='interact', coords=vec3(1,2,3), radius=3.0, text='Hotwire it', timerMs=60000 },
        { id='return',   type='goto', coords=vec3(4,5,6), radius=20.0, text='Return it to the lot' },
    },
    reward = { money = { account='cash', amount=1200 } },
}

-- start trigger: NPC giver fires mission:requestStart 'repo_car'
-- objective 1 goto: server checks distance on a client 'reached' request
-- objective 2 interact: client runs lib.progressBar (8s) at the car, then requests complete;
--   server verifies player is within radius AND the objective is current AND timer not expired
-- objective 3 goto: server checks distance at the lot
-- finish: rewardPlayer for each participant, cleanupMission
```

Every step's completion is decided by the server from its own state — the client requests, never asserts. The progress bars and text UI are presentation. This is the whole archetype; bigger missions are more objectives of the same types plus beats and the occasional branch.
