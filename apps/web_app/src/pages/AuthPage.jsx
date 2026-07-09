import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { doc, setDoc } from 'firebase/firestore';
import { auth, db } from '../api/firebase';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import {
  ScalesIcon, BrainCircuitIcon, ShieldCheckIcon, LockIcon,
  EyeIcon, EyeOffIcon, ArrowRightIcon, SparkleIcon,
} from '../components/Icons';
import styles from './AuthPage.module.css';

/* ---- Validation helpers ---- */
const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const pwRe = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;

function PasswordStrength({ password }) {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  if (/[!@#$%^&*]/.test(password)) strength++;

  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
  const colors = ['', '#EF4444', '#F59E0B', '#3B82F6', '#22C55E'];

  if (!password) return null;
  return (
    <div className={styles.pwStrength}>
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className={styles.pwBar}
          style={{ background: i <= strength ? colors[strength] : 'var(--glass-border)' }}
        />
      ))}
      <span style={{ color: colors[strength], fontSize: '0.72rem' }}>
        {labels[strength]}
      </span>
    </div>
  );
}

/* ---- Feature cards shown on left brand pane ---- */
const FEATURES = [
  {
    Icon: BrainCircuitIcon,
    title: 'AI Legal Research',
    desc: 'Hybrid RAG-powered search across Indian case law and statutes',
    color: 'var(--blue)',
    glowClass: 'icon-glow icon-glow-blue',
  },
  {
    Icon: ShieldCheckIcon,
    title: 'Verified Advocates',
    desc: 'Connect with Bar Council verified legal professionals instantly',
    color: 'var(--green)',
    glowClass: 'icon-glow icon-glow-green',
  },
  {
    Icon: LockIcon,
    title: 'Encrypted Legal Vault',
    desc: 'Secure document storage with end-to-end encryption',
    color: 'var(--amber)',
    glowClass: 'icon-glow icon-glow-amber',
  },
];

