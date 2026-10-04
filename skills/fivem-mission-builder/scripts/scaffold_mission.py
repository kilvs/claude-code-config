#!/usr/bin/env python3
"""
scaffold_mission.py — generate a runnable, server-authoritative FiveM mission/event resource.

Emits a complete resource (fxmanifest.lua, shared/missions.lua, server.lua, client.lua)
with the mission engine, one example mission (directed) or event (random), the
server-side state machine, group sync, server-authoritative completion + reward, and
the single cleanup function already wired. TODOs mark what you customize.

Usage:
    python scaffold_mission.py --name repo_car   --mode directed --framework qbox       --output ./resources
    python scaffold_mission.py --name gang_attack --mode random   --framework qbox       --output ./resources
    python scaffold_mission.py --name patrol      --mode directed --framework standalone --output ./resources

Modes:      directed (default), random
Frameworks: qbox (default), qbcore, esx, standalone

Output is runnable but intentionally minimal — fill the TODOs (coords, objective
targets, reward, dialogue). Never emits real keys or credentials.
"""
import argparse
import os
import sys
import textwrap

# ---- framework reward hook fragments ----------------------------------------
# Only the reward/identity touch differs. The engine is framework-agnostic.
FW = {
    "qbox": {
        "deps": ["qbx_core", "ox_lib", "ox_target", "ox_inventory"],
        "shared_init": "    '@ox_lib/init.lua',",
        "server_init": "",
        "get_player": "exports.qbx_core:GetPlayer(src)",
        "cid": "player.PlayerData.citizenid",
        "reward_body": (
            "    local player = exports.qbx_core:GetPlayer(src)\n"
            "    if not player then return end\n"
            "    if reward.money then player.Functions.AddMoney(reward.money.account, reward.money.amount, 'mission') end\n"
            "    if reward.items then for _, it in ipairs(reward.items) do exports.ox_inventory:AddItem(src, it.name, it.count) end end"
        ),
        "item_count": "exports.ox_inventory:GetItemCount(src, %s)",
        "notify": "lib.notify(src, { type = '%s', description = '%s' })",
    },
    "qbcore": {
        "deps": ["qb-core", "ox_lib", "ox_target", "ox_inventory"],
        "shared_init": "    '@ox_lib/init.lua',",
        "server_init": "local QBCore = exports['qb-core']:GetCoreObject()\n",
        "get_player": "QBCore.Functions.GetPlayer(src)",
        "cid": "player.PlayerData.citizenid",
        "reward_body": (
            "    local player = QBCore.Functions.GetPlayer(src)\n"
            "    if not player then return end\n"
            "    if reward.money then player.Functions.AddMoney(reward.money.account, reward.money.amount, 'mission') end\n"
            "    if reward.items then for _, it in ipairs(reward.items) do exports.ox_inventory:AddItem(src, it.name, it.count) end end"
        ),
        "item_count": "exports.ox_inventory:GetItemCount(src, %s)",
        "notify": "lib.notify(src, { type = '%s', description = '%s' })",
    },
    "esx": {
        "deps": ["es_extended", "ox_lib", "ox_target", "ox_inventory"],
        "shared_init": "    '@ox_lib/init.lua',",
        "server_init": "local ESX = exports['es_extended']:getSharedObject()\n",
        "get_player": "ESX.GetPlayerFromId(src)",
        "cid": "player.identifier",
        "reward_body": (
            "    local player = ESX.GetPlayerFromId(src)\n"
            "    if not player then return end\n"
            "    if reward.money then player.addAccountMoney(reward.money.account, reward.money.amount) end\n"
            "    if reward.items then for _, it in ipairs(reward.items) do exports.ox_inventory:AddItem(src, it.name, it.count) end end"
        ),
        "item_count": "exports.ox_inventory:GetItemCount(src, %s)",
        "notify": "TriggerClientEvent('esx:showNotification', src, '%s')",  # ignores type
    },
    "standalone": {
        "deps": ["ox_lib"],
        "shared_init": "    '@ox_lib/init.lua',",
        "server_init": "",
        "get_player": "{ src = src }",  # no framework player object
        "cid": "tostring(src)",         # use server id as the key when no framework
        "reward_body": (
            "    -- STANDALONE: no framework money. Implement your server's payout here,\n"
            "    -- or grant items via ox_inventory if present:\n"
            "    -- if reward.items then for _, it in ipairs(reward.items) do exports.ox_inventory:AddItem(src, it.name, it.count) end end\n"
            "    print(('[mission] reward to %d'):format(src))"
        ),
        "item_count": "0 --[[ standalone: wire ox_inventory or your own check for %s ]]",
        "notify": "TriggerClientEvent('chat:addMessage', src, { args = { 'Mission', '%s: %s' } })",
    },
}


