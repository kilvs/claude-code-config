#!/usr/bin/env python3
"""
scaffold_job.py — generate a runnable, server-authoritative FiveM job resource.

Emits a complete job resource (fxmanifest.lua, config.lua, client.lua, server.lua)
wired for the chosen archetype and framework, with the payout already validated
server-side and clearly-marked TODOs for the parts you customize.

Usage:
    python scaffold_job.py --name mechanic --archetype legal --framework qbox --output ./resources
    python scaffold_job.py --name dealer   --archetype illegal --framework qbox --output ./resources
    python scaffold_job.py --name police   --archetype whitelisted --framework qbox --output ./resources

Frameworks: qbox (default), qbcore, esx
Archetypes: legal (default), illegal, whitelisted

The output is runnable but intentionally minimal — fill the TODOs (coords, pay,
items, grades) for your server. It NEVER emits real keys or credentials.
"""
import argparse
import os
import sys
import textwrap

# ---- framework API fragments -------------------------------------------------
# Only the bits that differ between frameworks. Structure stays identical.
FW = {
    "qbox": {
        "get_player": "exports.qbx_core:GetPlayer(src)",
        "job_name":   "player.PlayerData.job.name",
        "grade_lvl":  "player.PlayerData.job.grade.level",
        "on_duty":    "player.PlayerData.job.onduty",
        "is_boss":    "player.PlayerData.job.isboss",
        "add_money":  "player.Functions.AddMoney('cash', %s, '%s')",
        "set_duty":   "player.Functions.SetJobDuty(not player.PlayerData.job.onduty)",
        "item_count": "exports.ox_inventory:GetItemCount(src, %s)",
        "add_item":   "exports.ox_inventory:AddItem(src, %s, %s)",
        "rm_item":    "exports.ox_inventory:RemoveItem(src, %s, %s)",
        "notify_sv":  "lib.notify(src, { type = '%s', description = %s })",
        "deps":       ["qbx_core", "ox_lib", "ox_target", "ox_inventory"],
    },
    "qbcore": {
        "get_player": "QBCore.Functions.GetPlayer(src)",
        "job_name":   "player.PlayerData.job.name",
        "grade_lvl":  "player.PlayerData.job.grade.level",
        "on_duty":    "player.PlayerData.job.onduty",
        "is_boss":    "player.PlayerData.job.isboss",
        "add_money":  "player.Functions.AddMoney('cash', %s, '%s')",
        "set_duty":   "player.Functions.SetJobDuty(not player.PlayerData.job.onduty)",
        "item_count": "exports.ox_inventory:GetItemCount(src, %s)",
        "add_item":   "exports.ox_inventory:AddItem(src, %s, %s)",
        "rm_item":    "exports.ox_inventory:RemoveItem(src, %s, %s)",
        "notify_sv":  "lib.notify(src, { type = '%s', description = %s })",
        "deps":       ["qb-core", "ox_lib", "ox_target", "ox_inventory"],
    },
    "esx": {
        "get_player": "ESX.GetPlayerFromId(src)",
        "job_name":   "player.getJob().name",
        "grade_lvl":  "player.getJob().grade",
        "on_duty":    "player.getJob().onDuty",
        "is_boss":    "(player.getJob().grade_name == 'boss')",
        "add_money":  "player.addAccountMoney('money', %s) --[[ %s ]]",
        "set_duty":   "-- ESX duty handling depends on your policejob/ambulance resource",
        "item_count": "exports.ox_inventory:GetItemCount(src, %s)",
        "add_item":   "exports.ox_inventory:AddItem(src, %s, %s)",
        "rm_item":    "exports.ox_inventory:RemoveItem(src, %s, %s)",
        "notify_sv":  "TriggerClientEvent('esx:showNotification', src, %s)",
        "deps":       ["es_extended", "ox_lib", "ox_target", "ox_inventory"],
    },
}


