#!/usr/bin/env python3
"""Generate a sane starting server.cfg for a FiveM server.

Framework-aware: orders the `ensure` lines correctly (libraries -> framework core
-> your resources) for standalone / qbox / qbcore / esx. Emits PLACEHOLDERS for the
license key and DB connection string — never real secrets.

Usage:
    python generate_server_cfg.py --framework qbox --name "My RP Server" --output .
    python generate_server_cfg.py --framework esx --name "ESX City" --max 64 --port 30120 --output .

Run with --help for all options.
"""
import argparse
import os
import sys

# Ordered resource lists per framework: libraries first, framework core, then a
# placeholder for the user's resources. Names reflect common conventions; the user
# adjusts to their actual installed resource folder names.
FRAMEWORK_ENSURE = {
    "standalone": {
        "label": "Standalone (no framework)",
        "lines": [
            "# No framework. Add your resources below.",
            "# ensure my_resource",
        ],
    },
    "qbox": {
        "label": "Qbox (recommended)",
        "lines": [
            "ensure oxmysql",
            "ensure ox_lib",
            "ensure qbx_core",
            "ensure ox_inventory",
            "ensure ox_target",
            "# --- your resources below (after the core) ---",
            "# ensure my_resource",
        ],
    },
    "qbcore": {
        "label": "QBCore",
        "lines": [
            "ensure oxmysql",
            "ensure ox_lib",
            "ensure qb-core",
            "# inventory/target vary by setup (qb-inventory or ox_inventory)",
            "# ensure ox_inventory",
            "# --- your resources below (after the core) ---",
            "# ensure my_resource",
        ],
    },
    "esx": {
        "label": "ESX Legacy",
        "lines": [
            "ensure oxmysql",
            "ensure ox_lib",
            "ensure es_extended",
            "# inventory varies (esx_inventory or ox_inventory)",
            "# ensure ox_inventory",
            "# --- your resources below (after the core) ---",
            "# ensure my_resource",
        ],
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a starting server.cfg.")
    ap.add_argument("--framework", default="qbox", choices=list(FRAMEWORK_ENSURE.keys()))
    ap.add_argument("--name", default="My FiveM Server", help="Server hostname")
    ap.add_argument("--desc", default="A FiveM roleplay server.")
    ap.add_argument("--max", type=int, default=48, help="Max players (default 48)")
    ap.add_argument("--port", type=int, default=30120, help="Server port (default 30120)")
    ap.add_argument("--db", default="fivem", help="Database name (default fivem)")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    fw = FRAMEWORK_ENSURE[args.framework]
    needs_db = args.framework != "standalone"
    ensure_block = "\n".join(fw["lines"])

    db_block = ""
    if needs_db:
        db_block = f"""
# --- Database (required for {fw['label']}) -------------------------------------
# Replace user:password with your MySQL credentials. KEEP THIS PRIVATE.
set mysql_connection_string "mysql://user:password@localhost/{args.db}?charset=utf8mb4"
"""

    cfg = f"""# ==============================================================================
# server.cfg  —  {fw['label']}
# Generated starter config. Fill in the PLACEHOLDERS (license key, DB password).
# Never commit this file publicly with real secrets in it.
# ==============================================================================

# --- Endpoints (the port players connect on) ----------------------------------
endpoint_add_tcp "0.0.0.0:{args.port}"
endpoint_add_udp "0.0.0.0:{args.port}"

# --- Identity / server list ---------------------------------------------------
sv_hostname "{args.name}"
sets sv_projectName "{args.name}"
sets sv_projectDesc "{args.desc}"
sv_maxclients {args.max}

# locale / tags help your server list entry
sets locale "en-US"
sets tags "roleplay, {args.framework}"
{db_block}
# --- Resource load order ------------------------------------------------------
# Libraries and framework core load BEFORE the resources that depend on them.
# A resource ensured before its dependency will fail to start.
{ensure_block}

# --- Admin permissions (ACE) --------------------------------------------------
# Give your own identifier admin. Find your identifiers via txAdmin or the console.
add_ace group.admin command allow
# add_principal identifier.fivem:0000000 group.admin
# add_principal identifier.discord:000000000000000000 group.admin

# --- Misc ---------------------------------------------------------------------
sv_scriptHookAllowed 0          # disallow single-player script hook (cheat vector)
sv_enforceGameBuild 2944        # pin a game build if your resources need it (adjust/remove)

# --- License key (REQUIRED) ---------------------------------------------------
# Generate at the Cfx.re portal -> Server Registration Keys. KEEP THIS PRIVATE.
sv_licenseKey "YOUR_LICENSE_KEY_HERE"
"""
    out = os.path.join(args.output, "server.cfg")
    if os.path.exists(out):
        print(f"Error: {out} already exists (refusing to overwrite).", file=sys.stderr)
        return 1
    os.makedirs(args.output, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(cfg)

    print(f"Wrote {out}  ({fw['label']})")
    print("Fill in: sv_licenseKey" + (", mysql_connection_string" if needs_db else "")
          + ", and your admin identifier.")
    print("Adjust ensure names to match your actually-installed resource folders.")
    print("Note: sv_enforceGameBuild is a placeholder value — set to the build your resources need, or remove.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
