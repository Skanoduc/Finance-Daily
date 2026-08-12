"""
config.py
Interrupteurs centraux du projet. Change ces valeurs pour activer/désactiver
des fonctionnalités sans avoir à toucher au reste du code.

Chaque script (fetch_data.py, generate_analysis.py, build_site.py) importe
ce fichier et adapte son comportement en fonction.
"""

FEATURES = {
    # Deep dives = la fonctionnalité la plus coûteuse (recherche web +
    # beaucoup de texte généré). Mets False pour la mettre en pause :
    # le site continue de fonctionner normalement, juste sans cette section.
    "deepdives": False,

    # Pages / catégories de données
    "macro": True,
    "etfs": True,

    # Notification (Telegram) une fois le rapport du jour prêt.
    # Nécessite les secrets TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID
    # (voir README pour la configuration) -> ignoré silencieusement si absents.
    "notifications": True,

    # Petits graphiques (sparklines) sur les 20 dernières séances,
    # affichés à côté de chaque actif sur les pages Indices/Devises/ETFs.
    "sparklines": True,
}
