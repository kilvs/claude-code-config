# NUI Focus & Lifecycle — the part everyone gets wrong

The single most common NUI bug is a stuck cursor / trapped player, and it's always a focus that was taken but never released. This file is the discipline that prevents it. Read it for any interactive (focus-taking) NUI and for any "cursor stuck / can't move / won't close" bug.

## `SetNuiFocus(focus, cursor)` — what the two args mean

```lua
SetNuiFocus(hasFocus, hasCursor)
```

- **`hasFocus`** (bool) — does the NUI capture keyboard/mouse *input*? `true` means key presses and clicks go to the web page instead of the game. The player can't move/shoot while this is `true`.
- **`hasCursor`** (bool) — is the mouse *cursor* shown and movable over the page? Usually `true` together with focus for a clickable menu.

Common combinations:
- `SetNuiFocus(true, true)` — interactive menu/panel: page gets input, cursor visible. The player is "in the UI."
- `SetNuiFocus(false, false)` — released: game gets all input back, cursor hidden. The player is back in the game. **This is the state you must always return to.**
- `SetNuiFocus(true, false)` — keyboard-only focus, no cursor (rare; e.g. a text input you drive without a pointer). Use sparingly.
- A **HUD never calls this at all** — see the bottom of this file.

## Why the cursor gets stuck (the core failure)

The bug is structural, not a typo: **a code path takes focus, but some exit from the UI doesn't release it.** The player closes the menu via a route you didn't wire (alt-tab, an action that completes and hides the page, a server-forced close) and `SetNuiFocus(false, false)` never runs — so the game still thinks the NUI owns input. Cursor frozen on screen, character won't move.

The fix is not "remember to release focus everywhere." It's **route every close through one function** so there is exactly one place focus is released, and every exit calls it.

## The single-close-path pattern

One open function, one close function, on the Lua side. Every way the UI can end calls the close function.

```lua
-- client.lua
local isOpen = false

local function openUI(data)
    if isOpen then return end
    isOpen = true
    SetNuiFocus(true, true)
    SendNUIMessage({ type = 'open', data = data })
end

local function closeUI()
    if not isOpen then return end          -- idempotent: safe to call twice
    isOpen = false
    SetNuiFocus(false, false)              -- THE release — the one place it happens
    SendNUIMessage({ type = 'close' })     -- tell the page to hide too
end

-- every exit routes here:
RegisterNUICallback('uiClose', function(_, cb) closeUI(); cb('ok') end)  -- page asked to close
-- a server-forced close:
RegisterNetEvent('myui:forceClose', function() closeUI() end)
-- a keybind to toggle:
RegisterCommand('+openui', function() openUI(currentData) end, false)
RegisterKeyMapping('+openui', 'Open the UI', 'keyboard', 'F2')
```

The `isOpen` guard makes `closeUI()` idempotent — calling it twice (e.g. ESC *and* a button) is harmless. That idempotency is what lets you call it liberally from every exit without double-releasing.

## The ESC / keyboard escape hatch

When the page has focus, the *game's* ESC handling is suppressed — so the page must provide the way out. Handle ESC on the web side and post back to Lua, which routes to `closeUI`:

```js
// app.js
document.addEventListener('keyup', (e) => {
    if (e.key === 'Escape') closeUI();     // page-side close -> post('uiClose') -> Lua closeUI()
});

function closeUI() {
    document.body.classList.remove('visible');
    post('uiClose');                        // the bridge call that triggers Lua's release
}
```

Test it explicitly: open the UI, press ESC, confirm the cursor disappears and you can move *every time*, including mid-action. If ESC ever fails to free you, you have an exit that doesn't route through the close path.

## The full lifecycle, both sides

```
OPEN:   Lua openUI()  -> SetNuiFocus(true,true) + SendNUIMessage('open')
                      -> page shows (.visible), renders data
USE:    page posts callbacks (select/buy/etc) -> Lua handles -> server validates
CLOSE:  any exit -> (page) closeUI() -> post('uiClose')
                  -> Lua closeUI() -> SetNuiFocus(false,false) + SendNUIMessage('close')
                  -> page hides (.visible removed)
```

Both sides end in agreement: Lua thinks it's closed (`isOpen=false`, focus released) and the page is hidden. They must never diverge — a page hidden while Lua still holds focus is the stuck-cursor bug; Lua released while the page still shows is a ghost panel that eats clicks.

## Server-forced close

Sometimes the server needs to close a player's UI (they got cuffed, the shop closed, they were kicked from the menu). The server triggers a client event that calls the same `closeUI()`:

```lua
-- server: TriggerClientEvent('myui:forceClose', src)
-- client: RegisterNetEvent('myui:forceClose', function() closeUI() end)
```

Same close path. Never write a separate "force close" that re-implements focus release — reuse the one function.

## HUDs take no focus

A passive HUD (health bar, money, speedometer, notifications) **must never call `SetNuiFocus`**. It renders on top of the game and lets all input pass through. Two requirements:

1. **Never `SetNuiFocus(true, ...)`** for a HUD — there's nothing to click, so don't trap input.
2. **`pointer-events: none`** on the HUD's elements (CSS) so even though the page is technically on top, mouse events fall through to the game. If a HUD has one interactive widget, set `pointer-events: auto` on *just* that widget and leave the rest `none`.

A HUD updates purely via `SendNUIMessage` (push values in) and draws — no callbacks, no focus, no lifecycle beyond show/hide. That's why HUDs never cause the stuck-cursor bug: they never take focus in the first place.

## Quick focus checklist
- [ ] Exactly one `closeUI()` on each side; every exit routes through it.
- [ ] `closeUI()` is idempotent (guarded by an `isOpen` flag).
- [ ] Every `SetNuiFocus(true, ...)` has a guaranteed matching `SetNuiFocus(false, false)`.
- [ ] ESC on the page posts back and frees the player — tested every time, including mid-action.
- [ ] Server-forced close reuses the same `closeUI()`.
- [ ] HUDs call `SetNuiFocus` never, and use `pointer-events: none`.
