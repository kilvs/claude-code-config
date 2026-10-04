# Security: Server-Authoritative Design

The most important reference in this skill. Almost every serious FiveM exploit traces back to one mistake: trusting the client. Internalize this before going public or touching money/items/permissions.

## Contents
1. The trust boundary
2. Validating client→server events
3. Worked example: a safe purchase
4. Why client-side "anti-cheat" is weak
5. Practical hardening
6. Admin & permissions
7. Logging

---

## 1. The trust boundary

The **client runs on the player's computer**, which a cheater fully controls. They can modify client Lua, send arbitrary events with arbitrary arguments, call your `RegisterNetEvent` handlers directly, spoof values, and read anything the client knows. Therefore:

> The client may **request**. The server **decides** and **persists**. Nothing the client sends is trusted as true.

Money, inventory, positions that gate actions, job/permission checks, prices, cooldowns, ownership — all live and are verified **server-side**. The client's role is input and display, never the source of truth. This isn't paranoia; public FiveM servers are constantly probed, and a single trusting event handler is enough to mint infinite money or items.

## 2. Validating client→server events

Treat every `RegisterNetEvent` server handler as a public, hostile-facing endpoint. For each one:

1. **Capture the real source.** `local src = source` immediately — the server sets this, the client can't spoof it. Capture before any `Wait()`.
2. **Resolve and authorize.** Get the framework player from `src`; confirm they're allowed to do this (right job/grade, is admin, owns the thing).
3. **Distrust arguments.** Treat every parameter as attacker-chosen. Validate type and range; never use a client-passed price, amount, or balance as authoritative. If the client sends an item name, confirm it's a real, allowed item — don't pass it straight into inventory/SQL.
4. **Verify against server state.** Do they actually have the item/money? Are they actually near the shop? (Don't trust a client-sent position; check server-known coords or use a server-validated zone.)
5. **Then act**, and tell the client the result.

```lua
RegisterNetEvent('shop:buy', function(itemName, amount)
    local src = source
    amount = tonumber(amount)
    if type(itemName) ~= 'string' or not amount or amount < 1 or amount > 100 then return end
    if not Config.Items[itemName] then return end          -- whitelist, not client's word
    local player = getPlayer(src)
    if not player then return end
    -- price comes from SERVER config, never from the client
    local price = Config.Items[itemName].price * amount
    if getMoney(player) < price then return end
    -- (optional) verify proximity to the shop using server-known position
    removeMoney(player, price)
    giveItem(src, itemName, amount)
    notify(src, 'Bought '..amount..'x '..itemName)
end)
```

Note what's absent: the client never sends the price or the new balance, and the item must exist in a server-side whitelist.

## 3. Worked example: the classic exploit it prevents

The naive version:
```lua
-- DANGEROUS — do not do this
RegisterNetEvent('shop:buy', function(item, price)
    removeMoney(source, price)   -- client chose the price...
    giveItem(source, item)       -- ...and the item
end)
```
A cheater sends `TriggerServerEvent('shop:buy', 'goldbar', -100000)` and is now infinitely rich with free gold. The §2 version is immune because price and item validity come from the server.

## 4. Why client-side "anti-cheat" is weak

Detection that runs on the client can be disabled, hooked, or spoofed by the same cheater it's trying to catch. Client checks add friction but are not a security boundary. Real protection is **architectural**: if the server never trusts the client, most cheats can't achieve anything that matters (they might see-through-walls locally, but they can't give themselves money or items, because those decisions are server-side). Spend your effort making the server authoritative, not on client-side detection theater. Third-party anti-cheats exist and help at the margins, but never substitute for server-authoritative design.

## 5. Practical hardening

- **Rate-limit** sensitive events server-side (cooldown per player) so a flood can't be abused.
- **Whitelist, don't blacklist** — accept known-good item names, job actions, etc., rather than trying to reject bad ones.
- **Parameterized SQL only** (`oxmysql` `?` placeholders) — never concatenate client input into queries.
- **Don't expose admin actions as plain net events** without a server-side permission check (see below).
- **Keep secrets out of client/shared files** — the client can read everything in its realm. License key and DB creds live only in `server.cfg`.
- **Minimize `RegisterNetEvent` surface** — every networked event is an attack entry point; don't register ones you don't need.
- **Validate entity ownership** before acting on entities a client references.

## 6. Admin & permissions

Use the ACE permission system rather than hardcoding identifiers in scripts:
```cfg
# server.cfg
add_ace group.admin command allow
add_principal identifier.fivem:0000000 group.admin
```
```lua
-- server: gate an admin action
RegisterNetEvent('admin:kick', function(targetId, reason)
    local src = source
    if not IsPlayerAceAllowed(src, 'command') then return end  -- server-side check
    -- ... validated kick
end)
```
The permission check is **server-side**; a client claiming to be admin proves nothing.

## 7. Logging

Log sensitive actions (money transfers, item spawns, admin commands) server-side — to console, a file, or a Discord webhook — with the player identifier and what happened. When something goes wrong (or someone exploits), logs are how you find it. Don't log secrets.