def fxmanifest(name, fw):
    deps = "\n".join(f"    '{d}'," for d in FW[fw]["deps"])
    server_extra = "    '@oxmysql/lib/MySQL.lua',\n" if fw != "standalone" else ""
    return textwrap.dedent(f"""\
    fx_version 'cerulean'
    game 'gta5'
    lua54 'yes'

    name '{name}'
    description 'FiveM mission/event: {name} (scaffolded — server-authoritative)'
    author 'you'
    version '0.1.0'

    shared_scripts {{
    {FW[fw]["shared_init"]}
        'shared/missions.lua',
    }}

    client_scripts {{
        'client.lua',
    }}

    server_scripts {{
    {server_extra}    'server.lua',
    }}

    dependencies {{
    {deps}
    }}
    """).replace("\n    \n", "\n")


def shared_missions(name, mode):
    if mode == "directed":
        return textwrap.dedent(f"""\
        -- Mission definitions (data, not code). The engine in server.lua runs these.
        -- The client receives only a sanitized view (labels, current objective).
        Missions = Missions or {{}}

        Missions['{name}'] = {{
            id = '{name}',
            label = 'Example Mission',                 -- TODO
            coop = {{ min = 1, max = 2, progress = 'shared' }},
            cooldownMs = 300000,                        -- per-starter cooldown (5 min)
            objectives = {{
                {{ id = 'goto_a', type = 'goto',
                   coords = vec3(0.0, 0.0, 0.0), radius = 15.0,   -- TODO coords
                   text = 'Go to the location' }},
                {{ id = 'do_thing', type = 'interact',
                   coords = vec3(0.0, 0.0, 0.0), radius = 3.0,    -- TODO coords
                   text = 'Do the thing', timerMs = 60000 }},
                {{ id = 'return', type = 'goto',
                   coords = vec3(0.0, 0.0, 0.0), radius = 20.0,   -- TODO coords
                   text = 'Return' }},
            }},
            reward = {{ money = {{ account = 'cash', amount = 1200 }}, split = 'even' }},  -- TODO tune
        }}
        """)
    # random
    return textwrap.dedent(f"""\
        -- Event definitions (data). Same schema as missions plus scheduler fields.
        Events = Events or {{}}

        Events['{name}'] = {{
            id = '{name}',
            label = 'Example Event',                    -- TODO
            coop = {{ min = 1, max = 12, progress = 'shared' }},
            cooldownMs = 1800000,                       -- 30 min global re-arm
            maxConcurrent = 1,
            minPlayersOnline = 2,
            spawnChance = 0.5,
            joinRadius = 150.0,
            timeoutMs = 900000,                         -- 15 min to resolve
            locationPool = {{                            -- TODO real coords
                vec3(0.0, 0.0, 0.0),
                vec3(0.0, 0.0, 0.0),
            }},
            objectives = {{
                {{ id = 'clear', type = 'kill', count = 5,
                   text = 'Clear the hostiles (0/5)' }},   -- spawn delegated to fivem-lua-dev
                {{ id = 'grab', type = 'collect', item = 'loot', count = 1,
                   coords = vec3(0.0, 0.0, 0.0), radius = 4.0,
                   text = 'Grab the loot' }},
            }},
            reward = {{ money = {{ account = 'cash', amount = 3000 }}, split = 'contribution' }},
        }}
        """)


