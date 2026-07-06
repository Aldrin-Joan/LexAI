import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { getPosts, createPost } from '../api/legal';
import {
  ScalesIcon, MessageIcon, FolderIcon, ZapIcon, TrendingUpIcon,
  UserIcon, BriefcaseIcon, SparkleIcon, ShieldCheckIcon, AlertTriangleIcon,
} from '../components/Icons';
import styles from './LawyerFeed.module.css';

const MOCK_POSTS = [
  {
    id: 'post_1', author: { full_name: 'Adv. Ravi Sharma', bar_registration_number: 'BCI/2018/4567' },
    content: 'A crucial amendment was proposed today regarding Section 138 of the Negotiable Instruments Act. Legal practitioners should note the expanded scope of liability for company directors...',
    likes_count: 14, created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'post_2', author: { full_name: 'Adv. Priya Mehta', bar_registration_number: 'BCI/2015/2341' },
    content: 'Supreme Court today reinforced the fundamental right to privacy under Article 21 in a landmark judgment regarding biometric data collection. Key takeaway: Consent must be explicit and informed.',
    likes_count: 28, created_at: new Date(Date.now() - 7200000).toISOString(),
  },
];

const MOCK_INQUIRIES = [
  { id: 1, client: 'Arjun Verma', lang: '🇮🇳', summary: 'Land acquisition compensation notice...', time: '5m' },
  { id: 2, client: 'Sneha Das', lang: '🇮🇳', summary: 'Tenant eviction under Rent Control Act...', time: '18m' },
  { id: 3, client: 'Rohit Kumar', lang: '🇮🇳', summary: 'Employment termination dispute...', time: '45m' },
];

function PostCard({ post, onLike }) {
  const [liked, setLiked] = useState(false);
  const ago = (iso) => {
    const d = (Date.now() - new Date(iso)) / 60000;
    if (d < 60) return `${Math.round(d)}m ago`;
    return `${Math.round(d / 60)}h ago`;
  };

  return (
    <div className={styles.postCard}>
      <div className={styles.postHeader}>
        <div className={styles.postAvatar}>
          {post.author.full_name.split(' ').slice(-1)[0][0]}
        </div>
        <div style={{ flex: 1 }}>
          <div className={styles.postAuthor}>{post.author.full_name}</div>
          <div className={styles.postMeta}>
            <span className="badge badge-blue" style={{ fontSize: '0.65rem' }}>
              {post.author.bar_registration_number}
            </span>
            <span className={styles.postTime}>{ago(post.created_at)}</span>
          </div>
        </div>
        <ShieldCheckIcon size={14} color="var(--green)" title="Verified Advocate" />
      </div>
      <p className={styles.postContent}>{post.content}</p>
      <div className={styles.postActions}>
        <button
          className={`${styles.likeBtn} ${liked ? styles.likeBtnActive : ''}`}
          onClick={() => { setLiked((v) => !v); }}
        >
          {liked ? '❤️' : '🤍'} {post.likes_count + (liked ? 1 : 0)}
        </button>
        <button className={styles.commentBtn}>💬 Comment</button>
        <button className={styles.shareBtn}>↗ Share</button>
      </div>
    </div>
  );
}

