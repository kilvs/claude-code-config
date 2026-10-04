# Golden Rule 2 — Never Trust Parameters

> Always validate arguments sent from the client. If a client says "give me $50," the server checks whether the client *earned* it, not whether the client *claims* it.

Every argument that arrives in a server handler came from the client, and the client is attacker-controlled. An amount, a price, an item name, an index, a target id — all of it is a *claim*, not a fact, until the server validates it. Read this whenever a handler takes arguments from the client.

## Three things to check on every parameter

1. **Type.** Is it actually the type you expect? A handler expecting a number can be sent a table, a string, `nil`, or a crafted value. Coerce and check:
   ```lua
   amount = tonumber(amount)
   if not amount then return end                 -- rejects nil, tables, non-numeric strings
   if type(itemName) ~= 'string' then return end
   ```
2. **Range / bounds.** Within sane limits? Negative amounts and absurd quantities are the classic attacks:
   ```lua
   if amount < 1 or amount > 100 then return end  -- no negatives, no 999999
   if not math.type or math.type(amount) ~= 'integer' then amount = math.floor(amount) end
   ```
   A negative amount is the canonical exploit: "buy -100000 gold" can *add* money if you don't reject it.
3. **Whitelist membership** (for ids/names/choices). Is it a real, allowed value from a server-side set?
   ```lua
   if not Config.Items[itemName] then return end  -- must exist in server config
   ```

## The authoritative-value rule

The most important application: **a client-supplied amount, price, or balance is never authoritative.** The server derives the real number from its own config or state.

```lua
-- the client sends WHICH item and HOW MANY. The server decides the PRICE.
local def = Config.Items[itemName]               -- server config
if not def then return end
local price = def.price * amount                  -- server computes price, never trusts a sent one
```

If you ever find the client sending a `price`, `cost`, `reward`, or `newBalance` and the server using it — that is the bug. The client sends *intent* (what, how many); the server computes *consequences* (cost, reward, result).

## Whitelist, never blacklist

Accept known-good values; don't try to reject known-bad ones. A blacklist always misses a case.

```lua
-- GOOD: whitelist — only these actions exist
local Allowed = { repair = true, refuel = true, clean = true }
if not Allowed[action] then return end

-- BAD: blacklist — what about the action you didn't think of?
if action == 'delete_everything' then return end   -- misses every other malicious action
```

This applies to item names, job actions, menu choices, weapon names, vehicle models — any id-like parameter. Define the allowed set server-side and reject anything outside it.

## Sanitize before inventory and SQL

A validated-as-existing id is still going somewhere sensitive. Two hard rules:

- **Inventory**: only grant/remove items confirmed to be in a server-side item set. Never pass a raw client string into `AddItem` without confirming it's a real, allowed item — otherwise a cheater names any item into existence.
- **SQL**: **parameterized queries only.** Never concatenate client input into a query string — that's SQL injection.
  ```lua
  -- GOOD
  MySQL.query('SELECT * FROM owned WHERE citizenid = ? AND plate = ?', { cid, plate })
  -- DANGEROUS
  MySQL.query('SELECT * FROM owned WHERE plate = "' .. plate .. '"')  -- injectable
  ```

## Validate structure, not just scalars

If the client sends a table (common with NUI callbacks), validate its shape and every field you read — don't assume keys exist or have the right type:

```lua
RegisterNUICallback('buy', function(data, cb)
    if type(data) ~= 'table' then return cb(false) end
    local id = data.itemId
    local qty = tonumber(data.qty)
    if type(id) ~= 'string' or not Config.Items[id] then return cb(false) end
    if not qty or qty < 1 or qty > 100 then return cb(false) end
    -- ... safe to proceed
    cb('ok')
end)
```

Nested data is still client data. A missing-key crash is a denial-of-service; a wrong-type field used unchecked is an exploit.

## The exploits this rule prevents

- **Free money / dupe**: negative or client-chosen amounts/prices. Stopped by range checks + server-derived prices.
- **Item spawning**: arbitrary item names granted unchecked. Stopped by the item whitelist.
- **SQL injection**: client strings concatenated into queries. Stopped by parameterized queries.
- **Crash/DoS**: wrong-type or malformed payloads. Stopped by type/structure checks.

The throughline: the client sends intent; the server validates it against types, bounds, and a whitelist, then computes every consequence itself.
