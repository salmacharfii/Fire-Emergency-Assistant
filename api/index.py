import sys, pathlib, traceback
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
try:
    from main import app
except Exception:
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    err = traceback.format_exc()
    app = FastAPI()
    @app.get("/{p:path}")
    def show(p: str):
        return PlainTextResponse(err)