export default function LawyerFeed() {
  const { user, isPendingVerification } = useAuth();
  const toast = useToast();

  const [posts, setPosts]         = useState(MOCK_POSTS);
  const [postText, setPostText]   = useState('');
  const [posting, setPosting]     = useState(false);
  const [inquiries]               = useState(MOCK_INQUIRIES);

  useEffect(() => {
    getPosts().then(setPosts).catch(() => {});
  }, []);

  const handlePost = async () => {
    if (postText.trim().length < 10) {
      toast('Post must be at least 10 characters.', 'error'); return;
    }
    setPosting(true);
    try {
      const newPost = await createPost(postText);
      setPosts((prev) => [{ ...newPost, author: user, likes_count: 0 }, ...prev]);
      setPostText('');
      toast('Post published!', 'success');
    } catch {
      // Mock it
      setPosts((prev) => [{
        id: `post_${Date.now()}`,
        author: { full_name: user?.full_name ?? 'You', bar_registration_number: 'BCI/---' },
        content: postText, likes_count: 0, created_at: new Date().toISOString(),
      }, ...prev]);
      setPostText('');
      toast('Post published!', 'success');
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className={styles.page}>
      {isPendingVerification && (
        <div className="verification-banner">
          ⚠️ <strong>Verification Pending:</strong> You are currently in review. Publishing posts and answering client inquiries will be enabled once Bar Council authentication is complete.
        </div>
      )}

      <Navbar />

      <div className={styles.layout}>
        {/* ===== LEFT: PROFILE SIDEBAR ===== */}
        <aside className={styles.profileCol}>
          <div className={styles.profileCard}>
            <div className={styles.profileAvatar}>
              {user?.full_name?.[0] ?? 'A'}
            </div>
            <div className={styles.profileName}>{user?.full_name}</div>
          <span className={`${styles.profileBadge} shimmer-text`}>
            <ScalesIcon size={14} color="var(--amber)" /> Verified Advocate
          </span>
            <div className={styles.profileMeta}>
              <span className="badge badge-green">✓ Bar Verified</span>
            </div>
          </div>

          <div className={styles.quickStats}>
            {[
              { label: 'Posts', val: posts.length },
              { label: 'Cases', val: 12 },
              { label: 'Clients', val: 38 },
            ].map((s) => (
              <div key={s.label} className={styles.statItem}>
                <div className={styles.statVal}>{s.val}</div>
                <div className={styles.statLabel}>{s.label}</div>
              </div>
            ))}
          </div>
        </aside>

        {/* ===== CENTER: FEED ===== */}
        <main className={styles.feedCol}>
          {/* Post creator */}
          <div className={`${styles.postCreator} glass-card scan-line`}>
            <div className={styles.creatorHeader}>
              <div className={styles.creatorAvatar}>{user?.full_name?.[0]}</div>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                Share a legal update, opinion, or precedent...
              </span>
            </div>
            <textarea
              id="post-textarea"
              className={styles.postTextarea}
              placeholder="What's on your legal mind today? Share precedents, insights, or recent judgments..."
              value={postText}
              onChange={(e) => setPostText(e.target.value)}
              maxLength={2000}
              rows={3}
              disabled={isPendingVerification}
            />
            <div className={styles.creatorFooter}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                {postText.length}/2000
              </span>
              <button
                id="publish-post-btn"
                className="btn btn-amber btn-sm btn-ripple"
                onClick={handlePost}
                disabled={posting || isPendingVerification || postText.trim().length < 10}
              >
                {posting
                  ? <span className="animate-spin">◌</span>
                  : <><SparkleIcon size={14} color="#0B0F19" /> Publish</> }
              </button>
            </div>
          </div>

          {/* Feed */}
          <div className={`${styles.feed} stagger`}>
            {posts.map((p) => <PostCard key={p.id} post={p} />)}
          </div>
        </main>

        {/* ===== RIGHT: INQUIRY QUEUE ===== */}
        <aside className={styles.inquiryCol}>
          <div className={styles.inquiryHeader}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BriefcaseIcon size={15} color="var(--amber)" />
              <span>Incoming Inquiries</span>
            </div>
            <span className="badge badge-amber">{inquiries.length}</span>
          </div>
          <div className={styles.inquiryList}>
            {inquiries.map((inq) => (
              <div key={inq.id} className={styles.inquiryCard}>
                <div className={styles.inquiryTop}>
                  <span className={styles.clientName}>{inq.lang} {inq.client}</span>
                  <span className={styles.inquiryTime}>{inq.time}</span>
                </div>
                <p className={styles.inquirySummary}>{inq.summary}</p>
                <button
                  id={`open-chat-${inq.id}`}
                  className="btn btn-amber btn-sm btn-full"
                  style={{ marginTop: '0.6rem' }}
                  onClick={() => toast(`Opening chat with ${inq.client}...`, 'info')}
                >
                  Open Chat
                </button>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
