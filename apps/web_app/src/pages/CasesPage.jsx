/**
 * CasesPage — case management for clients and advocates.
 *
 * Clients see their consultation timeline with live stage progress.
 * Advocates see incoming requests with accept/decline actions and a
 * stage advancement dropdown for accepted cases.
 *
 * All data is fetched from the backend on mount and after every
 * state-changing action (accept, decline, stage update). Mock data
 * is only used as a fallback if the API is unreachable.
 */

import React, { useState, useEffect, useCallback } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import {
  getCases,
  submitCaseRequest,
  resolveCase,
  updateCaseStage,
  getPosts,
} from '../api/legal';
import styles from './CasesPage.module.css';

// ---------------------------------------------------------------------------
// Stage metadata
// ---------------------------------------------------------------------------

const STAGE_LABELS = {
  submitted: 'Request Sent',
  accepted: 'Accepted by Advocate',
  in_review: 'Case File Review',
  advice_drafted: 'Legal Advice Ready',
  completed: 'Completed',
  declined: 'Declined',
};

const STAGE_COLORS = {
  submitted: 'badge-amber',
  accepted: 'badge-blue',
  in_review: 'badge-blue',
  advice_drafted: 'badge-purple',
  completed: 'badge-green',
  declined: 'badge-red',
};

const TIMELINE_STAGES = [
  'submitted',
  'accepted',
  'in_review',
  'advice_drafted',
  'completed',
];

// ---------------------------------------------------------------------------
// Mock lawyers directory (sidebar — will connect to GET /legal/lawyers later)
// ---------------------------------------------------------------------------

