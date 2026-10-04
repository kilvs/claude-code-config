# Job Registration — defining the job in the framework

Before any job logic runs, the job has to exist in the framework's shared job list. Every later check (`player.PlayerData.job.name == 'mechanic'`) depends on the name you register here. Read this first.

## Qbox — `qbx_core/shared/jobs.lua`

Jobs are a Lua table keyed by the **job name** (the internal id you'll reference everywhere — lowercase, no spaces). Each job has a label and a `grades` table; each grade has a `name`, `payment`, and optional flags.

```lua
['mechanic'] = {
    label = 'Mechanic',
    type = 'mechanic',          -- optional grouping tag
    defaultDuty = true,         -- start on duty when assigned?
    offDutyPay = false,         -- receive paycheck while off duty?
    grades = {
        [0] = { name = 'Recruit',   payment = 50 },
        [1] = { name = 'Novice',    payment = 75 },
        [2] = { name = 'Experienced', payment = 100 },
        [3] = { name = 'Advanced',  payment = 125 },
        [4] = { name = 'Boss', isboss = true, bankAuth = true, payment = 150 },
    },
},
```

For a **whitelisted** job (police/EMS — can't be self-assigned, only granted by an admin/boss), add `whitelisted = true`:

```lua
['police'] = {
    label = 'Police',
    type = 'leo',
    defaultDuty = false,
    offDutyPay = false,
    whitelisted = true,
    grades = {
        [0] = { name = 'Cadet',    payment = 100 },
        [1] = { name = 'Officer',  payment = 150 },
        [2] = { name = 'Sergeant', payment = 200 },
        [3] = { name = 'Lieutenant', payment = 250 },
        [4] = { name = 'Chief', isboss = true, bankAuth = true, payment = 300 },
    },
},
```

Key fields:
- **`payment`** — the per-paycheck salary for that grade (paid automatically by the framework on its paycheck cycle). This is separate from the per-action pay your job script hands out. Don't double-count: if the job already gives a salary, your per-loop pay can be smaller.
- **`isboss`** — grade can use the boss/management menu (hire/fire/set grade, society funds).
- **`bankAuth`** — grade can access society funds.
- **`whitelisted`** — job can't be taken via a normal job-changer; must be granted. The framework enforces who *has* it, but your script still must enforce on-duty/grade for actions (see Hard rules).

## Setting a player's job (server-side)

From your script (e.g. a job center NPC, or an admin command), assign the job server-side:

```lua
local player = exports.qbx_core:GetPlayer(src)
player.Functions.SetJob('mechanic', 2)  -- jobname, grade level
```

For whitelisted jobs this is typically done by a boss via the management menu or by an admin — not self-served. Always validate the *caller's* authority before calling `SetJob` for someone else.

## Reading the job in checks

Everywhere you gate behaviour:

```lua
local job   = player.PlayerData.job.name          -- 'mechanic'
local grade = player.PlayerData.job.grade.level   -- 2
local onDuty = player.PlayerData.job.onduty       -- bool
local isBoss = player.PlayerData.job.isboss       -- bool
```

Client-side, the same data is on `QBX.PlayerData.job` (via `exports.qbx_core:GetPlayerData()` or the `'qbx_core:client:onJobUpdate'` event). Use the client copy only for UX (showing/hiding menu options); the **server** copy is the one that authorizes rewards.

## QBCore / ESX

- **QBCore**: same shape, in `qb-core/shared/jobs.lua`. Grades use `name`/`payment`/`isboss`. `whitelisted` flag exists. Read job via `Player.PlayerData.job`.
- **ESX**: jobs and grades live in **database tables** (`jobs`, `job_grades`), not a Lua file — insert rows, or use a job-management resource. Read job via `xPlayer.getJob()` which returns `{ name, grade, grade_name, grade_label, ... }`. Salary is the `salary` column on `job_grades`.

See `frameworks-jobs.md` for the full API map.
