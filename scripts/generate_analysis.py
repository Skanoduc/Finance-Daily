"""
generate_analysis.py
Prend le fichier data/raw_<date>.json (chiffres bruts) et demande à Claude
de rédiger les textes du jour : titre, synthèse, section "à surveiller demain",
commentaires par catégorie, et deep dives sur les plus fortes variations.

Nécessite la variable d'environnement ANTHROPIC_API_KEY.
"""

import json
import os
import sys
import datetime as dt
import anthropic

MODEL = "claude-sonnet-4-6"  # rapport qualité/prix adapté à une tâche quotidienne de ce type


SYSTEM_PROMPT = """Tu es un analyste financier senior qui rédige la synthèse quotidienne
d'une newsletter destinée à un lecteur avancé mais non-professionnel.
Ton style : factuel, précis, sans emphase artificielle, tu expliques le "pourquoi" derrière les chiffres.
Tu écris en français.
Tu réponds UNIQUEMENT en JSON valide, sans texte avant/après, sans balises markdown."""


def build_user_prompt(raw: dict) -> str:
    return f"""Voici les données de marché du {raw['date']} (format JSON, variations en %):

{json.dumps(raw, ensure_ascii=False, indent=2)}

Rédige la synthèse du jour. Réponds avec un objet JSON ayant EXACTEMENT cette forme :

{{
  "headline": "Titre court et factuel de l'actualité principale du jour (max 12 mots)",
  "headline_sub": "Une phrase de contexte (max 30 mots)",
  "synthese": ["paragraphe 1", "paragraphe 2", "paragraphe 3"],
  "a_venir": ["paragraphe sur ce qu'il faut surveiller dans les prochains jours"],
  "commentaire_indices_europe": "1-2 phrases sur les indices européens",
  "commentaire_indices_us": "1-2 phrases sur les indices américains",
  "commentaire_indices_asie": "1-2 phrases sur les indices asiatiques",
  "commentaire_devises": "1-2 phrases sur les devises",
  "commentaire_matieres_premieres": "1-2 phrases sur les matières premières",
  "deepdives": [
    {{
      "tag": "ACTION | INDICE | MACRO",
      "title": "Nom de l'actif + variation",
      "paragraphs": ["Explication détaillée de pourquoi ce mouvement a eu lieu, en te basant sur les données fournies et le contexte de marché connu."]
    }}
  ]
}}

Choisis 2 à 4 deep dives correspondant aux plus fortes variations (positives ou négatives)
présentes dans les données. Base-toi uniquement sur les chiffres fournis, ne prétends pas
avoir accès à des news en temps réel que tu n'as pas — reste factuel sur les ordres de grandeur."""


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    raw_path = f"data/raw_{date_str}.json"

    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)

    client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY depuis l'environnement

    resp = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(raw)}],
    )

    text = resp.content[0].text.strip()
    # Sécurité : au cas où le modèle encadrerait quand même sa réponse de ```json
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    analysis = json.loads(text)

    out_path = f"data/analysis_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"Analyse enregistrée dans {out_path}")


if __name__ == "__main__":
    main()
