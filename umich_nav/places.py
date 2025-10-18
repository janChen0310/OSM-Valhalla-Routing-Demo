from typing import Dict, Optional, Tuple

LatLon = Tuple[float, float]

# Approximate coordinates for U-M North Campus landmarks (may be refined)
_PLACES: Dict[str, LatLon] = {
    "Pierpont Commons": (42.291096,-83.717606),
    "Duderstadt Center": (42.291143,-83.715849),
    "Chrysler Center": (42.290901,-83.716790),
    "EECS Building": (42.292373,-83.713915),
    "BBB": (42.293041,-83.716355),  # Bob and Betty Beyster Building
    "G.G. Brown": (42.293364,-83.714132),
    "Lurie Engineering Center": (42.291523,-83.713887),
    "FXB": (42.293548,-83.712117),  # François-Xavier Bagnoud Building
    "Walgreen Drama Center": (42.291977,-83.717434),
    "Lurie Biomedical Engineering": (42.288837,-83.713646),
    "Lurie Engineering Center": (42.291532,-83.713801),
    "Ann and Lurie Tower": (42.292036,-83.716184),
    "DOW Building": (42.293032,-83.715471),
    "Leinweber Center": (42.293032,-83.715471),
    "Cooley Laboratory": (42.290650,-83.713706),
    "Nuclear Engineering Laboratory": (42.291305,-83.714709),
    "Bursley Hall": (42.293719,-83.720956),
    "North Campus Recreation Building": (42.295566,-83.720194),
    "FMCRB": (42.294651,-83.709433),  # Ford Motor Company Robotics Building
}


def resolve_place(name: str) -> Optional[LatLon]:
    return _PLACES.get(name) or _PLACES.get(name.strip().title())
