# World Entities: Peds, Vehicles, Objects, Physics & Placement

Scripting the game world — spawning and controlling entities, manipulating their physics, and placing gameplay (shops, jobs, interactions) into the map. This is mostly **client-side** work (the game world lives on the client), but with the trust boundary from `security.md` always in mind: the server decides *whether* something happens, the client *renders* it. For events between realms see `lua-scripting.md`.

## Contents
1. Entities and the model/streaming basics
2. Peds (NPCs)
3. Vehicles
4. Objects / props
5. Entity physics via natives
6. Animations, particles (ptfx), sound
7. World placement: markers, blips, zones
8. Networking & cleanup

---

## 1. Entities and the model/streaming basics

Peds, vehicles, and objects are all **entities**. Spawning any of them follows the same shape: request the model, wait for it to load, create the entity, then release the model. Models are referenced by name (hashed) and must be streamed in before use.

```lua
local function loadModel(model)
    local hash = type(model) == 'number' and model or joaat(model)
    RequestModel(hash)
    while not HasModelLoaded(hash) do Wait(0) end   -- bounded loop; yields each frame
    return hash
end
```

Always `SetModelAsNoLongerNeeded(hash)` after spawning so memory frees. Forgetting model cleanup across many spawns is a common slow leak.

## 2. Peds (NPCs)

Spawn a ped:
```lua
local hash = loadModel('a_m_y_business_01')
local ped = CreatePed(4, hash, x, y, z, heading, false, true)
SetModelAsNoLongerNeeded(hash)
```

Make a ped useful:
- **Freeze / invincible / static NPC** (e.g. a shopkeeper): `FreezeEntityPosition(ped, true)`, `SetEntityInvincible(ped, true)`, `SetBlockingOfNonTemporaryEvents(ped, true)` (stops it fleeing/reacting), `SetPedDiesWhenInjured(ped, false)`.
- **Scenarios** — canned looping behaviours: `TaskStartScenarioInPlace(ped, 'WORLD_HUMAN_CLIPBOARD', 0, true)`. Scenario names are GTA-defined; look them up rather than guessing.
- **AI tasks** — `TaskGoToCoordAnyMeans`, `TaskCombatPed`, `TaskWanderStandard`, etc. Tasks are issued client-side to the ped's owner.
- **Relationship groups** control who's hostile/friendly: `AddRelationshipGroup`, `SetPedRelationshipGroupHash`, `SetRelationshipBetweenGroups`. Use these for guards/enemies instead of hacky aggro scripts.

A shopkeeper NPC is the canonical pattern: spawn frozen + invincible + non-reactive at the counter, attach an interaction (zone/target, §7) that fires a **server-validated** purchase event (`security.md`).

## 3. Vehicles

```lua
local hash = loadModel('adder')
local veh = CreateVehicle(hash, x, y, z, heading, true, false)  -- networked = true
SetModelAsNoLongerNeeded(hash)
SetPedIntoVehicle(PlayerPedId(), veh, -1)  -- -1 = driver seat
```

Common operations: `SetVehicleNumberPlateText`, `SetVehicleEngineOn`, `SetVehicleDoorsLocked(veh, 2)` (2 = locked), `SetVehicleColours`, `SetVehicleModKit`/`SetVehicleMod` (tuning). Fuel, keys, and persistence are usually **framework/script concerns** (e.g. `ox_fuel`, a keys script), not raw natives — don't reinvent them if your framework provides them.

Spawning vehicles from a client request is a classic exploit vector: a naive "spawn me this car" net event lets cheaters spawn anything. Gate it server-side (job/permission, whitelist of allowed models) per `security.md`.

## 4. Objects / props

```lua
local hash = loadModel('prop_barrier_work05')
local obj = CreateObject(hash, x, y, z, true, true, false)
SetModelAsNoLongerNeeded(hash)
PlaceObjectOnGroundProperly(obj)
```

**Attaching** a prop to a ped (e.g. a clipboard, a phone) is extremely common:
```lua
AttachEntityToEntity(obj, ped, GetPedBoneIndex(ped, 28422), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, true, true, false, true, 1, true)
```
Bone indices and offsets are fiddly — copy known-good values for the bone you want (hand, head) rather than guessing, and tweak offsets live.

## 5. Entity physics via natives

FiveM does **not** give you a scriptable physics engine — you use GTA's existing RAGE physics and nudge entities through natives. The useful, modest toolbox:

