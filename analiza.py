from __future__ import annotations
import sys
import json
import time
import pathlib
import logging
import datetime as dt
from typing import Dict, Any, List

import requests
import pandas as pd

OSNOVA_OM_ARHIV = "https://archive-api.open-meteo.com/v1/era5"
OSNOVA_OM_GEOKODA = "https://geocoding-api.open-meteo.com/v1/search"

MAPA_PODATKI = pathlib.Path("podatki"); MAPA_PODATKI.mkdir(exist_ok=True)
MAPA_DNEVNIK = MAPA_PODATKI / "dnevniki"; MAPA_DNEVNIK.mkdir(exist_ok=True)
DNEVNIK_DATOTEKA = MAPA_DNEVNIK / "zgodovina.log"

logging.basicConfig(
    level=getattr(logging, "INFO", logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(DNEVNIK_DATOTEKA, mode="a", encoding="utf-8")],
    force=True,
)
dnevnik = logging.getLogger("zgodovina")
dnevnik.info("prenos_zgodovine se začenja – zapisovanje v %s", DNEVNIK_DATOTEKA)


def geokodiraj_mesto(poisce: str, meja: int = 1) -> Dict[str, Any] | None:
    try:
        r = requests.get(OSNOVA_OM_GEOKODA, params={"name": poisce, "count": meja}, timeout=20)
        r.raise_for_status()
        js = r.json()
    except Exception as e:
        dnevnik.error("Geokodiranje ni uspelo za '%s': %s", poisce, e)
        return None

    rezultati = js.get("results") or []
    if not rezultati:
        dnevnik.warning("Ni geokodnega rezultata za '%s'", poisce)
        return None

    vrstica = rezultati[0]
    oznaka_mesta = vrstica.get("name", poisce.split(",")[0].strip())
    rez = {
        "poizvedba": poisce,
        "mesto": oznaka_mesta,
        "drzava": vrstica.get("country_code"),
        "sirina": vrstica["latitude"],
        "dolzina": vrstica["longitude"],
    }
    dnevnik.info("Geokodirano %-18s -> širina=%s dolžina=%s država=%s", oznaka_mesta, rez["sirina"], rez["dolzina"], rez["drzava"])
    return rez


def openmeteo_dnevna_povprecja(sirina: float, dolzina: float, zacetek: str, konec: str, casovni_pas: str | None = None) -> pd.DataFrame:
    parametri = {
        "latitude": sirina,
        "longitude": dolzina,
        "start_date": zacetek,
        "end_date": konec,
        "daily": "temperature_2m_mean",
        "timezone": casovni_pas or "auto",
    }
    r = requests.get(OSNOVA_OM_ARHIV, params=parametri, timeout=40)
    r.raise_for_status()
    js = r.json()

    dnevni = (js or {}).get("daily") or {}
    datumi = dnevni.get("time") or []
    temperature = dnevni.get("temperature_2m_mean") or []

    if not datumi:
        dnevnik.warning("Open-Meteo ni vrnil podatkov za širina=%s dolžina=%s", sirina, dolzina)
        return pd.DataFrame(columns=["datum", "Povprečna temperatura (v °C)"])

    df = pd.DataFrame({"datum": datumi, "Povprečna temperatura (v °C)": temperature})
    return df


def obseg_zadnjih_365(danes: dt.date | None = None) -> tuple[str, str]:
    danes = danes or dt.date.today()
    konec = danes - dt.timedelta(days=1)       # do včeraj
    zacetek = konec - dt.timedelta(days=364)   # skupaj 365 dni
    return (zacetek.isoformat(), konec.isoformat())


def glavni(argv: List[str]):
    mesta = argv or ["Ljubljana", "Berlin", "Pariz"]
    zacetek, konec = obseg_zadnjih_365()
    dnevnik.info("Pridobivam dnevna povprečja od %s do %s", zacetek, konec)

    vsi_okvirji: List[pd.DataFrame] = []

    for p in mesta:
        g = geokodiraj_mesto(p)
        if not g:
            continue
        df = openmeteo_dnevna_povprecja(g["sirina"], g["dolzina"], zacetek, konec)
        if df.empty:
            dnevnik.warning("Ni podatkov za %s", g["mesto"])
            continue
        df.insert(0, "mesto", g["mesto"])  # dodaj stolpec mesto
        mesto_csv = MAPA_PODATKI / f"zgodovina_{g['mesto']}.csv"
        df.to_csv(mesto_csv, index=False)
        dnevnik.info("Shranjeno %d vrstic -> %s", len(df), mesto_csv)
        vsi_okvirji.append(df)

    if not vsi_okvirji:
        dnevnik.error("Ni podatkov za nobeno mesto. Izhod.")
        sys.exit(2)

    zdruzeno = pd.concat(vsi_okvirji, ignore_index=True)
    izhod_csv = MAPA_PODATKI / "zgodovina_vsa_mesta.csv"
    zdruzeno.to_csv(izhod_csv, index=False)
    dnevnik.info("Shranjeno skupaj %d vrstic -> %s", len(zdruzeno), izhod_csv)


if __name__ == "__main__":
    try:
        glavni(sys.argv[1:])
    except SystemExit:
        raise
    except Exception:
        dnevnik.exception("Nepričakovana napaka v prenos_zgodovine")
        sys.exit(99)

