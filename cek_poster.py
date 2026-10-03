import json, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

with open("docs/movies.json", encoding="utf-8") as f:
    film = json.load(f)

def cek(item):
    url = "https://image.tmdb.org/t/p/w500" + item["poster"]
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as r:
            return item["id"], r.status == 200
    except urllib.error.HTTPError as e:
        return item["id"], False if e.code == 404 else None
    except Exception:
        return item["id"], None   # gagal jaringan, tidak dihitung mati

with ThreadPoolExecutor(max_workers=8) as ex:
    hasil = list(ex.map(cek, film))

mati = [i for i, ok in hasil if ok is False]
ragu = [i for i, ok in hasil if ok is None]
with open("poster_mati.json", "w") as f:
    json.dump(mati, f)

print("total dicek:", len(hasil))
print("poster mati (404):", len(mati))
print("gagal dicek (jaringan):", len(ragu))
