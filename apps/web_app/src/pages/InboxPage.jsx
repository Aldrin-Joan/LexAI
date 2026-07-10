/**
 * InboxPage — real-time messaging between clients and advocates.
 *
 * - Selecting a contact loads their message history via GET /legal/chat/history.
 * - Sending a message first attempts delivery over the WebSocket.
 *   If the socket is disconnected, it falls back to POST /legal/chat/send.
 * - Messages are deduplicated by client_msg_id so that a page refresh or
 *   history fetch after a REST fallback never shows the same message twice.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { wsManager } from '../api/ws';
import { getCases, getChatHistory, sendChatMessage } from '../api/legal';
import {
  PaperclipIcon, SendIcon, SearchIcon,
  MessageIcon, UserIcon,
} from '../components/Icons';
import styles from './InboxPage.module.css';



// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const ago = (ts) => {
  const d = (Date.now() - ts) / 60000;
  if (d < 1) return 'just now';
  if (d < 60) return `${Math.round(d)}m`;
  return `${Math.round(d / 60)}h`;
};

/**
 * Merge an incoming message into the current list, deduplicating by
 * client_msg_id. Returns the existing list unchanged if a message with
 * the same id is already present.
 *
 * @param {Array} prev - Existing messages array.
 * @param {object} msg - Incoming message object.
 * @returns {Array} Updated messages array.
 */
