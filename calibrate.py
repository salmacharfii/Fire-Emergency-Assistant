"""Measure the best retrieval distance for every test question and propose MAX_DISTANCE.

Run:  py calibrate.py
"""
import json
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

import config

load_dotenv()                                              # reads OPENAI_API_KEY from .env
client = OpenAI()

# Same folder name as in build_index.py; falls back to "chroma_db" if config has no such name
CHROMA_DIR = getattr(config, "CHROMA_DIR", getattr(config, "CHROMA_PATH", "chroma_db"))
collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection("fire_safety")

questions = json.load(open("tests/questions.json", encoding="utf-8"))


def search(text):
    """Return (distance, source_doc, page) for the top-k chunks, closest first."""
    emb = client.embeddings.create(model=config.EMBED_MODEL, input=text).data[0].embedding
    res = collection.query(query_embeddings=[emb], n_results=config.TOP_K)
    return [(d, m.get("source_doc"), m.get("page")) for d, m in zip(res["distances"][0], res["metadatas"][0])]


answer_best, refuse_best = [], []
hits = total = 0

for q in questions:
    if q["uses"] not in ("documents", "none"):             # zone/equipment tools do not use distance
        continue
    hits_list = search(q["question"])
    best, doc, page = hits_list[0]
    if q["expect"] == "refuse":
        refuse_best.append((best, q["question"]))
        print(f"REFUSE  {best:.3f}  {q['question']}")
    else:
        answer_best.append((best, q["question"]))
        total += 1
        found = any(d == q["expected_doc"] and p in q["expected_pages"] for _, d, p in hits_list)
        hits += found
        print(f"ANSWER  {best:.3f}  {'HIT ' if found else 'MISS'}  {q['question']}  (top: {doc} p.{page})")

worst_answer = max(d for d, _ in answer_best)              # the answer question that is furthest away
closest_refuse = min(d for d, _ in refuse_best)            # the refuse question that is closest

print(f"\nRetrieval hit rate (right doc + page in top-{config.TOP_K}): {hits}/{total}")
print(f"Furthest answer question : {worst_answer:.4f}")
print(f"Closest refuse question  : {closest_refuse:.4f}")
if worst_answer < closest_refuse:
    print(f"Clean gap. Suggested MAX_DISTANCE = {(worst_answer + closest_refuse) / 2:.4f}")
else:
    print("Overlap: no single cutoff separates all questions. Look at the overlapping ones above;")
    print("pick a cutoff that keeps all answer questions and accept that the guard must refuse the rest.")
