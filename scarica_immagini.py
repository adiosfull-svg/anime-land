"""Scarica da Wayback Machine le immagini della skin di Anime-Land che mancano nella cartella img/.

Uso:  python scarica_immagini.py
Richiede solo Python 3 (nessuna libreria da installare). Si può rilanciare: salta quelle già scaricate.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "img")
os.makedirs(IMG, exist_ok=True)
dati = json.load(open(os.path.join(AQUI, "immagini_mancanti.json"), encoding="utf-8"))
TS = dati["timestamp"]
MAGIC = (b"\x89PNG", b"GIF8", b"\xff\xd8\xff", b"\x00\x00\x01\x00", b"BM")


def prova(url_originale):
    # prima la data esatta dello snapshot, poi le catture più vicine (Wayback reindirizza da solo)
    for ts in (TS, "2009", "2008", "2010", "2007", "2011"):
        url = f"https://web.archive.org/web/{ts}im_/{url_originale}"
        for tentativo in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    corpo = r.read()
                if corpo.startswith(MAGIC):
                    return corpo
                break  # risposta non valida (pagina HTML): passa alla data successiva
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(30)
                    continue
                break  # 404 ecc.: passa alla data successiva
            except Exception:
                time.sleep(3)
    return None


falliti = []
elenco = sorted(dati["images"].items())
for i, (nome, url) in enumerate(elenco, 1):
    destinazione = os.path.join(IMG, nome)
    if os.path.exists(destinazione) and os.path.getsize(destinazione) > 0:
        print(f"[{i}/{len(elenco)}] già presente  {nome}")
        continue
    corpo = prova(url)
    if corpo:
        open(destinazione, "wb").write(corpo)
        print(f"[{i}/{len(elenco)}] ok            {nome}")
    else:
        falliti.append((nome, url))
        print(f"[{i}/{len(elenco)}] NON TROVATA   {nome}")
    time.sleep(1.2)  # per non farsi bloccare da archive.org

if falliti:
    with open(os.path.join(AQUI, "non_trovate.txt"), "w", encoding="utf-8") as f:
        for nome, url in falliti:
            f.write(f"{nome}\t{url}\n")
print(f"\nFatto. Scaricate {len(elenco) - len(falliti)} su {len(elenco)}. Non trovate: {len(falliti)}"
      + (" (elenco in non_trovate.txt)" if falliti else ""))
