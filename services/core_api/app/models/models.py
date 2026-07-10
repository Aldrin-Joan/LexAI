"""Database models for the LegalTech Super-App.

All Firebase-authenticated users are referenced by their Firebase UID
(a string) rather than the local SQL User table's integer ID. This
avoids double-onboarding while keeping the RAG/search tables separate.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


# ---------------------------------------------------------------------------
# Enums — state machine for Case lifecycle
# ---------------------------------------------------------------------------

class CaseStatus(str, Enum):
    """High-level disposition of a case request."""

    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class CaseStage(str, Enum):
    """Granular workflow step for an active case.

    Valid forward transitions (enforced in the service layer):
        submitted  -> accepted | declined
        accepted   -> in_review | declined
        in_review  -> advice_drafted
        advice_drafted -> completed
    """

    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    IN_REVIEW = "in_review"
    ADVICE_DRAFTED = "advice_drafted"
    COMPLETED = "completed"


# Allowed forward transitions — anything not in this map is rejected.
# Note: "decline" is an out-of-band action handled by resolve_case(),
# not a stage transition — it is intentionally absent here.
VALID_TRANSITIONS: dict[str, list[str]] = {
    CaseStage.SUBMITTED: [CaseStage.ACCEPTED],
    CaseStage.ACCEPTED: [CaseStage.IN_REVIEW],
    CaseStage.IN_REVIEW: [CaseStage.ADVICE_DRAFTED],
    CaseStage.ADVICE_DRAFTED: [CaseStage.COMPLETED],
    CaseStage.COMPLETED: [],
}


# ---------------------------------------------------------------------------
# Case
# ---------------------------------------------------------------------------

class Case(SQLModel, table=True):
    """A legal consultation case between a client and an advocate.

    Attributes:
        client_id: Firebase UID of the requesting client.
        lawyer_id: Firebase UID of the assigned advocate.
        client_name: Denormalized display name (snapshot at submission).
        lawyer_name: Denormalized display name (snapshot at submission).
        summary: Client-provided description of the issue.
        status: High-level disposition (CaseStatus enum).
        current_stage: Granular workflow step (CaseStage enum).
        attached_document_ids: Comma-separated list of DocumentUpload IDs
            that the client attached to this case.
        created_at: UTC timestamp of submission.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: str = Field(index=True)
    client_name: str
    lawyer_id: str = Field(index=True)
    lawyer_name: str
    summary: str
    status: str = Field(default=CaseStatus.SUBMITTED)
    current_stage: str = Field(default=CaseStage.SUBMITTED)
    attached_document_ids: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Message  (peer-to-peer client ↔ advocate chat)
# ---------------------------------------------------------------------------

class Message(SQLModel, table=True):
    """A single message exchanged between two users.

    Attributes:
        sender_id: Firebase UID of the sender.
        receiver_id: Firebase UID of the recipient.
        content: Raw text content (HTML-escaped before storage).
        client_msg_id: Client-generated UUID used for idempotent retries.
            A UNIQUE constraint ensures double-sends are deduplicated at
            the database level.
        timestamp: UTC time the message was first persisted.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: str = Field(index=True)
    receiver_id: str = Field(index=True)
    content: str
    client_msg_id: str = Field(
        unique=True, index=True, description="Client UUID for idempotency"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Post  (advocate social feed)
# ---------------------------------------------------------------------------

class Post(SQLModel, table=True):
    """A public update published by a verified advocate.

    Attributes:
        author_id: Firebase UID of the posting advocate.
        author_name: Denormalized display name.
        author_bar_number: Denormalized Bar Council registration number.
        content: Post body text.
        likes_count: Optimistic like counter (not ACID-critical).
        created_at: UTC timestamp of publication.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: str = Field(index=True)
    author_name: str
    author_bar_number: str = Field(default="")
    content: str
    likes_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# DocumentUpload  (tracks file ownership for attachment IDOR protection)
# ---------------------------------------------------------------------------

class DocumentUpload(SQLModel, table=True):
    """Metadata record for a file uploaded via /legal/upload-document.

    Attributes:
        file_id: Unique file identifier (UUID assigned at upload time).
        owner_uid: Firebase UID of the user who uploaded this document.
        filename: Original filename as reported by the client.
        created_at: UTC timestamp of upload.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: str = Field(unique=True, index=True)
    owner_uid: str = Field(index=True)
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Legacy local-auth User table (kept for backward-compat with auth_routes)
# ---------------------------------------------------------------------------

class UserRole(str, Enum):  # type: ignore[no-redef]
    """Legacy role enum used by the SQL-based auth route."""

    CLIENT = "client"
    LAWYER = "lawyer"


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    role: UserRole = Field(default=UserRole.CLIENT)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    """Local user record for the legacy SQL-auth flow.

    New code should prefer Firebase UID string references.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
