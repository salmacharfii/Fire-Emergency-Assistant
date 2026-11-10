import hmac                                        # constant-time comparison for the admin token
import re                                          # to scan uploaded SVG files
import uuid                                        # random names for uploaded plan images

from fastapi import Body, FastAPI, File, Header, HTTPException, UploadFile   # the web framework and its helpers
from fastapi.staticfiles import StaticFiles        # serves the web page and the plan images
from openai import OpenAI                          # for the Whisper call
from pydantic import BaseModel                     # defines the shape of requests and responses

from config import WHISPER_MODEL, ADMIN_TOKEN, ACCESS_CODE, PLAN_IMAGE_DIR, STATIC_DIR   # (this import also loads .env)
from safety import is_fire_emergency, FIXED_STEPS  # fixed steps
from agent import run_agent                        # the LangChain agent
from guard import check_answer, extract_sources    # citation check
from tools import equipment_alerts, list_zones, _zone_key, POSITIONS, FOUND, ROUTES, find_nearest   # zone names for the UI, session state for the plan tool
from plan import load_plan, save_plan, clean_plan, nearest_room   # the building plan

app = FastAPI(title="Fire Emergency Assistant")    # the application object that uvicorn runs
openai_client = OpenAI()                           # reads OPENAI_API_KEY from the environment; the key stays on the server

MAX_AUDIO_BYTES = 25 * 1024 * 1024                 # the Whisper API accepts files up to 25 MB
MAX_IMAGE_BYTES = 10 * 1024 * 1024                 # plan images up to 10 MB


WHERE_WORDS = re.compile(r"\b(where|nearest|closest|near|find|locate|how (do|can|should) i (get|leave|escape|exit|go)|wo ist|wo finde|nächste[rnms]?|naechste[rnms]?|am nächsten|wie komme ich)\b", re.IGNORECASE)   # the user asks for a place
THING_WORDS = [                                    # what is asked for -> the thing name find_nearest understands; first match wins
    ("extinguisher", re.compile(r"extinguish|feuerlösch|feuerlosch|löscher", re.IGNORECASE)),
    ("alarm", re.compile(r"alarm|call point|fire button|melder", re.IGNORECASE)),
    ("assembly", re.compile(r"assembly|muster|meeting point|sammelplatz|sammelstelle", re.IGNORECASE)),
    ("first_aid", re.compile(r"first.?aid|medical|defibrillator|\baed\b|erste.?hilfe|defibrillator", re.IGNORECASE)),
    ("exit", re.compile(r"\bexits?\b|escape|get out|way out|leave|evacuat|stairs|staircase|ausgang|notausgang|ausgänge|fluchtweg|treppe|verlassen", re.IGNORECASE)),
]


def wanted_thing(question, fire):                  # which plan lookup this question needs, or None; decided by code, not by the AI
    if WHERE_WORDS.search(question):
        for name, pattern in THING_WORDS:
            if pattern.search(question):
                return name
    if fire:                                       # a fire report: always show the way out
        return "exit"
    return None


class Position(BaseModel):                         # where the user tapped on the plan
    floor: str                                     # floor id from plan.json
    x: float                                       # 0 = left edge, 1 = right edge
    y: float                                       # 0 = top edge, 1 = bottom edge


class AskRequest(BaseModel):                       # what the caller sends
    question: str                                  # the user's question
    session_id: str                                # one id per browser session, becomes the thread_id
    zone: str | None = None                        # the zone the user picked, if any
    position: Position | None = None               # the point the user marked on the plan, if any
    lang: str = "en"                               # interface language of the page: "en" or "de"


class Source(BaseModel):                           # one cited source
    source_doc: str                                # file name
    page: int | None = None                        # page number, empty for the JSON data files


class AskResponse(BaseModel):                      # what the caller receives
    answer: str                                    # answer text or the refusal
    sources: list[Source]                          # cited sources, empty when refused
    mode: str                                      # "answer" or "refused"
    safety_steps: list[str]                        # fixed steps, empty unless fire wording was found
    highlights: list[str] = []                     # marker ids the UI should highlight on the plan
    route: list[list[float]] = []                  # corner points [x, y] of the walking route to the nearest result


def require_admin(token):                          # stops everybody without the admin token
    if not ADMIN_TOKEN:                            # nothing configured: editing stays off
        raise HTTPException(status_code=403, detail="Plan editing is switched off. Set ADMIN_TOKEN in .env.")
    if not hmac.compare_digest(token or "", ADMIN_TOKEN):   # constant-time compare
        raise HTTPException(status_code=401, detail="Wrong admin token.")


def code_matches(code):                            # constant-time check of the access code
    return hmac.compare_digest((code or "").encode(), ACCESS_CODE.encode())


def require_access(code):                          # stops AI calls without the access code; no code configured = open app
    if ACCESS_CODE and not code_matches(code):
        raise HTTPException(status_code=401, detail="Access code required.")


@app.get("/access/check")                          # GET /access/check: does the page need a code, and is the one it holds right?
def access_check(x_access_code: str | None = Header(default=None)):
    if not ACCESS_CODE:
        return {"required": False, "ok": True}
    return {"required": True, "ok": code_matches(x_access_code)}


@app.get("/equipment/alerts")                      # GET /equipment/alerts: overdue and soon-due inspections for the banner
def get_equipment_alerts():
    try:
        return equipment_alerts(30)
    except (OSError, ValueError):                  # no equipment file: no alerts
        return []


@app.get("/zones")                                 # GET /zones for the UI drop-down
def zones():
    return list_zones()                            # e.g. ["kitchen", "open_office"]