def fxmanifest(name, fw):
    deps = "\n".join(f"    '{d}'," for d in FW[fw]["deps"])
    esx_init = ""
    return textwrap.dedent(f"""\
    fx_version 'cerulean'
    game 'gta5'
    lua54 'yes'

    name '{name}'
    description 'Custom job: {name} (scaffolded — server-authoritative)'
    author 'you'
    version '0.1.0'

    shared_scripts {{
        '@ox_lib/init.lua',
        'config.lua',
    }}

    client_scripts {{
        'client.lua',
    }}

    server_scripts {{
        '@oxmysql/lib/MySQL.lua',
        'server.lua',
    }}

    dependencies {{
{deps}
    }}
    """)


def config_lua(name, archetype):
    base = textwrap.dedent(f"""\
    Config = {{}}

    -- The internal job name. MUST match the job registered in your framework's
    -- job list (qbx_core/shared/jobs.lua etc). See references/job-registration.md
    Config.Job = '{name}'

    -- Pay is decided BY THE SERVER, never sent by the client.
    -- Balance to a target $/hr: pay = hourly * (loopSeconds / 3600). See job-economy.md.
    Config.Pay = 250          -- TODO: tune

    Config.PayCooldownMs = 3000   -- min ms between paid completions (anti-spam)
    """)
    if archetype == "legal":
        base += textwrap.dedent("""
        -- TODO: set your real coords. Server uses these to verify the player is actually there.
        Config.Pickup  = vec3(0.0, 0.0, 0.0)
        Config.Dropoff = vec3(0.0, 0.0, 0.0)
        Config.RequiredItem = nil   -- e.g. 'package' to require an item at dropoff; nil = flag-based
        """)
    elif archetype == "illegal":
        base += textwrap.dedent("""
        Config.SellZone   = vec3(0.0, 0.0, 0.0)   -- TODO
        Config.SellItem   = 'processed_goods'      -- TODO: must exist in ox_inventory/data/items.lua
        Config.BustChance = 0.15                   -- chance a sale goes bad (lose goods + alert)
        Config.AlertChance = 0.5                   -- chance on-duty police get a (blurred) blip
        Config.SaleDecay  = 0.1                    -- diminishing returns per consecutive sale
        Config.MinSaleMult = 0.3                   -- price floor as a fraction of base
        """)
    elif archetype == "whitelisted":
        base += textwrap.dedent("""
        Config.Station = vec3(0.0, 0.0, 0.0)   -- duty toggle point. TODO
        -- Minimum grade level required for each privileged action (server-checked).
        Config.Access = {
            armory  = 1,
            boss    = 4,
        }
        Config.MaxGrade = 4   -- bound for boss set-grade input
        """)
    return base


