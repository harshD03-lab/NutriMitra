"""Dietary compatibility rules for NutriMitra.

The nutrition dataset (ICMR-NIN / IFCT 2017) stores dish names plus per-100 g
nutrient values.  It has no structured ingredient, allergen or diet-tag
columns, so diet compatibility is derived from two sources:

1. the dish name (token level, so "Eggplant" is not an egg and "Khaman" is
   not ham), and
2. the dataset's own vegetarian flag, which is used only as a tie breaker
   when the name carries no signal.

Everything in this module is *filtering* logic.  It never produces medical
claims - medical conditions are handled by :mod:`app.ml.medical_rules`.
"""

import re

_WORD_RE = re.compile(r"[a-z0-9]+")

# Animal flesh / seafood.  Matched on whole words only.
MEAT_TOKENS = {
    "chicken", "mutton", "beef", "pork", "lamb", "goat", "duck", "rabbit",
    "quail", "pigeon", "venison", "bacon", "ham", "sausage", "salami",
    "meat", "keema", "kheema", "mince", "luncheon", "chorizo",
}

FISH_TOKENS = {
    "fish", "machli", "rohu", "surmai", "prawn", "shrimp", "crab", "lobster",
    "tuna", "salmon", "sardine", "anchovy", "pomfret", "hilsa", "seer",
    "catfish", "tilapia", "sole", "squid", "calamari", "roe",
}

EGG_TOKENS = {
    "egg", "eggs", "anda", "ande", "omelette", "omlet", "mayonnaise",
}

DAIRY_TOKENS = {
    "milk", "curd", "dahi", "paneer", "butter", "ghee", "cream", "cheese",
    "yogurt", "yoghurt", "lassi", "buttermilk", "khoya", "rabri", "custard",
    "chocolate", "malt", "horlicks", "icecream",
}

# Honey and other bee products are animal derived, so they are not vegan.
HONEY_TOKENS = {"honey"}

# Words that mark a dish as plant based.
#
# ``VEG_OVERRIDE_TOKENS`` are explicit vegetarian statements.  They override
# an egg/ambiguous match, so "Vegetarian egg kofta curry" stays vegetarian.
#
# ``VEG_HINT_TOKENS`` are only used to disambiguate preparations whose name
# contains a word that is usually - but not always - animal based
# ("Vegetable seekh kebab" vs "Boti kebab").  They must never override a
# named animal product, otherwise "Spinach mushroom scrambled egg" would be
# treated as vegetarian.
VEG_OVERRIDE_TOKENS = {
    "vegetarian", "vegeterian", "vegetable", "vegetables", "veg", "veggie",
    "vegan", "eggless", "jain",
}

VEG_HINT_TOKENS = VEG_OVERRIDE_TOKENS | {
    "soya", "soy", "soyaabean", "soyabean", "paneer", "mushroom", "dal",
    "daal", "chana", "chickpea", "besan", "aloo", "potato", "tofu", "peas",
    "corn", "spinach", "cabbage", "cauliflower", "brinjal", "okra", "bhindi",
    "rajma", "sprouts", "lentil", "beans", "dal", "rice", "roti", "chapati",
    "paratha", "dosa", "idli", "upma", "poha", "halwa", "laddu", "tofu",
    "besan", "peanut", "groundnut", "sesame", "walnut", "cashew", "almond",
    "pistachio", "raisin", "banana", "mango", "orange", "apple", "grapes",
    "pear", "papaya", "guava", "pineapple", "watermelon",
}

# Preparations that are non-vegetarian unless the dish name also carries a
# vegetable marker ("Vegetable seekh kebab" is vegetarian, "Boti kebab" is not).
AMBIGUOUS_MEAT_TOKENS = {"kebab", "seekh", "boti", "shammi", "kofta", "tikka"}

# Phrases that must not trigger the dairy rule ("Butter bean" is a vegetable).
DAIRY_FALSE_POSITIVES = {"butter bean", "butter beans"}

# Allergen groups a user can declare.  Each group maps to name tokens.
ALLERGEN_GROUPS: dict[str, set[str]] = {
    "milk": {"milk", "curd", "dahi", "paneer", "butter", "ghee", "cream",
             "cheese", "yogurt", "yoghurt", "buttermilk", "khoya", "rabri",
             "custard", "malt", "horlicks", "chocolate"},
    "dairy": {"milk", "curd", "dahi", "paneer", "butter", "ghee", "cream",
              "cheese", "yogurt", "yoghurt", "buttermilk", "khoya", "rabri",
              "custard", "malt", "horlicks", "chocolate"},
    "egg": {"egg", "eggs", "anda", "ande", "omelette", "omlet", "mayonnaise"},
    "peanut": {"peanut", "peanuts", "groundnut", "groundnuts"},
    "nuts": {"nut", "nuts", "almond", "almonds", "cashew", "cashews",
             "walnut", "walnuts", "pistachio", "pistachios", "hazelnut"},
    "soy": {"soy", "soya", "soyaabean", "soyabean", "soya-bean"},
    "wheat": {"wheat", "maida", "bread", "roti", "chapati", "paratha", "puri",
              "pita", "noodles", "pasta", "biscuit", "rusk", "vermicelli",
              "sooji", "rava", "semolina", "daliya", "suji", "daliya"},
    "gluten": {"wheat", "maida", "bread", "roti", "chapati", "paratha", "puri",
               "pita", "noodles", "pasta", "biscuit", "rusk", "vermicelli",
               "sooji", "rava", "semolina", "daliya", "suji", "barley"},
    "fish": FISH_TOKENS,
    "seafood": FISH_TOKENS,
    "shellfish": {"prawn", "prawns", "shrimp", "crab", "lobster", "squid",
                  "oyster", "mussel", "clam"},
    "sesame": {"sesame", "sesame seed", "til"},
    "mustard": {"mustard", "sarson", "rai"},
    "corn": {"corn", "maize"},
}

