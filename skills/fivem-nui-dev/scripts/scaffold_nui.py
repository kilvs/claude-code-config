#!/usr/bin/env python3
"""
scaffold_nui.py — generate a runnable plain HTML/CSS/JS FiveM NUI resource.

Emits a complete resource with the manifest, the Lua bridge (SendNUIMessage +
RegisterNUICallback + correct SetNuiFocus open/close handling), and an html/ page
wired with the message listener, a fetch helper, and a single close path. No build
step, no npm — the game loads the files directly.

Usage:
    python scaffold_nui.py --name myshop --kind menu  --output ./resources
    python scaffold_nui.py --name statushud --kind hud --output ./resources
    python scaffold_nui.py --name jobpanel  --kind panel --output ./resources

Kinds:
    menu  — interactive list menu (takes focus, single close path, ESC escape hatch)
    hud   — passive overlay (NO focus, pointer-events:none, push-updated)
    panel — interactive panel with data + an action callback (takes focus)

Output is runnable but minimal — fill the TODOs (content, message types, styling).
Never emits real keys or credentials.
"""
import argparse
import os
import sys
import textwrap


def fxmanifest(name, kind):
    server = "    'server.lua',\n" if kind != "hud" else ""
    server_block = ("\nserver_scripts {\n    'server.lua',\n}\n" if kind != "hud" else "")
    return textwrap.dedent(f"""\
    fx_version 'cerulean'
    game 'gta5'
    lua54 'yes'

    name '{name}'
    description 'FiveM NUI: {name} ({kind}) — plain HTML/CSS/JS, no build step'
    author 'you'
    version '0.1.0'

    ui_page 'html/index.html'

    files {{
        'html/index.html',
        'html/style.css',
        'html/app.js',
        -- list any fonts/images the page loads here, e.g.:
        -- 'html/fonts/Inter.woff2',
    }}

    client_scripts {{
        'client.lua',
    }}
    """) + server_block


def client_lua(name, kind):
    if kind == "hud":
        return textwrap.dedent(f"""\
        -- {name} — CLIENT (HUD). A HUD is passive: it NEVER takes focus.
        -- It only pushes data into the page; the page draws it. No callbacks, no SetNuiFocus.

        local function pushHud(payload)
            SendNUIMessage({{ type = 'hud', data = payload }})
        end

        -- Example: throttle updates to a few times a second (don't spam every frame).
        CreateThread(function()
            while true do
                Wait(250)   -- 4x/sec; widen for slower-changing values
                local ped = PlayerPedId()
                pushHud({{
                    health = math.max(0, GetEntityHealth(ped) - 100),   -- TODO real values
                    armor  = GetPedArmour(ped),
                }})
            end
        end)

        -- Show/hide the HUD (no focus involved).
        RegisterNetEvent('{name}:setVisible', function(visible)
            SendNUIMessage({{ type = visible and 'show' or 'hide' }})
        end)
        """)

    # menu / panel share the focus-taking bridge
    extra_open_data = ""
    callback = ""
    if kind == "menu":
        extra_open_data = textwrap.dedent("""\
            data = {
                title = 'Menu',
                items = {                                  -- TODO real items
                    { id = 'opt_a', label = 'Option A' },
                    { id = 'opt_b', label = 'Option B' },
                },
            },""")
        callback = textwrap.dedent(f"""\

        -- Player chose an item. data.id came FROM THE PAGE = untrusted.
        RegisterNUICallback('select', function(data, cb)
            -- Validate server-side before doing anything that matters:
            TriggerServerEvent('{name}:select', data.id)    -- server re-checks eligibility/bounds
            cb('ok')
        end)
        """)
    else:  # panel
        extra_open_data = textwrap.dedent("""\
            data = {
                title = 'Panel',
                fields = { name = 'TODO', balance = 0 },    -- TODO real data
            },""")
        callback = textwrap.dedent(f"""\

        -- Player triggered the panel's action. payload came FROM THE PAGE = untrusted.
        RegisterNUICallback('action', function(data, cb)
            TriggerServerEvent('{name}:action', data)        -- server validates everything
            cb('ok')
        end)
        """)

    return textwrap.dedent(f"""\
    -- {name} — CLIENT ({kind}). Interactive: takes focus, with ONE close path.
    -- The page is an untrusted client; validate every callback server-side (server.lua).

    local isOpen = false
    local currentData = nil

    local function openUI(data)
        if isOpen then return end
        isOpen = true
        currentData = data
        SetNuiFocus(true, true)                             -- take input + cursor
        SendNUIMessage({{
            type = 'open',
    {textwrap.indent(extra_open_data, '        ')}
        }})
    end

    -- THE single close path. Idempotent. Every exit routes here.
    local function closeUI()
        if not isOpen then return end
        isOpen = false
        SetNuiFocus(false, false)                           -- release input + cursor (the fix for stuck cursor)
        SendNUIMessage({{ type = 'close' }})
    end

    -- Page asked to close (button / ESC) -> release focus here.
    RegisterNUICallback('uiClose', function(_, cb)
        closeUI()
        cb('ok')
    end)
    {callback}
    -- Open via a keybind (F2 by default; change in settings).
    RegisterCommand('+open_{name}', function() openUI(currentData) end, false)
    RegisterCommand('-open_{name}', function() end, false)
    RegisterKeyMapping('+open_{name}', 'Open {name}', 'keyboard', 'F2')

    -- Server can force-close (reuses the SAME close path — never re-implement focus release).
    RegisterNetEvent('{name}:forceClose', function() closeUI() end)

    -- Release focus if the resource stops while the UI is open.
    AddEventHandler('onResourceStop', function(res)
        if res == GetCurrentResourceName() and isOpen then SetNuiFocus(false, false) end
    end)
    """)


