from pathlib import Path          # path handling that works the same on Windows and Linux
from dotenv import load_dotenv    # reads the .env file
import os

load_dotenv()                     # puts the OpenAI and LangSmith keys into the environment, where both libraries look for them

BASE_DIR = Path(__file__).parent                        # the folder that contains this file = the project root
PDF_DIR = BASE_DIR / "data" / "pdfs"                    # where the PDFs live (sub-folders: company, standards)
ZONES_FILE = BASE_DIR / "data" / "zones.json"           # zone data read by get_zone_info
EQUIPMENT_FILE = BASE_DIR / "data" / "equipment.json"   # equipment data read by check_equipment

PLAN_FILE = BASE_DIR / "data" / "plan.json" 
PLAN_IMAGE_DIR = BASE_DIR / "data" / "plan_images" 
STATIC_DIR = BASE_DIR / "static" 
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

CHROMA_DIR = BASE_DIR / "chroma_db"                     # where Chroma saves the index on disk
COLLECTION_NAME = "fire_safety"         # name of the Chroma collection that holds all chunks
EMBED_MODEL = "text-embedding-3-small"  # OpenAI model that turns text into vectors
LLM_MODEL = "gpt-4o-mini"               # OpenAI chat model used by the agent
WHISPER_MODEL = "whisper-1"             # OpenAI model that turns speech into text
CHUNK_SIZE = 1200                        # maximum characters per chunk
CHUNK_OVERLAP = 100                     # characters repeated between neighbouring chunks
TOP_K = 5                               # chunks retrieved per search
MAX_DISTANCE = 0.60                     # largest distance still accepted as a match
BATCH_SIZE = 100                        # chunks sent to the embedding API per request