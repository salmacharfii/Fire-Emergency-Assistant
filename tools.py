import json                                        # reads the two data files
from datetime import date                          # today's date, for the overdue check
from langchain.tools import tool                   # decorator that turns a function into an agent tool
from langchain_core.runnables import RunnableConfig    # gives a tool access to the session (thread_id)

from config import ZONES_FILE, EQUIPMENT_FILE      # file paths from config.py
from retrieval import retrieve, format_context, filter_relevant   # the search plus the relevance check
from plan import load_plan, nearest, describe      # the building plan the admin drew

POSITIONS = {}                                     # session_id -> {"floor", "x", "y"}; set by the API before every question
FOUND = {}                                         # session_id -> marker ids found by find_nearest; the API sends them to the UI
ROUTES = {}                                        # session_id -> corner points of the walking route to the nearest result

THING_TYPES = {                                    # what the agent may ask for -> marker types on the plan
    "exit": {"exit", "stairs"},
    "extinguisher": {"ext"},
    "alarm": {"alarm"},
    "assembly": {"assembly"},
    "first_aid": {"aid"},
}


def _load(path):                                   # reads one JSON file
    with open(path, encoding="utf-8") as f:        # UTF-8 so umlauts survive
        return json.load(f)                        # returns a dictionary or a list


def _zone_key(zone):                               # "Open Office" becomes "open_office"
    return zone.strip().lower().replace(" ", "_")  # same spelling as the keys in the JSON files


def list_zones():                                  # used by the API to fill the UI drop-down
    return sorted(_load(ZONES_FILE).keys())        # zone names in alphabetical order


@tool                                              # the docstring below is what the agent reads to choose this tool
def search_documents(query: str) -> str:
    """Search the approved fire safety documents (company rules and public standards).
    Use it for procedures, rules, extinguisher types and any 'what should I do' question.
    Returns text chunks, each labelled [file, p.N]."""
    hits = retrieve(query, top_k=8)                # wider net: 8 candidates, already cut by MAX_DISTANCE
    hits = filter_relevant(query, hits)            # keep only chunks that directly answer; the agent can then cite nothing else
    if not hits:                                   # nothing close enough, or nothing that really answers
        return "NO_RESULTS: nothing relevant found in the approved documents."   # the agent must then refuse
    return format_context(hits)                    # labelled chunks


@tool
def get_zone_info(zone: str) -> str:
    """Look up the nearest exit, extinguisher, alarm button and assembly point for one zone of the building.
    Use it when the user says where they are or asks where something is near them.
    The zone name looks like 'kitchen' or 'open_office'."""
    zones = _load(ZONES_FILE)                      # all zones
    info = zones.get(_zone_key(zone))              # this zone, or None if unknown
    if info is None:                               # unknown zone name
        return f"NO_RESULTS: unknown zone '{zone}'. Known zones: {', '.join(sorted(zones))}."   # tell the agent what exists
    return (f"Zone {zone}: nearest exit: {info['nearest_exit']}; extinguisher: {info['extinguisher']}; "
            f"alarm button: {info['alarm_button']}; assembly point: {info['assembly_point']}. [zones.json]")   # label for the guard

def equipment_alerts(days=30):                     # items overdue or due within `days` days, for the warning banner
    today, out = date.today(), []
    def add(ident, kind, where, due_text):         # one record, from equipment.json or from a plan marker
        try:
            left = (date.fromisoformat(due_text) - today).days
        except (TypeError, ValueError):            # no valid date: skipped
            return
        if left <= days:
            out.append({"id": ident, "type": kind, "zone": where, "next_check": due_text,
                        "days_left": left, "status": "overdue" if left < 0 else "soon"})
    try:
        for e in _load(EQUIPMENT_FILE):            # the older list in data/equipment.json
            add(e.get("id", "?"), e.get("type", "equipment"), e.get("zone", ""), e.get("next_check"))
    except (OSError, ValueError, AttributeError):
        pass
    for fl in load_plan().get("floors", []):       # extinguishers placed on the plan, with the date the admin set
        for m in fl.get("markers", []):
            if m.get("t") == "ext" and m.get("d"):
                add(m.get("l") or "Extinguisher", m.get("k", "abc"), fl.get("name", ""), m["d"])
    return sorted(out, key=lambda a: a["days_left"])   # most urgent first


