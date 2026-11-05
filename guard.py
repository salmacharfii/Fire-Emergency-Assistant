import re                                          # regular expressions

PDF_SOURCE_PATTERN = re.compile(r"\[(?:source:\s*)?([^\]]+?), p\.(\d+)\]", re.IGNORECASE)   # [file.pdf, p.3], also [source: file.pdf, p.3]
DATA_SOURCE_PATTERN = re.compile(r"\[(?:source:\s*)?((?:zones|equipment|plan).json)\]", re.IGNORECASE)   # [zones.json], also [source: zones.json]

REFUSAL = (                                        # the one refusal text for every case
    "I found nothing about this in the approved documents. "
    "Please check your site's fire safety rules. "
    "In an emergency call 112 and follow the Brandschutzordnung."
)


def check_answer(answer):                          # returns (text to show, mode)
    text = answer.strip()                          # remove leading and trailing spaces
    if text == "NO_ANSWER":                        # the agent said the tools found nothing
        return REFUSAL, "refused"
    cited = PDF_SOURCE_PATTERN.search(text) or DATA_SOURCE_PATTERN.search(text)   # any valid citation at all
    if cited is None:                              # an answer without a citation is not trusted
        return REFUSAL, "refused"
    return text, "answer"                          # cited answer passes


def extract_sources(answer):                       # list the cited pages for the UI
    sources, seen = [], set()                      # unique (document, page) pairs
    for doc, page in PDF_SOURCE_PATTERN.findall(answer):    # every [file.pdf, p.N] in the text
        key = (doc, int(page))
        if key not in seen:                        # skip duplicates
            seen.add(key)
            sources.append({"source_doc": doc, "page": int(page)})
    for doc in DATA_SOURCE_PATTERN.findall(answer):          # every [zones.json] or [equipment.json]
        key = (doc, None)                          # data files have no page number
        if key not in seen:
            seen.add(key)
            sources.append({"source_doc": doc, "page": None})
    return sources