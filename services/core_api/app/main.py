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
except ImportError:
    # Fallback for if running from within app/ directory
    from api import auth_routes, legal_api, chat_ws

app = FastAPI(title="LegalTech Super-App API")

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
