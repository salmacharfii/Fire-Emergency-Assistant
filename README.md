# EmberAid

A fire-safety assistant for companies. Employees mark where they are on the building plan and ask questions by typing or speaking. EmberAid answers only from the company's approved documents, shows the nearest exit, extinguisher, alarm point or assembly point with a walking route, and lets people report an SOS, a blocked exit or a fire. The interface is available in English and German.

> **EmberAid supplements the official Brandschutzordnung. It never replaces the emergency call: if anyone is in danger, call 112 first.**

## Features

- **Questions from approved documents.** A LangChain agent searches the PDFs (ChromaDB index). If the documents say nothing about a question, it refuses and gives no source instead of guessing. Answers cite their source, for example `[plan.json]` or `[file.pdf, p. 3]`.
- **Fixed emergency steps.** When a question reports a fire, fixed safety steps are shown first. They are decided by code, not by the AI.
- **Building plan.** The admin draws floors, walls and doors and places markers (extinguishers, exits, stairs, assembly points, alarm points, first aid, rooms). Employees tap the plan to set their position. Routes are calculated around walls and through doors.
- **Quick questions and voice.** Buttons for the common questions; voice input through Whisper; optional read-aloud.
- **SOS.** A trapped person sends an SOS from the plan. Everyone using the app sees it, and colleagues can answer "I am on my way". It does not call anyone.
- **Blocked exits and fire sources.** Anyone can report a blocked exit or path, and it appears on the plan at once. A fire appears when the admin reports it, or when two different users report it within about 8 m of each other. Routes and answers avoid blocked spots (2 m radius) and fires (5 m radius). Only the admin can clear a report.
- **QR codes per room.** The admin prints a sheet of QR codes. Scanning one with the phone camera sets the position (`/?room=floor|marker`). No image recognition is involved.
- **Extinguisher training game.** Six scenarios, the right extinguisher type, then the PASS steps in order.
- **Inspection banner.** Overdue and soon-due extinguisher inspections from the equipment data.
- **English / German interface.** Switch in the menu. The interface texts are translated in `static/i18n.js`. With German selected, the assistant is also asked to answer in German.
- **Access code.** An optional code protects the paths that cost money (`/ask` and `/transcribe`).

## Project structure

```
main.py        FastAPI app: /ask, /transcribe, /plan, access check, serves static/
agent.py       the LangChain agent and its instructions
tools.py       tools for the agent (nearest exit, extinguisher, ...)
plan.py        plan loading and saving, walls, doors, routes
guard.py       citation check: no source, no answer
safety.py      detects fire reports and holds the fixed steps
sos.py         /sos endpoints
hazards.py     /hazards endpoints (blocked spots and fires)
config.py      settings and environment variables
ingest.py      reads the PDFs and prepares the text
build_index.py builds the ChromaDB index
data/          plan.json, plan_images/, equipment data
static/        index.html, extinguisher.html, i18n.js, access.js, qrcode.js
```

## Requirements

- Python 3.11 or newer
- An OpenAI API key (answers and Whisper voice input)

## Run it locally (Windows)

```
py -m pip install -r requirements.txt
```

Create a `.env` file next to `main.py`:

```
OPENAI_API_KEY=sk-...
ADMIN_TOKEN=choose-a-long-secret
ACCESS_CODE=optional-code-for-users
```

Put the approved PDFs in the documents folder, then build the index:

```
py ingest.py
py build_index.py
```

Start the app and open http://localhost:8000:

```
py -m uvicorn main:app --reload
```

Whenever you add or change a PDF, run `ingest.py` and `build_index.py` again. If the Chroma folder already exists, delete it first so documents are not added twice.

## Settings (environment variables)

| Variable | Meaning |
|---|---|
| `OPENAI_API_KEY` | Key for the AI and Whisper. Never put it in the code or in git. |
| `ADMIN_TOKEN` | Secret for the plan editor and for clearing reports. Empty means editing is switched off. |
| `ACCESS_CODE` | Code users must enter to ask questions. Empty means the app is open. |

On Render, add these under **Environment**.

## Using the app

**Employees:** tap the plan where you are (or scan a room's QR code), then use the quick buttons or type a question. Use the SOS, Blocked exit/path and Fire here buttons for reports.

**Admin:** open **Menu, then Edit plan**, enter the admin token, then:
1. Create a floor and upload its plan image.
2. Set the plan width in metres.
3. Place markers and name the rooms.
4. Draw walls and add doors so that routes work.
5. Fill in the site name and company notes (assembly point, fire wardens).
6. Print the QR codes from the editor, then clear reports with **Clear (admin)** when they are resolved.

## Deploying (Render)

The app is a normal FastAPI service. Set the three environment variables above. After a change to the PDFs, commit the rebuilt Chroma index too, because only the repository is deployed. After changing `i18n.js`, `access.js` or `index.html`, users may need a hard refresh (Ctrl+Shift+R) until their browser fetches the new file.

## Known limits

- SOS and report data is kept in server memory. It disappears when the server restarts, and each restart starts clean.
- "Two different users" for a fire report is counted by a random id stored in each browser, so it is not a security measure.
- Walls are used only to compute routes and are not shown to employees. Distances are estimates.
- Answers come only from the approved documents. German typed fire reports may not trigger the fixed steps until German keywords are added to `safety.py`.
- The assistant gives general guidance. It does not replace the fire service, medical care or the site's own fire safety rules.

## Sources and licences

- QR codes are drawn with `qrcode-generator` (MIT licence).
- The approved documents are the company's own and carry their own copyright.