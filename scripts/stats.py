"""Fetches real GitHub numbers and draws assets/stats.svg.  Runs in the 'Update GitHub stats' workflow (needs GITHUB_TOKEN).
Usage:  GITHUB_TOKEN=... python scripts/stats.py devs901 [--theme neon]"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import build

QUERY = """query($login:String!){ user(login:$login){
  repositories(ownerAffiliations:OWNER, isFork:false, first:100){ totalCount nodes{ stargazerCount languages(first:6, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } } }
  contributionsCollection{ totalCommitContributions }
  pullRequests{ totalCount } } }"""

def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "devs901"
    if "--theme" in sys.argv: os.environ["THEME"] = sys.argv[sys.argv.index("--theme") + 1]
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
    u = json.load(urllib.request.urlopen(req))["data"]["user"]
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]: langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    data = {"repos": u["repositories"]["totalCount"], "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
            "commits": u["contributionsCollection"]["totalCommitContributions"], "prs": u["pullRequests"]["totalCount"],
            "langs": sorted(langs.items(), key=lambda kv: -kv[1])}
    build.stats(data)
    try:   # live activity feed from the public events API (best effort: the stats card must never fail because of it)
        import jarvis_x
        ev_req = urllib.request.Request(f"https://api.github.com/users/{login}/events/public?per_page=50",
                                        headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"})
        items = jarvis_x.events_to_items(json.load(urllib.request.urlopen(ev_req)), login)
        jarvis_x.feed(items or None, login)
        print("feed.svg written:", len(items), "events")
    except Exception as ex:
        print("feed skipped:", ex)
    print("stats.svg written:", {k: v for k, v in data.items() if k != "langs"}, data["langs"][:4])

if __name__ == "__main__":
    main()
