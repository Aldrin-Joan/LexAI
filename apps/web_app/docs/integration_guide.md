# Developer Integration Guide: Chat & Voice Backend Communication 🔗🎤

This document outlines the step-by-step technical details required for the frontend web application to integrate with the backend's WebSocket chat router and HTTP REST voice query pipelines.

---

## 🏛️ Network Protocol Overview

The web client communicates with `services/core_api` using two channels:
1. **WebSockets (WS)**: Persistent two-way channel for standard conversational AI chat.
2. **HTTP REST (HTTP)**: Multipart request channel for uploading microphone recordings and receiving speech-to-text / audio results.

```mermaid
graph TD
    subgraph Web_Client [React Frontend]
        ChatBox[Chat Input Console]
        VoiceRec[Voice Recorder]
    end

    subgraph API_Gateways [FastAPI Backend Router]
        WSEndpoint[ws/chat/{user_id}]
        RESTEndpoint[legal/voice-query]
    end

    ChatBox -->|WebSocket Frame| WSEndpoint
    WSEndpoint -->|Echo AI Text Response| ChatBox
    
    VoiceRec -->|POST FormData Audio| RESTEndpoint
    RESTEndpoint -->|JSON: Text + MP3 URL| VoiceRec
```

---

## 💬 1. Chat Integration (WebSocket)

The backend exposes a WebSocket route for real-time text chatting with the AI.

### **Establish Connection**
The frontend initiates connection utilizing the standard browser WebSocket client:
```javascript
const userId = 101; // Obtained from auth state
const socket = new WebSocket(`ws://localhost:8001/ws/chat/${userId}`);

socket.onopen = () => {
    console.log("WebSocket connection established with Legal AI");
};
```

### **Sending Messages**
Messages are dispatched to the socket as plain text strings:
```javascript
function sendTextMessage(messageText) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(messageText);
    }
}
```

### **Receiving Responses**
Listen for incoming events. The backend returns plain text answers:
```javascript
socket.onmessage = (event) => {
    const aiAnswer = event.data;
    appendMessageToChatFeed({
        sender: "ai",
        text: aiAnswer,
        timestamp: new Date().toISOString()
    });
};
```

---

## 🎤 2. Voice Query Integration (HTTP REST)

The voice pipeline handles binary file uploads, Whisper Speech-to-Text, and Text-to-Speech playback.

### **API Specifications**
* **Endpoint**: `POST http://localhost:8001/legal/voice-query`
* **Headers**: `Content-Type: multipart/form-data`
* **Payload**:
  * `audio`: (Binary `.wav` or `.aac` audio blob file captured via client microphone).
  * `query`: (Optional plain text query, if overriding audio).
  * `search_mode`: "hybrid"

### **Frontend Integration Example (JavaScript/Axios)**
```javascript
async function uploadVoiceQuery(audioBlob) {
    const formData = new FormData();
    // Append the captured microphone recording
    formData.append("audio", audioBlob, "user_voice_query.wav");
    formData.append("search_mode", "hybrid");

    try {
        const response = await axios.post("http://localhost:8001/legal/voice-query", formData, {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        });

        // 1. Display transcribed text in feed
        appendMessageToChatFeed({ sender: "user", text: response.data.transcription });

        // 2. Display AI Answer in feed
        appendMessageToChatFeed({ sender: "ai", text: response.data.answer });

        // 3. Playback spoken audio file returned by gTTS
        if (response.data.audio_response_url) {
            playVoiceResponse(`http://localhost:8001${response.data.audio_response_url}`);
        }
    } catch (error) {
        console.error("Voice Query pipeline execution failed", error);
    }
}

// Playback returned audio response using HTML5 Audio API
function playVoiceResponse(audioUrl) {
    const audio = new Audio(audioUrl);
    audio.play();
}
```
---

## 🔒 Error Handling & WebSocket Recovery
1. **Auto-Reconnect**: If the socket closes due to network loss, implement an exponential backoff reconnection loop:
   ```javascript
   socket.onclose = () => {
       setTimeout(() => reconnectSocket(), 3000);
   };
   ```
2. **Audio Fallback**: If the browser mic permissions are blocked or the user is on a slow connection, the UI should gracefully disable the microphone button and prompt standard text input.
