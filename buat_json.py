import ast, json, os
import pandas as pd

D = "data-source/"
OUT = "docs"          # GitHub Pages nanti membaca dari folder docs/
VOTE_MIN = 500

GENRE = {
    "Action": "Aksi", "Adventure": "Petualangan", "Animation": "Animasi",
    "Comedy": "Komedi", "Crime": "Kriminal", "Documentary": "Dokumenter",
    "Drama": "Drama", "Family": "Keluarga", "Fantasy": "Fantasi",
    "History": "Sejarah", "Horror": "Horor", "Music": "Musik",
    "Mystery": "Misteri", "Romance": "Romansa", "Science Fiction": "Sci-Fi",
    "TV Movie": "Film TV", "Thriller": "Thriller", "War": "Perang",
    "Western": "Western",
}

def baca_list(teks):
    # kolom di CSV berupa teks mirip list Python, diubah jadi list asli
    try:
        return ast.literal_eval(teks)
    except Exception:
        return []

def simpan(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

# 1. Metadata film + saringan
m = pd.read_csv(D + "movies_metadata.csv", low_memory=False)
for kol in ["id", "vote_count", "vote_average", "popularity", "runtime"]:
    m[kol] = pd.to_numeric(m[kol], errors="coerce")
m = m[
    m["id"].notna()
    & m["poster_path"].notna()
    & m["overview"].notna()
    & m["release_date"].notna()
    & (m["adult"].astype(str) == "False")
    & (m["status"] == "Released")
    & (m["vote_count"] >= VOTE_MIN)
]
m = m[m["release_date"].astype(str).str.len() == 10]
m["id"] = m["id"].astype(int)

if os.path.exists("poster_mati.json"):
    mati = set(json.load(open("poster_mati.json")))
    m = m[~m["id"].isin(mati)]

m = m.drop_duplicates("id").sort_values("vote_count", ascending=False)
ids = set(m["id"])

# 2. Pemeran dan kru (hanya baris untuk film terpilih)
c = pd.read_csv(D + "credits.csv")
c = c[c["id"].isin(ids)].drop_duplicates("id").set_index("id")

# 3. Trailer: youtubeId -> movieId (MovieLens) -> tmdbId (links.csv)
links = pd.read_csv(D + "links.csv").dropna(subset=["tmdbId"])
links["tmdbId"] = links["tmdbId"].astype(int)
t = pd.read_csv(D + "ml-youtube.csv").merge(links, on="movieId")
t = t.drop_duplicates("tmdbId")
trailer = dict(zip(t["tmdbId"], t["youtubeId"]))

# 4. Tulis JSON
os.makedirs(OUT + "/movies", exist_ok=True)
ringkas = []
jumlah_trailer = 0

for _, r in m.iterrows():
    mid = int(r["id"])
    genres = [GENRE.get(g["name"], g["name"]) for g in baca_list(r["genres"])]

    cast, crew = [], []
    if mid in c.index:
        cast = baca_list(c.at[mid, "cast"])
        crew = baca_list(c.at[mid, "crew"])
    cast = sorted(cast, key=lambda x: x.get("order", 999))[:5]
    director = next((x["name"] for x in crew if x.get("job") == "Director"), None)
    writers = []
    for x in crew:
        if x.get("job") in ("Screenplay", "Writer", "Story") and x["name"] not in writers:
            writers.append(x["name"])
    writers = writers[:2]

    overview = str(r["overview"]).strip()
    potongan = overview if len(overview) <= 140 else overview[:140].rstrip() + "…"
    yt = trailer.get(mid)
    if yt:
        jumlah_trailer += 1

    dasar = {
        "id": mid,
        "title": r["title"],
        "year": int(str(r["release_date"])[:4]),
        "releaseDate": r["release_date"],
        "genres": genres,
        "rating": round(float(r["vote_average"]), 1),
        "popularity": round(float(r["popularity"]), 1),
        "poster": r["poster_path"],
        "director": director,
        "trailerId": yt,
    }

    ringkas.append({**dasar, "overview": potongan,
                    "cast": [x["name"] for x in cast[:3]]})

    detail = {**dasar, "overview": overview,
              "runtime": None if pd.isna(r["runtime"]) else int(r["runtime"]),
              "writers": writers,
              "cast": [{"name": x["name"], "character": x.get("character", "")}
                       for x in cast]}
    simpan(f"{OUT}/movies/{mid}.json", detail)

simpan(f"{OUT}/movies.json", ringkas)

# 5. Laporan singkat
print("jumlah film:", len(ringkas))
print("punya trailer:", jumlah_trailer)
print("tanpa sutradara:", sum(1 for x in ringkas if not x["director"]))
print("tahun >= 2016:", sum(1 for x in ringkas if x["year"] >= 2016))
print("tahun < 1990:", sum(1 for x in ringkas if x["year"] < 1990))
print("ukuran movies.json (KB):", round(os.path.getsize(f"{OUT}/movies.json") / 1024))
