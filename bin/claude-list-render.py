#!/usr/bin/env python3
"""Renderer for claude-list: profile table plus a 7-day usage overview per profile.

Reads JSON on stdin: {"root": str, "color": bool, "days": int,
  "profiles": [{"index","alias","config_dir","login","github","commit","wired"}]}
Usage is computed from each profile's projects/**/*.jsonl session logs. Files are parsed
once and cached by size and mtime in ~/.cache/claude-list/usage-cache.json.
"""
import json, os, re, sys, datetime as dt, glob

CACHE = os.path.expanduser("~/.cache/claude-list/usage-cache.json")
TS = re.compile(r'"timestamp":"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)')
REQ = re.compile(r'"requestId":"([^"]+)"')
OUT = re.compile(r'"output_tokens":(\d+)')
INP = re.compile(r'"input_tokens":(\d+)')
CR = re.compile(r'"cache_read_input_tokens":(\d+)')
CC = re.compile(r'"cache_creation_input_tokens":(\d+)')
LOCAL_TZ = dt.datetime.now().astimezone().tzinfo


def local_date(ts):
    return dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).astimezone(LOCAL_TZ).strftime("%Y-%m-%d")


def parse_file(path):
    """Per-day counters for one session log: prompts, turns, output, input, last timestamp."""
    days, seen = {}, set()
    with open(path, "rb") as fh:
        for raw in fh:
            if b'"type":"user"' in raw and b'"kind":"human"' in raw and b'"toolUseResult"' not in raw \
                    and b'<ide_opened_file>' not in raw and b'<ide_selection>' not in raw:
                m = TS.search(raw.decode("utf-8", "replace"))
                if not m: continue
                d = days.setdefault(local_date(m.group(1)), {"p": 0, "t": 0, "o": 0, "i": 0, "last": ""})
                d["p"] += 1; d["last"] = max(d["last"], m.group(1))
            elif b'"type":"assistant"' in raw and b'"usage"' in raw:
                line = raw.decode("utf-8", "replace")
                r = REQ.search(line)
                if r and r.group(1) in seen: continue
                if r: seen.add(r.group(1))
                m = TS.search(line)
                if not m: continue
                d = days.setdefault(local_date(m.group(1)), {"p": 0, "t": 0, "o": 0, "i": 0, "last": ""})
                d["t"] += 1; d["last"] = max(d["last"], m.group(1))
                d["o"] += int(OUT.search(line).group(1)) if OUT.search(line) else 0
                d["i"] += sum(int(x.search(line).group(1)) for x in (INP, CR, CC) if x.search(line))
    return days


def usage_for(config_dir, since_dates):
    try: cache = json.load(open(CACHE))
    except Exception: cache = {}
    changed = False
    total = {"sessions": 0, "p": 0, "t": 0, "o": 0, "i": 0, "last": "", "by_day": {d: 0 for d in since_dates}}
    active_sessions = set()
    cutoff = dt.datetime.now().timestamp() - (len(since_dates) + 1) * 86400
    for path in glob.glob(os.path.join(config_dir, "projects", "**", "*.jsonl"), recursive=True):
        st = os.stat(path)
        if st.st_mtime < cutoff: continue
        key = path; ent = cache.get(key)
        if not ent or ent["size"] != st.st_size or ent["mtime"] != st.st_mtime:
            ent = {"size": st.st_size, "mtime": st.st_mtime, "days": parse_file(path)}
            cache[key] = ent; changed = True
        # session id: the top-level <id>.jsonl, or <id>/subagents/agent-*.jsonl for a subagent log
        rel = os.path.relpath(path, os.path.join(config_dir, "projects")).split(os.sep)
        session = rel[1] if len(rel) > 2 else os.path.splitext(rel[-1])[0]
        active = False
        for day, d in ent["days"].items():
            if day not in total["by_day"]: continue
            if d["p"] or d["t"]: active = True
            total["p"] += d["p"]; total["t"] += d["t"]; total["o"] += d["o"]; total["i"] += d["i"]
            total["by_day"][day] += d["p"]; total["last"] = max(total["last"], d["last"])
        if active: active_sessions.add(session)
    total["sessions"] = len(active_sessions)
    if changed:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump(cache, open(CACHE, "w"))
    return total


# ---------- formatting ----------
def fmt_n(n):
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.0f}k"
    return str(n)


def spark(vals, peak):
    bars = "▁▂▃▄▅▆▇█"
    return "".join(" " if v == 0 else bars[min(7, int(v / peak * 7.999))] for v in vals) if peak else " " * len(vals)


