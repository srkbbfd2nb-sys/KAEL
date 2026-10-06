"""
Authenticité comportementale — timing organique, heures de sommeil, délais.

Le rythme n'existe pas pour cacher l'IA (le profil la déclare) mais pour donner
au persona un rythme narratif lisible. Ce module ne contient délibérément pas
l'« imperfection calculée » (fautes de frappe volontaires) : sa mise en place est
une décision ouverte (D-10), voir priorisation.
"""

from __future__ import annotations

import random
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

PROFIL_DEFAUT = {
    "fuseau": "Europe/Paris",
    "sommeil": [23, 7],              # de 23 h à 7 h, heure locale
    "heures_preferees": [9, 13, 19],
    "sigma_minutes": 40,
}


def en_sommeil(instant: datetime, profil: dict = PROFIL_DEFAUT) -> bool:
    h = instant.astimezone(ZoneInfo(profil["fuseau"])).hour
    debut, fin = profil["sommeil"]
    return (h >= debut or h < fin) if debut > fin else (debut <= h < fin)


def prochain_creneau(apres: datetime, profil: dict = PROFIL_DEFAUT,
                     rng: random.Random | None = None, jours_max: int = 7) -> datetime:
    """Prochain instant de publication : une heure préférée, décalée d'un bruit
    gaussien, hors sommeil, strictement après `apres` (datetime avec fuseau)."""
    rng = rng or random.Random()
    tz = ZoneInfo(profil["fuseau"])
    local = apres.astimezone(tz)
    for j in range(jours_max):
        jour = (local + timedelta(days=j)).date()
        for h in sorted(profil["heures_preferees"]):
            centre = datetime.combine(jour, time(h), tzinfo=tz)
            t = centre + timedelta(minutes=rng.gauss(0, profil["sigma_minutes"]))
            if t > local and not en_sommeil(t, profil):
                return t
    raise RuntimeError("aucun créneau trouvé — profil de rythme incohérent")


def delai_reponse_minutes(canal: str, rng: random.Random | None = None) -> float:
    """Commentaire : 1 à 15 min. Message privé : 1 à 6 h. Spécification 3.2.2."""
    rng = rng or random.Random()
    if canal == "commentaire":
        return round(rng.uniform(1, 15), 1)
    if canal == "dm":
        return round(rng.uniform(60, 360), 1)
    raise ValueError(f"canal inconnu : {canal!r}")
