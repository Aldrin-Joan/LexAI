import React, { useState, useEffect, useRef } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { wsManager } from '../api/ws';
import {
  PaperclipIcon, SendIcon, SearchIcon, ScalesIcon,
  MessageIcon, UserIcon,
} from '../components/Icons';
import styles from './InboxPage.module.css';

const MOCK_CONTACTS = [
  {
    id: 'ai', name: '⚖️ LexAI Assistant', lastMsg: 'How can I help you with legal research?',
    unread: 0, online: true, time: 'now',
  },
  {
    id: 'adv1', name: 'Adv. Ravi Sharma', lastMsg: 'I have reviewed your case documents.',
    unread: 2, online: true, time: '3m',
  },
  {
    id: 'adv2', name: 'Adv. Priya Mehta', lastMsg: 'Your appointment is confirmed for tomorrow.',
    unread: 0, online: false, time: '1h',
  },
];

const MOCK_HISTORY = {
  ai: [
    { id: 1, sender: 'ai',   text: 'Hello! I am your AI legal assistant. Ask me anything about Indian law.',  ts: Date.now() - 120000 },
    { id: 2, sender: 'user', text: 'What is Section 302 IPC?', ts: Date.now() - 100000 },
    { id: 3, sender: 'ai',   text: 'Section 302 of the Indian Penal Code deals with punishment for murder. It provides for death or imprisonment for life, along with a fine.', ts: Date.now() - 98000 },
  ],
  adv1: [
    { id: 1, sender: 'ai',   text: 'I have reviewed your case documents. The ownership transfer clause in Section 4 is ambiguous.', ts: Date.now() - 600000 },
  ],
  adv2: [
    { id: 1, sender: 'ai',   text: 'Your appointment is confirmed for tomorrow at 11:00 AM.', ts: Date.now() - 3600000 },
  ],
};

export default function InboxPage() {
  const { user, token } = useAuth();
  const [activeId, setActiveId]   = useState('ai');
  const [messages, setMessages]   = useState(MOCK_HISTORY['ai']);
  const [contacts, setContacts]   = useState(MOCK_CONTACTS);
  const [input, setInput]         = useState('');
  const [typing, setTyping]       = useState(false);
  const [connected, setConnected] = useState(false);
  const [search, setSearch]       = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    wsManager.connect(`/ws/chat/${user?.id || 1}`, token);
    const offOpen  = wsManager.on('open',  () => setConnected(true));
    const offClose = wsManager.on('close', () => setConnected(false));
    const offMsg   = wsManager.on('message', (data) => {
      setTyping(false);
      const text = data.raw ?? data.content ?? JSON.stringify(data);
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), sender: 'ai', text, ts: Date.now() },
      ]);
    });
    return () => { offOpen(); offClose(); offMsg(); wsManager.disconnect(); };
  }, [user, token]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  const selectContact = (c) => {
    setActiveId(c.id);
    setMessages(MOCK_HISTORY[c.id] || []);
    setContacts((prev) => prev.map((x) => x.id === c.id ? { ...x, unread: 0 } : x));
  };

  const sendMsg = () => {
    if (!input.trim()) return;
    const text = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { id: Date.now(), sender: 'user', text, ts: Date.now() }]);
    if (activeId === 'ai') {
      setTyping(true);
      if (wsManager.isOpen) {
        wsManager.send(text);
      } else {
        setTimeout(() => {
          setTyping(false);
          setMessages((prev) => [
            ...prev,
            { id: Date.now(), sender: 'ai', text: 'Thank you for your query. Let me analyze the relevant legal provisions for you.', ts: Date.now() },
          ]);
        }, 1600);
      }
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); }
    if (e.key !== 'Enter') {
      // typing indicator
      wsManager.send({ action: 'typing', receiver_id: activeId });
    }
  };

  const activeContact = contacts.find((c) => c.id === activeId);
  const filteredContacts = contacts.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  const ago = (ts) => {
    const d = (Date.now() - ts) / 60000;
    if (d < 1) return 'just now';
    if (d < 60) return `${Math.round(d)}m`;
    return `${Math.round(d / 60)}h`;
  };

  return (
    <div className={styles.page}>
      <Navbar />
      <div className={styles.workspace}>

        {/* ===== CONTACTS PANEL ===== */}
        <aside className={styles.contacts}>
          <div className={styles.searchWrap}>
            <input
              id="inbox-search"
              className={`glass-input ${styles.searchInput}`}
              placeholder="🔍 Search conversations..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className={styles.contactList}>
            {filteredContacts.map((c) => (
              <div
                key={c.id}
                id={`contact-${c.id}`}
                className={`${styles.contactItem} ${activeId === c.id ? styles.contactActive : ''}`}
                onClick={() => selectContact(c)}
              >
                <div className={styles.contactAvatar}>
                  {c.name.replace('⚖️ ', '')[0]}
                  {c.online && <span className={styles.onlineDot} />}
                </div>
                <div className={styles.contactInfo}>
                  <div className={styles.contactName}>{c.name}</div>
                  <div className={styles.contactLastMsg}>{c.lastMsg}</div>
                </div>
                <div className={styles.contactMeta}>
                  <span className={styles.contactTime}>{c.time}</span>
                  {c.unread > 0 && (
                    <span className={styles.unreadBadge}>{c.unread}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* ===== CHAT PANEL ===== */}
        <main className={styles.chatPanel}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatAvatar}>
              {activeContact?.name.replace('⚖️ ', '')[0]}
              {activeContact?.online && <span className={styles.chatOnlineDot} />}
            </div>
            <div>
              <div className={styles.chatName}>{activeContact?.name}</div>
              <div className={styles.chatStatus}>
                {activeId === 'ai' ? (
                  <span className="badge badge-blue" style={{ fontSize: '0.68rem' }}>
                    {connected ? '🟢 AI Connected' : '🔴 Disconnected'}
                  </span>
                ) : (
                  <span style={{ fontSize: '0.75rem', color: activeContact?.online ? 'var(--green)' : 'var(--text-muted)' }}>
                    {activeContact?.online ? 'Online' : 'Offline'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className={styles.messages}>
            {messages.map((m) => {
              const isUser = m.sender === 'user';
              return (
                <div key={m.id} className={`${styles.msg} ${isUser ? styles.msgUser : styles.msgAI}`}>
                  {!isUser && <div className={styles.msgSender}>{activeContact?.name}</div>}
                  <div className={`${styles.msgBubble} ${isUser ? styles.msgBubbleUser : styles.msgBubbleAI}`}>
                    {m.text}
                  </div>
                  <div className={styles.msgTime}>{ago(m.ts)}</div>
                </div>
              );
            })}
            {typing && (
              <div className={`${styles.msg} ${styles.msgAI}`}>
                <div className={`${styles.msgBubble} ${styles.msgBubbleAI}`} style={{ padding: '0.75rem 1rem' }}>
                  <div className={styles.typingDots}>
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className={styles.inputRow}>
            <button className={`${styles.inputRow} btn btn-glass btn-sm icon-glow`} style={{ padding: '0.5rem' }} title="Attach file">
              <PaperclipIcon size={17} color="var(--text-secondary)" />
            </button>
            <textarea
              id="inbox-input"
              className={styles.msgInput}
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={1}
            />
            <button
              id="inbox-send-btn"
              className="btn btn-amber btn-sm btn-ripple"
              onClick={sendMsg}
              disabled={!input.trim()}
              style={{ borderRadius: '50%', width: 40, height: 40, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              <SendIcon size={16} color="#0B0F19" />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
