# Job Economy — server-authoritative rewards, items, persistence, balancing

This is the most important reference in the skill. Every job pays money or grants items, and **the server must be the only thing that decides a reward is earned.** Read this whenever money or items change hands.

## Contents
1. The exploit you are preventing
2. The server-authoritative payout pattern (the template)
3. The validation checklist
4. Qbox money functions (`exports.qbx_core`)
5. ox_inventory items server-side
6. Cooldowns, sequence, and rate-limiting
7. Persistence with oxmysql
8. Balancing $/hour

---

## 1. The exploit you are preventing

A naive job pays like this:

```lua
-- server.lua — DO NOT DO THIS
RegisterNetEvent('myjob:finishDelivery', function(amount)
    local src = source
    local player = exports.qbx_core:GetPlayer(src)
    player.Functions.AddMoney('cash', amount) -- client decided 'amount'. game over.
end)
```

A cheater opens the console and runs `TriggerServerEvent('myjob:finishDelivery', 999999)` in a loop. They are now infinitely rich and your economy is dead. **The client passing the amount — or the client merely asserting the task is done — is the vulnerability.** The fix is never "obfuscate the event name." The fix is: the server independently re-derives whether a reward is owed, and how much, from state it controls.

## 2. The server-authoritative payout pattern (the template)

Use this shape for *every* paying action. The client triggers it with **no reward data** — at most an identifier of *which* action it's attempting. The server looks everything up.

```lua
-- config (SHARED or server-only). Server owns the real numbers & coords.
Config.Dropoffs = {
    ['warehouse'] = { coords = vec3(123.4, 567.8, 90.1), pay = 450, requiredItem = 'package' },
    ['docks']     = { coords = vec3(987.6, 543.2, 10.9), pay = 600, requiredItem = 'package' },
}
Config.Job = 'trucker'
Config.PayCooldownMs = 3000

local lastPay = {} -- [src] = GetGameTimer() ms, server-side cadence guard

RegisterNetEvent('trucker:completeDropoff', function(dropoffId)
    local src = source
    local player = exports.qbx_core:GetPlayer(src)
    if not player then return end

    -- (a) the action must exist in SERVER config, not be a client-supplied number
    local dropoff = Config.Dropoffs[dropoffId]
    if not dropoff then return end

    -- (b) right job
    if player.PlayerData.job.name ~= Config.Job then return end

    -- (c) really there — check the player's ped coords as the SERVER sees them
    local ped = GetPlayerPed(src)
    local pcoords = GetEntityCoords(ped)
    if #(pcoords - dropoff.coords) > 5.0 then return end

    -- (d) really has the item — ask ox_inventory, don't trust the client
    local count = exports.ox_inventory:GetItemCount(src, dropoff.requiredItem)
    if count < 1 then return end

    -- (e) cadence: can't spam completions
    local now = GetGameTimer()
    if lastPay[src] and (now - lastPay[src]) < Config.PayCooldownMs then return end
    lastPay[src] = now

    -- all checks passed — NOW the server acts. amount comes from server config.
    exports.ox_inventory:RemoveItem(src, dropoff.requiredItem, 1)
    player.Functions.AddMoney('cash', dropoff.pay, 'trucker-dropoff')
    lib.notify(src, { type = 'success', description = ('Delivered. +$%d'):format(dropoff.pay) })
end)
```

Note what the client sent: a string id (`'warehouse'`). Even if the cheater lies and sends `'docks'`, every other check still has to pass — they must hold the docks job, be standing at the docks, hold the package, and respect the cooldown. There is no argument they can pass that mints money.

**Prefer `lib.callback` over a raw event** when the client needs a yes/no result back (e.g. to show success UI). Same validation inside; the callback just lets you return a result:

```lua
lib.callback.register('trucker:completeDropoff', function(src, dropoffId)
    -- run the exact same (a)-(e) checks; return true only on success
end)
```

## 3. The validation checklist

Before any `AddMoney` / `AddItem` in a job handler, the server has confirmed **all** of:

- [ ] **Player exists** — `exports.qbx_core:GetPlayer(src)` returned non-nil.
- [ ] **Correct job** — `player.PlayerData.job.name == Config.Job`.
- [ ] **Correct grade** (if reward is grade-gated) — `player.PlayerData.job.grade.level >= required`.
- [ ] **On duty** (if the job uses duty) — `player.PlayerData.job.onduty`.
- [ ] **Location** — server-side ped coords within range of the *server's* coord for this action.
- [ ] **Required items/state** — verified via `ox_inventory` server export, not a client claim.
- [ ] **Cadence** — per-player cooldown / not-too-fast guard passed.
- [ ] **Sequence** — prerequisite steps for this action were actually completed (track step state server-side).
- [ ] **Amount is from server config**, never from a client argument.

