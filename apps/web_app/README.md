# LexAI Web Client ⚖️

The React + Vite production web workspace for the LexAI platform. It is fully integrated with Firebase services for hosting, authentication, and database storage, and queries the containerized Cloud Run search backend directly.

---

## 🚀 Live Demo
Access the live web deployment at: **[https://lexai-3fd1a.web.app](https://lexai-3fd1a.web.app)**

---

## 🏛️ System Features

* **Real-time Legal Consultation**: A conversational interface leveraging Gemini's retrieval-augmented synthesis pipeline for answering case queries.
* **Firebase Authentication**: Support for secure Email/Password registration/login and native **Google Sign-In**.
* **Auto-Provisioning Client Profiles**: Automatically spins up database records in Firestore (`/users/{uid}`) upon first sign-in (for both Google and email users) to track active sessions.
* **Environment-Aware Core API**: Automatically directs API traffic to your local serverless proxy (`/core-api`) in development mode, and connects directly to the live serverless Cloud Run domain in production.

---

## 📂 Project Structure

* `/src/api/firebase.js`: Firebase client initialization (Auth and Firestore DB).
* `/src/api/legal.js`: Interface to backend RAG API, resolving base URLs dynamically based on environment.
* `/src/context/AuthContext.jsx`: Authentication context provider handling Firebase triggers, login status, and auto-profiling.
* `/src/pages/AuthPage.jsx`: Beautiful glassmorphic design login and registration layout, including Google Sign-in buttons.
* `/src/pages/LexAIChatPage.jsx`: Clean, responsive RAG chat console with source precedents and citations.

---

## ⚙️ Development & Deployment

### 1. Run Locally
Install dependencies and run the Vite server locally:
```bash
npm install
npm run dev
```

### 2. Build and Deploy to Firebase
Build the static distribution files and upload them to Firebase Hosting:
```bash
npm run build
firebase deploy --only hosting
```