def server_lua(name, mode, fw):
    f = FW[fw]
    gp = f["get_player"]
    cid = f["cid"]
    if fw == "esx":
        notify_join = f["notify"] % "You joined the event."
    else:
        notify_join = f["notify"] % ("success" if fw == "qbox" or fw == "qbcore" else "info", "You joined the event.")

    header = textwrap.dedent(f"""\
    -- {name} — SERVER. The server owns mission state and decides every completion/reward.
    -- See references/mission-engine.md for the pattern this implements.
    {f["server_init"]}
    local active = {{}}      -- [instId] = state record
    local cooldowns = {{}}   -- [cid or eventId] = expiry ms

    -- ---- reward hook (swappable per framework / standalone) --------------------
    local function rewardPlayer(src, reward)
    {f["reward_body"]}
    end

    -- ---- helpers ---------------------------------------------------------------
    local function isParticipant(inst, src)
        for _, s in ipairs(inst.participants) do if s == src then return true end end
        return false
    end

    local function playerInMission(src)
        for _, inst in pairs(active) do if isParticipant(inst, src) then return true end end
        return false
    end

    local function syncMission(instId)
        local inst = active[instId]; if not inst then return end
        local obj = inst.def.objectives[inst.objIndex]
        local view = {{
            label = inst.def.label, objIndex = inst.objIndex,
            objective = obj and {{ id = obj.id, text = obj.text, coords = obj.coords, radius = obj.radius }} or nil,
        }}
        for _, src in ipairs(inst.participants) do
            TriggerClientEvent('mission:sync', src, instId, view)
        end
    end

    -- ---- spawning hand-off -----------------------------------------------------
    -- Objectives needing entities (kill/escort/defend) spawn them HERE, recording
    -- handles in inst.handles so cleanup is reliable. The actual CreatePed / tasks /
    -- relationship groups come from the fivem-lua-dev skill (world-entities.md).
    local function spawnForObjective(instId, idx)
        local inst = active[instId]; if not inst then return end
        local obj = inst.def.objectives[idx]; if not obj then return end
        -- TODO: if obj.type == 'kill' then spawn obj.count enemies (via fivem-lua-dev),
        --       push handles into inst.handles.peds, and credit their deaths server-side:
        --         inst.progress[obj.id] = (inst.progress[obj.id] or 0) + 1; syncMission(instId)
        if obj.timerMs then
            inst.timers[obj.id] = SetTimeout(obj.timerMs, function()
                if active[instId] and active[instId].objIndex == idx then
                    failMission(instId, 'timeout')
                end
            end)
        end
    end

    -- ---- the single cleanup ----------------------------------------------------
    function cleanupMission(instId)
        local inst = active[instId]; if not inst then return end
        for _, h in ipairs(inst.handles.peds)     do if DoesEntityExist(h) then DeleteEntity(h) end end
        for _, h in ipairs(inst.handles.vehicles) do if DoesEntityExist(h) then DeleteEntity(h) end end
        for _, h in ipairs(inst.handles.objects)  do if DoesEntityExist(h) then DeleteEntity(h) end end
        for _, src in ipairs(inst.participants) do TriggerClientEvent('mission:cleanup', src, instId) end
        active[instId] = nil
    end

    function failMission(instId, reason)
        local inst = active[instId]; if not inst then return end
        for _, src in ipairs(inst.participants) do
            {(f["notify"] % ("error", "Mission failed.")) if fw not in ("esx","standalone") else (f["notify"] % ("Mission failed.")) if fw == "esx" else (f["notify"] % ("error", "Mission failed."))}
        end
        cleanupMission(instId)
    end

    -- ---- reward + advance ------------------------------------------------------
    local function giveReward(instId)
        local inst = active[instId]; local r = inst.def.reward
        if r.split == 'even' and r.money then
            local per = math.floor(r.money.amount / math.max(1, #inst.participants))
            for _, src in ipairs(inst.participants) do
                rewardPlayer(src, {{ money = {{ account = r.money.account, amount = per }}, items = r.items }})
            end
        else
            for _, src in ipairs(inst.participants) do rewardPlayer(src, r) end
        end
    end

    local function advance(instId)
        local inst = active[instId]; if not inst then return end
        local doneObj = inst.def.objectives[inst.objIndex]
        if doneObj and inst.timers[doneObj.id] then inst.timers[doneObj.id] = nil end
        inst.objIndex = inst.objIndex + 1
        if inst.objIndex > #inst.def.objectives then
            giveReward(instId)
            cleanupMission(instId)
        else
            spawnForObjective(instId, inst.objIndex)
            syncMission(instId)
        end
    end

    -- ---- server-authoritative completion check ---------------------------------
    local function tryComplete(instId, src, objId)
        local inst = active[instId]; if not inst then return false end
        if not isParticipant(inst, src) then return false end
        local obj = inst.def.objectives[inst.objIndex]
        if not obj or obj.id ~= objId then return false end       -- must be on THIS step
        if obj.type == 'goto' then
            if #(GetEntityCoords(GetPlayerPed(src)) - obj.coords) > (obj.radius or 5.0) then return false end
        elseif obj.type == 'interact' then
            if obj.coords and #(GetEntityCoords(GetPlayerPed(src)) - obj.coords) > (obj.radius or 3.0) then return false end
        elseif obj.type == 'collect' then
            if {f["item_count"] % "obj.item"} < (obj.count or 1) then return false end
        elseif obj.type == 'kill' then
            if (inst.progress[obj.id] or 0) < (obj.count or 1) then return false end
        end
        advance(instId)
        return true
    end

    -- client requests an advance; server validates. Bound the ids.
    lib.callback.register('mission:complete', function(src, instId, objId)
        if type(instId) ~= 'string' or type(objId) ~= 'string' then return false end
        return tryComplete(instId, src, objId)
    end)

    -- ---- start (shared) --------------------------------------------------------
    local function startMission(def, starterSrc, party)
        local instId = ('%s:%d'):format(def.id, GetGameTimer())
        active[instId] = {{
            def = def, objIndex = 1, progress = {{}},
            handles = {{ peds = {{}}, vehicles = {{}}, objects = {{}} }},
            participants = party or {{ starterSrc }}, timers = {{}},
        }}
        spawnForObjective(instId, 1)
        syncMission(instId)
        return instId
    end

    AddEventHandler('playerDropped', function()
        local src = source
        for instId, inst in pairs(active) do
            for i, s in ipairs(inst.participants) do
                if s == src then table.remove(inst.participants, i) break end
            end
            if #inst.participants == 0 then
                cleanupMission(instId)
            else
                syncMission(instId)
            end
        end
    end)

    AddEventHandler('onResourceStop', function(res)
        if res ~= GetCurrentResourceName() then return end
        for instId in pairs(active) do cleanupMission(instId) end
    end)
    """)

    if mode == "directed":
        body = textwrap.dedent(f"""\

        -- ---- DIRECTED: a player starts it via a trigger ----------------------------
        RegisterNetEvent('mission:requestStart', function(missionId)
            local src = source
            local def = Missions[missionId]
            if not def then return end                            -- bound input
            local player = {gp}
            if not player then return end
            local key = {cid}
            if cooldowns[key] and GetGameTimer() < cooldowns[key] then
                {(f["notify"] % ("error", "Not available yet.")) if fw not in ("esx","standalone") else (f["notify"] % ("Not available yet.")) if fw == "esx" else (f["notify"] % ("error", "Not available yet."))}
                return
            end
            if playerInMission(src) then return end               -- one at a time
            cooldowns[key] = GetGameTimer() + (def.cooldownMs or 0)
            -- TODO: assemble a co-op party here if def.coop.max > 1 (coop-and-state.md)
            startMission(def, src, {{ src }})
        end)
        """)
    else:  # random
        body = textwrap.dedent(f"""\

        -- ---- RANDOM EVENT: the server scheduler starts it --------------------------
        local activeEvents = 0
        local lastSpawn = {{}}   -- [eventId] = ms

        local function spawnEvent(def)
            local loc = def.locationPool[math.random(#def.locationPool)]
            local instId = startMission(def, nil, {{}})
            local inst = active[instId]
            inst.eventLoc, inst.open = loc, true
            for _, pid in ipairs(GetPlayers()) do
                TriggerClientEvent('event:announce', tonumber(pid), instId, def.label, loc)
            end
            activeEvents = activeEvents + 1
            inst.timers['__timeout'] = SetTimeout(def.timeoutMs, function()
                if active[instId] then activeEvents = activeEvents - 1; failMission(instId, 'timeout') end
            end)
        end

        RegisterNetEvent('event:join', function(instId)
            local src = source
            if type(instId) ~= 'string' then return end
            local inst = active[instId]
            if not inst or not inst.open then return end
            if #(GetEntityCoords(GetPlayerPed(src)) - inst.eventLoc) > inst.def.joinRadius then return end
            if #inst.participants >= inst.def.coop.max then return end
            if isParticipant(inst, src) then return end
            inst.participants[#inst.participants + 1] = src
            syncMission(instId)
            {notify_join}
        end)

        CreateThread(function()
            local def = Events['{name}']
            while true do
                Wait(60000)
                local now = GetGameTimer()
                if activeEvents < def.maxConcurrent
                   and (not lastSpawn[def.id] or now - lastSpawn[def.id] >= def.cooldownMs)
                   and #GetPlayers() >= def.minPlayersOnline
                   and math.random() < def.spawnChance then
                    spawnEvent(def)
                    lastSpawn[def.id] = now
                end
            end
        end)
        """)

    return header + body


