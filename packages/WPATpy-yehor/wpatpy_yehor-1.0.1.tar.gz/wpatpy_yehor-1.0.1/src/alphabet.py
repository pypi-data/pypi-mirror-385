from typing import Dict, Union


nato_phonetic_alphabet: Dict[str, str] = {
    "a": "alfa",
    "b": "bravo",
    "c": "charlie",
    "d": "delta",
    "e": "echo",
    "f": "foxtrot",
    "g": "golf",
    "h": "hotel",
    "i": "india",
    "j": "juliett",
    "k": "kilo",
    "l": "lima",
    "m": "mike",
    "n": "november",
    "o": "oscar",
    "p": "papa",
    "q": "quebec",
    "r": "romeo",
    "s": "sierra",
    "t": "tango",
    "u": "uniform",
    "v": "victor",
    "w": "whiskey",
    "x": "xray",
    "y": "yankee",
    "z": "zulu",
    "1": "unaone",
    "2": "bissotwo",
    "3": "terrathree",
    "4": "kartefour",
    "5": "pantafive",
    "6": "soxisix",
    "7": "setteseven",
    "8": "oktoeight",
    "9": "novenine",
    "0": "nadazero",
    # Outdated old definitions but i thought i'd include them
    ",": "kilogramme",
    "/": "liverpool",
    "(break signal)": "madagascar",
    ".": "New York",
}

# DONT FORGET TO ADD IT TO ALIASES BELOW
custom_nato_alphabet: Dict[str, str] = {
    "a": "anarchy",
    "b": "bernard",
    "c": "ceremonial",
    "d": "dignity",
    "e": "eagle",
    "f": "franz",
    ".": "dotter",
    "*": "aster",
    "ae": "you can even do ts but idk why would you",
    # etc, u can add custom symbols! remember to make them strings
}


def get_alphabet(name: Union[str, Dict[str, str]]) -> Dict[str, str]:
    """Return an alphabet dictionary by name.

    Accepts either a dict (returned as-is) or a string identifying a dictionary
    defined in this module. Matching is tolerant to common aliases and case.

    Examples:
      get_alphabet('nato') -> nato_phonetic_alphabet
      get_alphabet('nato_phonetic_alphabet') -> nato_phonetic_alphabet
      get_alphabet(custom_dict) -> custom_dict

    Raises KeyError if no matching alphabet is found.
    """
    if isinstance(name, dict):
        # type: ignore[return-value]
        return name

    if not name:
        raise KeyError("Empty alphabet name")

    norm = str(name).strip().lower()

    # common alias mapping
# → ADD HERE YOUR ALPHABET ←
    aliases = {
        "nato": "nato_phonetic_alphabet",
        "nato_phonetic": "nato_phonetic_alphabet",
        "nato_phonetic_alphabet": "nato_phonetic_alphabet",
        "custom_nato": "custom_nato_alphabet",
        "custom_nato_alphabet": "custom_nato_alphabet",
    }

    key = aliases.get(norm, norm)

    if key in globals() and isinstance(globals()[key], dict):
        return globals()[key]

    for gk, gv in globals().items():
        if isinstance(gv, dict) and gk.lower() == norm:
            return gv

    raise KeyError(f"Alphabet '{name}' not found in alphabet module")