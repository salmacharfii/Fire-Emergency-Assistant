import sys                                         # to read the question and zone from the command line
import uuid                                        # a fresh session id, so memory does not interfere

from retrieval import retrieve, filter_relevant    # the two search steps
from agent import run_agent                        # the agent, before the guard touches its answer

question = sys.argv[1]                             # first argument: the question
zone = sys.argv[2] if len(sys.argv) > 2 else None  # second argument (optional): the zone

hits = retrieve(question, top_k=8)                 # step 1: the 8 closest chunks
print("RETRIEVED (top 8):")
for h in hits:
    print(f'  {h["distance"]:.3f}  {h["source_doc"]} p.{h["page"]}')

kept = filter_relevant(question, hits)             # step 2: what the grader keeps
print("KEPT BY GRADER:", [(h["source_doc"], h["page"]) for h in kept])

print("\nRAW AGENT ANSWER:\n", run_agent(question, str(uuid.uuid4()), zone))   # before the citation guard