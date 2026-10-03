import json, socket, urllib.request, urllib.error

film = json.load(open("docs/movies.json", encoding="utf-8"))
f = next(x for x in film if x["title"] == "Fight Club")
url = "https://image.tmdb.org/t/p/w500" + f["poster"]

print("poster di JSON:", f["poster"])
print("url:", url)
try:
    print("IP image.tmdb.org:", socket.gethostbyname("image.tmdb.org"))
except Exception as e:
    print("DNS gagal:", e)

try:
    urllib.request.urlopen(url, timeout=15)
except urllib.error.HTTPError as e:
    print("status:", e.code)
    print("header Server:", e.headers.get("Server"))
    print("content-type:", e.headers.get("Content-Type"))
    print("isi (200 karakter pertama):", e.read(200))
except Exception as e:
    print("error:", type(e).__name__, e)
