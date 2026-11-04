import re                                          # regular expressions for keyword matching

FIRE_PATTERN = re.compile(                         # matches whole words only
    r"\b(feuer|brand|brennt|rauch|flammen|fire|smoke|flames|burning)\b",   # German and English fire words
    re.IGNORECASE,                                 # Feuer = feuer = FEUER
)
# \b means word border: "Brand" matches, but "Brandschutzordnung" does not, so a document question never triggers the banner.

FIXED_STEPS = [                                    # shown in this order, always the same
    "1. Stay calm",
    "2. Raise the alarm: press the nearest fire alarm and call 112",
    "3. Get to safety: use the escape route, do not use the lift",
    "4. Go to the assembly point",
    "5. Fight the fire only if it is safe to do so",
]


def is_fire_emergency(question):                   # True if the question sounds like a fire right now
    return FIRE_PATTERN.search(question) is not None   # search finds the pattern anywhere in the text