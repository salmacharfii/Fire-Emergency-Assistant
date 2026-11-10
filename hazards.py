import hmac                                        # constant-time comparison for the admin token
import secrets                                     # random ids
import time

from fastapi import APIRouter, Body, Header, HTTPException

from config import ADMIN_TOKEN                     # (this import also loads .env)
from plan import load_plan, get_floor

router = APIRouter()
HAZARDS = {}                                       # id -> a confirmed blocked spot or fire; kept in memory (resets when the server restarts)
PENDING = []                                       # fire reports from users that still wait for a second person
RADIUS_M = {"blocked": 2.0, "fire": 5.0}           # metres around the spot that routes and answers avoid
NEED_REPORTS = 2                                   # different users needed to confirm a fire
SAME_SPOT_M = 8.0                                  # reports closer than this count as the same fire
PENDING_TTL = 15 * 60                              # an unconfirmed fire report is forgotten after 15 minutes
MAX_ACTIVE = 40                                    # most confirmed spots in the whole app
MAX_PER_CLIENT = 5                                 # most blocked reports per user (limits false alarms)


def _is_admin(token):
    return bool(ADMIN_TOKEN) and bool(token) and hmac.compare_digest(token, ADMIN_TOKEN)


def _num01(v):
    try:
        n = float(v)
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Bad position.")
    if not 0 <= n <= 1:
        raise HTTPException(status_code=422, detail="Bad position.")
    return round(n, 4)


def _metres(floor, a, b):                          # distance in metres between two points {x, y} of a floor
    width = floor.get("widthM") or 100.0
    height = width / (floor.get("aspect") or 1.5)
    return ((a["x"] - b["x"]) * width) ** 2 + ((a["y"] - b["y"]) * height) ** 2


def _purge():
    now = time.time()
    PENDING[:] = [p for p in PENDING if now - p["created"] <= PENDING_TTL]


def active_hazards(floor_id):                      # used by the routing: [{"kind", "x", "y", "r"}] on one floor
    return [{"kind": h["kind"], "x": h["x"], "y": h["y"], "r": RADIUS_M[h["kind"]]}
            for h in HAZARDS.values() if h["floor"] == floor_id]


def _public(hid, h):
    return {"id": hid, "kind": h["kind"], "floor": h["floor"], "x": h["x"], "y": h["y"],
            "note": h["note"], "r": RADIUS_M[h["kind"]], "age": int(time.time() - h["created"]), "by": h["by"]}


def _add(kind, floor, x, y, note, by):
    hid = secrets.token_hex(6)
    HAZARDS[hid] = {"kind": kind, "floor": floor, "x": x, "y": y, "note": note, "created": time.time(), "by": by}
    return hid


@router.get("/hazards")                            # GET /hazards: confirmed blocked spots and fires, polled by every open page
def list_hazards():
    _purge()
    return [_public(k, v) for k, v in sorted(HAZARDS.items(), key=lambda kv: kv[1]["created"])]


@router.post("/hazards")                           # POST /hazards: a blocked exit/path (anyone) or a fire (admin, or 2 different users)
def report(body: dict = Body(...), x_admin_token: str | None = Header(default=None)):
    _purge()
    kind = str(body.get("kind", ""))
    if kind not in RADIUS_M:
        raise HTTPException(status_code=422, detail="Unknown kind.")
    plan = load_plan()
    floor_id = str(body.get("floor", ""))
    floor = get_floor(plan, floor_id)
    if floor is None:
        raise HTTPException(status_code=422, detail="Unknown floor.")
    x, y = _num01(body.get("x")), _num01(body.get("y"))
    note = str(body.get("note", "")).strip()[:120]
    client = str(body.get("client", ""))[:40] or "?"          # random id the page keeps in its browser storage
    spot = {"x": x, "y": y}
    admin = _is_admin(x_admin_token)
    if len(HAZARDS) >= MAX_ACTIVE:
        raise HTTPException(status_code=429, detail="Too many active reports.")

    for h in HAZARDS.values():                     # the same spot is already on the plan
        if h["kind"] == kind and h["floor"] == floor_id and _metres(floor, h, spot) < RADIUS_M[kind] ** 2:
            return {"status": "known"}

    if kind == "blocked":
        if not admin and sum(1 for h in HAZARDS.values() if h["by"] == client) >= MAX_PER_CLIENT:
            raise HTTPException(status_code=429, detail="Too many reports from you.")
        _add("blocked", floor_id, x, y, note, "admin" if admin else client)
        return {"status": "added"}

    if admin:                                      # the admin confirms a fire at once
        _add("fire", floor_id, x, y, note, "admin")
        PENDING[:] = [p for p in PENDING if not (p["floor"] == floor_id and _metres(floor, p, spot) < SAME_SPOT_M ** 2)]
        return {"status": "added"}

    PENDING[:] = [p for p in PENDING if p["client"] != client or p["floor"] != floor_id
                  or _metres(floor, p, spot) >= SAME_SPOT_M ** 2]      # one report per user and spot: a repeat only refreshes it
    PENDING.append({"floor": floor_id, "x": x, "y": y, "note": note, "client": client, "created": time.time()})
    near = [p for p in PENDING if p["floor"] == floor_id and _metres(floor, p, spot) < SAME_SPOT_M ** 2]
    if len({p["client"] for p in near}) >= NEED_REPORTS:
        cx, cy = sum(p["x"] for p in near) / len(near), sum(p["y"] for p in near) / len(near)
        notes = [p["note"] for p in near if p["note"]]
        _add("fire", floor_id, round(cx, 4), round(cy, 4), notes[-1] if notes else "", "users")
        PENDING[:] = [p for p in PENDING if p not in near]
        return {"status": "added"}
    return {"status": "pending", "have": len({p["client"] for p in near}), "need": NEED_REPORTS}


@router.delete("/hazards/{hid}")                   # only the admin clears a report
def clear(hid: str, x_admin_token: str | None = Header(default=None)):
    if not _is_admin(x_admin_token):
        raise HTTPException(status_code=401, detail="Not allowed.")
    HAZARDS.pop(hid, None)
    return {"ok": True}
