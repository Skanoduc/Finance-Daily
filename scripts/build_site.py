"""
build_site.py
Assemble data/raw_<date>.json + data/analysis_<date>.json dans les templates
Jinja2 et génère le site statique dans docs/ (servi par GitHub Pages).
Met aussi à jour docs/archives.html avec la liste de tous les jours disponibles.
"""

import json
import os
import sys
import glob
import shutil
import datetime as dt
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")
STATIC = os.path.join(ROOT, "static")
DOCS = os.path.join(ROOT, "docs")

env = Environment(loader=FileSystemLoader(TEMPLATES))

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]


def fmt_date_fr(date_str):
    d = dt.date.fromisoformat(date_str)
    return f"{d.day} {MOIS_FR[d.month - 1]} {d.year}"


def fmt_pct(v):
    if v is None:
        return "—"
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.2f}%"


def cls_pct(v):
    if v is None or v == 0:
        return "flat"
    return "pos" if v > 0 else "neg"


def row_from_ticker(symbol, d):
    return {
        "name": d["name"], "value": d["value"],
        "day": fmt_pct(d["day"]), "day_cls": cls_pct(d["day"]),
        "week": fmt_pct(d["week"]), "week_cls": cls_pct(d["week"]),
        "mtd": fmt_pct(d["mtd"]), "mtd_cls": cls_pct(d["mtd"]),
        "ytd": fmt_pct(d["ytd"]), "ytd_cls": cls_pct(d["ytd"]),
        "y1": fmt_pct(d["y1"]), "y1_cls": cls_pct(d["y1"]),
    }


def build_ticker(raw):
    items = []
    for region in raw["indices"].values():
        for symbol, d in region.items():
            items.append({"name": d["name"], "value": d["value"],
                           "chg": fmt_pct(d["day"]), "cls": cls_pct(d["day"])})
    return items


def build_top_movers(raw, n=12):
    all_assets = []
    for region in raw["indices"].values():
        all_assets.extend(region.values())
    all_assets.extend(raw["devises"].values())
    all_assets.extend(raw["matieres_premieres"].values())
    all_assets.extend(raw["actions"].values())
    all_assets = [a for a in all_assets if a.get("day") is not None]
    all_assets.sort(key=lambda a: abs(a["day"]), reverse=True)
    return [{"name": a["name"], "value": a["value"],
             "chg": fmt_pct(a["day"]), "cls": cls_pct(a["day"])}
            for a in all_assets[:n]]


