# Server Setup, Hosting & server.cfg

From nothing to a running server, local then public. Version numbers, URLs, and "recommended build" change often — confirm specifics at `docs.fivem.net` and the Cfx.re portal when they matter.

## Contents
1. What you're installing (the pieces)
2. Local install (Windows) — step by step
3. txAdmin first run, Cfx.re account & server key
4. MySQL for framework servers
5. server.cfg anatomy
6. Local play: port forwarding
7. Going public: VPS + server list
8. Hosting cost reality

---

## 1. What you're installing (the pieces)

- **FXServer** — the FiveM server software, distributed as **artifacts** (a versioned build you download and extract). Contains `FXServer.exe` (Windows) / `run.sh` (Linux). txAdmin ships *inside* it.
- **txAdmin** — the web-based control panel for FXServer (start/stop, console, recipes, players, bans, scheduled restarts). Free, built in, opens in your browser on first run.
- **Cfx.re account + server key** — a free key tying your server to your Cfx.re account; required for the server to appear in the list and (above low player counts) to run. Generate at the Cfx.re portal's server-key page.
- **MySQL** (framework servers only) — stores players, characters, jobs, money, inventory. Vanilla/standalone servers don't need it; ESX/QBCore/Qbox do.
- **A framework** (for RP) — ESX / QBCore / Qbox resources, plus the `ox_lib`/`oxmysql` libraries most modern scripts expect.

## 2. Local install (Windows) — step by step

1. Make a folder, e.g. `C:\FiveMServer`, with a `server-files` subfolder (the artifacts) and a separate `server-data` (or `txData`) area for your config/resources. Keeping artifacts separate from your data means you can update the build without touching your server.
2. Download the **recommended artifacts** build from the FiveM artifacts page (search the current URL via `docs.fivem.net` — it changes). Extract into `server-files`.
3. Double-click `FXServer.exe`. Windows Defender may warn on the unsigned exe — that's expected for FXServer; "More info → Run anyway." A console window opens and txAdmin launches in your browser.
4. Continue in txAdmin (next section).

GTA V must be owned/installed by each *player* connecting (FiveM is a mod for the legit game); the server box itself does not need GTA V installed.

## 3. txAdmin first run, Cfx.re account & server key

On first launch txAdmin walks you through:
1. **PIN** — auto-filled from the console; click to link.
2. **Link your Cfx.re account** — log in, authorize. Create a txAdmin admin password.
3. **Name the server.**
4. **Deployment / recipe** — choose "Popular Recipes" to install a framework automatically, or the **CFX Default** template for a bare server with no scripts. ESX/QBCore/Qbox recipes require a database (next section).
5. **Server key** — generate one on the Cfx.re portal (Server Registration Keys → Generate Key) and put it in `server.cfg` as `sv_licenseKey`. Treat it like a password.

After setup txAdmin builds your server-data folder and can boot the server.

## 4. MySQL for framework servers

Frameworks persist everything in MySQL. For local dev, install **MySQL** or **MariaDB** (XAMPP is a common easy bundle giving you MySQL + phpMyAdmin). Then:
1. Create a database (e.g. `fivem`).
2. Import the framework's base SQL schema (each framework ships one; Qbox/QBCore/ESX docs say which).
3. Install **oxmysql** as a resource — it's the modern DB layer almost every script uses.
4. Put the connection string in `server.cfg`:
   ```
   set mysql_connection_string "mysql://user:password@localhost/fivem?charset=utf8mb4"
   ```
   Keep this private — it contains your DB password.

## 5. server.cfg anatomy

`server.cfg` is the server's boot configuration. Generate a sane one with `scripts/generate_server_cfg.py`; the key sections:

```cfg
# Endpoints — the ports players connect on (30120 is the FiveM default)
endpoint_add_tcp "0.0.0.0:30120"
endpoint_add_udp "0.0.0.0:30120"

# Identity / list listing
sv_hostname "My RP Server"
sv_maxclients 48
sets sv_projectName "My RP Server"
sets sv_projectDesc "Serious RP"

# Database (framework servers)
set mysql_connection_string "mysql://user:password@localhost/fivem?charset=utf8mb4"

# Resource load order — ensure libraries/framework BEFORE dependents
ensure oxmysql
ensure ox_lib
ensure qbx_core          # (framework core; name varies by framework)
ensure my_resource

# Admin principals (give yourself ace permissions)
add_ace group.admin command allow
add_principal identifier.fivem:0000000 group.admin   # your fivem id

# License key — REQUIRED, keep private
sv_licenseKey "YOUR_KEY_HERE"
```

`ensure` starts a resource (and restarts if already running). **Order matters**: `oxmysql` and `ox_lib` before the framework, framework before resources that depend on it. A resource that loads before its dependency throws "could not find dependency" and fails.

## 6. Local play: port forwarding

For friends to join your local server, the box must be reachable:
- Forward **TCP and UDP 30120** (or your chosen port) to the server machine's local IP on your router.
- Allow `FXServer.exe` through Windows Firewall.
- Players connect via your **public IP** (`direct connect` in FiveM: `your.public.ip:30120`).
- Troubleshooting: not in list → confirm 30120 TCP+UDP forwarding and the license key; can't connect → check public IP and NAT type; hitches → update artifacts.

For just yourself, `localhost:30120` works with no forwarding.

## 7. Going public: VPS + server list

For an always-on public server, run on a **VPS or dedicated host** (your home PC is fine for testing, not for a real community — uptime, bandwidth, DDoS exposure). Two common routes:
- **Windows VPS** — same flow as local: copy artifacts + server-data, run `FXServer.exe`, txAdmin on a port you open.
- **Linux VPS** — use the Linux artifacts and `run.sh`; manage via txAdmin or a process manager (systemd/pm2/screen) so it survives disconnects.
- **Managed FiveM hosts / game-panel hosts** (Pterodactyl-based panels are common) — they wrap artifacts + txAdmin in a panel; less setup, monthly cost.

To appear in the server list: valid `sv_licenseKey`, reachable endpoints, and the server registered to your Cfx.re account. Set scheduled restarts in txAdmin (RP servers commonly restart every few hours to clear memory).

## 8. Hosting cost reality

Rough current ranges (verify, they drift): hosting €15–80/month depending on player slots and specs; optional paid server templates €0–€350 one-time; paid scripts €0–€500+. A free local server costs nothing and is the right place to learn. Don't pay for hosting until you have something worth hosting.