# Canonical names used in the API response / explanation text.
ALLERGEN_ALIASES: dict[str, str] = {
    "milk": "milk", "dairy": "milk", "lactose": "milk", "casein": "milk",
    "egg": "egg", "eggs": "egg", "egg albumin": "egg",
    "peanut": "peanut", "peanuts": "peanut", "groundnut": "peanut",
    "nuts": "nuts", "treenuts": "nuts", "tree nuts": "nuts",
    "almond": "nuts", "cashew": "nuts", "walnut": "nuts", "pistachio": "nuts",
    "soy": "soy", "soya": "soy", "soyabean": "soy",
    "wheat": "wheat", "gluten": "gluten",
    "fish": "fish", "seafood": "fish",
    "shellfish": "shellfish", "crustaceans": "shellfish",
    "sesame": "sesame", "mustard": "mustard", "corn": "corn",
}

SUPPORTED_ALLERGENS = sorted(ALLERGEN_ALIASES)


def tokenize(name: str | None) -> set[str]:
    return set(_WORD_RE.findall((name or "").lower()))


def _normalised_phrase(name: str | None) -> str:
    return " ".join(_WORD_RE.findall((name or "").lower()))


def classify_food(name: str | None, is_veg_flag: bool | None = None) -> dict:
    """Classify a food record for diet compatibility.

    Returns a dict with the flags ``is_vegetarian``, ``is_dairy`` and
    ``is_egg``.  ``is_egg`` is also ``True`` for animal flesh/fish so callers
    can treat "animal derived" as a single concept.
    """
    tokens = tokenize(name)
    phrase = _normalised_phrase(name)

    has_meat = bool(tokens & MEAT_TOKENS) or bool(tokens & FISH_TOKENS)
    has_egg_token = bool(tokens & EGG_TOKENS)
    # "Mayonnaise without eggs" / "eggless cake" are explicitly egg free.
    egg_free = "eggless" in tokens or "without" in tokens
    if egg_free:
        has_egg_token = False

    has_veg_override = bool(tokens & VEG_OVERRIDE_TOKENS)
    has_veg_hint = has_veg_override or bool(tokens & VEG_HINT_TOKENS)
    ambiguous_meat = bool(tokens & AMBIGUOUS_MEAT_TOKENS)

    is_vegetarian = True
    if has_meat:
        # A named animal product always wins, except for mock versions that
        # explicitly declare themselves vegetarian.
        is_vegetarian = False
    elif ambiguous_meat and not has_veg_hint:
        is_vegetarian = False
    elif has_egg_token and not has_veg_override:
        is_vegetarian = False
    elif is_veg_flag is False:
        # The dataset explicitly flagged this row as non-vegetarian.
        is_vegetarian = False

    is_dairy = bool(tokens & DAIRY_TOKENS)
    for false_positive in DAIRY_FALSE_POSITIVES:
        if false_positive in phrase:
            is_dairy = False

    return {
        "is_vegetarian": is_vegetarian,
        "is_dairy": is_dairy,
        "is_egg": has_egg_token or has_meat,
        "is_honey": bool(tokens & HONEY_TOKENS),
    }


def normalise_allergens(allergies: str | None) -> tuple[set[str], list[str]]:
    """Split a free text allergy list into supported groups and the rest.

    Returns ``(supported, unsupported)`` where *supported* holds canonical
    allergen names that the filter can act on and *unsupported* holds the
    user supplied terms that could not be mapped (these are reported back to
    the user instead of being silently ignored).
    """
    supported: set[str] = set()
    unsupported: list[str] = []
    if not allergies:
        return supported, unsupported
    for raw in allergies.split(","):
        term = raw.strip().lower()
        if not term:
            continue
        canonical = ALLERGEN_ALIASES.get(term)
        if canonical:
            supported.add(canonical)
        else:
            unsupported.append(raw.strip())
    return supported, unsupported


def allergen_tokens(allergens: set[str]) -> set[str]:
    """Expand canonical allergen names into the name tokens to exclude."""
    tokens: set[str] = set()
    for allergen in allergens:
        tokens |= ALLERGEN_GROUPS.get(allergen, set())
    return tokens


def food_matches_allergens(name: str | None, tokens: set[str]) -> bool:
    """True when the food name indicates it contains one of the allergens."""
    if not tokens:
        return False
    return bool(tokenize(name) & tokens)
