# Finance Daily — guide de mise en route

Ce dossier contient tout ce qu'il faut pour que le rapport se génère
automatiquement chaque jour ouvré et soit publié sur un site web gratuit.

## Ce que fait le projet, en résumé

1. `scripts/fetch_data.py` récupère les cours (indices, devises, matières
   premières, actions) via Yahoo Finance, + les indicateurs macro via FRED.
2. `scripts/generate_analysis.py` envoie ces chiffres à l'API Claude qui
   rédige la synthèse, les commentaires et les "deep dives".
3. `scripts/build_site.py` assemble tout ça dans le site (dossier `docs/`).
4. `.github/workflows/daily.yml` exécute ces 3 étapes automatiquement,
   chaque jour ouvré, et publie le résultat.

Un exemple déjà généré (données fictives) se trouve dans `docs/` — ouvre
`docs/index.html` dans un navigateur pour voir le rendu.

## Étape 1 — Créer les comptes nécessaires

- **GitHub** (gratuit) : https://github.com/signup si tu n'as pas de compte
- **Anthropic Console** (pour la clé API Claude) : https://console.anthropic.com
  → Settings → API Keys → Create Key. Ajoute un peu de crédit (5-10€ suffisent
  pour des mois d'utilisation à ce rythme).
- **FRED API** (gratuit, optionnel mais recommandé pour la page Macro) :
  https://fred.stlouisfed.org/docs/api/api_key.html

## Étape 2 — Mettre le projet sur GitHub

1. Va sur https://github.com/new, crée un dépôt (ex: `finance-daily`),
   **privé ou public** au choix (public = gratuit et plus simple pour
   GitHub Pages).
2. Sur ton ordinateur, dans un terminal, à l'intérieur de ce dossier :
   ```bash
   git init
   git add .
   git commit -m "Premier commit"
   git branch -M main
   git remote add origin https://github.com/TON-PSEUDO/finance-daily.git
   git push -u origin main
   ```
   (GitHub te proposera la commande exacte avec ton pseudo dès que tu crées
   le dépôt — tu peux copier-coller directement depuis leur interface.)

## Étape 3 — Ajouter tes clés API en secret (jamais en clair dans le code)

Dans le dépôt GitHub : **Settings → Secrets and variables → Actions → New
repository secret**

Ajoute :
- `ANTHROPIC_API_KEY` → ta clé Anthropic
- `FRED_API_KEY` → ta clé FRED (optionnel)

## Étape 4 — Activer GitHub Pages

**Settings → Pages** → Source : "Deploy from a branch" → Branch : `main`,
dossier `/docs` → Save.

Ton site sera accessible à `https://TON-PSEUDO.github.io/finance-daily/`
en quelques minutes. C'est cette adresse que tu ouvres depuis ton téléphone
(tu peux l'ajouter à l'écran d'accueil pour qu'elle se comporte comme une
app).

## Étape 5 — Tester manuellement avant d'attendre le lendemain

**Actions** (onglet en haut du dépôt) → sélectionne "Rapport quotidien" →
**Run workflow** → Run. Ça prend 1-2 minutes. Tu peux suivre les logs en
direct, ce qui est utile pour corriger d'éventuelles erreurs (ticker
introuvable, quota API dépassé, etc.).

## Ajuster le contenu

- **Ajouter/retirer des indices, devises, actions** → modifie les
  dictionnaires en haut de `scripts/fetch_data.py`. N'importe quel ticker
  Yahoo Finance fonctionne (cherche le ticker sur finance.yahoo.com).
- **Changer l'heure d'exécution** → modifie les lignes `cron:` dans
  `.github/workflows/daily.yml` (horaires en UTC).
- **Changer le ton / le style des textes** → modifie `SYSTEM_PROMPT` dans
  `scripts/generate_analysis.py`.
- **Changer les couleurs / la mise en page** → tout est dans
  `static/style.css` (variables `:root` en haut du fichier) et les fichiers
  `templates/*.html`.

## Limites à connaître

- Les tickers `^FCHI`, `^GSPC` etc. sont des symboles Yahoo Finance non
  garantis à 100% dans la durée (Yahoo modifie parfois son API sans préavis)
  — c'est le compromis d'une solution gratuite. Si `yfinance` casse un jour,
  Financial Modeling Prep ou Twelve Data sont des alternatives payantes plus
  stables, avec la même logique de code.
- Le fichier `deep-dives` reste basé sur ce que Claude peut déduire des
  chiffres fournis — pas d'accès aux news en temps réel sauf si tu ajoutes
  une étape de recherche web complémentaire (possible dans une v2).
- Le cron GitHub Actions ne gère pas le changement heure été/hiver
  automatiquement — deux horaires sont programmés pour couvrir les deux cas.

## Pour aller plus loin (v2 possibles)

- Ajouter une vraie recherche de news du jour (API NewsAPI ou recherche web)
  pour enrichir les deep dives avec du contexte réel et non déductif.
- Générer aussi un PDF (via la bibliothèque `weasyprint`, qui convertit le
  HTML existant en PDF sans effort supplémentaire).
- Notification push (Telegram/ntfy) en plus du site, pour être alerté dès
  que le rapport du jour est prêt.
