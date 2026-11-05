import json                                        # reads and writes the plan file
import math                                        # distances and angles
import os                                          # atomic file replace
import re                                          # name checks
import tempfile                                    # temp file for a safe save

from config import PLAN_FILE                       # data/plan.json (this also loads .env)

MARKER_TYPES = {"ext", "exit", "stairs", "assembly", "alarm", "aid", "room"}   # what an admin can place on the plan
EXT_KINDS = {"abc", "co2", "foam", "f", "water"}   # extinguisher kinds
TYPE_NAMES = {                                     # words the agent sees in tool results
    "ext": "extinguisher", "exit": "emergency exit", "stairs": "stairs", "assembly": "assembly point",
    "alarm": "manual alarm call point", "aid": "first aid", "room": "room",
}
KIND_NAMES = {"abc": "ABC powder", "co2": "CO2", "foam": "foam", "f": "grease fire (F)", "water": "water"}
IMAGE_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}\.(png|jpg|jpeg|webp|svg)$")   # allowed plan image file names
ID_PATTERN = re.compile(r"[^A-Za-z0-9_-]")         # characters removed from ids
DIRECTIONS = ["right", "down-right", "down", "down-left", "left", "up-left", "up", "up-right"]   # 45 degree steps, 0 = right, clockwise on screen


def empty_plan():                                  # a plan with nothing in it
    return {"site": {"name": "", "note": ""}, "floors": []}


def load_plan():                                   # reads data/plan.json, or an empty plan if it does not exist yet
    try:
        with open(PLAN_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return empty_plan()


def save_plan(plan):                               # writes the file in one step, so a crash never leaves half a file
    PLAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(PLAN_FILE.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PLAN_FILE)


def _num(value, low, high, default=None):          # number inside [low, high], or the default
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if x != x:                                     # NaN
        return default
    return min(high, max(low, x))


def clean_plan(raw):                               # checks an uploaded plan and returns a safe copy; raises ValueError if it is unusable
    if not isinstance(raw, dict):
        raise ValueError("The plan must be a JSON object.")
    site_raw = raw.get("site") if isinstance(raw.get("site"), dict) else {}
    site = {"name": str(site_raw.get("name", ""))[:80], "note": str(site_raw.get("note", ""))[:500]}
    floors_raw = raw.get("floors")
    if not isinstance(floors_raw, list) or len(floors_raw) > 30:
        raise ValueError("floors must be a list of at most 30 floors.")
    floors, seen = [], set()
    for fr in floors_raw:
        if not isinstance(fr, dict):
            raise ValueError("Every floor must be an object.")
        fid = ID_PATTERN.sub("", str(fr.get("id", "")))[:40]
        if not fid or fid in seen:
            raise ValueError("Every floor needs a unique id.")
        seen.add(fid)
        image = fr.get("image") or None
        if image is not None and not IMAGE_NAME.match(str(image)):
            raise ValueError("Bad image file name.")
        markers = []
        for mr in (fr.get("markers") or [])[:500]:
            if not isinstance(mr, dict) or mr.get("t") not in MARKER_TYPES:
                continue                           # unknown marker types are dropped
            x, y = _num(mr.get("x"), 0, 1), _num(mr.get("y"), 0, 1)
            if x is None or y is None:
                continue
            m = {"id": ID_PATTERN.sub("", str(mr.get("id", "")))[:40] or f"m{len(markers)}",
                 "t": mr["t"], "x": round(x, 4), "y": round(y, 4), "l": str(mr.get("l", ""))[:60]}
            if m["t"] == "ext":
                m["k"] = mr.get("k") if mr.get("k") in EXT_KINDS else "abc"
            markers.append(m)
        floors.append({
            "id": fid, "name": str(fr.get("name", ""))[:40], "image": image,
            "aspect": round(_num(fr.get("aspect"), 0.2, 5, 1.5), 4),
            "widthM": _num(fr.get("widthM"), 1, 2000, None),   # plan width in metres; None = unknown scale
            "markers": markers,
        })
    return {"site": site, "floors": floors}


def get_floor(plan, floor_id):                     # the floor with this id, or None
    return next((f for f in plan.get("floors", []) if f["id"] == floor_id), None)


def direction(dx, dy):                             # words for the direction of a vector on the plan
    angle = math.degrees(math.atan2(dy, dx)) % 360     # y grows downwards on a screen
    return DIRECTIONS[int(round(angle / 45)) % 8] + " on the plan"


def nearest(plan, floor_id, x, y, types, kind=None, n=3):   # markers of the given types, closest first (straight line)
    floor = get_floor(plan, floor_id)
    if floor is None:
        return []
    width = floor.get("widthM") or 100.0           # without a scale only the order is meaningful
    height = width / (floor.get("aspect") or 1.5)  # plan height in the same unit
    found = []
    for m in floor["markers"]:
        if m["t"] not in types or (kind and m.get("k") != kind):
            continue
        dx, dy = (m["x"] - x) * width, (m["y"] - y) * height
        found.append({"marker": m, "distance": math.hypot(dx, dy),
                      "direction": direction(dx, dy), "scaled": bool(floor.get("widthM"))})
    found.sort(key=lambda r: r["distance"])
    return found[:n]


def nearest_room(plan, floor_id, x, y):            # label of the closest room marker, or ""
    found = nearest(plan, floor_id, x, y, {"room"}, n=1)
    return found[0]["marker"]["l"] if found else ""


def describe(r):                                   # one result as a short sentence part
    m = r["marker"]
    name = TYPE_NAMES[m["t"]] + (f' "{m["l"]}"' if m["l"] else "")
    if m["t"] == "ext" and m.get("k"):
        name += f" ({KIND_NAMES[m['k']]})"
    distance = f"about {round(r['distance'])} m" if r["scaled"] else "distance unknown"
    return f"{name}: {distance}, {r['direction']}"
