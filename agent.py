from langchain.agents import create_agent          # builds an agent that can call tools in a loop
from langchain_openai import ChatOpenAI            # the OpenAI chat model as a LangChain object
from langgraph.checkpoint.memory import InMemorySaver   # keeps each conversation in the server's memory

from config import LLM_MODEL                       # "gpt-4o-mini" (this import also loads .env, including the LangSmith keys)
from tools import search_documents, get_zone_info, check_equipment, find_nearest   # the tools

SYSTEM_PROMPT = (                                  # the rules the agent follows on every question
    "You are a fire safety assistant for employees of one company. "
    "Use the tools to find facts: search_documents for rules and procedures (search with the user's own key words, for example 'maximum distance to the nearest fire extinguisher'), "
    "get_zone_info for exits, extinguishers and assembly points of a zone, "
    "find_nearest for the closest exits, extinguishers, alarm buttons, assembly points or first aid points on the building plan, "
    "check_equipment for inspection dates. "
    "If the message contains a line [User is in zone: X], use that zone for questions about the user's surroundings. "
    "If the message contains a line [User position is marked on the plan ...], call find_nearest for questions about the nearest exit, extinguisher, alarm button, assembly point or first aid point. "
    "A line [Plan lookup ...] in the message is the result of find_nearest: use it, do not call find_nearest again. "
    "find_nearest says whether a distance is a walking distance around the drawn walls or a straight line; repeat that. Fire, smoke and blocked doors are never known: never say that a route is free or safe, tell the user to follow corridors and escape-route signs. "
    "Answer ONLY from tool results, never from your own knowledge. "   # no outside knowledge
    "Cite only passages that contain the statement you make. "   # no decorative citations
    "A citation must be the label of the passage the statement comes from; never put a statement under another passage's label. "   # stops mixed-up pages
    "Write citations in square brackets exactly as labelled, without the word 'source'. "   # the guard expects this exact shape
    "EVERY numbered step and EVERY sentence must end with its own citation in square brackets: [<file name>, p.<page>] copied from the passage label, or [zones.json], [equipment.json], [plan.json]. An answer without a citation is rejected. "
    "Copy the label printed above the passage exactly, with its real file name and page number, or use [zones.json], [equipment.json] or [plan.json]. "   # no example text to copy
    "A tool result that answers the question is a valid answer even if it says 'none' or 'ok'; cite it. "   # e.g. "Overdue items: none"
    "If a passage contains the number, distance or rule that answers the question, answer with it and cite it. "
    "If search_documents returns NO_RESULTS, or the results clearly contain nothing about the question "
    "(for example questions about laws, fines, prices or other places), reply with exactly: NO_ANSWER. "   # a fixed word the code can detect
    "(for example questions about laws, fines, prices or other places), reply with exactly: NO_ANSWER. "   # a fixed word the code can detect
    "Always answer in English, even if a document is in German. "
    "Be short. Use numbered steps for instructions."
)

model = ChatOpenAI(model=LLM_MODEL, temperature=0)  # temperature 0 = least random wording

agent = create_agent(                              # one agent object, created once when the server starts
    model=model,                                   # which model decides and answers
    tools=[search_documents, get_zone_info, check_equipment, find_nearest],   # what it may call
    system_prompt=SYSTEM_PROMPT,                   # the rules above
    checkpointer=InMemorySaver(),                  # memory: stores the messages of each thread_id
)


def run_agent(question, session_id, zone=None, room=None, has_position=False, lookup=None):    # one user turn in, answer text out
    lines = []                                     # context lines in front of the question
    if has_position:                               # the user tapped the plan
        where = f", nearest room: {room}" if room else ""
        lines.append(f"[User position is marked on the plan{where}]")
    if zone:                                       # a zone is known (picked, or taken from the nearest room)
        lines.append(f"[User is in zone: {zone}]")
    if lookup:                                     # the plan lookup the server already ran for this question
        lines.append(f"[Plan lookup, already done for this question; treat it as a tool result and cite [plan.json]: {lookup}]")
    text = "\n".join(lines + [question])           # context first, then the question
    result = agent.invoke(                         # run the tool loop until the agent has an answer
        {"messages": [{"role": "user", "content": text}]},   # the new message
        config={"configurable": {"thread_id": session_id}},   # same thread_id = same conversation
    )
    return result["messages"][-1].content          # the last message is the final answer