def server_lua(name, kind):
    if kind == "hud":
        return None
    action_event = "select" if kind == "menu" else "action"
    return textwrap.dedent(f"""\
    -- {name} — SERVER. The NUI is an untrusted client. Validate every action here.
    -- This is the same trust boundary as any client event
    -- (see fivem-lua-dev/references/security.md).

    RegisterNetEvent('{name}:{action_event}', function(payload)
        local src = source
        -- payload came from the player's NUI = hostile input. Before doing anything:
        --   * confirm the player is allowed to do this (job/grade/distance/state)
        --   * never trust a price/amount/id from the payload — re-derive from server config
        --   * bound and type-check every field
        -- TODO: validate, then act (give item / take money / etc) using server-owned values.
        print(('[{name}] {action_event} from %s: %s'):format(src, json.encode(payload or {{}})))
    end)
    """)


def html_index(name, kind):
    if kind == "hud":
        return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="style.css">
        </head>
        <body class="hud">
            <!-- HUD: anchored, non-interactive overlay. No buttons, no focus. -->
            <div id="hud">
                <div class="stat"><span class="label">Health</span> <span id="health">100</span>%</div>
                <div class="stat"><span class="label">Armor</span> <span id="armor">0</span>%</div>
            </div>
            <script src="app.js"></script>
        </body>
        </html>
        """)
    title = "Menu" if kind == "menu" else "Panel"
    body = textwrap.dedent("""\
            <div id="items"></div>""") if kind == "menu" else textwrap.dedent("""\
            <div id="fields"></div>
            <button id="actionBtn">Do action</button>""")
    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div id="root" class="panel">
            <header id="title">{title}</header>
    {textwrap.indent(body, '        ')}
            <button id="closeBtn">Close</button>
        </div>
        <script src="app.js"></script>
    </body>
    </html>
    """)


def html_style(name, kind):
    base = textwrap.dedent("""\
    html, body {
        margin: 0; height: 100%;
        background: transparent;            /* never paint the whole page — it'd hide the game */
        overflow: hidden;
        font-family: 'Segoe UI', system-ui, sans-serif;
        color: #f2f4f8;
        font-size: 1.6vh;                   /* scales with screen height: 1080p -> 4K */
    }
    """)
    if kind == "hud":
        return base + textwrap.dedent("""\

    /* HUD: passive overlay. pointer-events:none so all clicks reach the game. */
    body.hud { pointer-events: none; }
    #hud {
        position: fixed; left: 2vw; bottom: 3vh;
        display: flex; gap: .8vw;
        pointer-events: none;
    }
    #hud .stat {
        background: rgba(0,0,0,.45);        /* tinted so it reads over any scene */
        padding: .5vh 1vw; border-radius: .6vh;
        font-weight: 600;
    }
    #hud .label { opacity: .7; margin-right: .3vw; }
    """)
    # menu / panel
    return base + textwrap.dedent("""\

    /* Interactive panel: hidden by default; .visible reveals it. */
    body { opacity: 0; pointer-events: none; transition: opacity .15s ease; }
    body.visible { opacity: 1; pointer-events: auto; }

    .panel {
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -48%);
        min-width: 32vh; max-width: 50vh;
        background: rgba(20,22,28,.94);     /* solid-ish so text reads over any scene */
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 1.2vh;
        box-shadow: 0 1vh 5vh rgba(0,0,0,.5);
        padding: 2vh;
        transition: transform .15s ease;
    }
    body.visible .panel { transform: translate(-50%, -50%); }

    header { font-size: 2.2vh; font-weight: 700; margin-bottom: 1.5vh; }

    #items button, #actionBtn, #closeBtn {
        display: block; width: 100%;
        margin: .6vh 0; padding: 1.2vh;
        background: rgba(255,255,255,.06); color: inherit;
        border: 1px solid rgba(255,255,255,.1); border-radius: .8vh;
        font: inherit; cursor: pointer; text-align: left;
    }
    #items button:hover, #actionBtn:hover { background: rgba(255,255,255,.14); }
    #closeBtn { text-align: center; margin-top: 1.5vh; background: rgba(220,60,60,.18); }
    #fields { margin-bottom: 1vh; line-height: 1.8; }
    """)


