import React, { useState, useEffect, useRef, useCallback } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { askLexAI } from '../api/legal';
import {
  collection, query, where, orderBy, getDocs, doc, setDoc, updateDoc, arrayUnion, getDoc
} from 'firebase/firestore';
import { db } from '../api/firebase';
import {
  MicIcon, SendIcon, SparkleIcon, ScalesIcon,
} from '../components/Icons';
import styles from './LexAIChatPage.module.css';

const SEARCH_MODES = ['Keyword', 'Semantic', 'Hybrid', 'Ultra'];

function CitationPill({ text }) {
  return <span className="citation-pill">{text}</span>;
}

function parseCitations(text) {
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

export default function LexAIChatPage() {
  const { user } = useAuth();
  const toast = useToast();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [searchMode, setSearchMode] = useState('Hybrid');
  const [sessionId, setSessionId] = useState(null);
  const [sessionsList, setSessionsList] = useState([]);

  // Voice recording mock state
  const [recording, setRecording] = useState(false);

  const chatEndRef = useRef(null);

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

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || !user?.uid) return;
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
        text: data.answer || 'No answer returned.',
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
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleRecording = () => {
    if (recording) {
      setRecording(false);
      toast('Voice recording stopped.', 'info');
    } else {
      setRecording(true);
      toast('Voice query recording started...', 'info');
      setTimeout(() => {
        setRecording(false);
        setInput('What is Article 21 of the Constitution of India?');
      }, 2000);
    }
  };

  return (
    <div className={styles.page}>
      <Navbar />

      <div className={styles.layout}>
        {/* ====== LEFT SIDEBAR: SAVED SESSIONS ====== */}
        <aside className={styles.sidebar}>
          <div className={styles.sidebarTitle}>
            <span>📁 Active Sessions</span>
            <button
              className="btn btn-ghost btn-xs"
              onClick={() => {
                setSessionId(null);
                setMessages([]);
                toast('Started new LexAI chat session', 'info');
              }}
              style={{ fontSize: '0.7rem', border: '1px solid rgba(255,255,255,0.1)' }}
            >
              + New
            </button>
          </div>
          <div className={styles.sessionsList}>
            {sessionsList.length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>
                No active sessions found.
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
                  >
                    <span className={styles.sessionName}>
                      Session: {id}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* ====== CHAT PANEL ====== */}
        <main className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <div className={styles.headerTitle}>
              <SparkleIcon size={18} color="var(--amber)" />
              <span>LexAI <span>Legal Assistant</span></span>
            </div>
            <select
              className={styles.modeSelect}
              value={searchMode}
              onChange={(e) => setSearchMode(e.target.value)}
            >
              {SEARCH_MODES.map((m) => (
                <option key={m} value={m}>{m} Search Mode</option>
              ))}
            </select>
          </div>

          <div className={styles.messagesArea}>
            {messages.length === 0 ? (
              <div className={styles.greeting}>
                <div className={styles.greetIconWrap}>
                  <ScalesIcon size={30} color="var(--amber)" />
                </div>
                <h1 className={styles.greetTitle}>
                  Hello, <span>{user?.full_name?.split(' ')[0] || 'Advocate'}</span>
                </h1>
                <p className={styles.greetSub}>
                  Welcome to LexAI. Ask any legal research questions, find precedents, or analyze statutes. Your conversation is secure and grounded in supreme court judgements.
                </p>
              </div>
            ) : (
              messages.map((m, i) => <MessageBubble key={i} msg={m} />)
            )}
            {typing && <TypingIndicator />}
            <div ref={chatEndRef} />
          </div>

          {/* Sticky Input Bar at Bottom */}
          <div className={styles.inputBarContainer}>
            <div className={styles.inputBar}>
              <button
                className={`${styles.micBtn} ${recording ? styles.micBtnActive : ''}`}
                onClick={toggleRecording}
                title="Voice query"
              >
                <MicIcon size={18} />
              </button>
              <textarea
                className={styles.chatInput}
                placeholder="Ask LexAI a legal question..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKey}
                rows={1}
              />
              <button
                className={styles.sendBtn}
                onClick={sendMessage}
                disabled={!input.trim()}
              >
                <SendIcon size={16} />
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