const MOCK_LAWYERS = [
  { id: 1, name: 'Adv. Ravi Sharma',  domains: ['Criminal Law', 'Constitutional Law'], exp: 8,  online: true },
  { id: 2, name: 'Adv. Priya Mehta',  domains: ['Corporate Law', 'Tax Law'],           exp: 12, online: true },
  { id: 3, name: 'Adv. Suresh Nair',  domains: ['Family Law', 'Civil Law'],             exp: 5,  online: false },
  { id: 4, name: 'Adv. Kavitha Iyer', domains: ['Property Law', 'Labour Law'],          exp: 9,  online: true },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ClientTimeline({ c }) {
  const stageIdx = TIMELINE_STAGES.indexOf(c.current_stage);
  return (
    <div className={styles.caseCard}>
      <div className={styles.caseCardHeader}>
        <div>
          <div className={styles.caseTitle}>Case #{c.id}</div>
          <div className={styles.caseLawyer}>👨‍⚖️ {c.lawyer_name}</div>
          <p className={styles.caseSummary}>{c.summary}</p>
        </div>
        <span className={`badge ${STAGE_COLORS[c.status] || 'badge-amber'}`}>
          {STAGE_LABELS[c.status] || c.status}
        </span>
      </div>

      {c.status !== 'declined' && (
        <div className={styles.timeline}>
          {TIMELINE_STAGES.map((stage, i) => (
            <React.Fragment key={stage}>
              <div className={styles.timelineItem}>
                <div
                  className={`${styles.timelineNode} ${
                    i < stageIdx
                      ? styles.nodeComplete
                      : i === stageIdx
                      ? styles.nodeActive
                      : styles.nodePending
                  }`}
                >
                  {i < stageIdx ? '✓' : i + 1}
                </div>
                <div className={styles.nodeLabel}>{STAGE_LABELS[stage]}</div>
              </div>
              {i < TIMELINE_STAGES.length - 2 && (
                <div
                  className={`${styles.timelineLine} ${
                    i < stageIdx ? styles.lineComplete : ''
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      )}

      <div className={styles.caseDate}>
        Filed: {new Date(c.created_at).toLocaleDateString()}
      </div>
    </div>
  );
}

function LawyerInquiryCard({ inq, onAccept, onDecline, onStageChange }) {
  const [localStatus, setLocalStatus] = useState(inq.status);
  const [stage, setStage]             = useState(inq.current_stage || 'submitted');
  const [dismissed, setDismissed]     = useState(false);

  if (dismissed) return null;

  return (
    <div className={styles.caseCard}>
      <div className={styles.caseCardHeader}>
        <div>
          <div className={styles.caseTitle}>👤 {inq.client_name}</div>
          <p className={styles.caseSummary}>{inq.summary}</p>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {new Date(inq.created_at).toLocaleDateString()}
          </div>
        </div>
        <span className={`badge ${STAGE_COLORS[localStatus] || 'badge-amber'}`}>
          {STAGE_LABELS[localStatus] || localStatus}
        </span>
      </div>

      {localStatus === 'submitted' && (
        <div className={styles.actionRow}>
          <button
            id={`accept-${inq.id}`}
            className="btn btn-success btn-sm"
            onClick={async () => {
              await onAccept(inq.id);
              setLocalStatus('accepted');
              setStage('accepted');
            }}
          >
            ✓ Accept Request
          </button>
          <button
            id={`decline-${inq.id}`}
            className="btn btn-danger btn-sm"
            onClick={async () => {
              await onDecline(inq.id);
              setDismissed(true);
            }}
          >
            ✕ Decline
          </button>
        </div>
      )}

      {localStatus === 'accepted' && (
        <div className={styles.stageRow}>
          <label className="form-label">Update Stage:</label>
          <select
            className={styles.stageSelect}
            value={stage}
            onChange={async (e) => {
              const s = e.target.value;
              setStage(s);
              await onStageChange(inq.id, s);
              if (s === 'completed') setLocalStatus('completed');
            }}
          >
            <option value="accepted">Accepted</option>
            <option value="in_review">Mark as In Review</option>
            <option value="advice_drafted">Upload Advice Brief</option>
            <option value="completed">Mark Completed</option>
          </select>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function CasesPage() {
  const { user, token, isLawyer } = useAuth();
  const toast = useToast();

  const [cases, setCases]     = useState([]);
  const [loading, setLoading] = useState(true);

  /** Fetch cases from the backend and update state. */
  const loadCases = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await getCases(token);
      setCases(data);
    } catch (err) {
      console.warn('getCases API error, using empty list:', err);
      setCases([]);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  // --- Actions ---

  const handleAccept = async (caseId) => {
    try {
      await resolveCase(token, caseId, 'accept');
      toast('Case accepted!', 'success');
      loadCases();
    } catch (err) {
      toast(err?.response?.data?.detail || 'Failed to accept case.', 'error');
    }
  };

  const handleDecline = async (caseId) => {
    try {
      await resolveCase(token, caseId, 'decline');
      toast('Case declined.', 'info');
      loadCases();
    } catch (err) {
      toast(err?.response?.data?.detail || 'Failed to decline case.', 'error');
    }
  };

  const handleStageChange = async (caseId, stage) => {
    try {
      await updateCaseStage(token, caseId, stage);
      toast(`Stage updated to "${STAGE_LABELS[stage] || stage}"`, 'success');
      loadCases();
    } catch (err) {
      toast(
        err?.response?.data?.detail || 'Stage transition not permitted.',
        'error',
      );
    }
  };

  // --- Consult shortcut (client sidebar) ---
  const handleRequestConsult = async (lawyer) => {
    if (!token) return;
    const summary = prompt(
      `Briefly describe your situation for ${lawyer.name}:`,
    );
    if (!summary || summary.trim().length < 10) {
      toast('Please provide at least 10 characters.', 'error');
      return;
    }
    try {
      await submitCaseRequest(token, {
        lawyerId: `lawyer-${lawyer.id}`, // placeholder — real UID once lawyer dir is live
        lawyerName: lawyer.name,
        querySummary: summary,
      });
      toast(`Consultation request sent to ${lawyer.name}!`, 'success');
      loadCases();
    } catch (err) {
      toast(
        err?.response?.data?.detail || 'Failed to submit request.',
        'error',
      );
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className={styles.page}>
      <Navbar />
      <div className={styles.layout}>

        {/* ===== MAIN CONTENT ===== */}
        <main className={styles.main}>
          <div className={styles.pageHeader}>
            <h1 className={styles.pageTitle}>
              {isLawyer ? '📋 Case Inquiries' : '⚖️ My Cases'}
            </h1>
            <p className={styles.pageSub}>
              {isLawyer
                ? 'Manage incoming consultation requests and track active case progress.'
                : 'Track your consultation requests and case progress with verified advocates.'}
            </p>
          </div>

          {loading ? (
            <div style={{ color: 'var(--text-muted)', padding: '2rem 0' }}>
              Loading cases…
            </div>
          ) : cases.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', padding: '2rem 0' }}>
              {isLawyer
                ? 'No pending inquiries.'
                : 'You have no active cases. Use the sidebar to request a consult.'}
            </div>
          ) : (
            <div className={styles.caseList}>
              {isLawyer
                ? cases.map((c) => (
                    <LawyerInquiryCard
                      key={c.id}
                      inq={c}
                      onAccept={handleAccept}
                      onDecline={handleDecline}
                      onStageChange={handleStageChange}
                    />
                  ))
                : cases.map((c) => <ClientTimeline key={c.id} c={c} />)}
            </div>
          )}
        </main>

        {/* ===== SIDEBAR: LAWYER DIRECTORY (client only) ===== */}
        {!isLawyer && (
          <aside className={styles.directory}>
            <div className={styles.dirHeader}>🛡️ Find Advocates</div>
            <input
              className="glass-input"
              placeholder="Filter by domain…"
              style={{ marginBottom: '1rem' }}
            />
            <div className={styles.lawyerGrid}>
              {MOCK_LAWYERS.map((l) => (
                <div key={l.id} className={styles.lawyerCard}>
                  <div className={styles.lawyerTop}>
                    <div className={styles.lawyerAvatar}>
                      {l.name.split(' ')[1][0]}
                      {l.online && <span className={styles.onlineDot} />}
                    </div>
                    <div>
                      <div className={styles.lawyerName}>{l.name}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {l.exp} yrs
                      </div>
                    </div>
                  </div>
                  <div className={styles.lawyerDomains}>
                    {l.domains.map((d) => (
                      <span key={d} className="badge badge-amber" style={{ fontSize: '0.65rem' }}>
                        {d}
                      </span>
                    ))}
                  </div>
                  <button
                    id={`consult-${l.id}`}
                    className="btn btn-amber btn-sm btn-full"
                    style={{ marginTop: '0.75rem' }}
                    onClick={() => handleRequestConsult(l)}
                  >
                    Request Consult
                  </button>
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
