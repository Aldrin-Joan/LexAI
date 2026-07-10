"""Legal API router — advocate feed, case management, and document upload.

Endpoints
---------
GET  /legal/posts                – Fetch paginated advocate feed (any auth user)
POST /legal/posts                – Publish a post (verified advocates only)
GET  /legal/cases                – Fetch the caller's cases (token-scoped)
POST /legal/cases/request        – Submit a consultation request (clients only)
POST /legal/cases/resolve        – Accept or decline a case (assigned lawyer)
PATCH /legal/cases/{case_id}/stage – Advance case stage (assigned lawyer)
POST /legal/upload-document      – Upload a file and record ownership
POST /legal/voice-query          – Voice query (STT → RAG → TTS)
GET  /legal/audio/{filename}     – Serve a generated audio response
GET  /legal/lawyers              – Public lawyer directory stub
"""

import os
import shutil
import time
import uuid
from collections import defaultdict, deque
from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session, select

try:
    from app.core.db import get_session
    from app.core.security import FirebaseUser, get_current_user, require_lawyer
    from app.models.models import (
        Case,
        CaseStage,
        CaseStatus,
        DocumentUpload,
        Post,
        VALID_TRANSITIONS,
    )
except ImportError:
    from core.db import get_session
    from core.security import FirebaseUser, get_current_user, require_lawyer
    from models.models import (
        Case,
        CaseStage,
        CaseStatus,
        DocumentUpload,
        Post,
        VALID_TRANSITIONS,
    )

router = APIRouter(prefix="/legal", tags=["legal"])


# ---------------------------------------------------------------------------
# In-memory rate limiter (per user, per minute)
# NOTE: This is process-level. Migrate to Redis for clustered deployments.
# ---------------------------------------------------------------------------

_rate_windows: dict[str, deque[float]] = defaultdict(deque)
_RATE_LIMITS: dict[str, int] = {
    "post": 5,
    "case_request": 3,
}


def _check_rate_limit(uid: str, action: str, window: int = 60) -> None:
    """Enforce a sliding-window rate limit per user per action.

    Args:
        uid: The caller's Firebase UID.
        action: A key into ``_RATE_LIMITS`` (e.g. "post", "case_request").
        window: Sliding window size in seconds (default 60).

    Raises:
        HTTPException: 429 if the limit for this action/window is exceeded.
    """
    now = time.time()
    key = f"{uid}:{action}"
    q = _rate_windows[key]
    # Expire entries outside the window
    while q and q[0] < now - window:
        q.popleft()
    limit = _RATE_LIMITS.get(action, 10)
    if len(q) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded: max {limit} '{action}' "
                f"actions per {window} seconds."
            ),
        )
    q.append(now)


# ---------------------------------------------------------------------------
# Pydantic request/response schemas
# ---------------------------------------------------------------------------

class PostCreate(BaseModel):
    content: str


class PostRead(BaseModel):
    id: int
    author_id: str
    author_name: str
    author_bar_number: str
    content: str
    likes_count: int
    created_at: str

    class Config:
        from_attributes = True


class CaseRequestBody(BaseModel):
    lawyer_id: str
    lawyer_name: str
    user_query_summary: str
    attached_document_ids: list[str] = []


class CaseResolveBody(BaseModel):
    case_id: int
    action: str  # "accept" | "decline"


class CaseStageBody(BaseModel):
    new_stage: str


class CaseRead(BaseModel):
    id: int
    client_id: str
    client_name: str
    lawyer_id: str
    lawyer_name: str
    summary: str
    status: str
    current_stage: str
    attached_document_ids: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Advocate Feed
# ---------------------------------------------------------------------------

