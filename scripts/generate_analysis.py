"""
generate_analysis.py
Prend le fichier data/raw_<date>.json (chiffres bruts) et demande à Claude
de rédiger les textes du jour : titre, synthèse, section "à surveiller demain",
commentaires par catégorie, et deep dives sourcés sur les plus fortes variations.

Claude a accès à la recherche web en direct (outil web_search de l'API) pour
appuyer ses deep dives sur de vraies news du jour plutôt que sur de simples
déductions à partir des chiffres. Chaque deep dive inclut ses sources.

Nécessite la variable d'environnement ANTHROPIC_API_KEY.
"""

import json
import os
import sys
import datetime as dt
import anthropic
from config import FEATURES

MODEL = "claude-sonnet-4-6"  # rapport qualité/prix adapté à une tâche quotidienne de ce type
MAX_SEARCH_ROUNDS = 8  # limite de sécurité sur le nombre d'allers-retours avec l'outil de recherche
MAX_TOKENS = 12000 if FEATURES["deepdives"] else 3000  # bien moins de texte à générer sans deep dives


SYSTEM_PROMPT = """Tu es un analyste financier senior qui rédige la synthèse quotidienne
d'une newsletter destinée à un lecteur avancé mais non-professionnel.
Ton style : factuel, précis, sans emphase artificielle, tu expliques le "pourquoi" derrière les chiffres.
Tu écris en français.
""" + ("""
Tu as accès à un outil de recherche web : utilise-le systématiquement pour les deep dives,
afin d'expliquer les mouvements de marché avec de vrais faits du jour (résultats d'entreprise,
annonces, données macro, événements géopolitiques) plutôt que des suppositions. Ne te contente
jamais des chiffres seuls pour un deep dive : cherche toujours le "pourquoi" réel, et note l'URL
de chaque source utilisée.
""" if FEATURES["deepdives"] else """
Tu n'as PAS accès à la recherche web pour cette tâche : base-toi uniquement sur les chiffres
fournis pour la synthèse générale, sans détailler de deep dives sur des mouvements individuels.
""") + """
Ta réponse finale doit être UNIQUEMENT le JSON demandé, sans texte avant/après, sans balises
markdown, sans commentaire. N'écris aucune phrase d'introduction du type "Let me compile..." :
ton message doit commencer directement par l'accolade ouvrante du JSON."""


def build_user_prompt(raw: dict) -> str:
    deepdives_section = """
Choisis 3 à 6 deep dives correspondant aux plus fortes variations (positives ou négatives,
tous types d'actifs confondus) présentes dans les données. Chaque deep dive doit citer au
moins une source réelle trouvée par la recherche web. Si tu ne trouves vraiment aucune
information fiable sur un mouvement, dis-le explicitement dans le paragraphe plutôt que
d'inventer une explication.""" if FEATURES["deepdives"] else """
La fonctionnalité "deep dives" est actuellement en pause -> renvoie "deepdives": [] (liste vide),
ne cherche pas à en produire."""

    return f"""Voici les données de marché du {raw['date']} (format JSON, variations en %):

{json.dumps(raw, ensure_ascii=False, indent=2)}

Rédige la synthèse du jour.

Ta réponse finale doit être un objet JSON ayant EXACTEMENT cette forme :

{{
  "headline": "Titre court et factuel de l'actualité principale du jour (max 12 mots)",
  "headline_sub": "Une phrase de contexte (max 30 mots)",
  "synthese": ["paragraphe 1", "paragraphe 2", "paragraphe 3"],
  "a_venir": ["paragraphe sur ce qu'il faut surveiller dans les prochains jours"],
  "commentaire_indices_europe": "1-2 phrases sur les indices européens",
  "commentaire_indices_us": "1-2 phrases sur les indices américains",
  "commentaire_indices_asie": "1-2 phrases sur les indices asiatiques",
  "commentaire_indices_ameriques": "1-2 phrases sur le Canada/Brésil/Mexique",
  "commentaire_devises": "1-2 phrases sur les devises",
  "commentaire_matieres_premieres": "1-2 phrases sur les matières premières",
  "deepdives": [
    {{
      "tag": "ACTION | INDICE | MACRO | MATIÈRE PREMIÈRE",
      "title": "Nom de l'actif + variation",
      "paragraphs": ["Explication détaillée et factuelle de pourquoi ce mouvement a eu lieu."],
      "sources": [{{"title": "Nom de la source", "url": "https://..."}}]
    }}
  ]
}}
{deepdives_section}"""


def run_analysis(client, raw):
    """Appelle l'API. Si les deep dives sont activés, l'outil web_search est
    utilisé (outil "serveur" : Anthropic exécute les recherches en interne).
    Sinon, un simple appel sans outil est fait -> beaucoup plus rapide et
    beaucoup moins cher.

    Le seul cas où l'on doit rappeler l'API nous-même est "pause_turn"
    (recherche encore en cours côté serveur) : on renvoie alors simplement
    le contenu déjà généré et Claude reprend là où il s'est arrêté."""
    messages = [{"role": "user", "content": build_user_prompt(raw)}]
    tools = [{"type": "web_search_20250305", "name": "web_search"}] if FEATURES["deepdives"] else None

    for _ in range(MAX_SEARCH_ROUNDS):
        kwargs = dict(model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT, messages=messages)
        if tools:
            kwargs["tools"] = tools
        resp = client.messages.create(**kwargs)

        if resp.stop_reason == "pause_turn":
            # Recherche encore en cours -> on renvoie le contenu tel quel pour continuer
            messages.append({"role": "assistant", "content": resp.content})
            continue

        if resp.stop_reason == "max_tokens":
            raise RuntimeError(
                f"Réponse coupée avant la fin (max_tokens={MAX_TOKENS} atteint). "
                f"Augmente MAX_TOKENS dans le script."
            )

        text_blocks = [b.text for b in resp.content if b.type == "text"]
        text = "\n".join(text_blocks).strip()
        if not text:
            raise RuntimeError(
                f"Réponse vide de Claude (stop_reason={resp.stop_reason}). "
                f"Contenu brut reçu : {resp.content}"
            )
        return text

    raise RuntimeError("Trop d'allers-retours (pause_turn) sans réponse finale")


def extract_json(text: str) -> str:
    """Isole le premier objet JSON valide dans le texte, même si Claude a
    ajouté du texte de narration avant/après (ex: 'Let me research...') malgré
    la consigne de ne répondre qu'en JSON."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"Aucun objet JSON trouvé dans la réponse :\n{text}")
    return text[start:end + 1]


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    raw_path = f"data/raw_{date_str}.json"

    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)

    client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY depuis l'environnement

    text = run_analysis(client, raw)
    # Extraction robuste : isole le JSON même si Claude a ajouté du texte
    # de narration avant/après malgré la consigne, ou des balises ```json.
    json_text = extract_json(text)
    try:
        analysis = json.loads(json_text)
    except json.JSONDecodeError as e:
        print("[erreur] Impossible de parser la réponse de Claude en JSON.")
        print("--- Réponse brute reçue ---")
        print(text)
        print("--- Fin de la réponse brute ---")
        raise

    out_path = f"data/analysis_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"Analyse enregistrée dans {out_path}")


if __name__ == "__main__":
    main()
