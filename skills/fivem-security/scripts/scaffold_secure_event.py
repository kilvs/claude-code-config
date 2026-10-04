#!/usr/bin/env python3
"""
scaffold_secure_event.py — emit a correctly-structured, server-authoritative FiveM
event handler that applies all four Golden Rules, plus the optional sv_security.lua helper.

This is a STARTING TEMPLATE, not a finished feature — it shows the right shape (source
capture, authorization, parameter validation, distance, rate-limit, server-derived action)
with TODOs where your specifics go.

Usage:
    python scaffold_secure_event.py --name shop_buy --output ./out
    python scaffold_secure_event.py --name drugs_sell --kind callback --output ./out

--kind:  event (default, RegisterNetEvent) or callback (lib.callback.register)
Outputs: <name>_server.lua (the handler) and sv_security.lua (the helper) in <output>/.
Never emits real keys or credentials.
"""
import argparse
import os
import shutil
import sys
import textwrap


def handler_event(name):
    return textwrap.dedent(f"""\
    -- {name} — SERVER handler. Applies all four Golden Rules. See the fivem-security skill.
    -- This is a TEMPLATE: fill the TODOs. Every check here exists for a reason (rules/*.md).
    local sec = require 'sv_security'   -- or paste the helper functions inline

    -- Server-owned config. The client NEVER supplies prices, coords, or the allowed set.
    local Config = {{
        job = nil,                       -- e.g. 'mechanic'; nil = no job gate. TODO
        point = vec3(0.0, 0.0, 0.0),     -- the real interaction location. TODO
        radius = 5.0,
        cooldownMs = 3000,
        allowed = {{ -- whitelist of valid ids/items. TODO
            -- example = {{ price = 100 }},
        }},
    }}

    RegisterNetEvent('{name}', function(itemId, amount)
        local src = source                                   -- RULE 1: capture source FIRST

        local player = sec.validatePlayer(src)               -- RULE 1: resolve + authorize
        if not player then return end
        if Config.job and not sec.hasJob(player, Config.job) then return end

        if not sec.inWhitelist(itemId, Config.allowed) then return end  -- RULE 2: whitelist id
        amount = sec.validateAmount(amount, 1, 100)          -- RULE 2: type + bounds
        if not amount then return end

        if not sec.validateDistance(src, Config.point, Config.radius) then return end  -- RULE 3

        if not sec.rateLimit(src, '{name}', Config.cooldownMs) then return end          -- RULE 4

        -- RULE 1/2: derive the consequence from SERVER data, never from the client.
        local def = Config.allowed[itemId]
        local price = (def and def.price or 0) * amount
        -- TODO: verify the player can afford it / holds prerequisites, then act with server values:
        --   player.Functions.RemoveMoney('cash', price, '{name}')
        --   exports.ox_inventory:AddItem(src, itemId, amount)
        sec.notify(src, ('OK: %dx %s'):format(amount, itemId), 'success')
    end)
    """)


def handler_callback(name):
    return textwrap.dedent(f"""\
    -- {name} — SERVER lib.callback. Same Golden Rules; returns feedback to the client.
    -- The return is FEEDBACK, not authority — the server already did (or refused) the work.
    local sec = require 'sv_security'

    local Config = {{
        job = nil, point = vec3(0.0, 0.0, 0.0), radius = 5.0, cooldownMs = 3000,
        allowed = {{ }},   -- TODO whitelist
    }}

    lib.callback.register('{name}', function(src, itemId, amount)
        local player = sec.validatePlayer(src)
        if not player then return false end
        if Config.job and not sec.hasJob(player, Config.job) then return false end
        if not sec.inWhitelist(itemId, Config.allowed) then return false end
        amount = sec.validateAmount(amount, 1, 100)
        if not amount then return false end
        if not sec.validateDistance(src, Config.point, Config.radius) then return false end
        if not sec.rateLimit(src, '{name}', Config.cooldownMs) then return false end

        -- TODO: act with server-derived values; return true only on success.
        return true
    end)
    """)


def main():
    ap = argparse.ArgumentParser(description="Scaffold a server-authoritative FiveM event handler.")
    ap.add_argument("--name", required=True, help="event/callback name (lowercase, no spaces)")
    ap.add_argument("--kind", default="event", choices=["event", "callback"])
    ap.add_argument("--output", required=True, help="output directory")
    args = ap.parse_args()

    name = args.name.strip().lower().replace(" ", "_")
    if not name:
        print("error: --name is empty", file=sys.stderr); sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    handler = handler_event(name) if args.kind == "event" else handler_callback(name)
    handler_path = os.path.join(args.output, f"{name}_server.lua")
    with open(handler_path, "w") as fh:
        fh.write(handler)

    # copy the helper next to the handler so the template runs as-is
    helper_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sv_security.lua")
    helper_dst = os.path.join(args.output, "sv_security.lua")
    if os.path.exists(helper_src):
        shutil.copyfile(helper_src, helper_dst)

    print(f"Scaffolded secure {args.kind} '{name}' -> {handler_path}")
    print(f"Helper copied -> {helper_dst}" if os.path.exists(helper_dst) else "(helper not found to copy)")
    print()
    print("Next:")
    print("  1. Fill the Config TODOs (job gate, real coords, whitelist + prices).")
    print("  2. Replace the action TODO with your real money/item logic, using SERVER values.")
    print("  3. Confirm: firing this event with junk args, from far away, or spammed gets nothing.")
    print("  4. The handler and helper are server-side only — never trust a client result.")


if __name__ == "__main__":
    main()
