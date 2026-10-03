import json, random, urllib.request, urllib.error

with open("docs/movies.json", encoding="utf-8") as f:
    film = json.load(f)

random.seed(1)
contoh = random.sample(film, 25)
UA = {"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"}

def status(url, metode, header):
    try:
        req = urllib.request.Request(url, method=metode, headers=header)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return type(e).__name__

print(f"{'id':>8}  HEAD-polos  GET-polos  GET-browser  judul")
ok = {"head": 0, "get": 0, "ua": 0}
for f in contoh:
    url = "https://image.tmdb.org/t/p/w500" + f["poster"]
    h = status(url, "HEAD", {})
    g = status(url, "GET", {})
    u = status(url, "GET", UA)
    ok["head"] += h == 200
    ok["get"] += g == 200
    ok["ua"] += u == 200
    print(f"{f['id']:>8}  {str(h):>10}  {str(g):>9}  {str(u):>11}  {f['title'][:30]}")

print("\nstatus 200 dari 25 contoh:", ok)
