import json, os, sys, time, urllib.request, datetime

API = "https://r8t00r3qx7.execute-api.ap-northeast-1.amazonaws.com/PRD"
LOCS = ["10", "7", "2", "12", "11", "13"]   # 都立大 中目黒 恵比寿 原宿 赤坂 自由が丘
GENS = ["01,18", "09"]                       # HIP-HOP / リズムトレーニング
OUT = "data.json"

def post(loc, gen, is_month):
    body = json.dumps({"location": [loc], "genre": gen.split(","), "brand": "1", "is_month": is_month}).encode()
    req = urllib.request.Request(API, body, {
        "Content-Type": "application/json",
        "Origin": "https://www.noadance.com",
        "Referer": "https://www.noadance.com/",
        "User-Agent": "Mozilla/5.0",
    })
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                j = json.load(r)
            if str(j.get("statusCode")) != "200":
                raise RuntimeError("statusCode %s" % j.get("statusCode"))
            return j["body"].get("Items", [])
        except Exception as e:
            print("retry", loc, gen, is_month, e, file=sys.stderr)
            time.sleep(3)
    sys.exit("failed: %s %s %s" % (loc, gen, is_month))

d = {"this": {}, "next": {}}
for key, flag in (("this", True), ("next", False)):
    for loc in LOCS:
        for gen in GENS:
            d[key][loc + "|" + gen] = post(loc, gen, flag)

old = {}
if os.path.exists(OUT):
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except Exception:
        old = {}
if old.get("d") == d:
    print("no change")
else:
    jst = datetime.timezone(datetime.timedelta(hours=9))
    out = {"updated": datetime.datetime.now(jst).strftime("%Y-%m-%d %H:%M"), "d": d}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("updated")
