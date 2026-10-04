#!/usr/bin/env python3
"""Scaffold a runnable FiveM Lua resource.

Emits fxmanifest.lua + client.lua + server.lua + config.lua wired with a command,
a client->server event round-trip, and a SERVER-SIDE VALIDATION example so the
trust boundary is demonstrated by default (the single most important FiveM habit).

Frameworks: standalone, qbox, qbcore, esx. Qbox is the recommended default.

Usage:
    python scaffold_resource.py --name my_shop --framework qbox --output ./resources
    python scaffold_resource.py --name hello --framework standalone --output .

Run with --help for all options.
"""
import argparse
import os
import re
import sys

FX_VERSION = "cerulean"  # current manifest schema at time of writing; verify at docs.fivem.net


def safe_name(name: str) -> str:
    n = re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_")
    if not n:
        n = "my_resource"
    if n[0].isdigit():
        n = "r_" + n
    return n


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# Framework-specific snippets: how to get a player and remove money, server-side.
FRAMEWORK = {
    "standalone": {
        "shared_init": "",
        "server_init": "",
        "get_player": "-- standalone: no framework player object. Track your own state server-side.",
        "deps": [],
        "label": "Standalone (no framework)",
    },
    "qbox": {
        "shared_init": "'@ox_lib/init.lua',\n    ",
        "server_init": "'@oxmysql/lib/MySQL.lua',\n    ",
        "get_player": "local player = exports.qbx_core:GetPlayer(src)",
        "deps": ["ox_lib", "oxmysql", "qbx_core"],
        "label": "Qbox (recommended)",
    },
    "qbcore": {
        "shared_init": "'@ox_lib/init.lua',\n    ",
        "server_init": "'@oxmysql/lib/MySQL.lua',\n    ",
        "get_player": "local QBCore = exports['qb-core']:GetCoreObject()\n    local player = QBCore.Functions.GetPlayer(src)",
        "deps": ["ox_lib", "oxmysql", "qb-core"],
        "label": "QBCore",
    },
    "esx": {
        "shared_init": "'@ox_lib/init.lua',\n    ",
        "server_init": "'@oxmysql/lib/MySQL.lua',\n    ",
        "get_player": "local ESX = exports['es_extended']:getSharedObject()\n    local xPlayer = ESX.GetPlayerFromId(src)",
        "deps": ["ox_lib", "oxmysql", "es_extended"],
        "label": "ESX Legacy",
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a runnable FiveM Lua resource.")
    ap.add_argument("--name", required=True, help="Resource name (lowercase_with_underscores)")
    ap.add_argument("--framework", default="qbox", choices=list(FRAMEWORK.keys()),
                    help="Target framework (default: qbox)")
    ap.add_argument("--output", required=True, help="Output dir (resource folder created inside)")
    ap.add_argument("--author", default="You")
    ap.add_argument("--description", default="A FiveM resource.")
    ap.add_argument("--no-oxlib", action="store_true",
                    help="Don't wire ox_lib/oxmysql even for a framework (rarely wanted)")
    args = ap.parse_args()

    name = safe_name(args.name)
    fw = FRAMEWORK[args.framework]
    root = os.path.join(args.output, name)
    if os.path.exists(root):
        print(f"Error: {root} already exists.", file=sys.stderr)
        return 1

    use_ox = not args.no_oxlib and args.framework != "standalone"
    shared_init = fw["shared_init"] if use_ox else ""
    server_init = fw["server_init"] if use_ox else ""
    deps = fw["deps"] if use_ox else ([] if args.framework == "standalone" else [args.framework])

    deps_block = ""
    if deps:
        dep_lines = "\n".join(f"    '{d}'," for d in deps)
        deps_block = f"\ndependencies {{\n{dep_lines}\n}}\n"

    manifest = f"""fx_version '{FX_VERSION}'
game 'gta5'
lua54 'yes'

author '{args.author}'
description '{args.description}'
version '1.0.0'

shared_scripts {{
    {shared_init}'config.lua',
}}

client_scripts {{
    'client.lua',
}}

server_scripts {{
    {server_init}'server.lua',
}}
{deps_block}"""
    write(os.path.join(root, "fxmanifest.lua"), manifest)

    config = f"""-- {name} configuration (shared: loaded on client AND server).
-- Keep prices, item lists, and anything authoritative here on the SERVER side of
-- your logic. Never let the client send these values.

Config = {{}}

-- Example server-authoritative item list. The server reads price from here,
-- NOT from whatever the client sends.
Config.Items = {{
    water = {{ price = 5 }},
    bread = {{ price = 8 }},
}}
"""
    write(os.path.join(root, "config.lua"), config)

    # Client: a command that REQUESTS a purchase. It does not decide anything.
    if use_ox:
        notify = "lib.notify({ title = '" + name + "', description = msg, type = 'inform' })"
    else:
        notify = "print('[" + name + "] '..msg)"
    client = f"""-- {name} CLIENT (runs on each player's machine — UNTRUSTED).
-- The client REQUESTS; the server DECIDES. Never make money/item decisions here.

local function notify(msg)
    {notify}
end

-- Receive the server's result.
RegisterNetEvent('{name}:result', function(msg)
    notify(msg)
end)

-- /{name}buy <item> <amount>  -> ask the server to buy. The server validates.
RegisterCommand('{name}buy', function(_, rawArgs)
    local item = rawArgs[1]
    local amount = tonumber(rawArgs[2]) or 1
    if not item then
        notify('usage: /{name}buy <item> <amount>')
        return
    end
    -- We send only the REQUEST. We do NOT send a price or a balance.
    TriggerServerEvent('{name}:buy', item, amount)
end, false)
"""
    write(os.path.join(root, "client.lua"), client)

    # Server: validates everything. This is the trust boundary in action.
    server = f"""-- {name} SERVER (authoritative). Validate every client request as hostile input.

local function getPlayer(src)
    {fw["get_player"]}
    -- TODO: return the framework player object / your own player state.
end

RegisterNetEvent('{name}:buy', function(item, amount)
    local src = source                 -- set by the server; the client cannot spoof it
    amount = tonumber(amount)

    -- 1. Distrust arguments: validate type and range.
    if type(item) ~= 'string' then return end
    if not amount or amount < 1 or amount > 100 then return end

    -- 2. Whitelist: the item must exist in our SERVER-side config.
    local def = Config.Items[item]
    if not def then return end

    -- 3. Price comes from the SERVER, never from the client.
    local price = def.price * amount

    -- 4. Resolve + authorize the player, then verify they can afford it.
    --    (Pseudo-code: wire to your framework's money API — see references/frameworks.md.)
    -- local player = getPlayer(src)
    -- if not player then return end
    -- if getMoney(player) < price then
    --     TriggerClientEvent('{name}:result', src, 'Not enough money')
    --     return
    -- end
    -- removeMoney(player, price)
    -- giveItem(src, item, amount)

    -- 5. Tell the client the result.
    TriggerClientEvent('{name}:result', src, ('Bought %dx %s for $%d'):format(amount, item, price))
end)
"""
    write(os.path.join(root, "server.lua"), server)

    write(os.path.join(root, "README.md"),
          f"# {name}\n\n{fw['label']} starter resource.\n\n"
          f"1. Place this folder under `resources/[local]/` (or any scanned `[category]`).\n"
          f"2. Add `ensure {name}` to server.cfg, AFTER its dependencies"
          + (f" ({', '.join(deps)}).\n" if deps else ".\n")
          + f"3. `refresh` then `ensure {name}` in the console.\n"
          f"4. In-game: `/{name}buy water 2`.\n\n"
          "The server.lua shows the trust boundary: the client requests, the server validates "
          "and decides. Fill in the framework money/item calls where marked. See references/security.md.\n")

    print(f"Scaffolded '{name}' ({fw['label']}) at {root}")
    print(f"Files: fxmanifest.lua, config.lua, client.lua, server.lua, README.md")
    if deps:
        print(f"server.cfg: ensure {' , '.join(deps)} BEFORE  ensure {name}")
    print("Next: read references/lua-scripting.md and references/security.md before extending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
