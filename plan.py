import heapq                                       # shortest-path search around the walls
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
        walls = []
        for wr in (fr.get("walls") or [])[:2000]:  # wall lines drawn by the admin, as fractions of the plan
            if not isinstance(wr, dict):
                continue
            c = [_num(wr.get(k), 0, 1) for k in ("x1", "y1", "x2", "y2")]
            if None in c or (abs(c[0] - c[2]) < 0.0005 and abs(c[1] - c[3]) < 0.0005):
                continue                           # broken or zero-length walls are dropped
            walls.append({"x1": round(c[0], 4), "y1": round(c[1], 4), "x2": round(c[2], 4), "y2": round(c[3], 4)})
        doors = []
        for dr in (fr.get("doors") or [])[:500]:   # doors: openings in the walls, 'h' = in a horizontal wall, 'v' = in a vertical wall
            if not isinstance(dr, dict):
                continue
            dx_, dy_ = _num(dr.get("x"), 0, 1), _num(dr.get("y"), 0, 1)
            if dx_ is None or dy_ is None:
                continue
            doors.append({"x": round(dx_, 4), "y": round(dy_, 4), "o": "v" if dr.get("o") == "v" else "h",
                          "w": round(_num(dr.get("w"), 0.5, 6, 1.0), 2)})   # width in metres
        floors.append({
            "id": fid, "name": str(fr.get("name", ""))[:40], "image": image,
            "aspect": round(_num(fr.get("aspect"), 0.2, 5, 1.5), 4),
            "widthM": _num(fr.get("widthM"), 1, 2000, None),   # plan width in metres; None = unknown scale
            "markers": markers,
            "walls": walls,
            "doors": doors,
        })
    return {"site": site, "floors": floors}


def get_floor(plan, floor_id):                     # the floor with this id, or None
    return next((f for f in plan.get("floors", []) if f["id"] == floor_id), None)


def direction(dx, dy):                             # words for the direction of a vector on the plan
    angle = math.degrees(math.atan2(dy, dx)) % 360     # y grows downwards on a screen
    return DIRECTIONS[int(round(angle / 45)) % 8] + " on the plan"


def _grid(floor):                                  # turns the walls into a blocked/free grid of about 0.5 m cells
    width = floor.get("widthM")
    aspect = floor.get("aspect") or 1.5
    cols = int(min(200, max(60, round(width / 0.5))))
    rows = max(10, int(round(cols / aspect)))
    blocked = bytearray(cols * rows)
    for w in floor.get("walls") or []:
        length = max(abs(w["x2"] - w["x1"]) * cols, abs(w["y2"] - w["y1"]) * rows)
        steps = max(1, int(length * 3))            # three samples per cell, so the line has no holes
        for i in range(steps + 1):
            t = i / steps
            cx = min(cols - 1, int((w["x1"] + (w["x2"] - w["x1"]) * t) * cols))
            cy = min(rows - 1, int((w["y1"] + (w["y2"] - w["y1"]) * t) * rows))
            blocked[cy * cols + cx] = 1
    cw, ch = width / cols, (width / aspect) / rows  # metres per cell, horizontal and vertical
    for d in floor.get("doors") or []:             # a door opens the wall for its width (and about 1.5 m of depth)
        r0, c0 = int(d["y"] * rows), int(d["x"] * cols)
        half = d["w"] / 2
        if d.get("o") == "v":
            rr = range(max(0, int(round(r0 - half / ch))), min(rows, int(round(r0 + half / ch)) + 1))
            cc = range(max(0, c0 - 1), min(cols, c0 + 2))
        else:
            rr = range(max(0, r0 - 1), min(rows, r0 + 2))
            cc = range(max(0, int(round(c0 - half / cw))), min(cols, int(round(c0 + half / cw)) + 1))
        for r in rr:
            for c in cc:
                blocked[r * cols + c] = 0
    return cols, rows, blocked, cw, ch   # last two: metres per cell, horizontal and vertical


def _cell(cols, rows, x, y):                       # grid cell (row, column) of a point on the plan
    return min(rows - 1, max(0, int(y * rows))), min(cols - 1, max(0, int(x * cols)))


def _free_cell(cols, rows, blocked, r, c, radius=6):   # the nearest walkable cell (a marker may sit on a wall line)
    if not blocked[r * cols + c]:
        return r, c
    for rad in range(1, radius + 1):
        for dr in range(-rad, rad + 1):
            for dc in range(-rad, rad + 1):
                if max(abs(dr), abs(dc)) != rad:
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols and not blocked[rr * cols + cc]:
                    return rr, cc
    return None