If any box can't be ticked from server-controlled data, the reward doesn't go out.

## 4. Qbox money functions (`exports.qbx_core`)

Get the player object server-side, then use its functions. Always pass a reason string (shows in logs).

```lua
local player = exports.qbx_core:GetPlayer(src)

player.Functions.AddMoney('cash', 500, 'myjob-pay')      -- 'cash' | 'bank' | 'crypto'
player.Functions.RemoveMoney('bank', 200, 'myjob-fee')
local cash = player.PlayerData.money.cash                  -- read balance
local bank = player.PlayerData.money.bank
```

`RemoveMoney` returns `false` if the player can't afford it — check it before delivering whatever they were buying. For QBCore/ESX equivalents see `frameworks-jobs.md`.

## 5. ox_inventory items, server-side

Items are the other half of rewards. All authoritative checks/grants use the **server** exports.

```lua
-- check
local n = exports.ox_inventory:GetItemCount(src, 'package')        -- number held
-- grant (returns true on success; false if no room)
local ok = exports.ox_inventory:AddItem(src, 'fish', 3)
-- take
exports.ox_inventory:RemoveItem(src, 'package', 1)
-- search with metadata, set durability, etc. — see ox_inventory docs
```

Items must be defined in `ox_inventory/data/items.lua` before a job can grant them. If the job introduces new items (a harvested crop, a job tool), add them there first. `AddItem` can fail when the inventory is full — handle the `false` so the player doesn't lose the source item without receiving the reward.

## 6. Cooldowns, sequence, and rate-limiting

Even fully-validated payouts get farmed without these. Keep per-player state **on the server**:

```lua
local jobState = {} -- [src] = { step = 'idle'|'carrying'|..., lastAction = ms, runsThisHour = n }
```

- **Cooldown**: reject if `GetGameTimer() - jobState[src].lastAction < cooldown`.
- **Sequence**: a dropoff only pays if `jobState[src].step == 'carrying'`; pickup sets it, dropoff clears it. A client can't claim a dropoff it never picked up.
- **Diminishing returns / soft cap** (esp. illegal jobs): reduce or zero pay after N runs in a window so the loop can't be ground 24/7. See `illegal-jobs.md`.
- Clear `jobState[src]` on `playerDropped` to avoid leaks.

## 7. Persistence with oxmysql

Anything that must survive a reconnect or restart goes to the DB. Two common cases:

**Per-player job progress** (e.g. fishing level, deliveries done):
```lua
MySQL.insert('INSERT INTO job_progress (citizenid, job, xp) VALUES (?, ?, ?) '
  .. 'ON DUPLICATE KEY UPDATE xp = xp + ?',
  { citizenid, 'fisher', gained, gained })

local row = MySQL.single.await('SELECT xp FROM job_progress WHERE citizenid = ? AND job = ?',
  { citizenid, 'fisher' })
```

**Society / job funds** (shared money pool for whitelisted jobs) — store the balance in a table keyed by job name and mutate it only through server-side, grade-checked handlers. Never let a client set a society balance.

Use prepared statements (`?` placeholders) — never string-concatenate player input into SQL. `citizenid` is the stable player key in Qbox/QBCore (`player.PlayerData.citizenid`); ESX uses `identifier`.

## 8. Balancing $/hour

Design to a target hourly rate for the job, then derive per-loop pay:

```
pay_per_loop = target_hourly * (loop_seconds / 3600)
```

Example: a delivery loop takes ~90s end to end, and you want truckers earning ~$2,000/hr → pay ≈ 2000 × (90/3600) = **$50 per loop**. (Round to a clean number.)

Guidelines:
- **Legal jobs**: lowest risk → lowest rate. Set the baseline economy floor here.
- **Whitelisted jobs**: paid via salary/`payment` per paycheck cycle and/or per-action; factor the paycheck in so you don't double-pay.
- **Illegal jobs**: higher rate to justify risk, but apply diminishing returns and item/seizure risk so *expected* value stays bounded. Tune the failure/seizure chance, not just the headline pay.
- Sanity check against your server's prices (a meal, a cheap car) so the number means something.
- Always re-test the exploit path after balancing: fire the payout event directly with junk args and confirm $0 comes out.