def client_lua(name, archetype, fw):
    job = name
    if archetype == "legal":
        return textwrap.dedent(f"""\
        -- {name} (legal loop) — client is UX only. The server authorizes every payout.
        local hasItem = false   -- local flag for UX; server is the source of truth

        CreateThread(function()
            exports.ox_target:addBoxZone({{
                coords = Config.Pickup, size = vec3(2.0, 2.0, 2.0), rotation = 0.0,
                options = {{ {{
                    name = '{job}_pickup', label = 'Start task', icon = 'fa-solid fa-box',
                    groups = {{ ['{job}'] = 0 }},
                    onSelect = function()
                        if hasItem then return lib.notify({{ type = 'error', description = 'Already working' }}) end
                        if lib.progressBar({{ duration = 3000, label = 'Working...', disable = {{ move = true }} }}) then
                            local ok = lib.callback.await('{job}:pickup', false)
                            if ok then hasItem = true; lib.notify({{ type = 'success', description = 'Now go finish it.' }}) end
                        end
                    end,
                }} }},
            }})

            exports.ox_target:addBoxZone({{
                coords = Config.Dropoff, size = vec3(2.0, 2.0, 2.0), rotation = 0.0,
                options = {{ {{
                    name = '{job}_dropoff', label = 'Finish task', icon = 'fa-solid fa-flag-checkered',
                    groups = {{ ['{job}'] = 0 }},
                    onSelect = function()
                        local ok = lib.callback.await('{job}:dropoff', false)
                        if ok then hasItem = false end
                    end,
                }} }},
            }})
        end)
        """)
    if archetype == "illegal":
        return textwrap.dedent(f"""\
        -- {name} (illegal) — client requests a sale; the server rolls risk and pays.
        CreateThread(function()
            exports.ox_target:addBoxZone({{
                coords = Config.SellZone, size = vec3(3.0, 3.0, 3.0), rotation = 0.0,
                options = {{ {{
                    name = '{job}_sell', label = 'Sell goods', icon = 'fa-solid fa-sack-dollar',
                    groups = {{ ['{job}'] = 0 }},
                    onSelect = function()
                        if lib.progressBar({{ duration = 2500, label = 'Making the deal...', disable = {{ move = true }} }}) then
                            lib.callback.await('{job}:sell', false)
                        end
                    end,
                }} }},
            }})
        end)

        -- police alert receiver (blurred coords)
        RegisterNetEvent('{job}:copBlip', function(coords)
            local blip = AddBlipForCoord(coords.x, coords.y, coords.z)
            SetBlipSprite(blip, 161); SetBlipColour(blip, 1); SetBlipScale(blip, 1.2)
            SetBlipAsShortRange(blip, true)
            BeginTextCommandSetBlipName('STRING'); AddTextComponentSubstringPlayerName('Suspicious activity'); EndTextCommandSetBlipName(blip)
            SetTimeout(60000, function() RemoveBlip(blip) end)
        end)
        """)
    # whitelisted
    return textwrap.dedent(f"""\
    -- {name} (whitelisted) — duty toggle + an example grade-gated action.
    -- Menus/targets here are UX; the server re-checks job, grade, and duty on every action.
    CreateThread(function()
        exports.ox_target:addBoxZone({{
            coords = Config.Station, size = vec3(2.0, 2.0, 2.0), rotation = 0.0,
            options = {{
                {{
                    name = '{job}_duty', label = 'Toggle duty', icon = 'fa-solid fa-clipboard-check',
                    groups = {{ ['{job}'] = 0 }},
                    onSelect = function() TriggerServerEvent('{job}:toggleDuty') end,
                }},
                {{
                    name = '{job}_armory', label = 'Open armory', icon = 'fa-solid fa-gun',
                    groups = {{ ['{job}'] = 0 }},
                    onSelect = function() TriggerServerEvent('{job}:armory') end,
                }},
            }},
        }})
    end)

    RegisterNetEvent('{job}:dutyChanged', function(onDuty)
        lib.notify({{ type = onDuty and 'success' or 'inform',
                     description = onDuty and 'You are now ON duty.' or 'You are now OFF duty.' }})
    end)
    """)