def _clear(cols, rows, blocked, a, b):             # True when the straight line between two cells crosses no wall
    (r1, c1), (r2, c2) = a, b
    steps = max(1, int(max(abs(r2 - r1), abs(c2 - c1)) * 4))
    for i in range(steps + 1):
        t = i / steps
        r, c = int(round(r1 + (r2 - r1) * t)), int(round(c1 + (c2 - c1) * t))
        if blocked[r * cols + c]:
            return False
    return True


def _walk_all(cols, rows, blocked, dx, dy, start):    # shortest walking distance (metres) from start to every cell
    inf = float("inf")
    dist = [inf] * (cols * rows)
    parent = [-1] * (cols * rows)
    dist[start[0] * cols + start[1]] = 0.0
    queue = [(0.0, start[0], start[1])]
    diag = math.hypot(dx, dy)
    moves = [(-1, 0, dy), (1, 0, dy), (0, -1, dx), (0, 1, dx), (-1, -1, diag), (-1, 1, diag), (1, -1, diag), (1, 1, diag)]
    while queue:
        d, r, c = heapq.heappop(queue)
        if d > dist[r * cols + c]:
            continue
        for mr, mc, cost in moves:
            rr, cc = r + mr, c + mc
            if not (0 <= rr < rows and 0 <= cc < cols) or blocked[rr * cols + cc]:
                continue
            if mr and mc and (blocked[r * cols + cc] or blocked[rr * cols + c]):
                continue                           # no cutting a wall corner diagonally
            nd = d + cost
            if nd < dist[rr * cols + cc]:
                dist[rr * cols + cc] = nd
                parent[rr * cols + cc] = r * cols + c
                heapq.heappush(queue, (nd, rr, cc))
    return dist, parent


def _route(cols, rows, blocked, parent, goal, x, y, gx, gy):   # corner points of the walking route, as plan fractions
    cells, i = [], goal[0] * cols + goal[1]
    while i != -1:
        cells.append((i // cols, i % cols))
        i = parent[i]
    cells.reverse()                                # start ... goal
    keep, i = [cells[0]], 0
    while i < len(cells) - 1:                      # pull the string tight: jump to the farthest cell that is in sight
        j = len(cells) - 1
        while j > i + 1 and not _clear(cols, rows, blocked, cells[i], cells[j]):
            j -= 1
        keep.append(cells[j])
        i = j
    pts = [[round(x, 4), round(y, 4)]]
    for r, c in keep[1:-1]:
        pts.append([round((c + 0.5) / cols, 4), round((r + 0.5) / rows, 4)])
    pts.append([round(gx, 4), round(gy, 4)])
    return pts


def nearest(plan, floor_id, x, y, types, kind=None, n=3, walk=True):   # markers of the given types, closest first
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
    if walk and found and floor.get("walls") and floor.get("widthM"):   # walls are drawn: measure the way a person walks
        cols, rows, blocked, cw, ch = _grid(floor)
        start = _free_cell(cols, rows, blocked, *_cell(cols, rows, x, y))
        if start is not None:
            dist, parent = _walk_all(cols, rows, blocked, cw, ch, start)
            walked = []
            for r in found:
                m = r["marker"]
                goal = _free_cell(cols, rows, blocked, *_cell(cols, rows, m["x"], m["y"]))
                if goal is None or dist[goal[0] * cols + goal[1]] == float("inf"):
                    continue                       # no way there through the drawn walls and doors
                pts = _route(cols, rows, blocked, parent, goal, x, y, m["x"], m["y"])
                first = ((pts[1][0] - pts[0][0]) * width, (pts[1][1] - pts[0][1]) * height)
                walked.append({"marker": m, "distance": dist[goal[0] * cols + goal[1]], "direction": direction(*first),
                               "scaled": True, "walking": True, "route": pts})
            walked.sort(key=lambda r: r["distance"])
            if walked:
                return walked[:n]
        for r in found:
            r["blocked"] = True                    # walls are drawn but no walkable way was found: say so
    return found[:n]


def nearest_room(plan, floor_id, x, y):            # label of the closest room marker, or ""
    found = nearest(plan, floor_id, x, y, {"room"}, n=1, walk=False)
    return found[0]["marker"]["l"] if found else ""


def describe(r):                                   # one result as a short sentence part
    m = r["marker"]
    name = TYPE_NAMES[m["t"]] + (f' "{m["l"]}"' if m["l"] else "")
    if m["t"] == "ext" and m.get("k"):
        name += f" ({KIND_NAMES[m['k']]})"
    distance = f"about {round(r['distance'])} m" if r["scaled"] else "distance unknown"
    if r.get("walking"):                           # walked around the drawn walls
        return f"{name}: {distance} walking, first head {r['direction']}"
    if r.get("blocked"):                           # walls are drawn, but the search found no way
        return f"{name}: {distance} in a straight line, {r['direction']} (no walkable route found on the plan, a door may be missing)"
    return f"{name}: {distance}, {r['direction']}"
