#!/usr/bin/env python3
"""
Draws the "Live Telemetry" terminal card for the profile README.

It asks the GitHub GraphQL API for your public profile data (stats,
languages, latest commits) and writes it as an amber terminal-style SVG.

Run by .github/workflows/profile-cards.yml every day.

    GITHUB_TOKEN=... USERNAME=Rajan3103 python3 terminal_card.py profile/terminal.svg
    python3 terminal_card.py --sample out.svg      # draw with fake data (no token)
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

# ── Terminal Amber colours ────────────────────────────────────────────────
BG, BAR_BG, BORDER = "#000000", "#1a1400", "#3a2c00"
AMBER, SOFT, GREEN, MUTED = "#ffb000", "#ffcc66", "#00ff9c", "#7a6a3a"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    name login createdAt
    followers { totalCount }
    pullRequests { totalCount }
    merged: pullRequests(states: MERGED) { totalCount }
    issues { totalCount }
    contributionsCollection {
      totalCommitContributions totalPullRequestReviewContributions
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false,
                 privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name nameWithOwner stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
        defaultBranchRef { target { ... on Commit {
          history(first: 10) { nodes { messageHeadline committedDate } }
        } } }
      }
    }
  }
}
"""


def fetch(login, token):
    """Ask GitHub for the profile data (one GraphQL request)."""
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise SystemExit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]


