import json, random, urllib.request, urllib.error

film = json.load(open("docs/movies.json", encoding="utf-8"))
random.seed(2)
contoh = random.sample(film, 40)
ukuran = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]

def ada(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False

for u in ukuran:
    hidup = sum(ada(f"https://image.tmdb.org/t/p/{u}" + f["poster"]) for f in contoh)
    print(f"{u:>9}: {hidup} dari {len(contoh)} ada")
