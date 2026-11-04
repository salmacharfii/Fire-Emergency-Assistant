import re                                          # regular expressions for keyword matching

FIRE_PATTERN = re.compile(                         # matches phrases that describe a fire happening NOW
    r"\b("
    r"there(?:'s| is) a fire"                      # "there is a fire", "there's a fire"
    r"|(?:is|are|am|was|were|got|gets?)\s+on\s+fire"   # "the kitchen is on fire"
    r"|on\s+fire"                                  # "on fire" in any other position
    r"|(?:caught|catch(?:es)?|catching)\s+fire"    # "caught fire"
    r"|fire\s+(?:has\s+)?broke(?:n)?\s+out"        # "fire broke out"
    r"|(?:is|are|something(?:'s| is))\s+burning"   # "something is burning"
    r"|burning\s+smell|smell\s+(?:of\s+)?(?:smoke|burning)"   # "I smell smoke"
    r"|(?:full\s+of|filled\s+with|see|seeing)\s+smoke|smoke\s+(?:is\s+)?(?:coming|filling|blocks?|everywhere)"
    r"|fire\s+alarm\s+(?:is\s+)?(?:sounding|going\s+off|ringing)"   # an alarm is ringing now
    r"|es\s+brennt|feuer(?:\s+im|\s+in)?(?=\W|$)|brennt|rauch\s+(?:im|in|überall)|flammen"   # German
    r")\b|\bfire!|\bfeuer!",                       # a shouted "Fire!"
    re.IGNORECASE,
)
# Only phrases that describe a fire right now trigger the steps.
# "fire hazard", "fire safety helpers" or "fire extinguisher" alone do not.

FIXED_STEPS = [                                    # shown in this order, always the same
    "1. Stay calm",
    "2. Raise the alarm: press the nearest fire alarm and call 112",
    "3. Get to safety: use the escape route, do not use the lift",
    "4. Go to the assembly point",
    "5. Fight the fire only if it is safe to do so",
]


def is_fire_emergency(question):                   # True if the question sounds like a fire right now
    return FIRE_PATTERN.search(question) is not None   # search finds the pattern anywhere in the text