@tool
def check_equipment(zone: str) -> str:
    """List the fire equipment (extinguishers, first aid kits) in one zone,
    with its next inspection date and whether that date has passed."""
    items = [e for e in _load(EQUIPMENT_FILE) if e["zone"] == _zone_key(zone)]   # equipment of this zone
    if not items:                                  # none recorded
        return f"NO_RESULTS: no equipment recorded for zone '{zone}'."
    today = date.today()                           # compared with each due date
    lines = []                                     # one text line per item
    for e in items:
        due = date.fromisoformat(e["next_check"])  # "2027-03-01" becomes a date
        status = "OVERDUE" if due < today else "ok"    # past due date = overdue
        lines.append(f"{e['id']} ({e['type']}): next check {e['next_check']}, {status}")
    overdue = [e["id"] for e in items if date.fromisoformat(e["next_check"]) < today]   # ids with a passed due date
    summary = f"Overdue items: {', '.join(overdue) if overdue else 'none'}."   # explicit answer, also when nothing is overdue
    return "; ".join(lines) + f". {summary} [equipment.json]"   # label for the guard


@tool
def find_nearest(thing: str, config: RunnableConfig) -> str:
    """Find the nearest exits, extinguishers, alarm buttons, assembly points or first aid points
    on the building plan, measured in a straight line from the position the user marked on the plan.
    thing must be one of: exit, extinguisher, alarm, assembly, first_aid.
    Use it when the user asks where the nearest one is, or how to get out."""
    session_id = (config or {}).get("configurable", {}).get("thread_id")   # same id the API used for the memory
    key = thing.strip().lower().replace(" ", "_").replace("-", "_")        # tolerate small spelling differences
    key = {"extinguishers": "extinguisher", "exits": "exit", "alarm_button": "alarm", "assembly_point": "assembly",
           "firstaid": "first_aid", "first_aid_kit": "first_aid"}.get(key, key)
    if key not in THING_TYPES:
        return f"NO_RESULTS: unknown thing '{thing}'. Use one of: {', '.join(THING_TYPES)}."
    pos = POSITIONS.get(session_id)                # where the user stands, set by the API
    if pos is None:
        return "NO_RESULTS: the user has not marked a position on the plan."
    found = nearest(load_plan(), pos["floor"], pos["x"], pos["y"], THING_TYPES[key], n=3)
    if not found:
        return f"NO_RESULTS: nothing of type '{key}' is marked on the user's floor."
    FOUND[session_id] = [r["marker"]["id"] for r in found]    # the UI highlights these on the plan
    if found[0].get("route"):                      # walls are drawn: the UI also draws the way to the nearest result
        ROUTES[session_id] = found[0]["route"]
    lines = "; ".join(describe(r) for r in found)
    if found[0].get("walking"):
        basis = "walking distance around the walls drawn on the plan; fire, smoke and blocked doors are not known"
    elif found[0].get("blocked"):
        basis = "straight line, because no walkable route was found on the drawn plan"
    else:
        basis = "straight line, walls are not known"
    return (f"Nearest {key} from the user's position ({basis}): {lines}. "
            f"Tell the user to follow corridors and escape-route signs. [plan.json]")   # label for the guard


if __name__ == "__main__":                         # runs only with: py tools.py
    print(search_documents.invoke({"query": "Where is the assembly point?"}))   # tools are called with a dictionary of arguments
    print(get_zone_info.invoke({"zone": "kitchen"}))
    print(check_equipment.invoke({"zone": "open_office"}))
