import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

# Optional: Redis clients
try:
    from upstash_redis import Redis as UpstashRedis
except ImportError:
    UpstashRedis = None

try:
    import redis as PyRedis
except ImportError:
    PyRedis = None

class SessionManager:
    """Manages chat sessions stored as JSON files, Upstash, or Redis Cloud."""

    def __init__(self, sessions_dir: str = "sessions"):
        """Initialize session storage."""
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Check for Standard Redis (TCP) - Higher Priority
        self.redis_host = os.getenv("REDIS_HOST")
        self.redis_port = os.getenv("REDIS_PORT", "6379")
        self.redis_user = os.getenv("REDIS_USER", "default")
        self.redis_pass = os.getenv("REDIS_PASSWORD")
        
        self.use_standard_redis = PyRedis is not None and self.redis_host and self.redis_pass
        
        # 2. Check for Upstash Redis (HTTP) - Fallback
        self.upstash_url = os.getenv("UPSTASH_REDIS_REST_URL")
        self.upstash_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.use_upstash = UpstashRedis is not None and self.upstash_url and self.upstash_token
        
        if self.use_standard_redis:
            self.client = PyRedis.Redis(
                host=self.redis_host,
                port=int(self.redis_port),
                username=self.redis_user,
                password=self.redis_pass,
                decode_responses=True
            )
            self.mode = "standard_redis"
        elif self.use_upstash:
            self.client = UpstashRedis(url=self.upstash_url, token=self.upstash_token)
            self.mode = "upstash"
        else:
            self.client = None
            self.mode = "filesystem"
        
        self.current_session_id = str(uuid.uuid4())[:8]
        self.history: List[Dict[str, Any]] = []

    def start_new_session(self) -> str:
        """Create a new session ID and clear current history."""
        self.current_session_id = str(uuid.uuid4())[:8]
        self.history = []
        return self.current_session_id

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the current session history."""
        message = {
            "role": role,
            "content": str(content),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.history.append(message)
        self._save_session()

    def _save_session(self):
        """Save current history to storage (Redis or JSON)."""
        data = {
            "session_id": self.current_session_id,
            "last_updated": datetime.now().isoformat(),
            "messages": self.history
        }
        
        if self.mode != "filesystem":
            key = f"legal_rag:session:{self.current_session_id}"
            self.client.set(key, json.dumps(data))
        else:
            file_path = self.sessions_dir / f"session_{self.current_session_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_session(self, session_id: str) -> bool:
        """Load a session from storage."""
        if self.mode != "filesystem":
            key = f"legal_rag:session:{session_id}"
            data_str = self.client.get(key)
            if not data_str:
                return False
            data = json.loads(data_str)
        else:
            file_path = self.sessions_dir / f"session_{session_id}.json"
            if not file_path.exists():
                return False
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
        self.current_session_id = data["session_id"]
        self.history = data["messages"]
        return True

    def list_sessions(self) -> List[Dict[str, str]]:
        """List all available sessions."""
        sessions = []
        
        if self.mode != "filesystem":
            keys = self.client.keys("legal_rag:session:*")
            for key in keys:
                # Standard redis returns bytes or strings depending on config 
                # (we set decode_responses=True for std redis)
                data_str = self.client.get(key)
                if data_str:
                    data = json.loads(data_str)
                    sessions.append({
                        "id": data["session_id"],
                        "last_updated": data["last_updated"],
                        "message_count": len(data["messages"])
                    })
        else:
            for file in self.sessions_dir.glob("session_*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append({
                            "id": data["session_id"],
                            "last_updated": data["last_updated"],
                            "message_count": len(data["messages"])
                        })
                except Exception:
                    continue
                    
        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)