class Style:
    def __init__(self, on):
        self.on = on
    def __call__(self, code, s):
        return f"\033[{code}m{s}\033[0m" if self.on else s
    def bold(self, s): return self("1", s)
    def dim(self, s): return self("2", s)
    def head(self, s): return self("1;36", s)
    def good(self, s): return self("32", s)
    def bad(self, s): return self("31", s)
    def accent(self, s): return self("33", s)
    def title(self, s): return self("1;35", s)


ANSI = re.compile(r"\033\[[0-9;]*m")
def vis(s): return len(ANSI.sub("", s))


def table(st, headers, rows, aligns=None):
    aligns = aligns or ["l"] * len(headers)
    w = [max(vis(h), *(vis(r[i]) for r in rows)) if rows else vis(h) for i, h in enumerate(headers)]
    def cell(s, i):
        pad = w[i] - vis(s)
        return (" " * pad + s) if aligns[i] == "r" else (s + " " * pad)
    line = lambda l, m, r: st.dim(l + m.join("─" * (x + 2) for x in w) + r)
    out = [line("┌", "┬", "┐"),
           st.dim("│") + st.dim("│").join(" " + cell(st.head(h), i) + " " for i, h in enumerate(headers)) + st.dim("│"),
           line("├", "┼", "┤")]
    for r in rows:
        out.append(st.dim("│") + st.dim("│").join(" " + cell(c, i) + " " for i, c in enumerate(r)) + st.dim("│"))
    out.append(line("└", "┴", "┘"))
    return "\n".join(out)


def main():
    data = json.load(sys.stdin)
    st = Style(data.get("color", False))
    home = os.path.expanduser("~")
    tilde = lambda p: p.replace(home, "~", 1)
    ndays = int(data.get("days", 7))
    today = dt.date.today()
    dates = [(today - dt.timedelta(days=ndays - 1 - i)).isoformat() for i in range(ndays)]

    # Profile table
    def state(v, ok_words=()):
        low = v.lower()
        if low.startswith(("not ", "no")) and low not in ok_words: return st.dim(v)
        return v
    rows = []
    for p in data["profiles"]:
        wired = st.good("● yes") if p["wired"] == "yes" else st.bad("○ no")
        rows.append([st.accent(str(p["index"])), st.bold(p["alias"]), tilde(p["config_dir"]),
                     state(p["login"]), state(p["github"]), state(p["commit"]), wired])
    rows.append([st.accent("a"), st.bold("add a profile"), st.dim("new alias, dirs, git identity, wiring"), "", "", "", ""])
    print(st.title("Claude Code profiles"))
    print(table(st, ["#", "command", "config dir", "claude login", "github", "commit identity", "wired"], rows))
    print(st.dim(f"wired = CLAUDE.md, settings, skills and memory link into {tilde(data['root'])}"))
    print()

    # Usage table
    usage = [(p, usage_for(p["config_dir"], dates)) for p in data["profiles"]]
    peak = max((v for _, u in usage for v in u["by_day"].values()), default=0)
    day_letters = "per day"
    urows = []
    for p, u in usage:
        vals = [u["by_day"][d] for d in dates]
        last = u["last"]
        if last:
            ld = dt.datetime.strptime(last, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).astimezone(LOCAL_TZ)
            last_s = "today " + ld.strftime("%H:%M") if ld.date() == today else ld.strftime("%a %d %b")
        else:
            last_s = st.dim("no activity")
        sp = st.accent(spark(vals, peak)) if any(vals) else st.dim("·" * ndays)
        urows.append([st.bold(p["alias"]), str(u["sessions"]), str(u["p"]), str(u["t"]),
                      fmt_n(u["o"]), fmt_n(u["i"]), sp, last_s])
    span = f"{dt.date.fromisoformat(dates[0]).strftime('%d %b')} to {today.strftime('%d %b')}"
    print(st.title(f"Usage, last {ndays} days ({span})"))
    print(table(st, ["profile", "sessions", "prompts", "turns", "out tokens", "in tokens", day_letters, "last active"],
                urows, ["l", "r", "r", "r", "r", "r", "l", "l"]))
    first = dt.date.fromisoformat(dates[0]).strftime("%a")
    print(st.dim(f"prompts = things you typed; turns = model replies, subagents included; in tokens include cache reads"))
    print(st.dim(f"per day = prompts per day, {first} to {today.strftime('%a')}, left to right, scaled to the busiest day"))


if __name__ == "__main__":
    main()
