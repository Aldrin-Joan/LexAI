# Technical Specification: Backend Enhancements & Storage Strategy 🛠️

This document outlines the state of the backend service (`services/core_api`), identifies necessary database schemas, and outlines the self-contained deployment storage plan (explaining why third-party solutions like **Firebase** are not required).

---

## 💾 Storage & Hosting Strategy: Self-Contained vs. Firebase

Instead of introducing external services like Firebase, the monorepo will utilize a **100% self-contained Python-native architecture**:

* **Authentication (Local JWT)**: JWT sign-in tokens are generated, verified, and signed locally using the `python-jose` library. Hashing is performed using `passlib[bcrypt]`.
* **Database (Local SQLite / PostgreSQL)**:
  * **Development/Local**: SQLite database `data/app_data.db` managed via **SQLModel** (which sits on top of SQLAlchemy).
  * **Production**: Can toggle to PostgreSQL by changing `DATABASE_URL` in `.env` without modifying code (thanks to SQLModel).
* **Document Storage (Local Disk / StaticFiles)**:
  * Verification documents (Bar cards, PDFs) and generated voice `.mp3` files are saved directly under the `data/uploads/` and `data/audio/` directories.
  * Served safely via FastAPI's `StaticFiles` middleware with authenticated path routing.

---

## 🛠️ Required Backend Modifications

### 1. Database Schema Extension (`app/models/models.py`)
The current `User` SQLModel needs to be extended to capture lawyer verification states and professional details:

```python
class UserRole(str, Enum):
    CLIENT = "client"
    LAWYER = "lawyer"

class VerificationStatus(str, Enum):
    NONE = "none"                       # Client default
    PENDING_DOCS = "pending_documents"  # Lawyer registered but needs proof upload
    PENDING_REVIEW = "pending_review"   # Documents uploaded, awaiting admin review
    VERIFIED = "verified"               # Fully verified
    REJECTED = "rejected"               # Verification failed

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Extended Lawyer Onboarding Fields
    bar_registration_number: Optional[str] = Field(default=None, unique=True, index=True)
    practice_domains: Optional[str] = Field(default=None)  # JSON comma-separated string
    years_of_experience: Optional[int] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    verification_status: VerificationStatus = Field(default=VerificationStatus.NONE)
    
    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
```

---

## 📋 Backend Task List

### Task B1: Initialize Database Engine (`app/core/db.py`)
* [ ] Create `db.py` to establish the SQLModel database engine and session generator:
  ```python
  from sqlmodel import create_engine, Session, SQLModel
  from app.core.config import settings

  engine = create_engine(settings.DATABASE_URL, echo=True)

  def get_db():
      with Session(engine) as session:
          yield session
  ```
* [ ] Integrate database creation on FastAPI application startup (`app/main.py` lifespan event):
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      SQLModel.metadata.create_all(engine)
      yield
  ```

### Task B2: Replace Authentication Mock Route Handlers
* [ ] **`/auth/signup`**: Update to check email uniqueness in the active database, hash the password, write the user instance, and return `UserRead`.
* [ ] **`/auth/login`**: Update to fetch user by email, verify password via bcrypt, generate a JWT token containing `role` and `id` claims, and return it.

### Task B3: Document Uploads & Static Directories Setup
* [ ] Set up directory initializers for file uploads inside the main setup script:
  ```python
  import os
  os.makedirs("data/uploads/bar_cards", exist_ok=True)
  os.makedirs("data/audio", exist_ok=True)
  ```
* [ ] Mount static directory to FastAPI routes in `main.py`:
  ```python
  from fastapi.staticfiles import StaticFiles
  app.mount("/static", StaticFiles(directory="data"), name="static")
  ```

### Task B4: Persistent Database Logging
* [ ] Integrate active session database sessions into WebSocket handlers. On receiving a message frame, write it directly to the SQLite `Message` table so that historical messages can be loaded by offline clients upon reconnecting.

---

## 🚀 Future Roadmap (Post-MVP Extensions)

### [FUTURE] Task B5: Refactor WebSocket to Support Client-Lawyer Routing
* **Issue**: The current WebSocket endpoint in [chat_ws.py](file:///c:/Users/ayush/Documents/epap/Epics_App/services/core_api/app/api/chat_ws.py#L28) is an AI-only chatbot loop. Direct advocate consulting is planned for future implementation stages.
* **Target Refactoring**:
  1. Parse the client's JWT token to verify identity (`sender_id`).
  2. Implement **Dynamic Routing** by routing client messages to the target lawyer's connection channel (`manager.active_connections`) or storing them in the SQLite `Message` table if offline.