def summarise(user):
    """Turn the raw API answer into the numbers the card shows."""
    profile_repo = f"{user['login']}/{user['login']}"  # skip the README repo itself
    repos = [r for r in user["repositories"]["nodes"] if r["nameWithOwner"].lower() != profile_repo.lower()]

    # Languages: add up code size per language across all public repos.
    sizes = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    total = sum(sizes.values()) or 1
    langs = sorted(sizes.items(), key=lambda kv: -kv[1])[:5]
    langs = [(name, size * 100 / total) for name, size in langs]

    # Recent activity: latest non-merge commit of the 3 most recently pushed repos.
    activity = []
    for r in repos:
        target = (r.get("defaultBranchRef") or {}).get("target") or {}
        nodes = (target.get("history") or {}).get("nodes") or []
        # Skip "Merge pull request ..." commits and show the real change instead.
        nodes = [n for n in nodes if not n["messageHeadline"].startswith("Merge ")]
        if nodes:
            when = dt.datetime.fromisoformat(nodes[0]["committedDate"].replace("Z", "+00:00"))
            activity.append((when, r["nameWithOwner"], nodes[0]["messageHeadline"]))
        if len(activity) == 3:
            break

    joined = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    years = (dt.datetime.now(dt.timezone.utc) - joined).days // 365
    cc = user["contributionsCollection"]
    return {
        "name": user["name"] or user["login"], "login": user["login"],
        "joined": f"{years} year{'s' if years != 1 else ''} ago" if years else "this year",
        "repos": user["repositories"]["totalCount"],
        "commits": cc["totalCommitContributions"],
        "issues": user["issues"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in user["repositories"]["nodes"]),
        "prs": user["pullRequests"]["totalCount"], "merged": user["merged"]["totalCount"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "langs": langs, "activity": activity,
    }


SAMPLE = {
    "name": "Karthig Rajan S", "login": "Rajan3103", "joined": "2 years ago",
    "repos": 14, "commits": 175, "issues": 0, "followers": 18, "stars": 0,
    "prs": 10, "merged": 9, "reviews": 3,
    "langs": [("Python", 61.98), ("TypeScript", 17.43), ("Java", 10.23), ("JavaScript", 7.13), ("CSS", 2.71)],
    "activity": [
        (dt.datetime(2026, 11, 2), "Rajan3103/Doc_Drift", "Add Gemini retry back-off & a much longer message to test cutting"),
        (dt.datetime(2026, 10, 29), "Rajan3103/nlp-log-processor-and-bug-reporter", "Tune TF-IDF features"),
        (dt.datetime(2026, 10, 25), "Rajan3103/AI-BI-Bkups", "Add <indexes> & \"quotes\""),
    ],
}


def cut(text, n):
    """Shorten long text so it fits in its column."""
    return text if len(text) <= n else text[: n - 1] + "…"


def render(s):
    """Build the SVG text. Every text item gets an exact x position so the
    columns line up no matter which monospace font the viewer has."""
    W, LH, X = 860, 24, 22          # width, line height, left margin
    CH = 8.4                         # approx. width of one 14px monospace character
    out, y = [], 64

    def t(x, text, color=SOFT, extra=""):
        out.append(f'<text x="{x}" y="{y}" fill="{color}"{extra}>{escape(str(text))}</text>')

    def prompt(cmd):
        user = f"{s['login'].lower()}@github"
        t(X, user, GREEN)
        t(X + CH * len(user), ":~$", AMBER)
        t(X + CH * (len(user) + 4), cmd)

    # neofetch block
    prompt("neofetch --github"); y += LH
    t(X, s["name"], AMBER); t(X + CH * (len(s["name"]) + 2), "@" + s["login"], MUTED); y += 12
    out.append(f'<line x1="{X}" x2="{X + 520}" y1="{y}" y2="{y}" stroke="{MUTED}"/>'); y += LH
    rows = [("Joined", s["joined"], "Followers", s["followers"]),
            ("Repositories", f"{s['repos']} public", "Stars", s["stars"]),
            ("Commits", f"{s['commits']} last year", "PRs", f"{s['prs']} opened · {s['merged']} merged"),
            ("Issues", f"{s['issues']} opened", "Reviews", s["reviews"])]
    for k1, v1, k2, v2 in rows:
        t(X, k1, AMBER); t(X + 150, v1); t(X + 390, k2, AMBER); t(X + 500, v2); y += LH

    # languages block
    y += LH * 0.5
    prompt(f"languages --top {len(s['langs'])}"); y += LH
    for name, pct in s["langs"]:
        t(X, name, AMBER)
        out.append(f'<rect x="{X + 120}" y="{y - 13}" width="240" height="16" fill="{BAR_BG}"/>')
        out.append(f'<rect x="{X + 120}" y="{y - 13}" width="{max(2, 240 * pct / 100):.1f}" height="16" fill="{SOFT}"/>')
        t(X + 410, f"{pct:.1f}%", SOFT, ' text-anchor="end"'); y += LH

    # activity block
    y += LH * 0.5
    prompt("git log --recent"); y += LH
    for when, repo, msg in s["activity"]:
        t(X, when.strftime("[%b %d]"), MUTED); t(X + 80, "commit", GREEN)
        t(X + 150, cut(repo.split("/")[-1], 26), SOFT); t(X + 390, cut(msg, 48)); y += LH
    if not s["activity"]:
        t(X, "no public commits yet", MUTED); y += LH

    # final prompt with a blinking cursor
    prompt("")
    cx = X + CH * (len(s["login"]) + 12)
    out.append(f'<rect x="{cx}" y="{y - 14}" width="9" height="18" fill="{AMBER}">'
               '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>')
    H = int(y + 24)

    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}" font-size="14">'
            f'<title>{escape(s["name"])} — GitHub terminal</title>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>'
            f'<path d="M0.5 32 V8.5 a8 8 0 0 1 8 -8 H{W - 8.5} a8 8 0 0 1 8 8 V32 Z" fill="{BAR_BG}"/>'
            f'<circle cx="20" cy="16" r="5.5" fill="#ff5f57"/><circle cx="38" cy="16" r="5.5" fill="#febc2e"/>'
            f'<circle cx="56" cy="16" r="5.5" fill="#28c840"/>'
            f'<text x="78" y="20" fill="{MUTED}" font-size="12">{escape(s["login"].lower())}@github: ~</text>')
    return head + "".join(out) + "</svg>\n"


def main():
    args = sys.argv[1:]
    if "--sample" in args:
        args.remove("--sample")
        stats = SAMPLE
    else:
        stats = summarise(fetch(os.environ["USERNAME"], os.environ["GITHUB_TOKEN"]))
    path = args[0] if args else "profile/terminal.svg"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(stats))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
