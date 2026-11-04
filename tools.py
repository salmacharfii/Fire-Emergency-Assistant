import json                                        # reads the two data files
from datetime import date                          # today's date, for the overdue check
from langchain.tools import tool                   # decorator that turns a function into an agent tool

from config import ZONES_FILE, EQUIPMENT_FILE      # file paths from config.py
from retrieval import retrieve, format_context, filter_relevant   # the search plus the relevance check     # the search from this day


def _load(path):                                   # reads one JSON file
    with open(path, encoding="utf-8") as f:        # UTF-8 so umlauts survive
        return json.load(f)                        # returns a dictionary or a list


def _zone_key(zone):                               # "Open Office" becomes "open_office"
    return zone.strip().lower().replace(" ", "_")  # same spelling as the keys in the JSON files


def list_zones():                                  # used by the API on Day 4 to fill the UI drop-down
    return sorted(_load(ZONES_FILE).keys())        # zone names in alphabetical order


@tool                                              # the docstring below is what the agent reads to choose this tool
def search_documents(query: str) -> str:
    """Search the approved fire safety documents (company rules and public standards).
    Use it for procedures, rules, extinguisher types and any 'what should I do' question.
    Returns text chunks, each labelled [file, p.N]."""
    hits = retrieve(query, top_k=8)                # wider net: 8 candidates, already cut by MAX_DISTANCE
    hits = filter_relevant(query, hits)            # keep only chunks that directly answer; the agent can then cite nothing else
    if not hits:                                   # nothing close enough, or nothing that really answers                         # nothing close enough
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


if __name__ == "__main__":                         # runs only with: py tools.py
    print(search_documents.invoke({"query": "Where is the assembly point?"}))   # tools are called with a dictionary of arguments
    print(get_zone_info.invoke({"zone": "kitchen"}))
    print(check_equipment.invoke({"zone": "open_office"}))