export default function AuthPage() {
  const [tab, setTab] = useState('signin'); // 'signin' | 'signup'
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  /* ---- Sign In state ---- */
  const [siForm, setSiForm] = useState({ username: '', password: '' });
  const [siErrors, setSiErrors] = useState({});
  const [siLoading, setSiLoading] = useState(false);

  /* ---- Sign Up state ---- */
  const [suForm, setSuForm] = useState({
    fullName: '', username: '', email: '',
    password: '', confirm: '', consent: false,
  });
  const [suErrors, setSuErrors] = useState({});
  const [suLoading, setSuLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  /* ---- Sign In ---- */
  const handleSignIn = async (e) => {
    e.preventDefault();
    const errs = {};
    if (!siForm.username) errs.username = 'Email address is required';
    if (!siForm.password) errs.password = 'Password is required';
    setSiErrors(errs);
    if (Object.keys(errs).length) return;

    setSiLoading(true);
    try {
      const userData = await login(siForm.username, siForm.password);
      toast('Welcome back, ' + (userData.full_name || 'User') + '!', 'success');
      navigate(userData.is_lawyer ? '/feed' : '/workspace');
    } catch (err) {
      console.error(err);
      toast('Incorrect email or password. Please try again.', 'error');
    } finally {
      setSiLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      toast('Welcome back!', 'success');
      navigate('/workspace');
    } catch (err) {
      console.error(err);
      toast('Google login failed: ' + err.message, 'error');
    }
  };

  /* ---- Sign Up ---- */
  const handleSignUp = async (e) => {
    e.preventDefault();
    const errs = {};
    if (!suForm.fullName) errs.fullName = 'Full name is required';
    if (!suForm.username) errs.username = 'Username is required';
    if (!emailRe.test(suForm.email)) errs.email = 'Enter a valid email address';
    if (!pwRe.test(suForm.password))
      errs.password = 'Min 8 chars with uppercase, number, and special character';
    if (suForm.password !== suForm.confirm) errs.confirm = 'Passwords do not match';
    if (!suForm.consent) errs.consent = 'You must accept the legal terms';
    setSuErrors(errs);
    if (Object.keys(errs).length) return;

    setSuLoading(true);
    try {
      const cred = await createUserWithEmailAndPassword(auth, suForm.email, suForm.password);
      await setDoc(doc(db, 'users', cred.user.uid), {
        full_name: suForm.fullName,
        username: suForm.username,
        email: suForm.email,
        is_lawyer: false,
        is_active: true,
        created_at: new Date().toISOString(),
      });
      toast('Account created! Please sign in.', 'success');
      setTab('signin');
      setSiForm({ username: suForm.email, password: '' });
    } catch (err) {
      console.error(err);
      toast(err.message || 'Registration failed. Please try again.', 'error');
    } finally {
      setSuLoading(false);
    }
  };

  const siField = (field) => ({
    value: siForm[field],
    onChange: (e) => setSiForm((p) => ({ ...p, [field]: e.target.value })),
    className: `glass-input ${siErrors[field] ? styles.inputError : ''}`,
  });

  const suField = (field) => ({
    value: suForm[field],
    onChange: (e) => setSuForm((p) => ({ ...p, [field]: e.target.value })),
    className: `glass-input ${suErrors[field] ? styles.inputError : ''}`,
    onBlur: () => setSuErrors((p) => ({ ...p, [field]: undefined })),
  });

  return (
    <div className={styles.page}>
      <div className="bg-orbs" />

      {/* LEFT — Brand Pane */}
      <div className={styles.left}>
        <div className={styles.brandArea}>
          <div className={`${styles.scalesWrap} pulse-ring`}>
            <div className={styles.scalesIconSvg}>
              <ScalesIcon size={52} color="#FBBF24" />
            </div>
            <div className={styles.scalesGlow} />
          </div>
          <h1 className={styles.brandTitle}>LexAI</h1>
          <p className={styles.brandSub}>Indian Legal Intelligence Platform</p>
        </div>

        <div className={`${styles.features} stagger`}>
          {FEATURES.map((f, i) => (
            <div key={f.title} className={`${styles.featureCard} hover-lift scan-line`}>
              <div className={f.glowClass} style={{ flexShrink: 0 }}>
                <f.Icon size={22} color={f.color} />
              </div>
              <div>
                <div className={styles.featureTitle}>{f.title}</div>
                <div className={styles.featureDesc}>{f.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT — Auth Form Pane */}
      <div className={styles.right}>
        <div className={`${styles.formCard} glow-card`}>
          {/* Tab switcher */}
          <div className={styles.tabs}>
            <button
              id="auth-tab-signin"
              className={`${styles.tab} ${tab === 'signin' ? styles.tabActive : ''}`}
              onClick={() => setTab('signin')}
            >
              Sign In
            </button>
            <button
              id="auth-tab-signup"
              className={`${styles.tab} ${tab === 'signup' ? styles.tabActive : ''}`}
              onClick={() => setTab('signup')}
            >
              Register
            </button>
          </div>

          {/* SIGN IN FORM */}
          {tab === 'signin' && (
            <form onSubmit={handleSignIn} className={styles.form} noValidate>
              <h2 className={styles.formTitle}>Welcome back</h2>
              <p className={styles.formSub}>Sign in to your LexAI account</p>

              <div className="form-group">
                <label className="form-label" htmlFor="si-username">Username or Email</label>
                <input id="si-username" type="text" placeholder="your_username" {...siField('username')} />
                {siErrors.username && <span className="form-error">{siErrors.username}</span>}
              </div>

              <div className="form-group" style={{ position: 'relative' }}>
                <label className="form-label" htmlFor="si-password">Password</label>
                <input
                  id="si-password"
                  type={showPw ? 'text' : 'password'}
                  placeholder="••••••••"
                  style={{ paddingRight: '3rem' }}
                  {...siField('password')}
                />
                <button
                  type="button"
                  className={styles.eyeBtn}
                  onClick={() => setShowPw((v) => !v)}
                  tabIndex={-1}
                >
                  {showPw ? '🙈' : '👁️'}
                </button>
                {siErrors.password && <span className="form-error">{siErrors.password}</span>}
              </div>

              <button
                id="btn-signin"
                type="submit"
                className="btn btn-amber btn-full btn-lg btn-ripple"
                disabled={siLoading}
              >
                {siLoading
                  ? <span className="animate-spin">◌</span>
                  : <><SparkleIcon size={16} color="#0B0F19" /> Sign In</>}
              </button>

              <div style={{ display: 'flex', alignItems: 'center', margin: '0.75rem 0', justifyContent: 'center', gap: '0.5rem' }}>
                <div style={{ flex: 1, height: '1px', background: 'var(--glass-border)' }} />
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>OR</span>
                <div style={{ flex: 1, height: '1px', background: 'var(--glass-border)' }} />
              </div>

              <button
                type="button"
                className="btn btn-ghost btn-full btn-ripple"
                onClick={handleGoogleSignIn}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', border: '1px solid var(--glass-border)' }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24">
                  <path fill="#EA4335" d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114A5.5 5.5 0 0 1 8.5 13a5.5 5.5 0 0 1 5.491-5.518c1.483 0 2.825.54 3.868 1.438l3.167-3.167C19.066 3.879 16.711 3 13.99 3A9.99 9.99 0 0 0 4 13a9.99 9.99 0 0 0 9.99 10c5.38 0 9.778-3.9 9.778-10a9.04 9.04 0 0 0-.17-1.715H12.24z"/>
                </svg>
                Sign In with Google
              </button>

              <hr className="divider" style={{ marginTop: '1rem' }} />
              <p className={styles.switchText}>
                New to LexAI?{' '}
                <button type="button" className={styles.switchLink} onClick={() => setTab('signup')}>
                  Create an account
                </button>
              </p>
              <p className={styles.switchText} style={{ marginTop: '0.5rem' }}>
                A legal professional?{' '}
                <Link to="/lawyer-auth" className={styles.switchLink}>
                  Lawyer onboarding →
                </Link>
              </p>
            </form>
          )}

          {/* SIGN UP FORM */}
          {tab === 'signup' && (
            <form onSubmit={handleSignUp} className={styles.form} noValidate>
              <h2 className={styles.formTitle}>Create account</h2>
              <p className={styles.formSub}>Join thousands of clients using LexAI</p>

              <div className="form-group">
                <label className="form-label" htmlFor="su-name">Full Name</label>
                <input id="su-name" type="text" placeholder="Ayush Agarwal" {...suField('fullName')} />
                {suErrors.fullName && <span className="form-error">{suErrors.fullName}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="su-username">Username</label>
                <input id="su-username" type="text" placeholder="legal_client_01" {...suField('username')} />
                {suErrors.username && <span className="form-error">{suErrors.username}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="su-email">Email</label>
                <input id="su-email" type="email" placeholder="you@example.com" {...suField('email')} />
                {suErrors.email && <span className="form-error">{suErrors.email}</span>}
              </div>

              <div className="form-group" style={{ position: 'relative' }}>
                <label className="form-label" htmlFor="su-password">Password</label>
                <input
                  id="su-password"
                  type={showPw ? 'text' : 'password'}
                  placeholder="Min 8 chars"
                  style={{ paddingRight: '3rem' }}
                  {...suField('password')}
                />
                <button
                  type="button"
                  className={styles.eyeBtn}
                  onClick={() => setShowPw((v) => !v)}
                  tabIndex={-1}
                >
                  {showPw ? '🙈' : '👁️'}
                </button>
                <PasswordStrength password={suForm.password} />
                {suErrors.password && <span className="form-error">{suErrors.password}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="su-confirm">Confirm Password</label>
                <input id="su-confirm" type="password" placeholder="Repeat password" {...suField('confirm')} />
                {suErrors.confirm && <span className="form-error">{suErrors.confirm}</span>}
              </div>

              <div className={styles.consentRow}>
                <input
                  id="su-consent"
                  type="checkbox"
                  checked={suForm.consent}
                  onChange={(e) => setSuForm((p) => ({ ...p, consent: e.target.checked }))}
                  className={styles.checkbox}
                />
                <label htmlFor="su-consent" className={styles.consentLabel}>
                  I agree to the{' '}
                  <a href="#" className={styles.switchLink}>Terms of Service</a>{' '}
                  and acknowledge LexAI's legal data policies
                </label>
              </div>
              {suErrors.consent && <span className="form-error">{suErrors.consent}</span>}

              <button
                id="btn-register"
                type="submit"
                className="btn btn-amber btn-full btn-lg"
                disabled={suLoading}
              >
                {suLoading ? <span className="animate-spin">◌</span> : 'Create Account'}
              </button>

              <hr className="divider" />
              <p className={styles.switchText}>
                Already have an account?{' '}
                <button type="button" className={styles.switchLink} onClick={() => setTab('signin')}>
                  Sign In
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