def server_lua(name, archetype, fw):
    job = name
    gp = FW[fw]["get_player"]
    jn = FW[fw]["job_name"]
    gl = FW[fw]["grade_lvl"]
    od = FW[fw]["on_duty"]
    add_money = FW[fw]["add_money"]
    item_count = FW[fw]["item_count"]
    add_item = FW[fw]["add_item"]
    rm_item = FW[fw]["rm_item"]
    notify = FW[fw]["notify_sv"]

    header = textwrap.dedent(f"""\
    -- {name} — SERVER. This file is the authority. The client never decides a reward.
    -- See references/job-economy.md for the validation checklist this implements.
    """)
    if fw == "qbcore":
        header += "local QBCore = exports['qb-core']:GetCoreObject()\n"
    elif fw == "esx":
        header += "local ESX = exports['es_extended']:getSharedObject()\n"
    header += "\n"

    if archetype == "legal":
        notify_call = notify % ("success", "('Done. +$%d'):format(Config.Pay)") if fw != "esx" \
            else notify % "('Done. +$%d'):format(Config.Pay)"
        return header + textwrap.dedent(f"""\
        local carrying = {{}}   -- [src] = true  (server-owned sequence state)
        local lastPay  = {{}}

        lib.callback.register('{job}:pickup', function(src)
            local player = {gp}
            if not player then return false end
            if {jn} ~= Config.Job then return false end
            if #(GetEntityCoords(GetPlayerPed(src)) - Config.Pickup) > 5.0 then return false end
            carrying[src] = true
            return true
        end)

        lib.callback.register('{job}:dropoff', function(src)
            local player = {gp}
            if not player then return false end
            if {jn} ~= Config.Job then return false end
            if not carrying[src] then return false end                       -- sequence gate
            if #(GetEntityCoords(GetPlayerPed(src)) - Config.Dropoff) > 5.0 then return false end
            if Config.RequiredItem and {item_count % 'Config.RequiredItem'} < 1 then return false end
            local now = GetGameTimer()
            if lastPay[src] and now - lastPay[src] < Config.PayCooldownMs then return false end
            lastPay[src], carrying[src] = now, nil
            if Config.RequiredItem then {rm_item % ('Config.RequiredItem', '1')} end
            {add_money % ('Config.Pay', job + '-pay')}
            {notify_call}
            return true
        end)

        AddEventHandler('playerDropped', function()
            carrying[source] = nil; lastPay[source] = nil
        end)
        """)

    if archetype == "illegal":
        return header + textwrap.dedent(f"""\
        local sales = {{}}   -- [src] = {{ count = n, last = ms }}  (server-owned, anti-farm)

        local function alertPolice(coords)
            if math.random() > Config.AlertChance then return end
            local jitter = function(v) return v + (math.random() * 80 - 40) end   -- blur ~40m
            local approx = vec3(jitter(coords.x), jitter(coords.y), coords.z)
            for _, pid in ipairs(GetPlayers()) do
                local src = tonumber(pid)
                local cop = {gp.replace('(src)', '(src)')}
                if cop and cop.PlayerData and cop.PlayerData.job and cop.PlayerData.job.type == 'leo'
                   and cop.PlayerData.job.onduty then
                    TriggerClientEvent('{job}:copBlip', src, approx)
                end
            end
        end

        lib.callback.register('{job}:sell', function(src)
            local player = {gp}
            if not player then return false end
            if {jn} ~= Config.Job then return false end

            local held = {item_count % 'Config.SellItem'}
            if held < 1 then {notify % ('error', "'You have nothing to sell.'") if fw != 'esx' else notify % "'You have nothing to sell.'"} return false end

            local now = GetGameTimer()
            local s = sales[src] or {{ count = 0, last = 0 }}
            if now - s.last < Config.PayCooldownMs then return false end       -- cadence

            -- bust: lose the goods, alert police, no pay
            if math.random() < Config.BustChance then
                {rm_item % ('Config.SellItem', 'held')}
                alertPolice(Config.SellZone)
                {notify % ('error', "'The deal went bad. You lost the goods!'") if fw != 'esx' else notify % "'The deal went bad. You lost the goods!'"}
                s.last = now; sales[src] = s
                return false
            end

            -- diminishing returns on consecutive sales
            local mult = math.max(Config.MinSaleMult, 1.0 - s.count * Config.SaleDecay)
            local payout = math.floor(Config.Pay * mult)

            {rm_item % ('Config.SellItem', '1')}
            {add_money % ('payout', job + '-sale')}
            alertPolice(Config.SellZone)
            s.count = s.count + 1; s.last = now; sales[src] = s
            {notify % ('success', "('Sold. +$%d'):format(payout)") if fw != 'esx' else notify % "('Sold. +$%d'):format(payout)"}
            return true
        end)

        -- slowly recover diminishing-return counter
        CreateThread(function()
            while true do
                Wait(60000)
                for src, s in pairs(sales) do if s.count > 0 then s.count = s.count - 1 end end
            end
        end)

        AddEventHandler('playerDropped', function() sales[source] = nil end)
        """)

    # whitelisted — boss-check expression bound to the 'boss' player var
    boss_is_boss = FW[fw]["is_boss"].replace("player.", "boss.")
    return header + textwrap.dedent(f"""\
    -- Reused gate: must hold the job, be on duty, and meet a minimum grade. Server-side only.
    local function canAct(src, minGrade)
        local player = {gp}
        if not player then return false, nil end
        if {jn} ~= Config.Job then return false, nil end
        if not {od} then return false, player end
        if {gl} < (minGrade or 0) then return false, player end
        return true, player
    end

    RegisterNetEvent('{job}:toggleDuty', function()
        local src = source
        local player = {gp}
        if not player or {jn} ~= Config.Job then return end
        {FW[fw]["set_duty"]}
        TriggerClientEvent('{job}:dutyChanged', src, {od})
    end)

    RegisterNetEvent('{job}:armory', function()
        local src = source
        local ok, player = canAct(src, Config.Access.armory)
        if not ok then return end
        -- TODO: grant gear from a SERVER-side allowed set only, e.g.:
        -- {add_item % ("'weapon_pistol'", '1')}
        {notify % ('inform', "'Armory access granted.'") if fw != 'esx' else notify % "'Armory access granted.'"}
    end)

    -- Example boss action: set another employee's grade. Authority + bounds checked server-side.
    RegisterNetEvent('{job}:setGrade', function(targetSrc, newGrade)
        local src = source
        local ok, boss = canAct(src, Config.Access.boss)
        if not ok or not {boss_is_boss} then return end
        if type(newGrade) ~= 'number' or newGrade < 0 or newGrade > Config.MaxGrade then return end
        local target = {gp.replace('(src)', '(targetSrc)')}
        if not target then return end
        -- TODO: target must be the same job; then SetJob(Config.Job, newGrade) per your framework.
    end)
    """)


