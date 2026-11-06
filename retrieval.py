import sys                                         # to read the question from the command line
import chromadb                                    # the vector database
import re                                          
from openai import OpenAI                          # client for the OpenAI API

from config import (CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL, LLM_MODEL,
                    TOP_K, MAX_DISTANCE)           # settings from config.py (this also loads .env)          # settings from config.py (this also loads .env)

_client = OpenAI()                                 # one shared API client; the underscore marks it as internal
_collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(COLLECTION_NAME)   # open the index built on Day 2


def retrieve(question, top_k=TOP_K, max_distance=MAX_DISTANCE, where=None):
    # where = optional metadata filter, e.g. {"language": "en"}; unused for now
    embedding = _client.embeddings.create(         # turn the question into a vector ...
        model=EMBED_MODEL, input=[question]        # ... with the same model that embedded the chunks
    ).data[0].embedding                            # the first (and only) vector
    result = _collection.query(                    # ask Chroma for the nearest chunks
        query_embeddings=[embedding],              # one question = a list with one vector
        n_results=top_k,                           # how many chunks to return
        where=where,                               # optional metadata filter
        include=["documents", "metadatas", "distances"],   # texts, sources and distances; ids always come back
    )
    hits = []                                      # chunks that pass the cutoff
    for text, meta, distance in zip(               # walk through the three parallel lists
        result["documents"][0],                    # [0] = results for the first (only) question
        result["metadatas"][0],
        result["distances"][0],
    ):
        if distance <= max_distance:               # keep only close-enough chunks (smaller = closer)
            hits.append({                          # one dictionary per accepted chunk
                "text": text,                      # the chunk text
                "source_doc": meta["source_doc"],  # file name
                "page": meta["page"],              # page number
                "distance": distance,              # kept so calibrate.py can read it on Day 6
            })
    return hits                                    # empty list = nothing relevant found


def format_context(hits):                          # turns hits into the text block the agent receives
    return "\n\n".join(                            # a blank line between chunks
        f'[{h["source_doc"]}, p.{h["page"]}]\n{h["text"]}'   # label like [file.pdf, p.3] above each chunk
        for h in hits
    )


GRADER_PROMPT = (                                  # instructions for the relevance check
    "You check search results for a fire safety assistant. "
    "You get a question and numbered passages. "
    "Return the numbers of the passages that DIRECTLY contain the answer to the question, separated by commas, for example: 1,3. "
    "A passage that only mentions related words (fire, extinguisher, exit) but does not answer the question does not count. "
    "If the question names a special condition (for example increased fire hazard), include the passage that covers that condition. "
    "Treat a laptop, computer, phone, charger, battery or household appliance as electrical equipment: a passage about electrical equipment or electrical fires directly answers questions about them. "    
    "List the most direct passage first and return at most 3 numbers. "
    "If no passage directly answers the question, return exactly: NONE."
)

def filter_relevant(question, hits):               # keeps only the chunks that really answer the question
    if not hits:                                   # nothing to check
        return []
    numbered = "\n\n".join(f'[{i}] {h["text"]}' for i, h in enumerate(hits, start=1))   # [1] text, [2] text, ...
    reply = _client.chat.completions.create(       # one small, cheap model call
        model=LLM_MODEL,                           # the same gpt-4o-mini
        temperature=0,                             # same input = same decision
        max_tokens=20,                             # the reply is only a few numbers
        messages=[
            {"role": "system", "content": GRADER_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nPassages:\n{numbered}"},
        ],
    ).choices[0].message.content
    order = []                                     # numbers in the order the grader named them, most direct first
    for n in re.findall(r"\d+", reply):
        n = int(n)
        if 1 <= n <= len(hits) and n not in order:   # ignore numbers out of range and duplicates
            order.append(n)
    return [hits[n - 1] for n in order]            # the most direct passage comes first, so the agent cites it first


if __name__ == "__main__":                         # runs only with: py retrieval.py "question"
    question = " ".join(sys.argv[1:])              # everything after the file name is the question
    for h in retrieve(question):                   # run the search
        print(f'{h["distance"]:.3f}  {h["source_doc"]} p.{h["page"]}  {h["text"][:800]!r}')   # distance (3 decimals), source, first 800 characters