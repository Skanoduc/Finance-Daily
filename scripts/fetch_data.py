"""
fetch_data.py
Récupère les données de marché du jour + historique nécessaire au calcul
des variations (jour / semaine / début de mois / YTD / 1 an) et les
enregistre dans data/raw_<date>.json

Sources :
- Indices, devises, matières premières, actions -> Yahoo Finance (yfinance)
- Séries macro -> FRED (Federal Reserve Economic Data), clé API gratuite

Ce script est fait pour être exécuté par GitHub Actions (accès internet complet).
"""

import json
import datetime as dt
import os
import time
import yfinance as yf

# ---------------------------------------------------------------------
# 1. Définition de l'univers suivi
#    (tu peux librement ajouter/retirer des tickers ici)
# ---------------------------------------------------------------------

INDICES = {
    "Europe": {
        "^FCHI": "CAC 40",
        "^GDAXI": "DAX",
        "^FTSE": "FTSE 100",
        "^STOXX50E": "Euro Stoxx 50",
        "FTSEMIB.MI": "FTSE MIB",
        "^IBEX": "IBEX 35",
    },
    "États-Unis": {
        "^GSPC": "S&P 500",
        "^IXIC": "Nasdaq Composite",
        "^DJI": "Dow Jones",
        "^RUT": "Russell 2000",
    },
    "Asie-Pacifique": {
        "^N225": "Nikkei 225",
        "^HSI": "Hang Seng",
        "000001.SS": "Shanghai Composite",
        "^AXJO": "ASX 200",
        "^KS11": "KOSPI",
    },
}

DEVISES = {
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "EURGBP=X": "EUR/GBP",
    "USDCNY=X": "USD/CNY",
}

MATIERES_PREMIERES = {
    "GC=F": "Or (Gold)",
    "SI=F": "Argent (Silver)",
    "CL=F": "Pétrole WTI",
    "BZ=F": "Pétrole Brent",
    "NG=F": "Gaz naturel",
    "HG=F": "Cuivre",
}

# Tickers surveillés pour repérer les plus fortes variations du jour
# (grandes capitalisations US + Europe -> on peut étoffer cette liste)
WATCHLIST_ACTIONS = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "AMZN": "Amazon",
    "GOOGL": "Alphabet", "META": "Meta", "TSLA": "Tesla",
    "MC.PA": "LVMH", "OR.PA": "L'Oréal", "TTE.PA": "TotalEnergies",
    "SAP.DE": "SAP", "ASML.AS": "ASML", "NESN.SW": "Nestlé",
}

# Séries FRED utiles pour la partie macro (clé API gratuite sur fred.stlouisfed.org)
FRED_SERIES = {
    "FEDFUNDS": "Taux directeur Fed",
    "CPIAUCSL": "Inflation US (CPI)",
    "UNRATE": "Taux de chômage US",
    "DGS10": "Taux 10 ans US",
}


def pct_change(hist, days_back):
    """Variation en % entre la dernière clôture et celle il y a N séances."""
    if len(hist) <= days_back:
        return None
    last = hist["Close"].iloc[-1]
    ref = hist["Close"].iloc[-1 - days_back]
    return round((last / ref - 1) * 100, 2)


def variation_depuis(hist, start_date):
    """Variation en % depuis une date donnée (ex: 1er janvier -> YTD)."""
    sub = hist[hist.index >= start_date]
    if sub.empty:
        return None
    last = hist["Close"].iloc[-1]
    ref = sub["Close"].iloc[0]
    return round((last / ref - 1) * 100, 2)


def fetch_ticker_block(tickers: dict, period="2y"):
    """Télécharge l'historique et calcule toutes les variations pour un lot de tickers."""
    out = {}
    today = dt.datetime.now()
    ytd_start = dt.datetime(today.year, 1, 1)
    month_start = dt.datetime(today.year, today.month, 1)

    for symbol, name in tickers.items():
        try:
            hist = yf.Ticker(symbol).history(period=period)
            if hist.empty:
                continue
            out[symbol] = {
                "name": name,
                "value": round(hist["Close"].iloc[-1], 2),
                "day": pct_change(hist, 1),
                "week": pct_change(hist, 5),
                "mtd": variation_depuis(hist, month_start),
                "ytd": variation_depuis(hist, ytd_start),
                "y1": pct_change(hist, 252),
            }
        except Exception as e:
            print(f"[warn] échec récupération {symbol} ({name}) : {e}")
        time.sleep(0.2)  # éviter le rate-limit Yahoo
    return out


def fetch_fred(series_dict, api_key):
    """Récupère la dernière valeur + valeur précédente pour des séries FRED."""
    import urllib.request
    out = {}
    for series_id, label in series_dict.items():
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=2")
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                obs = json.load(r)["observations"]
            out[series_id] = {
                "label": label,
                "latest": obs[0]["value"],
                "latest_date": obs[0]["date"],
                "previous": obs[1]["value"] if len(obs) > 1 else None,
            }
        except Exception as e:
            print(f"[warn] échec récupération FRED {series_id} : {e}")
    return out


def main():
    today_str = dt.date.today().isoformat()
    result = {"date": today_str, "indices": {}, "devises": {}, "matieres_premieres": {},
              "actions": {}, "macro": {}}

    for region, tickers in INDICES.items():
        result["indices"][region] = fetch_ticker_block(tickers)

    result["devises"] = fetch_ticker_block(DEVISES)
    result["matieres_premieres"] = fetch_ticker_block(MATIERES_PREMIERES)
    result["actions"] = fetch_ticker_block(WATCHLIST_ACTIONS)

    fred_key = os.environ.get("FRED_API_KEY")
    if fred_key:
        result["macro"] = fetch_fred(FRED_SERIES, fred_key)
    else:
        print("[info] FRED_API_KEY absente -> section macro ignorée")

    os.makedirs("data", exist_ok=True)
    out_path = f"data/raw_{today_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Données enregistrées dans {out_path}")


if __name__ == "__main__":
    main()
