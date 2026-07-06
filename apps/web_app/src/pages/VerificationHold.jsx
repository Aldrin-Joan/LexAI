import React from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './VerificationHold.module.css';

export default function VerificationHold() {
  const { user, logout } = useAuth();

  return (
    <div className={styles.page}>
      <div className="bg-orbs" />
      <div className={styles.container}>
        <div className={styles.iconWrap}>
          <span className={styles.icon}>🔒</span>
          <div className={styles.iconGlow} />
        </div>

        <h1 className={styles.title}>Verification in Progress</h1>
        <p className={styles.sub}>
          Welcome, <strong style={{ color: 'var(--amber)' }}>{user?.full_name}</strong>
        </p>

        <div className={styles.card}>
          <div className={styles.statusRow}>
            <span className={styles.pulsingDot} />
            <span>Bar Council Authentication — <strong>Under Review</strong></span>
          </div>
          <p className={styles.message}>
            Our legal validation team is verifying your Bar Council Registry ID and the
            uploaded documentation. This typically takes <strong>24–48 hours</strong>.
          </p>

          <div className={styles.steps}>
            {[
              { label: 'Account Created', done: true },
              { label: 'Documents Submitted', done: true },
              { label: 'Bar Council Verification', done: false, active: true },
              { label: 'Access Granted', done: false },
            ].map((s, i) => (
              <div key={i} className={styles.stepRow}>
                <div className={`${styles.dot} ${s.done ? styles.dotDone : s.active ? styles.dotActive : styles.dotPending}`}>
                  {s.done ? '✓' : ''}
                </div>
                <span className={s.active ? styles.labelActive : styles.label}>{s.label}</span>
              </div>
            ))}
          </div>
        </div>

        <p className={styles.footer}>
          You will receive an email notification once your account is approved.
        </p>

        <button className="btn btn-ghost" style={{ marginTop: '1rem' }} onClick={logout}>
          Sign Out
        </button>
      </div>
    </div>
  );
}
