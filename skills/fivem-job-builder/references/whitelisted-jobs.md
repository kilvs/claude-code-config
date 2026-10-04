# Whitelisted Jobs — grades, duty, allowlist, restricted access

Police, EMS/ambulance, and boss-managed shops. The defining features are **grades with different permissions and pay**, explicit **clock-in/clock-out duty state**, an **allowlist** controlling who can have the job at all, and **grade-gated access** to restricted items/vehicles/areas. Register the job with `whitelisted = true` (see `job-registration.md`); the money/validation rules in `job-economy.md` still apply to anything that pays.

## Whitelist = server-enforced, always

A whitelist that only hides menu options client-side is not a whitelist — a cheater just calls the event anyway. The whitelist has two layers:
1. **Who can hold the job** — enforced by the framework's job assignment (`whitelisted = true` means it can't be self-assigned; only a boss/admin grants it via `SetJob`). Validate the *granter's* authority server-side before any `SetJob` on someone else.
2. **What a holder can do** — every privileged action re-checks, on the server, that the player has the job, the required grade, and is on duty. Repeat for every action; never once at the menu.

```lua
-- server: a gate function reused by every privileged action
local function canAct(src, minGrade)
    local p = exports.qbx_core:GetPlayer(src)
    if not p then return false end
    local job = p.PlayerData.job
    return job.name == 'police' and job.onduty and job.grade.level >= (minGrade or 0)
end

RegisterNetEvent('police:openArmory', function()
    if not canAct(source, 1) then return end   -- officer+ and on duty
    -- ... grant access ...
end)
```

## Clock-in / clock-out (duty state)

Duty is a boolean the server owns. Off-duty officers shouldn't get the salary (unless `offDutyPay = true`) or be able to use job powers. Toggle it via the framework:

```lua
-- server, on a duty-toggle action at the station:
local p = exports.qbx_core:GetPlayer(src)
if p.PlayerData.job.name ~= 'police' then return end
p.Functions.SetJobDuty(not p.PlayerData.job.onduty)
TriggerClientEvent('myjob:dutyChanged', src, p.PlayerData.job.onduty)
```

Common UX: a duty toggle on an `ox_target` at the station locker/sign-in, plus a duty blip/roster. The blip and roster are flavour; the *power* gate is the server `onduty` check on every action.

## Grades & permissions

Grades come from the job registration (`job-registration.md`). Map capabilities to grade levels in config and check `grade.level` server-side:

```lua
Config.Access = {
    armory   = 1,   -- Officer+
    impound  = 1,
    boss     = 4,   -- Chief only
    setGrade = 4,
}
```

Higher grades typically get: better salary (set in `payment` per grade), access to better armory/vehicles, the boss menu, and society-fund authority (`bankAuth`). Always read the grade as the **server** sees it.

## Restricted access by grade

- **Items** (armory): a grade-gated server handler hands out weapons/gear via `ox_inventory:AddItem`. Check `canAct(src, Config.Access.armory)` first. Never let the client pick the item id off a list the server doesn't re-validate against an allowed set.
- **Vehicles** (garage): spawn a job vehicle only after the server confirms job+grade+duty. Restrict vehicle models by grade via a server-checked allowed-set.
- **Areas / doors**: use `ox_doorlock` with job/grade locks, or gate a teleport/access action server-side. A locked door whose lock is only client-side is decorative.

## Boss / management menu

Boss-grade players (`isboss`) manage the workforce. The menu is built with `ox_lib` context/input menus client-side, but **every action is a server handler that re-checks the caller is actually a boss of that job**:

```lua
RegisterNetEvent('police:setGrade', function(targetSrc, newGrade)
    local boss = exports.qbx_core:GetPlayer(source)
    if not boss or not boss.PlayerData.job.isboss then return end          -- authority
    if boss.PlayerData.job.name ~= 'police' then return end
    if newGrade < 0 or newGrade > 4 then return end                        -- bound the input
    local target = exports.qbx_core:GetPlayer(targetSrc)
    if not target or target.PlayerData.job.name ~= 'police' then return end -- same job only
    target.Functions.SetJob('police', newGrade)
end)
```

Typical boss actions: hire (grant the whitelisted job), fire (set to unemployed), promote/demote (set grade), manage **society funds** (the shared job bank — store and mutate server-side only, gate on `bankAuth`; see `job-economy.md` §7). Bound and validate every argument — boss menus are a favourite injection target because they legitimately change other players' state.

## Salary vs per-action pay

Whitelisted jobs usually earn a framework **paycheck** (`payment` per grade, paid on the framework's cycle while on duty / or off-duty if `offDutyPay`). If you also pay per action (e.g. EMS revive bonus), keep the total sane — decide whether the job is salary-led or action-led so you don't accidentally double the intended $/hr (`job-economy.md` §8).

## Quick build checklist for a whitelisted job
1. Register job with `whitelisted = true` and grades with `payment` (`job-registration.md`).
2. Duty toggle at the station (`SetJobDuty`), server-owned.
3. `canAct(src, minGrade)` gate reused by every privileged action.
4. Armory / garage / doors gated by grade server-side.
5. Boss menu with per-action authority re-checks and bounded inputs.
6. Society funds (if used) mutated only through grade-checked server handlers.
