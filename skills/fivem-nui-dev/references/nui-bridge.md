# The NUI Bridge — manifest, message protocol, callbacks, debugging

The core of the skill. A NUI is a web page; the bridge is how your Lua and that page talk. Read this first for any NUI work. Focus/cursor handling has its own file (`nui-focus-lifecycle.md`) because it's the most error-prone part — but the data flow is here.

## Contents
1. Manifest wiring (`ui_page` + `files`)
2. The two directions of the bridge
3. The named-message protocol
4. Data in (Lua → NUI)
5. Actions out (NUI → Lua) + the callback response
6. The page skeleton
7. Debugging with CEF devtools

---

## 1. Manifest wiring

The game needs to know which page is your NUI and which files to ship. In `fxmanifest.lua`:

```lua
fx_version 'cerulean'
game 'gta5'

ui_page 'html/index.html'      -- the page the game loads as this resource's NUI

files {
    'html/index.html',
    'html/style.css',
    'html/app.js',
    -- list every asset the page loads at runtime: fonts, images, sounds
    'html/fonts/*.ttf',
    'html/img/*.png',
}

client_scripts { 'client.lua' }   -- the Lua side of the bridge
```

Two things people miss: **every file the page references must be in `files{}`** (a font or image not listed will 404 in-game even though it works in a browser), and the path is relative to the resource root. With this, plain HTML/CSS/JS runs directly — no build.

## 2. The two directions

| Direction | Lua side | Web side |
|---|---|---|
| Lua → NUI (data) | `SendNUIMessage(table)` | `window.addEventListener('message', e => { ... e.data ... })` |
| NUI → Lua (actions) | `RegisterNUICallback(name, cb)` | `fetch('https://<resource>/<name>', { method:'POST', body: JSON.stringify(data) })` |
| Focus control | `SetNuiFocus(focus, cursor)` | (Lua-only; see `nui-focus-lifecycle.md`) |

`SendNUIMessage` serializes a Lua table to JSON and posts it to the page. `fetch` to the special `https://<resource>/...` URL is intercepted by FiveM and routed to your matching `RegisterNUICallback`. The resource name in the fetch URL is **your resource's name** — use `GetParentResourceName()` from the page (see §6) so it works regardless of what the folder is called.

## 3. The named-message protocol

Don't invent ad-hoc messages. Use a small, explicit vocabulary: every Lua→NUI message carries a `type` (or `action`) field the page switches on, and every NUI→Lua callback has a clear name. This keeps both sides in sync and easy to reason about.

A typical menu's vocabulary:
- Lua → NUI: `{ type = 'open', data = {...} }`, `{ type = 'close' }`, `{ type = 'update', data = {...} }`
- NUI → Lua callbacks: `select` (player chose an option), `uiClose` (player closed it)

That's usually all you need. Add to it deliberately, not reflexively.

## 4. Data in (Lua → NUI)

```lua
-- client.lua — open the menu with some data
local function openMenu(items)
    SetNuiFocus(true, true)                 -- see nui-focus-lifecycle.md
    SendNUIMessage({ type = 'open', data = { items = items } })
end
```

```js
// app.js — receive and render
window.addEventListener('message', (event) => {
    const msg = event.data;
    switch (msg.type) {
        case 'open':
            renderItems(msg.data.items);
            document.body.classList.add('visible');
            break;
        case 'update':
            renderItems(msg.data.items);
            break;
        case 'close':
            closeUI();                       // the page's own close (see §5)
            break;
    }
});
```

`SendNUIMessage` only reaches the page if the resource's NUI is loaded (it always is, once the resource starts) — but the page only *acts* on it once its listener is attached, so attach the listener at top level, not behind a delayed init.

## 5. Actions out (NUI → Lua) + the callback response

The page posts an action; Lua handles it and **must call the callback** `cb` to complete the fetch (or the page's `await` hangs).

```js
// app.js — a small fetch helper, resource-name-safe
function post(name, data = {}) {
    return fetch(`https://${GetParentResourceName()}/${name}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=UTF-8' },
        body: JSON.stringify(data),
    }).then(r => r.json().catch(() => ({})));   // tolerate empty responses
}

// the page's helper to learn the resource name (works for plain pages)
function GetParentResourceName() {
    return window.GetParentResourceName ? window.GetParentResourceName()
        : (window.invokeNative ? 'nui-frame-app' : resourceNameFromUrl());
}
```

In practice the reliable pattern is to have Lua tell the page its own name on open (`SendNUIMessage({ type='open', resource = GetCurrentResourceName(), ... })`) and store it, OR use the well-known global. Keep one helper; don't scatter raw fetch calls.

```js
// player clicks 'buy' on an item
buyBtn.onclick = () => post('select', { itemId: chosenId, qty: 1 });
```

```lua
-- client.lua — handle the action, ALWAYS call cb to finish the fetch
RegisterNUICallback('select', function(data, cb)
    -- data.itemId / data.qty came from the page = UNTRUSTED. Validate server-side.
    TriggerServerEvent('myshop:requestBuy', data.itemId, data.qty)   -- server re-checks everything
    cb('ok')                                                          -- complete the fetch
end)

RegisterNUICallback('uiClose', function(_, cb)
    closeMenu()        -- the Lua close path: hide focus etc. (nui-focus-lifecycle.md)
    cb('ok')
end)
```

**The callback `cb` must always be called** — even on rejection (`cb('ok')` or `cb({ ok = false })`). Forgetting it leaves the page's `fetch` pending forever, which manifests as "buttons stop responding."

**Trust boundary (restated):** `data` from a callback is whatever the page sent, and the page is a client a cheater fully controls (they can open devtools and `fetch` any callback with any body). The Lua callback must not act on a NUI-supplied price, amount, or id without the server re-validating it — same rule as any client event (`fivem-lua-dev/references/security.md`).

## 6. The page skeleton

A correct plain page wires the listener and a close path up front:

```html
<!-- html/index.html -->
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="style.css"></head>
<body>            <!-- starts hidden; CSS .visible reveals it -->
    <div id="menu" class="menu">
        <header>Shop</header>
        <ul id="items"></ul>
        <button id="closeBtn">Close</button>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

```js
// app.js (top level — listener attached immediately)
let resourceName = 'nui';   // overwritten on 'open' if Lua sends it

window.addEventListener('message', (e) => { /* §4 switch */ });

document.getElementById('closeBtn').onclick = () => closeUI();

// ESC frees the player — the escape hatch (nui-focus-lifecycle.md)
document.addEventListener('keyup', (e) => { if (e.key === 'Escape') closeUI(); });

function closeUI() {
    document.body.classList.remove('visible');
    post('uiClose');           // tell Lua to release focus
}
```

## 7. Debugging with CEF devtools

The NUI is Chromium, so it has devtools — your main debugging tool for the web side.

- With the resource running, open `http://localhost:13172/` in a browser **while the game is running** (the CEF/NUI devtools port) to get a list of inspectable NUI pages; click yours for a full DevTools (console, elements, network).
- `console.log` in `app.js` shows up there; fetch calls appear in the Network tab so you can see if a callback is firing and what it returned.
- A page that works in a normal browser but is blank/broken in-game is almost always a **missing `files{}` entry** (404 on an asset) or an absolute path that resolves wrong — check the Network tab for 404s.
- `SendNUIMessage` not arriving → confirm the listener is attached at top level and you're switching on the right `type`.
- A hung button → a `RegisterNUICallback` that never called `cb`.

For the Lua side (events reaching the server, validation), that's the `fivem-lua-dev` toolset, not the web devtools.
