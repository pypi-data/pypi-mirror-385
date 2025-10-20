from enum import Enum

class Font(Enum):
    COMPUTER_MODERN = ""
    TIMES_NEW_ROMAN = r"\usepackage{mathptmx}"
    FIRA_SANS = r"\usepackage[sfdefault]{FiraSans}"
    ROBOTO = r"\usepackage[sfdefault]{roboto}"
    NOTO_SANS = r"\usepackage[sfdefault]{noto-sans}"
    SOURCE_SANS_PRO = r"\usepackage[default]{sourcesanspro}"
    CORMORANT_GARAMOND = r"\usepackage{CormorantGaramond}"
    CHARTER = r"\usepackage{charter}"