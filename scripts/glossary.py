"""
glossary.py
Descriptions pédagogiques affichées dans la fenêtre modale quand on clique
sur un actif. Descriptions spécifiques pour les actifs les plus consultés
(indices, devises, matières premières, ETFs) + un texte générique de secours
pour tout le reste (actions de la watchlist), généré à partir du nom et de
la catégorie -> pas besoin de tout écrire à la main.
"""

GLOSSARY = {
    # --- Indices ---
    "^FCHI": "Le CAC 40 regroupe les 40 plus grandes capitalisations boursières françaises cotées à la Bourse de Paris (Euronext Paris). C'est l'indice de référence de l'économie française.",
    "^GDAXI": "Le DAX regroupe les 40 plus grandes entreprises allemandes cotées à la Bourse de Francfort. C'est l'indice phare de la première économie européenne.",
    "^FTSE": "Le FTSE 100 regroupe les 100 plus grandes capitalisations cotées à la Bourse de Londres. Beaucoup de ses membres réalisent l'essentiel de leur chiffre d'affaires hors du Royaume-Uni.",
    "^STOXX50E": "L'Euro Stoxx 50 regroupe les 50 plus grandes entreprises de la zone euro, tous pays confondus. C'est l'indice de référence pour la zone euro dans son ensemble.",
    "FTSEMIB.MI": "Le FTSE MIB regroupe les principales valeurs cotées à la Bourse de Milan, reflet de l'économie italienne.",
    "^IBEX": "L'IBEX 35 regroupe les 35 plus grandes valeurs cotées à la Bourse de Madrid, indice de référence espagnol.",
    "^GSPC": "Le S&P 500 regroupe 500 grandes entreprises américaines cotées et est considéré comme le meilleur baromètre de l'économie et de la bourse américaines dans leur ensemble.",
    "^IXIC": "Le Nasdaq Composite regroupe toutes les valeurs cotées sur le Nasdaq, avec une forte concentration de valeurs technologiques (Apple, Microsoft, Nvidia...).",
    "^DJI": "Le Dow Jones Industrial Average regroupe 30 grandes entreprises américaines historiques. C'est l'un des plus vieux indices boursiers au monde, encore très suivi malgré sa composition restreinte.",
    "^RUT": "Le Russell 2000 regroupe 2000 petites capitalisations américaines. Il est souvent utilisé comme baromètre de la santé de l'économie domestique US, plus sensible au cycle que les grandes valeurs.",
    "^N225": "Le Nikkei 225 regroupe 225 grandes entreprises cotées à la Bourse de Tokyo, indice de référence de l'économie japonaise.",
    "^HSI": "Le Hang Seng regroupe les principales valeurs cotées à la Bourse de Hong Kong, avec une forte proportion d'entreprises chinoises continentales.",
    "000001.SS": "Le Shanghai Composite regroupe l'ensemble des actions cotées à la Bourse de Shanghai (marché continental chinois, accès partiellement restreint aux investisseurs étrangers).",
    "^AXJO": "L'ASX 200 regroupe les 200 plus grandes entreprises cotées à la Bourse australienne, avec une forte pondération des secteurs minier et bancaire.",
    "^KS11": "Le KOSPI regroupe les principales valeurs cotées à la Bourse de Séoul, indice de référence sud-coréen, marqué par le poids de Samsung et de l'industrie technologique.",
    "^BSESN": "Le Sensex regroupe 30 grandes entreprises cotées à la Bourse de Bombay (BSE), l'un des deux indices de référence indiens.",
    "^NSEI": "Le Nifty 50 regroupe 50 grandes entreprises cotées au National Stock Exchange de l'Inde, indice de référence indien le plus suivi par les investisseurs internationaux.",
    "^GSPTSE": "Le S&P/TSX regroupe les principales entreprises cotées à la Bourse de Toronto, avec une forte pondération du secteur des matières premières et de l'énergie.",
    "^BVSP": "Le Bovespa (Ibovespa) regroupe les principales valeurs cotées à la Bourse de São Paulo, indice de référence brésilien et sud-américain.",
    "^MXX": "L'IPC regroupe les principales valeurs cotées à la Bourse mexicaine (BMV), indice de référence du Mexique.",
    "^JALSH": "Le JSE All Share regroupe l'ensemble des valeurs cotées au Johannesburg Stock Exchange, principal indice sud-africain.",

    # --- Devises ---
    "EURUSD=X": "Taux de change entre l'euro et le dollar américain, la paire de devises la plus échangée au monde. Une hausse signifie que l'euro se renforce face au dollar.",
    "GBPUSD=X": "Taux de change entre la livre sterling et le dollar américain (surnommé « Cable » sur les marchés).",
    "USDJPY=X": "Taux de change entre le dollar américain et le yen japonais. Très suivi car lié aux écarts de taux d'intérêt entre Fed et Banque du Japon.",
    "EURGBP=X": "Taux de change entre l'euro et la livre sterling, référence pour les échanges commerciaux entre la zone euro et le Royaume-Uni.",
    "USDCNY=X": "Taux de change entre le dollar américain et le yuan chinois (renminbi), partiellement encadré par la Banque populaire de Chine.",

    # --- Matières premières ---
    "GC=F": "Contrat à terme sur l'or, valeur refuge classique en période d'incertitude économique ou géopolitique, et protection historique contre l'inflation.",
    "SI=F": "Contrat à terme sur l'argent métal, à la fois valeur refuge et matière premières industrielle (électronique, panneaux solaires).",
    "CL=F": "Contrat à terme sur le pétrole WTI (West Texas Intermediate), référence du pétrole brut américain.",
    "BZ=F": "Contrat à terme sur le pétrole Brent, référence du pétrole brut européen/mondial, extrait en mer du Nord.",
    "NG=F": "Contrat à terme sur le gaz naturel américain (Henry Hub), très sensible à la météo et à la demande énergétique saisonnière.",
    "HG=F": "Contrat à terme sur le cuivre, souvent surnommé « Dr. Copper » car considéré comme un baromètre avancé de l'activité industrielle mondiale.",

    # --- ETFs ---
    "SPY": "ETF répliquant le S&P 500, l'un des trackers les plus échangés au monde, exposition large au marché actions américain.",
    "QQQ": "ETF répliquant le Nasdaq 100, fortement exposé aux grandes valeurs technologiques américaines.",
    "VTI": "ETF Vanguard répliquant l'ensemble du marché actions américain (grandes, moyennes et petites capitalisations).",
    "IWDA.AS": "ETF iShares répliquant l'indice MSCI World, exposition diversifiée aux marchés développés mondiaux.",
    "VWCE.DE": "ETF Vanguard répliquant le FTSE All-World, l'un des trackers les plus utilisés en Europe pour une exposition actions mondiale tous pays.",
    "XLK": "ETF sectoriel répliquant les valeurs technologiques du S&P 500.",
    "XLE": "ETF sectoriel répliquant les valeurs du secteur de l'énergie du S&P 500.",
    "XLF": "ETF sectoriel répliquant les valeurs financières (banques, assurances) du S&P 500.",
    "SMH": "ETF répliquant les principales entreprises mondiales de semi-conducteurs (Nvidia, TSMC, ASML...).",
    "GLD": "ETF adossé physiquement à de l'or, permettant une exposition au métal précieux sans le détenir physiquement.",
    "SLV": "ETF adossé physiquement à l'argent métal.",
    "TLT": "ETF répliquant les obligations d'État américaines à long terme (plus de 20 ans), sensible aux variations des taux d'intérêt.",
    "EEM": "ETF répliquant les marchés actions émergents au sens large (Chine, Inde, Brésil, Taïwan...).",
    "MCHI": "ETF répliquant les grandes valeurs chinoises cotées, exposition ciblée au marché actions chinois.",
}

_GENERIC_BY_CATEGORY = {
    "action": "Action cotée en bourse suivie dans la watchlist quotidienne pour repérer les mouvements de marché significatifs.",
    "indice": "Indice boursier suivant la performance d'un panier d'actions représentatif d'une place financière ou d'une zone géographique.",
    "devise": "Paire de devises suivant le taux de change entre deux monnaies sur le marché des changes (Forex).",
    "matiere_premiere": "Contrat à terme sur une matière première, dont le prix reflète l'offre et la demande physique mondiale.",
    "etf": "Fonds indiciel coté (ETF) permettant une exposition à un panier d'actifs en un seul instrument négociable en bourse.",
}


def get_description(symbol: str, name: str, category: str = "action") -> str:
    """Retourne la description spécifique si elle existe, sinon un texte
    générique adapté à la catégorie (action/indice/devise/matière première/etf)."""
    if symbol in GLOSSARY:
        return GLOSSARY[symbol]
    return f"{name}. " + _GENERIC_BY_CATEGORY.get(category, _GENERIC_BY_CATEGORY["action"])
