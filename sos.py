import hmac                                        # constant-time comparison for keys and the admin token
import secrets                                     # random SOS ids and keys
import time

from fastapi import APIRouter, Body, Header, HTTPException, Request

from config import ADMIN_TOKEN                     # (this import also loads .env)
from plan import load_plan, get_floor, nearest_room

router = APIRouter()
SOS = {}                                           # id -> one active SOS; kept in memory (resets when the server restarts)
TTL = 30 * 60                                      # an SOS disappears 30 minutes after the sender's page last reported in
MAX_ACTIVE = 25                                    # at most this many SOS in the whole app
MAX_PER_VISITOR = 2                                # and this many per visitor (limits false alarms)


def _visitor(request):                             # Render puts the real address in X-Forwarded-For
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() or (request.client.host if request.client else "?")


def _purge():                                      # drop SOS whose sender stopped reporting
    now = time.time()
    for k in [k for k, v in SOS.items() if now - v["seen"] > TTL]:
        del SOS[k]


def _public(sid, s, plan):                         # what everybody may see: no key, no address
    return {"id": sid, "floor": s["floor"], "x": s["x"], "y": s["y"],
            "room": nearest_room(plan, s["floor"], s["x"], s["y"]) or "",
            "note": s["note"], "age": int(time.time() - s["created"]), "helpers": len(s["helpers"])}


def _num01(v):
    try:
        n = float(v)
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Bad position.")
    if not 0 <= n <= 1:
        raise HTTPException(status_code=422, detail="Bad position.")
    return round(n, 4)


@router.get("/sos")                                # GET /sos: all active SOS, polled by every open page
def list_sos():
    _purge()
    plan = load_plan()
    return [_public(k, v, plan) for k, v in sorted(SOS.items(), key=lambda kv: kv[1]["created"])]


@router.post("/sos")                               # POST /sos: "I am trapped" at the marked position
def send_sos(request: Request, body: dict = Body(...)):
    _purge()
    plan = load_plan()
    floor = str(body.get("floor", ""))
    if get_floor(plan, floor) is None:
        raise HTTPException(status_code=422, detail="Unknown floor.")
    who = _visitor(request)
    if len(SOS) >= MAX_ACTIVE or sum(1 for v in SOS.values() if v["who"] == who) >= MAX_PER_VISITOR:
        raise HTTPException(status_code=429, detail="Too many active SOS. Call 112.")
    sid, key = secrets.token_hex(6), secrets.token_urlsafe(16)
    now = time.time()
    SOS[sid] = {"key": key, "who": who, "floor": floor, "x": _num01(body.get("x")), "y": _num01(body.get("y")),
                "note": str(body.get("note", "")).strip()[:120], "created": now, "seen": now, "helpers": set()}
    return {"id": sid, "key": key}


@router.post("/sos/{sid}/ping")                    # the sender's page reports in every minute while it is open
def ping_sos(sid: str, x_sos_key: str | None = Header(default=None)):
    s = SOS.get(sid)
    if s is None or not hmac.compare_digest(x_sos_key or "", s["key"]):
        raise HTTPException(status_code=404, detail="SOS not found.")
    s["seen"] = time.time()
    return {"ok": True, "helpers": len(s["helpers"])}


@router.post("/sos/{sid}/help")                    # "I am on my way": the sender sees how many are coming
def help_sos(sid: str, body: dict = Body(...)):
    s = SOS.get(sid)
    if s is None:
        raise HTTPException(status_code=404, detail="SOS not found.")
    helper = str(body.get("helper", ""))[:40]
    if helper and len(s["helpers"]) < 50:
        s["helpers"].add(helper)
    return {"helpers": len(s["helpers"])}


@router.delete("/sos/{sid}")                       # the sender cancels, or the admin removes it
def cancel_sos(sid: str, x_sos_key: str | None = Header(default=None), x_admin_token: str | None = Header(default=None)):
    s = SOS.get(sid)
    if s is None:
        return {"ok": True}
    is_sender = bool(x_sos_key) and hmac.compare_digest(x_sos_key, s["key"])
    is_admin = bool(ADMIN_TOKEN) and bool(x_admin_token) and hmac.compare_digest(x_admin_token, ADMIN_TOKEN)
    if not (is_sender or is_admin):
        raise HTTPException(status_code=401, detail="Not allowed.")
    del SOS[sid]
    return {"ok": True}