def render(template_name, out_name, **kwargs):
    tpl = env.get_template(template_name)
    html = tpl.render(**kwargs)
    with open(os.path.join(DOCS, out_name), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()

    with open(f"data/raw_{date_str}.json", encoding="utf-8") as f:
        raw = json.load(f)
    with open(f"data/analysis_{date_str}.json", encoding="utf-8") as f:
        analysis = json.load(f)

    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(os.path.join(DOCS, "static"), exist_ok=True)
    shutil.copy(os.path.join(STATIC, "style.css"), os.path.join(DOCS, "static", "style.css"))

    date_label = fmt_date_fr(date_str)
    ticker = build_ticker(raw)
    common = dict(date_label=date_label, ticker=ticker, base_path="")

    # ---- Page d'accueil ----
    # Sélection volontairement restreinte aux indices "phares" de chaque zone
    # pour ne pas surcharger l'aperçu -> le détail complet est sur /indices.html
    HIGHLIGHT_SYMBOLS = {"^FCHI", "^GDAXI", "^FTSE", "^GSPC", "^IXIC", "^DJI",
                          "^N225", "^HSI", "^BSESN", "^GSPTSE", "^BVSP"}
    indices_overview = []
    for region_name, region in raw["indices"].items():
        for symbol, d in region.items():
            if symbol not in HIGHLIGHT_SYMBOLS:
                continue
            indices_overview.append({
                "name": d["name"], "value": d["value"],
                "day": fmt_pct(d["day"]), "day_cls": cls_pct(d["day"]),
                "week": fmt_pct(d["week"]), "week_cls": cls_pct(d["week"]),
                "ytd": fmt_pct(d["ytd"]), "ytd_cls": cls_pct(d["ytd"]),
            })

    render("index.html", "index.html", active="accueil",
           headline=analysis["headline"], headline_sub=analysis["headline_sub"],
           synthese=analysis["synthese"], a_venir=analysis["a_venir"],
           indices_overview=indices_overview,
           top_movers=build_top_movers(raw), **common)

    # ---- Page Indices ----
    groups = []
    region_keys = {"Europe": "europe", "États-Unis": "us", "Asie-Pacifique": "asie",
                   "Amériques": "ameriques", "Autres": "autres"}
    for region_name, region in raw["indices"].items():
        key = region_keys.get(region_name, "")
        comment = analysis.get(f"commentaire_indices_{key}", "")
        groups.append({"title": region_name,
                        "rows": [row_from_ticker(s, d) for s, d in region.items()],
                        "commentaire": comment})
    render("category.html", "indices.html", active="indices",
           page_title="Indices boursiers", page_headline="Indices — toutes zones",
           page_lede="Clôtures du jour et variations sur plusieurs horizons.",
           groups=groups, **common)

    # ---- Page Devises & Matières premières ----
    groups = [
        {"title": "Devises", "rows": [row_from_ticker(s, d) for s, d in raw["devises"].items()],
         "commentaire": analysis.get("commentaire_devises", "")},
        {"title": "Matières premières", "rows": [row_from_ticker(s, d) for s, d in raw["matieres_premieres"].items()],
         "commentaire": analysis.get("commentaire_matieres_premieres", "")},
    ]
    render("category.html", "devises-matieres.html", active="devises",
           page_title="Devises & Matières premières", page_headline="Devises & Matières premières",
           page_lede="Principales paires de change et matières premières suivies.",
           groups=groups, **common)

    # ---- Page Macro ----
    macro_rows = []
    for series_id, d in raw.get("macro", {}).items():
        macro_rows.append({"name": d["label"], "value": d["latest"],
                            "day": "", "day_cls": "flat", "week": "", "week_cls": "flat",
                            "mtd": "", "mtd_cls": "flat", "ytd": "", "ytd_cls": "flat",
                            "y1": f"préc. {d['previous']}" if d.get("previous") else "", "y1_cls": "flat"})
    render("category.html", "macro.html", active="macro",
           page_title="Macroéconomie", page_headline="Indicateurs macroéconomiques",
           page_lede="Derniers indicateurs publiés (Fed, inflation, emploi, taux).",
           groups=[{"title": "États-Unis", "rows": macro_rows, "commentaire": ""}], **common)

    # ---- Page Deep dives ----
    render("deepdive.html", "deep-dives.html", active="deepdive",
           deepdives=analysis.get("deepdives", []), **common)

    # ---- Archives ----
    build_archives(common)

    # ---- Copie du jour dans /docs/archives/<date>.html (snapshot figé) ----
    os.makedirs(os.path.join(DOCS, "archives"), exist_ok=True)
    shutil.copy(os.path.join(DOCS, "index.html"),
                os.path.join(DOCS, "archives", f"{date_str}.html"))

    print(f"Site généré dans {DOCS}/ pour le {date_str}")


def build_archives(common):
    dates = sorted(
        [os.path.basename(p).removeprefix("raw_").removesuffix(".json")
         for p in glob.glob("data/raw_*.json")],
        reverse=True,
    )
    tpl = env.from_string("""
{% extends "base.html" %}
{% block content %}
<div class="hero">
  <div class="eyebrow">Archives</div>
  <h1>Historique des rapports</h1>
</div>
<table class="data">
<thead><tr><th style="text-align:left">Date</th><th></th></tr></thead>
<tbody>
{% for d in dates %}
<tr><td>{{ d.label }}</td><td><a href="archives/{{ d.raw }}.html">Consulter →</a></td></tr>
{% endfor %}
</tbody>
</table>
{% endblock %}
""")
    html = tpl.render(active="archives",
                       dates=[{"label": fmt_date_fr(d), "raw": d} for d in dates],
                       **common)
    with open(os.path.join(DOCS, "archives.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