def client_lua(name, mode, fw):
    common = textwrap.dedent("""\
    -- __NAME__ — CLIENT. UX only: draws the current objective and requests advances.
    -- The server decides every completion. Nothing here authorizes a reward.
    local current = {}   -- [instId] = { blip = ..., objId = ... }

    local function clearInstance(instId)
        local c = current[instId]
        if not c then return end
        if c.blip and DoesBlipExist(c.blip) then RemoveBlip(c.blip) end
        lib.hideTextUI()
        current[instId] = nil
    end

    RegisterNetEvent('mission:sync', function(instId, view)
        clearInstance(instId)
        if not view.objective then return end
        local c = { objId = view.objective.id }
        if view.objective.coords then
            local co = view.objective.coords
            c.blip = AddBlipForCoord(co.x, co.y, co.z)
            SetBlipColour(c.blip, 5); SetBlipRoute(c.blip, true)
            BeginTextCommandSetBlipName('STRING')
            AddTextComponentSubstringPlayerName(view.label)
            EndTextCommandSetBlipName(c.blip)
        end
        current[instId] = c
        lib.showTextUI(view.objective.text or view.label)
    end)

    RegisterNetEvent('mission:cleanup', function(instId)
        clearInstance(instId)
    end)
    """).replace("__NAME__", name)

    # a generic "attempt current objective" interaction
    attempt = textwrap.dedent("""\

    -- Attempt to complete the current objective (e.g. on reaching a goto, or interacting).
    -- For 'goto' you might poll distance; for 'interact' put this behind an ox_target/progressBar.
    local function attemptCurrent(instId)
        local c = current[instId]; if not c then return end
        local ok = lib.callback.await('mission:complete', false, instId, c.objId)
        -- server returns true only if its own checks pass; UX reacts to ok
    end

    -- Example loop: tick while any mission is active. Replace with ox_target on the
    -- objective, or an automatic distance check for 'goto'. Kept minimal here.
    CreateThread(function()
        while true do
            local wait = 1000
            for instId, c in pairs(current) do
                wait = 500
                -- TODO: detect arrival / interaction, then attemptCurrent(instId)
            end
            Wait(wait)
        end
    end)
    """)

    if mode == "random":
        join = textwrap.dedent("""\

        RegisterNetEvent('event:announce', function(instId, label, loc)
            local blip = AddBlipForCoord(loc.x, loc.y, loc.z)
            SetBlipSprite(blip, 161); SetBlipColour(blip, 1); SetBlipScale(blip, 1.1)
            BeginTextCommandSetBlipName('STRING'); AddTextComponentSubstringPlayerName(label); EndTextCommandSetBlipName(blip)
            lib.notify({ description = label .. ' reported in the area' })
            -- TODO: when the player is within joinRadius, let them opt in:
            --   TriggerServerEvent('event:join', instId)
            SetTimeout(900000, function() if DoesBlipExist(blip) then RemoveBlip(blip) end end)
        end)
        """)
        return common + attempt + join
    return common + attempt