- **Velocity**: `SetEntityVelocity(entity, x, y, z)` / `GetEntityVelocity`. Direct velocity sets feel unnatural for big changes; use sparingly.
- **Forces** (more physical): `ApplyForceToEntity(...)` pushes an entity with a force vector at an offset — good for explosions, knockbacks. Many parameters; check the native reference for the force-type and component args.
- **Freeze**: `FreezeEntityPosition(entity, true)` locks an entity in place (also stops physics on it) — used for static props/NPCs and to stop a vehicle drifting before you're ready.
- **Ragdoll**: `SetPedToRagdoll(ped, time, time2, type, ...)` to knock a ped into physics ragdoll; `SetPedCanRagdoll(ped, bool)` to allow/deny.
- **Gravity / collision**: `SetEntityHasGravity`, `SetEntityCollision(entity, enabled, keepPhysics)`.
- **Heading/rotation/coords**: `SetEntityCoords`, `SetEntityHeading`, `SetEntityRotation`.

Physics runs on the entity's **network owner** (usually the nearest player). Applying force to an entity you don't own may not replicate; for reliable shared physics, the owner applies it, or you accept it's a local effect. Don't expect to script novel physics behaviour — you're directing the existing simulation, not replacing it.

## 6. Animations, particles (ptfx), sound

**Animations** load from a dictionary, then play on a ped:
```lua
RequestAnimDict('amb@world_human_clipboard@male@idle_a')
while not HasAnimDictLoaded('amb@world_human_clipboard@male@idle_a') do Wait(0) end
TaskPlayAnim(ped, 'amb@world_human_clipboard@male@idle_a', 'idle_c', 8.0, -8.0, -1, 49, 0, false, false, false)
```
(`ox_lib` and frameworks often wrap anim playback; prefer those for player-facing actions with progress bars, since they handle interruption.)

**Particle effects (ptfx)** need an asset loaded first: `RequestNamedPtfxAsset('core')`, then `UseParticleFxAssetNextCall('core')` and `StartParticleFxLoopedOnEntity(...)` / `StartParticleFxNonLoopedAtCoord(...)`.

**Sound**: `PlaySoundFrontend` for UI sounds; `PlaySoundFromEntity`/`PlaySoundFromCoord` for positional. Custom audio is its own data-file/streaming topic — see `maps-and-streaming.md`.

## 7. World placement: markers, blips, zones

This is the practical "level design" of an RP server — putting interaction points into the world. Three layers:

**Blips** (map/minimap icons):
```lua
local blip = AddBlipForCoord(x, y, z)
SetBlipSprite(blip, 52); SetBlipColour(blip, 2); SetBlipAsShortRange(blip, true)
BeginTextCommandSetBlipName('STRING'); AddTextComponentSubstringPlayerName('Shop'); EndTextCommandSetBlipName(blip)
```

**Markers** (the in-world cylinders/arrows). Drawn every frame, so only draw when the player is near:
```lua
CreateThread(function()
    while true do
        local sleep = 1000
        local p = GetEntityCoords(PlayerPedId())
        if #(p - vec3(x, y, z)) < 20.0 then
            sleep = 0
            DrawMarker(1, x, y, z - 1.0, 0,0,0, 0,0,0, 1.5,1.5,0.5, 0,150,255,100, false,false,2,false)
        end
        Wait(sleep)   -- back off when far away (resmon!)
    end
end)
```

**Zones / targeting** — the modern, cheaper way. Instead of per-frame distance checks, define a zone or a targetable point once and let the library handle detection:
- `ox_target` — look-at/interact on entities, models, or box/sphere zones with an on-select callback.
- `ox_lib` zones (`lib.zones.box`/`sphere`) — enter/exit/inside callbacks.

```lua
exports.ox_target:addBoxZone({
    coords = vec3(x, y, z), size = vec3(2, 2, 2), rotation = 0,
    options = { { label = 'Open Shop', icon = 'fa-store',
                  onSelect = function() TriggerServerEvent('shop:open') end } }
})
```
Prefer zones/target over hand-rolled marker loops for anything non-trivial — better performance and consistent UX. The interaction always fires a **server-validated** event for anything that matters.

## 8. Networking & cleanup

- `CreateVehicle`/`CreatePed`/`CreateObject` with the networked flag registers the entity across clients; local (non-networked) entities are visible only to the spawner — choose deliberately.
- For server-authoritative spawning of networked entities, modern code uses server-side `CreateVehicle`/`CreatePed` (server natives) so the server owns creation, then clients see it.
- **Always clean up**: `DeleteEntity(entity)` (or `DeleteVehicle`/`DeletePed`/`DeleteObject`). Orphaned entities accumulate and degrade the server. On resource stop, delete what you spawned (`AddEventHandler('onResourceStop', ...)`).
- Networked-entity ownership migrates between players; don't assume you still own an entity you spawned. Mutations to a networked entity should be done by its current owner or via server logic.
