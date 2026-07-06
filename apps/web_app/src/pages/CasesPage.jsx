import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { resolveCase, updateCaseStage } from '../api/legal';
import styles from './CasesPage.module.css';

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

const MOCK_CLIENT_CASES = [
  {
    case_id: 'case_001', lawyer_name: 'Adv. Ravi Sharma',
    summary: 'Land acquisition compensation notice under Act 2013.',
    status: 'accepted', current_stage: 'in_review', created_at: '2026-07-01',
  },
  {
    case_id: 'case_002', lawyer_name: 'Adv. Priya Mehta',
    summary: 'Rental lease dispute — clause 14 contradicts Indian Contract Act.',
    status: 'submitted', current_stage: 'submitted', created_at: '2026-07-04',
  },
  {
    case_id: 'case_003', lawyer_name: 'Adv. Suresh Nair',
    summary: 'Employment termination claim under Industrial Disputes Act.',
    status: 'completed', current_stage: 'completed', created_at: '2026-06-20',
  },
];

const MOCK_LAWYER_CASES = [
  { case_id: 'inq_001', client: 'Arjun Verma', summary: 'Land acquisition under RFCTLARR 2013.', status: 'submitted', created_at: '2026-07-05' },
  { case_id: 'inq_002', client: 'Sneha Das', summary: 'Tenant eviction procedure under Rent Control Act.', status: 'submitted', created_at: '2026-07-04' },
  { case_id: 'inq_003', client: 'Rohit Kumar', summary: 'Employment termination — Section 25F ID Act.', status: 'accepted', current_stage: 'in_review', created_at: '2026-07-01' },
];

const TIMELINE_STAGES = ['submitted', 'accepted', 'in_review', 'advice_drafted', 'completed'];

function ClientTimeline({ c }) {
  const stageIdx = TIMELINE_STAGES.indexOf(c.current_stage);
  return (
    <div className={styles.caseCard}>
      <div className={styles.caseCardHeader}>
        <div>
          <div className={styles.caseTitle}>Case #{c.case_id.split('_')[1]}</div>
          <div className={styles.caseLawyer}>👨‍⚖️ {c.lawyer_name}</div>
          <p className={styles.caseSummary}>{c.summary}</p>
        </div>
        <span className={`badge ${STAGE_COLORS[c.status]}`}>{STAGE_LABELS[c.status]}</span>
      </div>

      {/* Timeline nodes */}
      {c.status !== 'declined' && (
        <div className={styles.timeline}>
          {TIMELINE_STAGES.filter(s => s !== 'declined').map((stage, i) => (
            <React.Fragment key={stage}>
              <div className={styles.timelineItem}>
                <div className={`${styles.timelineNode} ${
                  i < stageIdx ? styles.nodeComplete :
                  i === stageIdx ? styles.nodeActive : styles.nodePending
                }`}>
                  {i < stageIdx ? '✓' : i + 1}
                </div>
                <div className={styles.nodeLabel}>{STAGE_LABELS[stage]}</div>
              </div>
              {i < TIMELINE_STAGES.length - 2 && (
                <div className={`${styles.timelineLine} ${i < stageIdx ? styles.lineComplete : ''}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      )}
      <div className={styles.caseDate}>Filed: {c.created_at}</div>
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
          <div className={styles.caseTitle}>👤 {inq.client}</div>
          <p className={styles.caseSummary}>{inq.summary}</p>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{inq.created_at}</div>
        </div>
        <span className={`badge ${STAGE_COLORS[localStatus]}`}>
          {STAGE_LABELS[localStatus]}
        </span>
      </div>

      {localStatus === 'submitted' && (
        <div className={styles.actionRow}>
          <button
            id={`accept-${inq.case_id}`}
            className="btn btn-success btn-sm"
            onClick={async () => {
              await onAccept(inq.case_id);
              setLocalStatus('accepted');
            }}
          >
            ✓ Accept Request
          </button>
          <button
            id={`decline-${inq.case_id}`}
            className="btn btn-danger btn-sm"
            onClick={async () => {
              await onDecline(inq.case_id);
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
              await onStageChange(inq.case_id, s);
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

const MOCK_LAWYERS = [
  { id: 1, name: 'Adv. Ravi Sharma', domains: ['Criminal Law', 'Constitutional Law'], exp: 8, online: true },
  { id: 2, name: 'Adv. Priya Mehta', domains: ['Corporate Law', 'Tax Law'], exp: 12, online: true },
  { id: 3, name: 'Adv. Suresh Nair', domains: ['Family Law', 'Civil Law'], exp: 5, online: false },
  { id: 4, name: 'Adv. Kavitha Iyer', domains: ['Property Law', 'Labour Law'], exp: 9, online: true },
];

export default function CasesPage() {
  const { isLawyer } = useAuth();
  const toast = useToast();
  const [cases, setCases] = useState(isLawyer ? MOCK_LAWYER_CASES : MOCK_CLIENT_CASES);

  const handleAccept = async (caseId) => {
    try {
      await resolveCase(caseId, 'accept');
      toast('Case accepted!', 'success');
    } catch {
      toast('Case accepted (offline mode)', 'success');
    }
  };

  const handleDecline = async (caseId) => {
    try {
      await resolveCase(caseId, 'decline');
      toast('Case declined.', 'info');
    } catch {
      toast('Case declined (offline mode)', 'info');
    }
  };

  const handleStageChange = async (caseId, stage) => {
    try {
      await updateCaseStage(caseId, stage);
      toast(`Stage updated to "${STAGE_LABELS[stage]}"`, 'success');
    } catch {
      toast(`Stage updated (offline mode)`, 'success');
    }
  };

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

          <div className={styles.caseList}>
            {isLawyer
              ? cases.map((c) => (
                  <LawyerInquiryCard
                    key={c.case_id}
                    inq={c}
                    onAccept={handleAccept}
                    onDecline={handleDecline}
                    onStageChange={handleStageChange}
                  />
                ))
              : cases.map((c) => <ClientTimeline key={c.case_id} c={c} />)
            }
          </div>
        </main>

        {/* ===== SIDEBAR: LAWYER DIRECTORY (client only) ===== */}
        {!isLawyer && (
          <aside className={styles.directory}>
            <div className={styles.dirHeader}>🛡️ Find Advocates</div>
            <input className="glass-input" placeholder="Filter by domain..." style={{ marginBottom: '1rem' }} />
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
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{l.exp} yrs</div>
                    </div>
                  </div>
                  <div className={styles.lawyerDomains}>
                    {l.domains.map((d) => (
                      <span key={d} className="badge badge-amber" style={{ fontSize: '0.65rem' }}>{d}</span>
                    ))}
                  </div>
                  <button
                    id={`consult-${l.id}`}
                    className="btn btn-amber btn-sm btn-full"
                    style={{ marginTop: '0.75rem' }}
                    onClick={() => toast(`Requesting consultation with ${l.name}...`, 'info')}
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
