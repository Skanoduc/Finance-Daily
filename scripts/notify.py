"""
notify.py
Envoie un message Telegram une fois le rapport du jour généré, avec le titre
du jour et le lien vers le site.

Nécessite les secrets TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID -> si absents,
le script ne fait rien (pas d'erreur, la notification est juste sautée).

Configuration (voir README pour le détail pas à pas) :
1. Parler à @BotFather sur Telegram -> /newbot -> récupérer le token
2. Démarrer une conversation avec ton bot, puis récupérer ton chat_id via
   https://api.telegram.org/bot<TOKEN>/getUpdates
3. Ajouter TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID dans les secrets GitHub
"""

import json
import os
import sys
import datetime as dt
import urllib.request
import urllib.parse

SITE_URL = "https://skanoduc.github.io/finance-daily/"


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[info] TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID absent -> notification sautée")
        return

    date_str = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    analysis_path = f"data/analysis_{date_str}.json"

    headline = "Le rapport du jour est prêt"
    try:
        with open(analysis_path, encoding="utf-8") as f:
            analysis = json.load(f)
        headline = analysis.get("headline", headline)
    except FileNotFoundError:
        pass

    text = f"📊 Finance Daily\n\n{headline}\n\n{SITE_URL}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=10) as r:
            r.read()
        print("Notification Telegram envoyée")
    except Exception as e:
        # On ne fait jamais échouer tout le workflow pour un souci de notification
        print(f"[warn] échec de l'envoi de la notification Telegram : {e}")


if __name__ == "__main__":
    main()