function dedupeAppend(prev, msg) {
  if (!msg.client_msg_id) return [...prev, msg];
  if (prev.some((m) => m.client_msg_id === msg.client_msg_id)) return prev;
  return [...prev, msg];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function InboxPage() {
  const { user, token } = useAuth();
  const toast = useToast();

  const [activeId, setActiveId]     = useState('ai');
  const [messages, setMessages]     = useState([]);
  const [contacts, setContacts]     = useState([]);
  const [input, setInput]           = useState('');
  const [typing, setTyping]         = useState(false);
  const [connected, setConnected]   = useState(false);
  const [search, setSearch]         = useState('');
  const [historyLoading, setHistoryLoading] = useState(false);

  const chatEndRef = useRef(null);

  // ---------------------------------------------------------------------------
  // Load Contacts list dynamically from active cases
  // ---------------------------------------------------------------------------

  const loadContacts = useCallback(async () => {
    if (!token) return;
    try {
      const casesData = await getCases(token);
      const uniqueContacts = new Map();

      // Ensure LexAI is always available as the first contact
      uniqueContacts.set('ai', {
        id: 'ai',
        name: '⚖️ LexAI Assistant',
        lastMsg: 'How can I help you with legal research?',
        unread: 0,
        online: true,
        time: 'now',
      });

      casesData.forEach((c) => {
        // For client, show lawyer as contact; for advocate, show client.
        const contactId = user?.isLawyer ? c.client_id : c.lawyer_id;
        const contactName = user?.isLawyer ? c.client_name : c.lawyer_name;

        if (contactId && !uniqueContacts.has(contactId)) {
          uniqueContacts.set(contactId, {
            id: contactId,
            name: contactName,
            lastMsg: c.summary,
            unread: 0,
            online: true,
            time: ago(new Date(c.created_at).getTime()),
          });
        }
      });

      setContacts(Array.from(uniqueContacts.values()));
    } catch (err) {
      console.warn('Failed to load active case contacts:', err);
    }
  }, [token, user]);

  useEffect(() => {
    loadContacts();
  }, [loadContacts]);

  // ---------------------------------------------------------------------------
  // WebSocket lifecycle
  // ---------------------------------------------------------------------------

  useEffect(() => {
    if (!user || !token) return;

    // Connect with the Firebase token for server-side verification
    wsManager.connect(`/ws/chat/${user.uid}`, token);

    const offOpen  = wsManager.on('open', () => setConnected(true));
    const offClose = wsManager.on('close', () => setConnected(false));
    const offMsg   = wsManager.on('message', (data) => {
      setTyping(false);
      const content =
        data.content ?? data.raw ?? JSON.stringify(data);
      const incomingMsg = {
        id: data.client_msg_id || Date.now(),
        client_msg_id: data.client_msg_id || null,
        sender: data.sender_id === user.uid ? 'user' : 'ai',
        text: content,
        ts: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
      };
      setMessages((prev) => dedupeAppend(prev, incomingMsg));
    });

    return () => {
      offOpen();
      offClose();
      offMsg();
      wsManager.disconnect();
    };
  }, [user, token]);

  // ---------------------------------------------------------------------------
  // Reconnect on WebSocket 4001 (session expired)
  // ---------------------------------------------------------------------------

  useEffect(() => {
    const offClose = wsManager.on('close', async () => {
      if (!user || !token) return;
      // The wsManager auto-reconnects with the same token; for a 4001
      // expiry, the AuthContext will have refreshed the token automatically
      // via Firebase's onAuthStateChanged.  The next reconnect attempt
      // in wsManager._open() will carry the new token.
    });
    return () => offClose();
  }, [user, token]);

  // ---------------------------------------------------------------------------
  // Scroll to bottom on new messages
  // ---------------------------------------------------------------------------

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  // ---------------------------------------------------------------------------
  // Load chat history when switching contacts
  // ---------------------------------------------------------------------------

  const selectContact = useCallback(
    async (c) => {
      setActiveId(c.id);
      setMessages([]);
      setContacts((prev) =>
        prev.map((x) => (x.id === c.id ? { ...x, unread: 0 } : x)),
      );

      if (c.id === 'ai') {
        // LexAI has no REST history — start fresh
        return;
      }

      if (!token) return;
      setHistoryLoading(true);
      try {
        const history = await getChatHistory(token, c.id);
        const normalised = history.map((m) => ({
          id: m.id,
          client_msg_id: m.client_msg_id,
          sender: m.sender_id === user?.uid ? 'user' : 'ai',
          text: m.content,
          ts: new Date(m.timestamp).getTime(),
        }));
        setMessages(normalised);
      } catch (err) {
        console.warn('getChatHistory failed:', err);
        toast('Could not load message history.', 'error');
      } finally {
        setHistoryLoading(false);
      }
    },
    [token, user, toast],
  );

  // ---------------------------------------------------------------------------
  // Send a message
  // ---------------------------------------------------------------------------

  const sendMsg = useCallback(async () => {
    if (!input.trim()) return;
    const text = input.trim();
    const clientMsgId = uuidv4();
    setInput('');

    const userMsg = {
      id: clientMsgId,
      client_msg_id: clientMsgId,
      sender: 'user',
      text,
      ts: Date.now(),
    };
    setMessages((prev) => dedupeAppend(prev, userMsg));

    if (activeId === 'ai') {
      // Route via WebSocket to the AI handler
      setTyping(true);
      if (wsManager.isOpen) {
        wsManager.send(
          JSON.stringify({
            receiver_id: 'ai',
            content: text,
            client_msg_id: clientMsgId,
          }),
        );
      } else {
        // Offline AI fallback
        setTimeout(() => {
          setTyping(false);
          setMessages((prev) =>
            dedupeAppend(prev, {
              id: uuidv4(),
              client_msg_id: null,
              sender: 'ai',
              text: 'Thank you for your query. Let me analyze the relevant legal provisions for you.',
              ts: Date.now(),
            }),
          );
        }, 1600);
      }
      return;
    }

    // P2P message — try WebSocket first
    if (wsManager.isOpen) {
      wsManager.send(
        JSON.stringify({
          receiver_id: activeId,
          content: text,
          client_msg_id: clientMsgId,
        }),
      );
    } else if (token) {
      // REST fallback when socket is disconnected
      try {
        const saved = await sendChatMessage(token, {
          receiverId: activeId,
          content: text,
          clientMsgId,
        });
        // Dedup is already enforced — the response will match clientMsgId
        // so dedupeAppend won't double-add it
        setMessages((prev) =>
          dedupeAppend(prev, {
            id: saved.id,
            client_msg_id: saved.client_msg_id,
            sender: 'user',
            text: saved.content,
            ts: new Date(saved.timestamp).getTime(),
          }),
        );
      } catch (err) {
        toast('Failed to send message. Please retry.', 'error');
        // Remove the optimistic message on failure
        setMessages((prev) =>
          prev.filter((m) => m.client_msg_id !== clientMsgId),
        );
      }
    }
  }, [input, activeId, token, toast]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMsg();
    }
  };

  // ---------------------------------------------------------------------------
  // Derived values
  // ---------------------------------------------------------------------------

  const activeContact = contacts.find((c) => c.id === activeId);
  const filteredContacts = contacts.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()),
  );

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

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
                className={`${styles.contactItem} ${
                  activeId === c.id ? styles.contactActive : ''
                }`}
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
              {activeContact?.online && (
                <span className={styles.chatOnlineDot} />
              )}
            </div>
            <div>
              <div className={styles.chatName}>{activeContact?.name}</div>
              <div className={styles.chatStatus}>
                {activeId === 'ai' ? (
                  <span
                    className="badge badge-blue"
                    style={{ fontSize: '0.68rem' }}
                  >
                    {connected ? '🟢 AI Connected' : '🔴 Disconnected'}
                  </span>
                ) : (
                  <span
                    style={{
                      fontSize: '0.75rem',
                      color: activeContact?.online
                        ? 'var(--green)'
                        : 'var(--text-muted)',
                    }}
                  >
                    {activeContact?.online ? 'Online' : 'Offline'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className={styles.messages}>
            {historyLoading ? (
              <div style={{ color: 'var(--text-muted)', padding: '1rem' }}>
                Loading history…
              </div>
            ) : (
              messages.map((m) => {
                const isUser = m.sender === 'user';
                return (
                  <div
                    key={m.client_msg_id || m.id}
                    className={`${styles.msg} ${
                      isUser ? styles.msgUser : styles.msgAI
                    }`}
                  >
                    {!isUser && (
                      <div className={styles.msgSender}>
                        {activeContact?.name}
                      </div>
                    )}
                    <div
                      className={`${styles.msgBubble} ${
                        isUser ? styles.msgBubbleUser : styles.msgBubbleAI
                      }`}
                    >
                      {m.text}
                    </div>
                    <div className={styles.msgTime}>{ago(m.ts)}</div>
                  </div>
                );
              })
            )}

            {typing && (
              <div className={`${styles.msg} ${styles.msgAI}`}>
                <div
                  className={`${styles.msgBubble} ${styles.msgBubbleAI}`}
                  style={{ padding: '0.75rem 1rem' }}
                >
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
            <button
              className="btn btn-glass btn-sm icon-glow"
              style={{ padding: '0.5rem' }}
              title="Attach file"
            >
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
              style={{
                borderRadius: '50%',
                width: 40,
                height: 40,
                padding: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <SendIcon size={16} color="#0B0F19" />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
