from fastapi import FastAPI, File, UploadFile      # the web framework and file upload types
from openai import OpenAI                          # for the Whisper call
from pydantic import BaseModel                     # defines the shape of requests and responses

from config import WHISPER_MODEL                   # "whisper-1" (this import also loads .env)
from safety import is_fire_emergency, FIXED_STEPS  # fixed steps
from agent import run_agent                        # the LangChain agent
from guard import check_answer, extract_sources    # citation check
from tools import list_zones                       # zone names for the UI

app = FastAPI(title="Fire Emergency Assistant")    # the application object that uvicorn runs
openai_client = OpenAI()                           # reads OPENAI_API_KEY from the environment; the key stays on the server


class AskRequest(BaseModel):                       # what the caller sends
    question: str                                  # the user's question
    session_id: str                                # one id per browser session, becomes the thread_id
    zone: str | None = None                        # the zone the user picked, if any


class Source(BaseModel):                           # one cited source
    source_doc: str                                # file name
    page: int | None = None                        # page number, empty for the JSON data files


class AskResponse(BaseModel):                      # what the caller receives
    answer: str                                    # answer text or the refusal
    sources: list[Source]                          # cited sources, empty when refused
    mode: str                                      # "answer" or "refused"
    safety_steps: list[str]                        # fixed steps, empty unless fire wording was found


@app.get("/zones")                                 # GET /zones for the UI drop-down
def zones():
    return list_zones()                            # e.g. ["kitchen", "open_office"]


@app.post("/transcribe")                           # POST /transcribe: speech to text
def transcribe(audio: UploadFile = File(...)):     # the recorded audio arrives as a file upload
    data = audio.file.read()                       # the raw bytes
    result = openai_client.audio.transcriptions.create(    # Whisper turns speech into text
        model=WHISPER_MODEL,                       # "whisper-1"
        file=(audio.filename or "question.wav", data),     # (file name, bytes); the name tells the API the format
    )
    return {"text": result.text}                   # the UI puts this text into the normal question flow


@app.post("/ask", response_model=AskResponse)     # POST /ask: the main endpoint
def ask(req: AskRequest):
    steps = FIXED_STEPS if is_fire_emergency(req.question) else []   # decided before any AI call
    raw = run_agent(req.question, req.session_id, req.zone)          # the agent picks tools and answers
    answer, mode = check_answer(raw)               # guard: citation present or refuse
    sources = [Source(**s) for s in extract_sources(answer)] if mode == "answer" else []   # sources only for real answers
    return AskResponse(answer=answer, sources=sources, mode=mode, safety_steps=steps)