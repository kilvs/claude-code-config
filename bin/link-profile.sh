#!/bin/zsh
# Wire a Claude Code profile (config dir) to this AI Agent Config folder. Safe to rerun.
# Usage: bin/link-profile.sh ~/.claude            (or ~/.claude-work for a second profile)
set -e; setopt null_glob
R="$(cd "$(dirname "$0")/.." && pwd)"   # the folder this script lives in
P="${1:?usage: link-profile.sh <config dir>}"; P="${P%/}"
SUP="$R/settings/superseded"; STAMP="$(date +%Y-%m-%d)"; NAME="$(basename "$P")"
mkdir -p "$P" "$P/skills" "$P/projects" "$SUP"

# Replace a path with a symlink; a real file or dir found there is moved aside, never deleted.
link() { # link <target> <path>
  local target="$1" dest="$2"
  if [ -L "$dest" ]; then
    [ "$(readlink "$dest")" = "$target" ] && return 0
    mv "$dest" "$SUP/$NAME-$(basename "$dest")-$STAMP.link"
  elif [ -e "$dest" ]; then
    mv "$dest" "$SUP/$NAME-$(basename "$dest")-$STAMP"
    echo "  moved aside: $dest -> $SUP/$NAME-$(basename "$dest")-$STAMP"
  fi
  ln -s "$target" "$dest"; echo "  linked: $dest"
}

echo "Wiring $P"
link "$R/CLAUDE.md"                    "$P/CLAUDE.md"
link "$R/settings/settings.json"       "$P/settings.json"
for s in "$R"/skills/*/; do [ -f "$s/SKILL.md" ] && link "${s%/}" "$P/skills/$(basename "$s")"; done

# Auto memory lives in $R/memory for every profile.
python3 - "$R/settings/settings.json" "$R/memory" <<'PY'
import json,sys
f,mem=sys.argv[1],sys.argv[2]; d=json.load(open(f))
if d.get('autoMemoryDirectory')!=mem:
    d['autoMemoryDirectory']=mem; json.dump(d,open(f,'w'),indent=2); open(f,'a').write('\n')
    print('  autoMemoryDirectory:',mem)
PY

# User-scope MCP servers: add any missing ones (never overwrite). The default profile keeps
# them in ~/.claude.json; a profile started with CLAUDE_CONFIG_DIR keeps them inside its dir.
CFG="$P/.claude.json"; [ "$P" = "$HOME/.claude" ] && CFG="$HOME/.claude.json"
python3 - "$CFG" "$R/settings/mcp-servers.json" <<'PY'
import json,sys,os
cfg,src=sys.argv[1],sys.argv[2]
d=json.load(open(cfg)) if os.path.exists(cfg) else {}
want=json.load(open(src))['mcpServers']; have=d.setdefault('mcpServers',{}); added=[]
for k,v in want.items():
    if k not in have: have[k]=v; added.append(k)
if added:
    json.dump(d,open(cfg,'w'),indent=2); print('  mcp servers added:',', '.join(added))
else: print('  mcp servers: already present')
PY
echo "Done. Start claude, run /mcp once to log in to the MCP servers."
