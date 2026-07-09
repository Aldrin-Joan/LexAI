import React, { useState, useEffect, useRef, useCallback } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { wsManager } from '../api/ws';
import { getLawyers, askLexAI } from '../api/legal';
import {
  collection, query, where, getDocs, doc, setDoc, updateDoc, arrayUnion, getDoc
} from 'firebase/firestore';
import { db } from '../api/firebase';
import {
  MicIcon, SendIcon, SearchIcon, ShieldCheckIcon,
  FolderIcon, SparkleIcon, ScalesIcon, ZapIcon,
  DocumentIcon, BrainCircuitIcon,
} from '../components/Icons';
import styles from './ClientWorkspace.module.css';

const SEARCH_MODES = ['Keyword', 'Semantic', 'Hybrid', 'Ultra'];

const SAMPLE_LAWYERS = [
  { id: 1, name: 'Adv. Ravi Sharma', domains: ['Criminal', 'Constitutional'], online: true, exp: 8 },
  { id: 2, name: 'Adv. Priya Mehta', domains: ['Corporate', 'Tax'], online: true, exp: 12 },
  { id: 3, name: 'Adv. Suresh Nair', domains: ['Family', 'Civil'], online: false, exp: 5 },
];

const TIP_CARDS = [
  { Icon: ScalesIcon, text: 'Ask legal precedents & case law', color: 'var(--amber)' },
  { Icon: DocumentIcon, text: 'Scan rental & compliance agreements', color: 'var(--blue)' },
  { Icon: ShieldCheckIcon, text: 'Connect with verified advocates', color: 'var(--green)' },
];

function CitationPill({ text }) {
  return <span className="citation-pill">{text}</span>;
}

