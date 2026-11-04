"""Run the 30 test questions through the assistant and score them in LangSmith.

Run:  py evaluate.py
Needs in .env: OPENAI_API_KEY, LANGSMITH_API_KEY, LANGSMITH_TRACING=true
"""
import json
import uuid

from dotenv import load_dotenv

load_dotenv()                                              # must run BEFORE importing main (keys, tracing flag)

from langsmith import Client, evaluate                     # noqa: E402
from main import ask, AskRequest                           # noqa: E402  (calls the same code as POST /ask)

DATASET = "fire-assistant-eval"
client = Client()
questions = json.load(open("tests/questions.json", encoding="utf-8"))

# ---------- 1. dataset: recreated on every run so it always matches questions.json ----------
if client.has_dataset(dataset_name=DATASET):
    client.delete_dataset(dataset_name=DATASET)
dataset = client.create_dataset(DATASET, description="30 test questions for the Fire Emergency Assistant")
client.create_examples(
    dataset_id=dataset.id,
    inputs=[{"question": q["question"], "zone": q["zone"]} for q in questions],
    outputs=[{k: q[k] for k in ("expect", "expected_doc", "expected_pages", "fire")} for q in questions],
)

# ---------- 2. target: what LangSmith runs for each question ----------
collected = {}                                             # question -> outputs, used for the local failure list


def target(inputs):
    req = AskRequest(question=inputs["question"], session_id=str(uuid.uuid4()), zone=inputs.get("zone"))
    res = ask(req)                                         # fresh session_id per question: no memory leaks between tests
    out = res.model_dump() if hasattr(res, "model_dump") else dict(res)
    collected[inputs["question"]] = out
    return out


# ---------- 3. evaluators: one score each, 1 = pass, 0 = fail ----------
def mode_correct(outputs, reference_outputs):
    """Answered when it should answer, refused when it should refuse."""
    answered = outputs.get("mode") == "answer"
    return {"key": "mode_correct", "score": int(answered == (reference_outputs["expect"] == "answer"))}


def source_correct(outputs, reference_outputs):
    """Right document (and right page for PDFs) is cited; a refusal must cite nothing."""
    sources = outputs.get("sources") or []
    if reference_outputs["expect"] == "refuse":
        return {"key": "source_correct", "score": int(len(sources) == 0)}
    docs = {s["source_doc"] for s in sources}
    pages = {s.get("page") for s in sources if s["source_doc"] == reference_outputs["expected_doc"]}
    in_text = f"[{reference_outputs['expected_doc']}" in (outputs.get("answer") or "")   # zones.json / equipment.json citations
    if reference_outputs["expected_pages"]:                # PDF question: doc AND page must match
        ok = bool(pages & set(reference_outputs["expected_pages"]))
    else:                                                  # JSON tool question: doc is enough
        ok = reference_outputs["expected_doc"] in docs or in_text
    return {"key": "source_correct", "score": int(ok)}


def fire_steps_correct(outputs, reference_outputs):
    """Fixed safety steps appear exactly when the question describes a fire."""
    shown = bool(outputs.get("safety_steps"))
    return {"key": "fire_steps_correct", "score": int(shown == reference_outputs["fire"])}


# ---------- 4. run ----------
results = evaluate(
    target,
    data=DATASET,
    evaluators=[mode_correct, source_correct, fire_steps_correct],
    experiment_prefix="fire-assistant",
    max_concurrency=2,                                     # gentle on rate limits
)

# ---------- 5. local summary: totals plus every failing question ----------
checks = {"mode_correct": mode_correct, "source_correct": source_correct, "fire_steps_correct": fire_steps_correct}
totals = {name: 0 for name in checks}
print("\nFAILURES")
for q in questions:
    out = collected.get(q["question"])
    if out is None:
        print("  (no output)", q["question"])
        continue
    for name, fn in checks.items():
        score = fn(out, q)["score"]
        totals[name] += score
        if not score:
            print(f"  {name:19} | {q['question']}  -> mode={out.get('mode')} sources={[(s['source_doc'], s.get('page')) for s in out.get('sources', [])]}")
print("\nSCORES (out of", len(questions), ")", totals)
print("Open LangSmith > Datasets & Experiments > fire-assistant-eval to see traces and per-question results.")