@router.get("/posts", response_model=list[PostRead])
def get_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Fetch paginated advocate feed posts.

    Accessible to all authenticated users (clients and advocates).

    Args:
        limit: Maximum number of posts to return (max 100).
        offset: Number of posts to skip for pagination.
        current_user: Verified Firebase caller (any role).
        session: Database session dependency.

    Returns:
        list[PostRead]: Paginated list of feed posts, newest first.
    """
    posts = session.exec(
        select(Post).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return [
        PostRead(
            id=p.id,
            author_id=p.author_id,
            author_name=p.author_name,
            author_bar_number=p.author_bar_number,
            content=p.content,
            likes_count=p.likes_count,
            created_at=p.created_at.isoformat(),
        )
        for p in posts
    ]


@router.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    body: PostCreate,
    current_user: FirebaseUser = Depends(require_lawyer),
    session: Session = Depends(get_session),
) -> Any:
    """Publish a new feed post. Restricted to verified advocates.

    Args:
        body: Post content.
        current_user: Verified FirebaseUser, must be is_lawyer=True.
        session: Database session dependency.

    Returns:
        PostRead: The newly created post.
    """
    _check_rate_limit(current_user.uid, "post")

    post = Post(
        author_id=current_user.uid,
        author_name=current_user.full_name,
        author_bar_number=current_user.bar_registration_number,
        content=body.content,
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return PostRead(
        id=post.id,
        author_id=post.author_id,
        author_name=post.author_name,
        author_bar_number=post.author_bar_number,
        content=post.content,
        likes_count=post.likes_count,
        created_at=post.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Case Management
# ---------------------------------------------------------------------------

@router.get("/cases", response_model=list[CaseRead])
def get_cases(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Fetch the caller's own cases.

    Cases are filtered by the verified caller's uid — clients see their
    own requests; advocates see cases assigned to them. No user_id
    query parameter is exposed (prevents IDOR).

    Args:
        limit: Maximum number of cases to return (max 100).
        offset: Number of cases to skip for pagination.
        current_user: Verified Firebase caller.
        session: Database session dependency.

    Returns:
        list[CaseRead]: Paginated list of cases belonging to the caller.
    """
    if current_user.is_lawyer:
        stmt = (
            select(Case)
            .where(Case.lawyer_id == current_user.uid)
            .order_by(Case.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    else:
        stmt = (
            select(Case)
            .where(Case.client_id == current_user.uid)
            .order_by(Case.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    cases = session.exec(stmt).all()
    return [
        CaseRead(
            id=c.id,
            client_id=c.client_id,
            client_name=c.client_name,
            lawyer_id=c.lawyer_id,
            lawyer_name=c.lawyer_name,
            summary=c.summary,
            status=c.status,
            current_stage=c.current_stage,
            attached_document_ids=c.attached_document_ids,
            created_at=c.created_at.isoformat(),
        )
        for c in cases
    ]


@router.post(
    "/cases/request",
    response_model=CaseRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_case_request(
    body: CaseRequestBody,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Submit a new consultation case request.

    The ``client_id`` is always set to the verified caller's uid —
    the request body cannot override this to prevent impersonation.

    Attachment ownership is verified: all referenced document IDs must
    have been uploaded by the calling user.

    Args:
        body: Case request payload.
        current_user: Verified Firebase client.
        session: Database session dependency.

    Returns:
        CaseRead: The newly created case.

    Raises:
        HTTPException: 403 if the caller is a lawyer (lawyers cannot
            submit cases as clients).
        HTTPException: 403 if any attachment ID was not uploaded by
            the caller (IDOR protection).
        HTTPException: 429 if the rate limit is exceeded.
    """
    if current_user.is_lawyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified advocates cannot submit case requests as clients.",
        )

    _check_rate_limit(current_user.uid, "case_request")

    # Attachment IDOR check
    doc_ids_str: Optional[str] = None
    if body.attached_document_ids:
        for doc_id in body.attached_document_ids:
            upload = session.exec(
                select(DocumentUpload).where(
                    DocumentUpload.file_id == doc_id
                )
            ).first()
            if not upload:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Document '{doc_id}' not found.",
                )
            if upload.owner_uid != current_user.uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"You do not own document '{doc_id}'. "
                        "Only documents you uploaded may be attached."
                    ),
                )
        doc_ids_str = ",".join(body.attached_document_ids)

    case = Case(
        client_id=current_user.uid,
        client_name=current_user.full_name,
        lawyer_id=body.lawyer_id,
        lawyer_name=body.lawyer_name,
        summary=body.user_query_summary,
        attached_document_ids=doc_ids_str,
    )
    session.add(case)
    session.commit()
    session.refresh(case)
    return CaseRead(
        id=case.id,
        client_id=case.client_id,
        client_name=case.client_name,
        lawyer_id=case.lawyer_id,
        lawyer_name=case.lawyer_name,
        summary=case.summary,
        status=case.status,
        current_stage=case.current_stage,
        attached_document_ids=case.attached_document_ids,
        created_at=case.created_at.isoformat(),
    )


@router.post("/cases/resolve", response_model=CaseRead)
def resolve_case(
    body: CaseResolveBody,
    current_user: FirebaseUser = Depends(require_lawyer),
    session: Session = Depends(get_session),
) -> Any:
    """Accept or decline a pending case request.

    Only the assigned advocate (``lawyer_id == caller.uid``) may resolve
    a case. Action must be "accept" or "decline".

    Args:
        body: Case ID and action ("accept" or "decline").
        current_user: Verified FirebaseUser, must be is_lawyer=True.
        session: Database session dependency.

    Returns:
        CaseRead: The updated case record.

    Raises:
        HTTPException: 404 if the case is not found.
        HTTPException: 403 if the caller is not the assigned advocate.
        HTTPException: 400 if the action is invalid or the state
            transition is not permitted.
    """
    case = session.get(Case, body.case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {body.case_id} not found.",
        )
    if case.lawyer_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned advocate for this case.",
        )
    if body.action == "accept":
        _assert_valid_transition(case.current_stage, CaseStage.ACCEPTED)
        case.status = CaseStatus.ACCEPTED
        case.current_stage = CaseStage.ACCEPTED
    elif body.action == "decline":
        case.status = CaseStatus.DECLINED
        case.current_stage = CaseStage.SUBMITTED  # frozen at entry stage
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'accept' or 'decline'.",
        )
    session.add(case)
    session.commit()
    session.refresh(case)
    return CaseRead(
        id=case.id,
        client_id=case.client_id,
        client_name=case.client_name,
        lawyer_id=case.lawyer_id,
        lawyer_name=case.lawyer_name,
        summary=case.summary,
        status=case.status,
        current_stage=case.current_stage,
        attached_document_ids=case.attached_document_ids,
        created_at=case.created_at.isoformat(),
    )


@router.patch("/cases/{case_id}/stage", response_model=CaseRead)
def update_case_stage(
    case_id: int,
    body: CaseStageBody,
    current_user: FirebaseUser = Depends(require_lawyer),
    session: Session = Depends(get_session),
) -> Any:
    """Advance a case to the next workflow stage.

    Only the assigned advocate may update stages. Invalid or backwards
    transitions are rejected.

    Args:
        case_id: Database ID of the case to update.
        body: Payload containing ``new_stage``.
        current_user: Verified FirebaseUser, must be is_lawyer=True.
        session: Database session dependency.

    Returns:
        CaseRead: The updated case record.

    Raises:
        HTTPException: 404 if the case is not found.
        HTTPException: 403 if the caller is not the assigned advocate.
        HTTPException: 400 if the stage value is invalid or the
            transition is not permitted by the state machine.
    """
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found.",
        )
    if case.lawyer_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned advocate for this case.",
        )

    # Validate enum membership
    try:
        new_stage = CaseStage(body.new_stage)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"'{body.new_stage}' is not a valid CaseStage. "
                f"Valid values: {[s.value for s in CaseStage]}"
            ),
        )

    _assert_valid_transition(case.current_stage, new_stage)
    case.current_stage = new_stage
    if new_stage == CaseStage.COMPLETED:
        case.status = CaseStatus.COMPLETED
    session.add(case)
    session.commit()
    session.refresh(case)
    return CaseRead(
        id=case.id,
        client_id=case.client_id,
        client_name=case.client_name,
        lawyer_id=case.lawyer_id,
        lawyer_name=case.lawyer_name,
        summary=case.summary,
        status=case.status,
        current_stage=case.current_stage,
        attached_document_ids=case.attached_document_ids,
        created_at=case.created_at.isoformat(),
    )


def _assert_valid_transition(current: str, target: str) -> None:
    """Raise a 400 if ``target`` is not a valid next stage from ``current``.

    Args:
        current: The current CaseStage value.
        target: The proposed next CaseStage value.

    Raises:
        HTTPException: 400 if the transition is not permitted.
    """
    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid stage transition: '{current}' → '{target}'. "
                f"Permitted next stages: {allowed}"
            ),
        )


# ---------------------------------------------------------------------------
# Document Upload (with ownership tracking)
# ---------------------------------------------------------------------------

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Upload a document and record the caller's ownership.

    Args:
        file: The uploaded file (PDF, DOCX, or image).
        current_user: Verified Firebase caller.
        session: Database session dependency.

    Returns:
        dict: Upload result including the assigned ``file_id``.

    Raises:
        HTTPException: 400 if the file type is not supported.
    """
    allowed_extensions = ["pdf", "docx", "jpg", "jpeg", "png"]
    ext = (file.filename or "").split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '.{ext}' not supported.",
        )

    content = await file.read()
    file_id = str(uuid.uuid4())

    # Persist file metadata with ownership
    upload_record = DocumentUpload(
        file_id=file_id,
        owner_uid=current_user.uid,
        filename=file.filename or "unknown",
    )
    session.add(upload_record)
    session.commit()

    # Lazy import — FileService pulls in heavy ML deps; only load on demand
    try:
        from app.services.file_service import FileService
    except ImportError:
        from services.file_service import FileService

    result = await FileService.process_document(content, file.filename)
    return {**result, "file_id": file_id}


# ---------------------------------------------------------------------------
# Voice Query
# ---------------------------------------------------------------------------

@router.post("/voice-query")
async def voice_query(
    file: UploadFile = File(...),
    language: str = Form(None),
    current_user: FirebaseUser = Depends(get_current_user),
) -> dict:
    """Process a voice audio query and return an AI answer with TTS audio.

    Args:
        file: Audio file (WAV, MP3, M4A, OGG, or AAC).
        language: Optional BCP-47 language hint.
        current_user: Verified Firebase caller.

    Returns:
        dict: Transcription, answer text, audio URL, and cited sources.

    Raises:
        HTTPException: 400 if the audio format is unsupported.
        HTTPException: 500 on STT or TTS errors.
    """
    if not (file.filename or "").endswith(
        (".wav", ".mp3", ".m4a", ".ogg", ".aac")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported audio format.",
        )

    if language == "string":
        language = None

    temp_dir = os.path.join(os.getcwd(), "backend", "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")

    with open(temp_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # Lazy imports — whisper, torch, and sentence-transformers are only
    # loaded when this voice endpoint is actually called, not at module import
    # time. This prevents numpy/numba incompatibilities from blocking startup.
    try:
        from app.services.ai_service import AIService
        from app.services.translation_service import TranslationService
        from app.services.voice.stt import transcribe_audio
        from app.services.voice.tts import text_to_speech
    except ImportError:
        from services.ai_service import AIService
        from services.translation_service import TranslationService
        from services.voice.stt import transcribe_audio
        from services.voice.tts import text_to_speech

    try:
        try:
            transcription = transcribe_audio(temp_path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"STT Error: {exc}",
            ) from exc

        translator = TranslationService()
        source_lang = language or translator.detect_language(transcription)
        supported_langs = ["en", "hi", "ta", "te", "kn", "ml", "bn", "es", "fr"]
        if source_lang not in supported_langs:
            source_lang = "en"

        answer_text, sources = await AIService.get_legal_advice(transcription)

        audio_filename = f"response_{uuid.uuid4()}.mp3"
        audio_path = os.path.join(
            os.getcwd(), "backend", "data", "audio", audio_filename
        )
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        text_to_speech(answer_text, lang=source_lang, output_path=audio_path)

        return {
            "transcription": transcription,
            "answer_text": answer_text,
            "audio_url": f"/legal/audio/{audio_filename}",
            "sources": sources,
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/audio/{filename}")
async def get_audio(filename: str) -> FileResponse:
    """Serve a previously generated TTS audio file.

    Args:
        filename: Name of the audio file to serve.

    Returns:
        FileResponse: The audio file in MPEG format.

    Raises:
        HTTPException: 404 if the file does not exist.
    """
    file_path = os.path.join(
        os.getcwd(), "backend", "data", "audio", filename
    )
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Audio file not found.",
    )


# ---------------------------------------------------------------------------
# Public lawyer directory stub
# ---------------------------------------------------------------------------

@router.get("/lawyers")
async def get_lawyers(
    current_user: FirebaseUser = Depends(get_current_user),
) -> list[dict]:
    """Fetch a stub of the verified lawyer directory.

    Args:
        current_user: Verified Firebase caller.

    Returns:
        list[dict]: Placeholder lawyer records.
    """
    return [
        {"id": 1, "name": "Adv. Rajesh Kumar", "specialization": "Criminal Law", "rating": 4.8},
        {"id": 2, "name": "Adv. Sneha Sharma", "specialization": "Corporate Law", "rating": 4.9},
        {"id": 3, "name": "Adv. Anjali Menon", "specialization": "Family Law", "rating": 4.7},
    ]
