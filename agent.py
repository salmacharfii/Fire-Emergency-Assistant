from langchain.agents import create_agent          # builds an agent that can call tools in a loop
from langchain_openai import ChatOpenAI            # the OpenAI chat model as a LangChain object
from langgraph.checkpoint.memory import InMemorySaver   # keeps each conversation in the server's memory

from config import LLM_MODEL                       # "gpt-4o-mini" (this import also loads .env, including the LangSmith keys)
from tools import search_documents, get_zone_info, check_equipment   # Day 3 tools

SYSTEM_PROMPT = (                                  # the rules the agent follows on every question
    "You are a fire safety assistant for employees of one company. "
    "Use the tools to find facts: search_documents for rules and procedures, "
    "get_zone_info for exits, extinguishers and assembly points of a zone, "
    "check_equipment for inspection dates. "
    "If the message starts with [User is in zone: X], use that zone for questions about the user's surroundings. "
    "Answer ONLY from tool results. "                            # no outside knowledge
    "After each statement write its source exactly as it appears in the tool result, "
    "like [file.pdf, p.3] or [zones.json]. "                     # makes the guard check possible
    "If the tools return nothing relevant, reply with exactly: NO_ANSWER. "   # a fixed word the code can detect
    "Always answer in English, even if a document is in German. "
    "Be short. Use numbered steps for instructions."
)

model = ChatOpenAI(model=LLM_MODEL, temperature=0)  # temperature 0 = least random wording

agent = create_agent(                              # one agent object, created once when the server starts
    model=model,                                   # which model decides and answers
    tools=[search_documents, get_zone_info, check_equipment],   # what it may call
    system_prompt=SYSTEM_PROMPT,                   # the rules above
    checkpointer=InMemorySaver(),                  # memory: stores the messages of each thread_id
)


def run_agent(question, session_id, zone=None):    # one user turn in, answer text out
    text = question if not zone else f"[User is in zone: {zone}]\n{question}"   # tell the agent where the user is
    result = agent.invoke(                         # run the tool loop until the agent has an answer
        {"messages": [{"role": "user", "content": text}]},   # the new message
        config={"configurable": {"thread_id": session_id}},   # same thread_id = same conversation
    )
    return result["messages"][-1].content          # the last message is the final answer