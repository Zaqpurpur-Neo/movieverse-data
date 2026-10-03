import pandas as pd, glob, os

D = "data-source/"
POT = lambda s: str(s)[:300]

# 1. movies_metadata
m = pd.read_csv(D + "movies_metadata.csv", low_memory=False)
print("== movies_metadata ==")
print("kolom:", list(m.columns))
print("baris:", len(m))
idnum = pd.to_numeric(m["id"], errors="coerce")
vc = pd.to_numeric(m["vote_count"], errors="coerce")
ok = (
    idnum.notna()
    & m["poster_path"].notna()
    & (m["adult"].astype(str) == "False")
    & (m["status"] == "Released")
    & vc.notna()
)
print("id bukan angka:", int(idnum.isna().sum()))
print("poster kosong:", int(m["poster_path"].isna().sum()))
print("adult True:", int((m["adult"].astype(str) == "True").sum()))
print("status bukan Released:", int((m["status"] != "Released").sum()))
print("lolos semua saringan:", int(ok.sum()))
for n in (50, 100, 500, 1000):
    print(f"  lolos & vote_count >= {n}:", int((ok & (vc >= n)).sum()))
print("contoh genres:", POT(m["genres"].dropna().iloc[0]))
print("contoh release_date:", list(m["release_date"].dropna().iloc[:3]))

# 2. credits (hanya 2 baris pertama)
c = pd.read_csv(D + "credits.csv", nrows=2)
print("\n== credits ==")
print("kolom:", list(c.columns))
print("contoh cast:", POT(c["cast"].iloc[0]))
print("contoh crew:", POT(c["crew"].iloc[0]))

# 3. links
l = pd.read_csv(D + "links.csv")
print("\n== links ==")
print("kolom:", list(l.columns), "| baris:", len(l))
print("tmdbId terisi:", int(l["tmdbId"].notna().sum()))

# 4. CSV lain (trailer)
known = {"movies_metadata.csv", "credits.csv", "links.csv",
         "links_small.csv", "ratings.csv", "keywords.csv"}
for f in glob.glob(D + "*.csv"):
    if os.path.basename(f) in known:
        continue
    t = pd.read_csv(f)
    print("\n== trailer:", os.path.basename(f), "==")
    print("kolom:", list(t.columns), "| baris:", len(t))
    print(t.head(2).to_string()[:400])
    if "movieId" in t.columns:
        tm = t.merge(l, on="movieId")
        tm = tm[tm["tmdbId"].notna()]
        print("cocok dengan links (tmdbId terisi):", len(tm))
        lolos_ids = set(idnum[ok].astype(int))
        print("cocok dengan film yang lolos saringan:",
              int(tm["tmdbId"].astype(int).isin(lolos_ids).sum()))
