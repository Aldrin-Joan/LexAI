# Security & Authentication Specifications 🔐🛡️

This document outlines the security architecture, token lifecycle, route protection strategies, and secure upload handlers for both the frontend (React) and backend (FastAPI) services.

---

## 🏛️ Security Architecture Overview

```mermaid
graph TD
    Client[React Browser Client] -->|1. Credentials| LoginAPI[POST /auth/login]
    LoginAPI -->|2. Verify via Bcrypt| DB[(SQLite DB)]
    LoginAPI -->>|3. Issue JWT Token| Client
    
    Client -->|4. Authenticated Request <br> Bearer Token| PrivateAPI[FastAPI Private Endpoints]
    Client -->|5. WebSocket Connection <br> ws://.../ws?token=JWT| WebSocketAPI[FastAPI WebSocket Router]
    
    PrivateAPI & WebSocketAPI -->|6. Verify JWT Signature| AuthGuard[Security Middleware]
```

---

## 🔑 1. Token Lifecycle & Specifications (JWT)

* **Algorithm**: `HS256` (HMAC SHA-256).
* **Token Content (Claims)**:
  * `sub`: Subject identifier (User email or Username).
  * `role`: User role claim (`client` or `lawyer`).
  * `exp`: Expiration time (Short-lived Access Tokens: 60 minutes).
* **Token Storage**:
  * **Frontend**: Stored in React state memory, backed up to `localStorage` for session persistence.
  * **Interceptors**: Axios/Fetch clients configure a global interceptor adding `Authorization: Bearer <token>` to all private REST calls.

---

## 🔌 2. Secure WebSockets Connection Guard

### **Backend Verification Hook**
To prevent spoofing and interception, connection parameters must be verified prior to WebSocket acceptance.

* **Target Router Code (`app/api/chat_ws.py`)**:
  ```python
  from app.core.auth import verify_access_token
  from fastapi import WebSocket, status

  @router.websocket("/ws/chat")
  async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
      # 1. Parse and verify JWT token signature
      user_data = verify_access_token(token)
      if not user_data:
          # Reject connection with Policy Violation code
          await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
          return
          
      # 2. Accept connection on success
      await manager.connect(user_data.user_id, websocket)
  ```

---

## 🛡️ 3. Frontend Route Guards & Steppers

The React Router redirects users dynamically depending on their Auth context:

* **Unauthenticated Users**: Routed exclusively to the Login/Signup portal pages.
* **Authenticated Clients**: Routed to `apps/web_app/docs/client_workspace.md`.
* **Authenticated Lawyers**:
  * If `verification_status == "pending_review"`: Redirected to a static **Holding Screen** stating verification is in progress.
  * If `verification_status == "verified"`: Full access to feed creation and inquiries terminal.
  * If `verification_status == "rejected"`: Access revoked with support appeal forms.

---

## 📁 4. Document Upload Sanitization

To prevent Remote Code Execution (RCE) and Directory Traversal attacks during lawyer onboarding document uploads:

1. **File Type (MIME) Restriction**: Only permit `application/pdf`, `image/png`, and `image/jpeg`. Reject all other types.
2. **File Size Hard Limit**: Restrict payload chunks to `10MB`.
3. **Filename Randomization**: Discard user-provided filenames. Rename files to randomized UUIDs (e.g. `doc_f81d4fae-7dec-11d0-a765-00a0c91e6bf6.pdf`) prior to disk writes:
   ```python
   import uuid
   from pathlib import Path

   unique_filename = f"{uuid.uuid4()}{Path(uploaded_file.filename).suffix}"
   ```
4. **Static Directory Protection**: The `/static/uploads/` directory must be mounted with directory-listing disabled (`directory_redirection=False`) to prevent document scraping.