function parseCitations(text) {
  // Detect patterns like "Sec. 302 IPC" or "Art. 21 Constitution"
  const re = /(Sec\.?\s*\d+[A-Z]*\s*\w*|Art\.?\s*\d+[A-Z]*\s*\w*|Section\s*\d+[A-Z]*\s*\w*|CrPC\s*\d+)/g;
  const parts = [];
  let last = 0;
  let match;
  while ((match = re.exec(text)) !== null) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    parts.push(<CitationPill key={match.index} text={match[0]} />);
    last = match.index + match[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

function MessageBubble({ msg }) {
  const isUser = msg.sender === 'user';
  return (
    <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleAI}`}>
      {!isUser && <div className={styles.aiLabel}>⚖️ LexAI</div>}
      <div className={styles.bubbleText}>
        {isUser ? msg.text : parseCitations(msg.text)}
      </div>
      {!isUser && msg.precedents && msg.precedents.length > 0 && (
        <div className={styles.precedentsList}>
          <div className={styles.precedentsHeader}>📚 Cited Precedents:</div>
          {msg.precedents.map((p) => (
            <div key={p.id} className={styles.precedentItem}>
              <span className={styles.precedentTitle} title={p.title}>
                {p.title} ({p.year})
              </span>
              <span className={styles.precedentScore}>
                Score: {p.score?.toFixed(4)}
              </span>
            </div>
          ))}
        </div>
      )}
      <div className={styles.bubbleTime}>
        {new Date(msg.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className={`${styles.bubble} ${styles.bubbleAI}`} style={{ padding: '0.75rem 1rem' }}>
      <div className={styles.aiLabel}>⚖️ LexAI</div>
      <div className={styles.typingDots}>
        <span /><span /><span />
      </div>
    </div>
  );
}

function WaveformBars({ active }) {
  return (
    <div className={styles.waveform}>
      {[...Array(12)].map((_, i) => (
        <div
          key={i}
          className={styles.waveBar}
          style={{
            animationDelay: `${i * 80}ms`,
            animationPlayState: active ? 'running' : 'paused',
          }}
        />
      ))}
    </div>
  );
}

export default function ClientWorkspace() {
  const { user, token } = useAuth();
  const toast = useToast();

  // Chat state
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState('');
  const [typing, setTyping]       = useState(false);
  const [connected, setConnected] = useState(false);
  const [searchMode, setSearchMode] = useState('Hybrid');
  const [sessionId, setSessionId] = useState(null);
  const [sessionsList, setSessionsList] = useState([]);

  // Voice recorder
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // UI states
  const [chatMode, setChatMode]   = useState(false);   // home → chat transition
  const [lawyers, setLawyers]     = useState(SAMPLE_LAWYERS);
  const chatEndRef = useRef(null);

  /* ---- Sessions Loader ---- */
  /* ---- Sessions Loader ---- */
  const loadSessions = useCallback(async () => {
    if (!user?.uid) return;
    try {
      const q = query(
        collection(db, 'sessions'),
        where('user_id', '==', user.uid)
      );
      const querySnapshot = await getDocs(q);
      const list = [];
      querySnapshot.forEach((docSnap) => {
        list.push({ id: docSnap.id, ...docSnap.data() });
      });
      list.sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
      setSessionsList(list);
    } catch (err) {
      console.error('Failed to load active sessions:', err);
    }
  }, [user]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  /* ---- WebSocket ---- */
  useEffect(() => {
    if (!user) return;
    wsManager.connect(`/ws/chat/${user.id || 1}`, token);

    const offOpen  = wsManager.on('open',  () => setConnected(true));
    const offClose = wsManager.on('close', () => setConnected(false));
    const offMsg   = wsManager.on('message', (data) => {
      // Optional: keep wsManager listener for backend socket logs
    });

    return () => {
      offOpen(); offClose(); offMsg();
      wsManager.disconnect();
    };
  }, [user, token]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  /* ---- Send text ---- */
  const sendMessage = useCallback(async () => {
    if (!input.trim() || !user?.uid) return;
    setChatMode(true);
    const text = input.trim();
    setInput('');

    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      setSessionId(currentSessionId);
    }

    const userMsg = { sender: 'user', text, ts: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setTyping(true);

    try {
      const sessionRef = doc(db, 'sessions', currentSessionId);
      await setDoc(sessionRef, {
        user_id: user.uid,
        last_updated: new Date().toISOString(),
        messages: arrayUnion(userMsg)
      }, { merge: true });

      const data = await askLexAI(text, currentSessionId, 5);

      const aiMsg = {
        sender: 'ai',
        text: data.answer || "No answer returned.",
        ts: Date.now(),
        precedents: data.precedents || [],
      };

      await updateDoc(sessionRef, {
        last_updated: new Date().toISOString(),
        messages: arrayUnion(aiMsg)
      });

      setTyping(false);
      setMessages((prev) => [...prev, aiMsg]);
      loadSessions();
    } catch (err) {
      console.error('LexAI API error, using mock fallback:', err);
      const fallbackMsg = {
        sender: 'ai',
        text: `[⚠️ API Error: ${err.message}] According to Sec. 302 IPC and CrPC 154, your query regarding "${text}" involves several provisions. Please consult a verified advocate for personalized advice.`,
        ts: Date.now(),
      };

      const sessionRef = doc(db, 'sessions', currentSessionId);
      await updateDoc(sessionRef, {
        last_updated: new Date().toISOString(),
        messages: arrayUnion(fallbackMsg)
      }).catch((e) => console.error("Failed saving fallback message:", e));

      setTyping(false);
      setMessages((prev) => [...prev, fallbackMsg]);
      loadSessions();
    }
  }, [input, sessionId, user, loadSessions]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  /* ---- Voice recording ---- */
  const toggleRecording = async () => {
    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      chunksRef.current = [];
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        stream.getTracks().forEach((t) => t.stop());
        // Simulate voice upload
        toast('Voice recorded — processing...', 'info');
        setTimeout(() => {
          setChatMode(true);
          setMessages((prev) => [
            ...prev,
            { sender: 'user', text: '🎤 [Voice Query]', ts: Date.now() },
            {
              sender: 'ai',
              text: 'I have processed your voice query. Under Sec. 304 IPC, culpable homicide is punishable with imprisonment for life. This involves Art. 21 Constitution rights as well.',
              ts: Date.now() + 100,
            },
          ]);
        }, 2000);
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setRecording(true);
    } catch {
      toast('Microphone access denied. Please enable mic permissions.', 'error');
    }
  };

  return (
    <div className={styles.page}>
      <Navbar />

      <div className={styles.workspace}>
        {/* ====== LEFT: CHAT COLUMN ====== */}
        <div className={styles.chatCol}>

          {/* Home greeting (before chat mode) */}
          {!chatMode && (
            <div className={styles.greeting} id="greeting-area">
              <div className={styles.greetingCard}>
                <h1 className={styles.greetTitle}>
                  Hello, <span style={{ color: 'var(--amber)' }}>{user?.full_name?.split(' ')[0]}</span> 👋
                </h1>
                <p className={styles.greetSub}>
                  How can we assist you with legal research today?
                </p>
              </div>
              <div className={styles.tipGrid}>
                {[
                  { Icon: ScalesIcon, text: 'Ask legal precedents & case law', color: 'var(--amber)' },
                  { Icon: DocumentIcon, text: 'Scan rental & compliance agreements', color: 'var(--blue)' },
                  { Icon: ShieldCheckIcon, text: 'Connect with verified advocates', color: 'var(--green)' },
                ].map((t) => (
                <div key={t.text} className={`${styles.tipCard} hover-lift`} onClick={() => setInput(t.text)}>
                  <span className="icon-glow" style={{ color: t.color, background: t.color + '22', border: `1px solid ${t.color}33` }}>
                    <t.Icon size={22} color={t.color} />
                  </span>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.text}</span>
                </div>
              ))}
              </div>
            </div>
          )}

          {/* Chat stream */}
          {chatMode && (
            <div className={styles.chatStream} id="chat-stream">
              <div className={styles.chatTopBar}>
                <span className={`${styles.connStatus}`}>
                  <span className={connected ? 'status-pulse status-pulse-green' : styles.offlineDot} />
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {connected ? 'AI Connected' : 'Connecting...'}
                  </span>
                </span>
                <select
                  id="search-mode-select"
                  className={styles.modeSelect}
                  value={searchMode}
                  onChange={(e) => setSearchMode(e.target.value)}
                >
                  {SEARCH_MODES.map((m) => (
                    <option key={m} value={m}>{m} Search</option>
                  ))}
                </select>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setChatMode(false)}
                  title="Back to dashboard"
                >
                  ← Dashboard
                </button>
              </div>

              <div className={styles.messagesArea}>
                {messages.map((m, i) => <MessageBubble key={i} msg={m} />)}
                {typing && <TypingIndicator />}
                <div ref={chatEndRef} />
              </div>
            </div>
          )}

          {/* Sticky Input Bar */}
          <div className={styles.inputBar} id="chat-input-bar">
            {recording && <WaveformBars active />}
            <button
              id="mic-btn"
              className={`${styles.micBtn} ${recording ? styles.micBtnActive : ''} icon-glow`}
              style={{ color: recording ? 'var(--blue)' : 'var(--text-secondary)' }}
              onClick={toggleRecording}
              title={recording ? 'Stop recording' : 'Voice query'}
            >
              <MicIcon size={19} color={recording ? 'var(--blue)' : 'var(--text-secondary)'} />
            </button>
            <textarea
              id="chat-input"
              className={styles.chatInput}
              placeholder="Ask a legal question or describe your situation..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={1}
              onFocus={() => input.trim() && setChatMode(true)}
            />
            <button
              id="send-btn"
              className={`btn btn-amber ${styles.sendBtn} btn-ripple`}
              onClick={sendMessage}
              disabled={!input.trim()}
            >
              <SendIcon size={17} color="#0B0F19" />
            </button>
          </div>
        </div>

        {/* ====== RIGHT: SIDEBAR ====== */}
        <div className={`${styles.sidebar} ${chatMode ? styles.sidebarVisible : ''}`}>
          {/* Verified Lawyers */}
          <div className={styles.sideSection}>
            <div className={styles.sideSectionTitle}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldCheckIcon size={16} color="var(--green)" />
                <span>Verified Advocates</span>
              </div>
              <span className="badge badge-green">Live</span>
            </div>
            {lawyers.map((l) => (
              <div key={l.id} className={styles.lawyerCard}>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <div className={styles.lawyerAvatar}>
                    {l.name.split(' ')[1]?.[0] ?? 'A'}
                    {l.online && <span className={styles.onlineDot} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className={styles.lawyerName}>{l.name}</div>
                    <div className={styles.lawyerDomains}>
                      {l.domains.map((d) => (
                        <span key={d} className="badge badge-amber" style={{ fontSize: '0.65rem' }}>{d}</span>
                      ))}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      {l.exp} yrs experience
                    </div>
                  </div>
                </div>
                <button
                  id={`consult-lawyer-${l.id}`}
                  className="btn btn-amber btn-sm btn-full"
                  style={{ marginTop: '0.75rem' }}
                  onClick={() => toast(`Connecting to ${l.name}...`, 'info')}
                >
                  Consult Now
                </button>
              </div>
            ))}
          </div>

          {/* Saved Transcripts */}
          <div className={styles.sideSection}>
            <div className={styles.sideSectionTitle}>
              <span>📁 Saved Sessions</span>
              <button
                className="btn btn-ghost btn-xs"
                onClick={() => {
                  setSessionId(null);
                  setMessages([]);
                  setChatMode(false);
                  toast('Started new LexAI chat session', 'info');
                }}
                style={{ fontSize: '0.7rem', padding: '0.1rem 0.3rem', height: 'auto', border: '1px solid rgba(255,255,255,0.1)' }}
              >
                + New
              </button>
            </div>
            {sessionsList.length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>
                No active sessions.
              </div>
            ) : (
              sessionsList.map((s) => {
                const id = typeof s === 'string' ? s : s.id;
                const isActive = sessionId === id;
                return (
                  <div
                    key={id}
                    className={`${styles.sessionItem} ${isActive ? styles.sessionItemActive : ''}`}
                    onClick={async () => {
                      setSessionId(id);
                      setChatMode(true);
                      try {
                        const sessionSnap = await getDoc(doc(db, 'sessions', id));
                        if (sessionSnap.exists() && sessionSnap.data().messages) {
                          setMessages(sessionSnap.data().messages);
                        } else {
                          setMessages([]);
                        }
                        toast(`Loaded session`, 'success');
                      } catch (err) {
                        toast(`Error loading session`, 'error');
                      }
                    }}
                    style={{ cursor: 'pointer', marginBottom: '0.25rem' }}
                  >
                    <span style={{ fontSize: '0.8rem', color: isActive ? 'var(--amber)' : 'var(--text-secondary)' }}>
                      Session: {id}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