def html_app(name, kind):
    if kind == "hud":
        return textwrap.dedent("""\
        // HUD: passive. Receive pushed values from Lua and draw. No focus, no callbacks.
        window.addEventListener('message', (event) => {
            const msg = event.data;
            switch (msg.type) {
                case 'hud':
                    if (msg.data.health !== undefined)
                        document.getElementById('health').textContent = msg.data.health;
                    if (msg.data.armor !== undefined)
                        document.getElementById('armor').textContent = msg.data.armor;
                    break;
                case 'hide': document.getElementById('hud').style.display = 'none'; break;
                case 'show': document.getElementById('hud').style.display = 'flex'; break;
            }
        });
        """)

    # menu / panel — full bridge with single close path + ESC escape hatch
    resource_helper = textwrap.dedent("""\
        // Resolve this resource's name for the fetch URL (works without a build step).
        function resName() {
            return (typeof GetParentResourceName === 'function')
                ? GetParentResourceName()
                : (window.RESOURCE_NAME || 'nui');
        }

        // One fetch helper for all callbacks. Always returns a (possibly empty) object.
        function post(name, data = {}) {
            return fetch(`https://${resName()}/${name}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json; charset=UTF-8' },
                body: JSON.stringify(data),
            }).then(r => r.json().catch(() => ({}))).catch(() => ({}));
        }

        // THE single close path on the page side -> tells Lua to release focus.
        function closeUI() {
            document.body.classList.remove('visible');
            post('uiClose');
        }

        // ESC always frees the player (the escape hatch).
        document.addEventListener('keyup', (e) => { if (e.key === 'Escape') closeUI(); });
        document.getElementById('closeBtn').onclick = () => closeUI();
        """)

    if kind == "menu":
        render = textwrap.dedent("""\

        function render(data) {
            document.getElementById('title').textContent = data.title || 'Menu';
            const box = document.getElementById('items');
            box.innerHTML = '';
            (data.items || []).forEach((item) => {
                const b = document.createElement('button');
                b.textContent = item.label;
                b.onclick = () => post('select', { id: item.id });   // action out -> Lua validates
                box.appendChild(b);
            });
        }

        window.addEventListener('message', (event) => {
            const msg = event.data;
            switch (msg.type) {
                case 'open':
                    if (msg.resource) window.RESOURCE_NAME = msg.resource;
                    render(msg.data || {});
                    document.body.classList.add('visible');
                    break;
                case 'update': render(msg.data || {}); break;
                case 'close':  document.body.classList.remove('visible'); break;
            }
        });
        """)
    else:  # panel
        render = textwrap.dedent("""\

        function render(data) {
            document.getElementById('title').textContent = data.title || 'Panel';
            const f = data.fields || {};
            document.getElementById('fields').innerHTML =
                Object.entries(f).map(([k, v]) => `<div><b>${k}:</b> ${v}</div>`).join('');
        }

        document.getElementById('actionBtn').onclick = () => post('action', { /* TODO payload */ });

        window.addEventListener('message', (event) => {
            const msg = event.data;
            switch (msg.type) {
                case 'open':
                    if (msg.resource) window.RESOURCE_NAME = msg.resource;
                    render(msg.data || {});
                    document.body.classList.add('visible');
                    break;
                case 'update': render(msg.data || {}); break;
                case 'close':  document.body.classList.remove('visible'); break;
            }
        });
        """)
    return resource_helper + render


def main():
    ap = argparse.ArgumentParser(description="Scaffold a plain HTML/CSS/JS FiveM NUI resource.")
    ap.add_argument("--name", required=True, help="resource name (lowercase, no spaces)")
    ap.add_argument("--kind", default="menu", choices=["menu", "hud", "panel"])
    ap.add_argument("--output", required=True, help="output directory (resource folder created inside)")
    args = ap.parse_args()

    name = args.name.strip().lower().replace(" ", "_")
    if not name:
        print("error: --name is empty", file=sys.stderr); sys.exit(1)

    out = os.path.join(args.output, name)
    os.makedirs(os.path.join(out, "html"), exist_ok=True)

    files = {
        "fxmanifest.lua":   fxmanifest(name, args.kind),
        "client.lua":       client_lua(name, args.kind),
        "html/index.html":  html_index(name, args.kind),
        "html/style.css":   html_style(name, args.kind),
        "html/app.js":      html_app(name, args.kind),
    }
    srv = server_lua(name, args.kind)
    if srv is not None:
        files["server.lua"] = srv

    for fname, content in files.items():
        with open(os.path.join(out, fname), "w") as fh:
            fh.write(content)

    print(f"Scaffolded '{name}' ({args.kind}) -> {out}")
    print("Files: " + ", ".join(files.keys()))
    print()
    print("Next:")
    print("  1. Fill the TODOs: real content in html/, real message types, your styling.")
    if args.kind != "hud":
        print("  2. Validate every callback in server.lua before acting (NUI = untrusted client).")
        print("  3. Test the close path: open, press ESC, confirm cursor frees EVERY time.")
    else:
        print("  2. HUD takes no focus — confirm pointer-events:none lets clicks reach the game.")
    print(f"  4. Add to server.cfg: ensure {name}")
    print("  5. Debug the web side via CEF devtools at http://localhost:13172/ while in-game.")
    print("  No build step or npm required — the game loads the html/ files directly.")


if __name__ == "__main__":
    main()