def main():
    ap = argparse.ArgumentParser(description="Scaffold a server-authoritative FiveM job resource.")
    ap.add_argument("--name", required=True, help="job/resource name (lowercase, no spaces), e.g. mechanic")
    ap.add_argument("--archetype", default="legal", choices=["legal", "illegal", "whitelisted"])
    ap.add_argument("--framework", default="qbox", choices=["qbox", "qbcore", "esx"])
    ap.add_argument("--output", required=True, help="output directory (the resource folder is created inside it)")
    args = ap.parse_args()

    name = args.name.strip().lower().replace(" ", "_")
    if not name:
        print("error: --name is empty", file=sys.stderr)
        sys.exit(1)

    out = os.path.join(args.output, name)
    os.makedirs(out, exist_ok=True)

    files = {
        "fxmanifest.lua": fxmanifest(name, args.framework),
        "config.lua":     config_lua(name, args.archetype),
        "client.lua":     client_lua(name, args.archetype, args.framework),
        "server.lua":     server_lua(name, args.archetype, args.framework),
    }
    for fname, content in files.items():
        with open(os.path.join(out, fname), "w") as f:
            f.write(content)

    print(f"Scaffolded '{name}' ({args.archetype}, {args.framework}) -> {out}")
    print("Files: " + ", ".join(files.keys()))
    print()
    print("Next:")
    print(f"  1. Register the '{name}' job + grades in your framework's job list "
          "(references/job-registration.md).")
    print("  2. Fill the TODOs in config.lua (coords, pay, items).")
    print(f"  3. Add the resource to server.cfg: ensure {name}")
    print("  4. Confirm load order: oxmysql -> ox_lib -> ox_inventory -> framework -> "
          f"ox_target -> {name}")
    print("  5. Test the exploit path: trigger the payout event directly with junk args; "
          "confirm $0 / no items.")


if __name__ == "__main__":
    main()
