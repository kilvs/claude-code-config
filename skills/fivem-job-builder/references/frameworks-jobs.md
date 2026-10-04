# Framework Job API Map — Qbox ↔ QBCore ↔ ESX

The job *structure* (register → loop → server-validated payout) is identical across frameworks. Only the export/event names differ. This table lets you write a Qbox job and port it, or target QBCore/ESX directly. Match every script to one framework + version — mixing targets is the top cause of "it doesn't work."

Default to **Qbox-native** (left column). Don't write QBCore-in-disguise on a Qbox server (`QBCore.Functions.*`, `qb-inventory`, tick loops) — it works in the weak sense but fights the framework.

## Server-side player & money

| Task | Qbox (`qbx_core`) | QBCore (`qb-core`) | ESX |
|---|---|---|---|
| Get player | `exports.qbx_core:GetPlayer(src)` | `QBCore.Functions.GetPlayer(src)` | `ESX.GetPlayerFromId(src)` |
| Citizen/identifier | `player.PlayerData.citizenid` | `Player.PlayerData.citizenid` | `xPlayer.identifier` |
| Add money | `player.Functions.AddMoney('cash', n, reason)` | `Player.Functions.AddMoney('cash', n, reason)` | `xPlayer.addMoney(n)` / `xPlayer.addAccountMoney('bank', n)` |
| Remove money | `player.Functions.RemoveMoney('cash', n, reason)` | `Player.Functions.RemoveMoney('cash', n, reason)` | `xPlayer.removeMoney(n)` / `removeAccountMoney` |
| Read balance | `player.PlayerData.money.cash` | `Player.PlayerData.money.cash` | `xPlayer.getMoney()` / `xPlayer.getAccount('bank').money` |

ESX money accounts are `money` (cash), `bank`, `black_money`. QBCore/Qbox use `cash`/`bank`/`crypto`.

## Job & grade

| Task | Qbox | QBCore | ESX |
|---|---|---|---|
| Get job name | `player.PlayerData.job.name` | `Player.PlayerData.job.name` | `xPlayer.getJob().name` |
| Get grade level | `player.PlayerData.job.grade.level` | `Player.PlayerData.job.grade.level` | `xPlayer.getJob().grade` |
| On duty | `player.PlayerData.job.onduty` | `Player.PlayerData.job.onduty` | `xPlayer.getJob().onDuty`* |
| Is boss | `player.PlayerData.job.isboss` | `Player.PlayerData.job.isboss` | grade flag / `job.grade_name == 'boss'` |
| Set job | `player.Functions.SetJob(name, grade)` | `Player.Functions.SetJob(name, grade)` | `xPlayer.setJob(name, grade)` |
| Set duty | `player.Functions.SetJobDuty(bool)` | `Player.Functions.SetJobDuty(bool)` | varies / esx_policejob duty events |

*ESX duty handling varies by job resource; vanilla ESX has weaker built-in duty than QB-lineage. Check the server's policejob/ambulance resource.

## Items (inventory)

The full ox stack (Qbox default, and increasingly used on QBCore/ESX too) uses **ox_inventory** server exports regardless of framework:

| Task | ox_inventory (any framework) | QBCore native (qb-inventory) | ESX native |
|---|---|---|---|
| Count item | `exports.ox_inventory:GetItemCount(src, name)` | `Player.Functions.GetItemByName(name)` | `xPlayer.getInventoryItem(name).count` |
| Give item | `exports.ox_inventory:AddItem(src, name, n)` | `Player.Functions.AddItem(name, n)` | `xPlayer.addInventoryItem(name, n)` |
| Take item | `exports.ox_inventory:RemoveItem(src, name, n)` | `Player.Functions.RemoveItem(name, n)` | `xPlayer.removeInventoryItem(name, n)` |

Define new items in `ox_inventory/data/items.lua` (ox) before granting. `AddItem` (ox) returns false if full — handle it.

## Notifications & UI

| Task | Qbox / ox | QBCore native | ESX native |
|---|---|---|---|
| Notify (server→client) | `lib.notify(src, { type='success', description='...' })` | `TriggerClientEvent('QBCore:Notify', src, '...', 'success')` | `TriggerClientEvent('esx:showNotification', src, '...')` |
| Notify (client) | `lib.notify({ ... })` | `QBCore.Functions.Notify('...', 'success')` | `ESX.ShowNotification('...')` |
| Progress bar | `lib.progressBar({ ... })` (client) | `QBCore` progressbar / `lib` | `ESX.Progressbar(...)` / `lib` |
| Context/input menu | `lib.registerContext` / `lib.inputDialog` | qb-menu / `lib` | esx_menu / `lib` |
| Server callback | `lib.callback.register` / `lib.callback.await` | `QBCore.Functions.CreateCallback` / `TriggerCallback` | `ESX.RegisterServerCallback` / `TriggerServerCallback` |

`ox_lib` (`lib.*`) works identically on any framework that has it loaded — preferring it makes a job portable. Qbox assumes ox_lib is present.

## DB

`oxmysql` (`MySQL.query`, `MySQL.single.await`, `MySQL.insert`, `MySQL.update`) is the standard across all three modern setups. Use `?` placeholders. Player key: `citizenid` (Qbox/QBCore), `identifier` (ESX).

## Porting checklist (Qbox → QBCore/ESX)

1. Swap player-get and money/job/item calls per the tables above.
2. Swap notify/callback/menu calls — or keep `lib.*` if ox_lib is installed on the target (preferred).
3. Swap item handling to the target's inventory unless it also runs ox_inventory.
4. Re-confirm the job + grades exist in the target's job list (Lua file for QB-lineage, DB rows for ESX — `job-registration.md`).
5. Re-test the server-authoritative payout path on the target — the validation logic itself doesn't change, only the API names.
