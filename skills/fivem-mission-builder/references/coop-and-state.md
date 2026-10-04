# Co-op & State — groups, sync, join/leave, reward splitting

Solo is one player and one state record — easy. Co-op is where missions break if state isn't planned. The rule from jobs holds doubled here: **the server owns mission state; clients render and request.** Read `mission-engine.md` first; this file is the group layer on top.

## Per-player vs shared progress

Decide per mission (`coop.progress` in the def):

- **shared** — one objective counter for the whole group. "Kill 5 guards" means 5 total, split however. Most co-op missions and all random events use this. Simpler to reason about, and the server is the single source of the count.
- **perPlayer** — each participant has their own progress; the objective completes when *each* (or *a quorum*) finishes. Use for "everyone must reach the extraction" or tutorial-style missions. More state, more sync.

Default to **shared** unless the mission's fiction needs per-player. Store progress on the instance record either way (`inst.progress[objId]` for shared; `inst.progress[objId][cid]` for per-player).

## Party formation and presence

Two patterns:

- **Locked party (directed missions)**: assembled at start via invite/accept or "everyone in the zone now," then frozen — no mid-mission joins. Simplest; avoids backfill.
- **Open join (random events)**: anyone eligible can opt in mid-event (`random-events.md`). Because progress is shared and server-owned, a late joiner just inherits the current objective — no special handling needed beyond adding them to `participants` and syncing.

Assemble a party server-side and validate it (size within `coop.min/max`, each member eligible):
```lua
local function assembleParty(starterSrc, coop)
    local party = { starterSrc }
    -- e.g. pull nearby accepted players, or members of a framework group/phone party
    -- validate each is online, eligible, not already in a mission; cap at coop.max
    return party
end
```

## Authoritative state + state-bag sync

The server mutates state; clients receive pushes. Never let one client's event mutate another client's view directly.

```lua
-- server: any progress change goes through here, then syncs everyone
local function bumpProgress(instId, objId, n, cid)
    local inst = active[instId]; if not inst then return end
    if inst.def.coop.progress == 'shared' then
        inst.progress[objId] = (inst.progress[objId] or 0) + n
    else
        inst.progress[objId] = inst.progress[objId] or {}
        inst.progress[objId][cid] = (inst.progress[objId][cid] or 0) + n
    end
    syncMission(instId)                                      -- push sanitized view to all participants
end
```

Use **state bags** (`Entity(...)` / `Player(...)` / global state) or targeted `TriggerClientEvent` for the push. State bags are idiomatic on Qbox and handle relevancy; for a small fixed party, targeted events are fine too. The client uses the pushed view only to draw blips/markers/text — it holds no authoritative copy.

## Join / leave / disconnect

Handle every way a participant can vanish. Decide the policy per mission and implement it in `playerDropped` and any leave command.

```lua
AddEventHandler('playerDropped', function()
    local src = source
    for instId, inst in pairs(active) do
        if removeParticipant(inst, src) then
            if #inst.participants == 0 then
                failMission(instId, 'abandoned')             -- nobody left → clean up
            else
                syncMission(instId)                          -- continue short-handed
                -- optional: rescale remaining enemies, or pause a defend timer
            end
        end
    end
end)
```

Policies (pick one per mission):
- **Continue short-handed** (most common): the group plays on; maybe rescale difficulty down.
- **Fail on empty** (always): if the last participant leaves, fail + cleanup. Non-negotiable to avoid orphaned instances.
- **Backfill** (random events only): open join already covers this — others can replace the leaver.

Removing a participant must also clear *their* client-side mission UI (`TriggerClientEvent('mission:cleanup', src, instId)` for just that player).

## Distance / relevance scoping

Don't run mission logic or sync for players who aren't involved or are far away.

- Only `participants` receive `mission:sync` and objective blips.
- For events, only announce within a region if you don't want server-wide blips.
- Server-side checks (distance, "all enemies dead") run on the instance, not per-frame per-player — the engine ticks the instance, not every client.

## Reward splitting

At resolve, decide how the `reward` block maps to a group. Server-authoritative (amounts from the def, never client):

- **Full to each** — everyone gets the full reward. Generous; inflationary for big groups. Fine for small directed parties.
- **Split evenly** — `reward.money.amount / #participants` each. Bounds total payout regardless of group size.
- **By contribution** (best for events) — track each participant's credited contribution server-side (kills credited, objectives they completed, damage dealt) and weight the split. Discourages AFK leeching.

```lua
local function giveReward(instId)
    local inst = active[instId]
    local r = inst.def.reward
    if inst.def.coop.progress == 'shared' and r.split == 'even' then
        local per = math.floor(r.money.amount / math.max(1, #inst.participants))
        for _, src in ipairs(inst.participants) do rewardPlayer(src, { money={account=r.money.account, amount=per}, items=r.items }) end
    elseif r.split == 'contribution' then
        -- weight by inst.contribution[cid] (server-tracked), pay proportionally
    else
        for _, src in ipairs(inst.participants) do rewardPlayer(src, r) end   -- full to each
    end
end
```

Whatever the split, the payout itself is the `fivem-job-builder` server-authoritative pattern — re-validate the player still holds the job/eligibility if the reward is gated, and confirm amounts come from the def. A cheater editing a client value can't change what the server pays.

## Co-op correctness checklist
- [ ] Progress mode (`shared`/`perPlayer`) chosen and stored on the instance, server-side.
- [ ] All progress changes go through one server function that then syncs.
- [ ] Clients hold no authoritative state — only a rendered view.
- [ ] `playerDropped` and leave handled with a defined policy; empty instance always fails+cleans.
- [ ] Departing player's client UI cleared.
- [ ] Reward split decided; amounts from the def; payout server-validated.
- [ ] Tested: two clients, one leaves mid-objective; counts stay correct; no orphaned entities.