def main():
    ap = argparse.ArgumentParser(description="Scaffold a server-authoritative FiveM mission/event resource.")
    ap.add_argument("--name", required=True, help="mission/event + resource name (lowercase, no spaces)")
    ap.add_argument("--mode", default="directed", choices=["directed", "random"])
    ap.add_argument("--framework", default="qbox", choices=["qbox", "qbcore", "esx", "standalone"])
    ap.add_argument("--output", required=True, help="output directory (resource folder created inside)")
    args = ap.parse_args()

    name = args.name.strip().lower().replace(" ", "_")
    if not name:
        print("error: --name is empty", file=sys.stderr); sys.exit(1)

    out = os.path.join(args.output, name)
    os.makedirs(os.path.join(out, "shared"), exist_ok=True)

    files = {
        "fxmanifest.lua":      fxmanifest(name, args.framework),
        "shared/missions.lua": shared_missions(name, args.mode),
        "server.lua":          server_lua(name, args.mode, args.framework),
        "client.lua":          client_lua(name, args.mode, args.framework),
    }
    for fname, content in files.items():
        with open(os.path.join(out, fname), "w") as fh:
            fh.write(content)

    print(f"Scaffolded '{name}' ({args.mode}, {args.framework}) -> {out}")
    print("Files: " + ", ".join(files.keys()))
    print()
    print("Next:")
    print("  1. Fill the TODOs in shared/missions.lua (coords, objectives, reward).")
    print("  2. Wire entity spawns in server.lua spawnForObjective() using the fivem-lua-dev "
          "spawning patterns; push handles into inst.handles so cleanup works.")
    print("  3. For 'kill' objectives, credit deaths server-side (see the TODO in spawnForObjective).")
    print(f"  4. Add to server.cfg: ensure {name}")
    print("  5. Load order: oxmysql -> ox_lib -> ox_inventory -> framework -> ox_target -> " + name)
    print("  6. Test: confirm a client calling mission:complete out of order / from far away "
          "gets false, and that abandoning the mission leaves no orphaned entities.")


if __name__ == "__main__":
    main()
