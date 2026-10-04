-- sv_security.lua — optional, dependency-free server-side validation helpers.
--
-- Drop this into a resource (server file) so the Golden Rule checks come out identical
-- every time. It uses ox_lib if present (for nicer notifications) but does NOT require it.
--
-- Usage (as a module):
--   local sec = require 'sv_security'        -- if your setup supports require
-- or just paste these functions into your server.lua and call them directly.
--
-- These are CONVENIENCE wrappers around the rules in this skill — they are not a
-- substitute for understanding why each check exists (see rules/*.md). Every function
-- here is server-side; never call validation from the client and trust the result.

local Security = {}

-- Resolve + existence check. Returns the framework player or nil.
-- Swap exports.qbx_core for your framework (see fivem-lua-dev/references/frameworks.md).
function Security.validatePlayer(src)
    if type(src) ~= 'number' or src <= 0 then return nil end
    local ok, player = pcall(function() return exports.qbx_core:GetPlayer(src) end)
    if not ok then return nil end
    return player or nil
end

-- Authorization by job (and optional minimum grade). Returns true/false.
function Security.hasJob(player, jobName, minGrade)
    if not player or not player.PlayerData or not player.PlayerData.job then return false end
    local job = player.PlayerData.job
    if job.name ~= jobName then return false end
    if minGrade and (job.grade and job.grade.level or 0) < minGrade then return false end
    return true
end

-- Golden Rule 3: server-side distance. Compares the player's SERVER-known ped coords
-- to a server-owned point. Returns true if within radius.
function Security.validateDistance(src, coords, radius)
    if type(src) ~= 'number' then return false end
    if type(radius) ~= 'number' then radius = 5.0 end
    local ped = GetPlayerPed(src)
    if not ped or ped == 0 then return false end
    local p = GetEntityCoords(ped)
    -- accept a vec3 or a plain {x,y,z}
    local x = coords.x or coords[1]
    local y = coords.y or coords[2]
    local z = coords.z or coords[3]
    if not x or not y or not z then return false end
    local dx, dy, dz = p.x - x, p.y - y, p.z - z
    return (dx * dx + dy * dy + dz * dz) <= (radius * radius)
end

-- Golden Rule 4: per-player cooldown / debounce. Returns true if the action is ALLOWED
-- (i.e. enough time has passed), and records the timestamp. Reject when it returns false.
local _last = {}   -- [src] = { [key] = ms }
function Security.rateLimit(src, key, ms)
    if type(src) ~= 'number' then return false end
    ms = type(ms) == 'number' and ms or 1000
    local now = GetGameTimer()
    _last[src] = _last[src] or {}
    local prev = _last[src][key]
    if prev and (now - prev) < ms then return false end
    _last[src][key] = now
    return true
end

-- Golden Rule 2: numeric amount validation. Returns a clean integer in [min, max], or nil.
function Security.validateAmount(v, min, max)
    v = tonumber(v)
    if not v then return nil end
    v = math.floor(v)                       -- no fractional quantities
    if min and v < min then return nil end
    if max and v > max then return nil end
    return v
end

-- Golden Rule 2: whitelist membership. `set` is a table used as a set ({ apple = true })
-- OR a list ({ 'apple', 'pear' }). Returns true if `value` is an allowed member.
function Security.inWhitelist(value, set)
    if type(set) ~= 'table' then return false end
    if set[value] ~= nil then return true end           -- set-style: { apple = true }
    for _, v in ipairs(set) do if v == value then return true end end  -- list-style
    return false
end

-- Convenience: server-side notify that uses ox_lib if present, else a chat fallback.
function Security.notify(src, msg, kind)
    if exports['ox_lib'] then
        exports.ox_lib:notify(src, { type = kind or 'inform', description = msg })
    else
        TriggerClientEvent('chat:addMessage', src, { args = { 'Server', msg } })
    end
end

-- Clean up per-player state on disconnect so it doesn't leak or misattribute.
AddEventHandler('playerDropped', function()
    local src = source
    _last[src] = nil
end)

return Security