@app.get("/plan")                                  # GET /plan: everybody may read the building plan
def get_plan():
    return load_plan()


@app.get("/plan/admin-check")                      # lets the editor test a token before it shows the tools
def admin_check(x_admin_token: str | None = Header(default=None)):
    require_admin(x_admin_token)
    return {"ok": True}


@app.put("/plan")                                  # PUT /plan: replace the whole plan (admin only)
def put_plan(body: dict = Body(...), x_admin_token: str | None = Header(default=None)):
    require_admin(x_admin_token)
    try:
        plan = clean_plan(body)                    # drops unknown marker types, clamps coordinates
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    used_before = {f.get("image") for f in load_plan().get("floors", [])}   # images the old plan used
    save_plan(plan)
    used_now = {f.get("image") for f in plan["floors"]}
    for name in used_before - used_now:            # a floor or the whole plan was deleted: remove its image file too
        if name:
            try:
                (PLAN_IMAGE_DIR / name).unlink()
            except OSError:
                pass
    return plan


def image_extension(data):                         # decides the file type from the bytes, not from the name the browser sent
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    head = data[:2000].lstrip().lower()
    if head.startswith((b"<?xml", b"<svg")) and b"<svg" in data[:2000].lower():
        return "svg"
    return None


@app.post("/plan/image")                           # POST /plan/image: upload a floor plan image (admin only)
def upload_plan_image(image: UploadFile = File(...), x_admin_token: str | None = Header(default=None)):
    require_admin(x_admin_token)
    data = image.file.read(MAX_IMAGE_BYTES + 1)    # read one byte more than allowed to detect oversize files
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="The image is larger than 10 MB.")
    ext = image_extension(data)
    if ext is None:
        raise HTTPException(status_code=422, detail="Use a PNG, JPG, WebP or SVG image.")
    if ext == "svg" and re.search(rb"<script|\son\w+\s*=|javascript:", data, re.IGNORECASE):
        raise HTTPException(status_code=422, detail="This SVG contains scripts and was rejected.")
    name = f"{uuid.uuid4().hex}.{ext}"             # random name, never the user's file name
    PLAN_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    (PLAN_IMAGE_DIR / name).write_bytes(data)
    return {"image": name}


@app.post("/transcribe")                           # POST /transcribe: speech to text
def transcribe(audio: UploadFile = File(...), x_access_code: str | None = Header(default=None)):     # the recorded audio arrives as a file upload
    require_access(x_access_code)                  # no code, no Whisper call
    data = audio.file.read()                       # the raw bytes
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="The recording is longer than the 25 MB limit.")
    result = openai_client.audio.transcriptions.create(    # Whisper turns speech into text
        model=WHISPER_MODEL,                       # "whisper-1"
        file=(audio.filename or "question.wav", data),     # (file name, bytes); the name tells the API the format
    )
    return {"text": result.text}                   # the UI puts this text into the normal question flow


@app.post("/ask", response_model=AskResponse)     # POST /ask: the main endpoint
def ask(req: AskRequest, x_access_code: str | None = Header(default=None)):
    require_access(x_access_code)                  # no code, no OpenAI call
    plan = load_plan()                             # the building plan, read fresh so admin edits count at once
    zone, room = req.zone, ""
    if req.position is not None:                   # the user marked a point on the plan
        pos = req.position
        x, y = min(1.0, max(0.0, pos.x)), min(1.0, max(0.0, pos.y))
        POSITIONS[req.session_id] = {"floor": pos.floor, "x": x, "y": y}   # find_nearest reads this
        room = nearest_room(plan, pos.floor, x, y)     # the closest room label, e.g. "Open office"
        if zone is None and room and _zone_key(room) in list_zones():   # reuse the zone tools when the names match
            zone = _zone_key(room)
    else:
        POSITIONS.pop(req.session_id, None)        # no position: forget an old one
    FOUND.pop(req.session_id, None)                # clear highlights from the previous question
    ROUTES.pop(req.session_id, None)               # and the route
    steps = FIXED_STEPS if is_fire_emergency(req.question) else []   # decided before any AI call
    lookup = None
    thing = wanted_thing(req.question, bool(steps)) if req.position is not None else None
    if thing:                                      # run the plan lookup in code, so the route is always found and drawn
        lookup = find_nearest.invoke({"thing": thing}, config={"configurable": {"thread_id": req.session_id}})
    raw = run_agent(req.question, req.session_id, zone, room, req.position is not None, lookup, "de" if req.lang == "de" else "en")   # the agent picks tools and answers
    answer, mode = check_answer(raw)               # guard: citation present or refuse
    sources = [Source(**s) for s in extract_sources(answer)] if mode == "answer" else []   # sources only for real answers
    highlights = FOUND.pop(req.session_id, []) if mode == "answer" else []   # only for answers that passed the guard
    route = ROUTES.pop(req.session_id, []) if mode == "answer" else []
    return AskResponse(answer=answer, sources=sources, mode=mode, safety_steps=steps, highlights=highlights, route=route)


try:
    PLAN_IMAGE_DIR.mkdir(parents=True, exist_ok=True)   # the folder must exist before it can be served
except OSError:
    pass                                           # read-only disk (e.g. Vercel): the folder comes from git
if PLAN_IMAGE_DIR.exists():
    app.mount("/plan-images", StaticFiles(directory=str(PLAN_IMAGE_DIR)), name="plan-images")   # uploaded plan images
if STATIC_DIR.exists():                            # only when the static folder is there
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")   # the web page; must stay the LAST line