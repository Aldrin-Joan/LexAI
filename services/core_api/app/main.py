from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Ensure the 'backend' directory is in the path so 'app' can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from app.api import auth_routes, legal_api, chat_ws
    from app.core.db import init_db
except ImportError:
    # Fallback for if running from within app/ directory
    from api import auth_routes, legal_api, chat_ws
    from core.db import init_db


def download_db_if_missing():
    """Download database file from public GCS URL if it does not exist locally."""
    import urllib.request
    import time
    
    db_path = "data/index.db"
    download_url = os.getenv(
        "DB_DOWNLOAD_URL", 
        "https://storage.googleapis.com/epics-legal-db/index.db"
    )
    
    if os.path.exists(db_path):
        print("Database already exists locally.")
        return
        
    print(f"Database not found. Downloading from {download_url}...")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    start_time = time.time()
    last_logged = start_time
    
    def report_hook(block_num, block_size, total_size):
        nonlocal last_logged
        current_time = time.time()
        if current_time - last_logged >= 5.0:
            downloaded = block_num * block_size
            percent = (downloaded / total_size) * 100 if total_size > 0 else 0
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024) if total_size > 0 else 0
            print(f"Download progress: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)...")
            last_logged = current_time

    urllib.request.urlretrieve(download_url, db_path, reporthook=report_hook)
    print(f"Database download complete. Elapsed time: {time.time() - start_time:.1f} seconds.")


@asynccontextmanager
async def app_lifespan(application: FastAPI):
    """Run database table initialization at app startup."""
    download_db_if_missing()
    init_db()
    yield


app = FastAPI(title="LegalTech Super-App API", lifespan=app_lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(legal_api.router)
app.include_router(chat_ws.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the LegalTech Super-App API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
