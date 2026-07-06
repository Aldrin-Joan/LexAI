import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerLawyer, uploadVerificationDoc, loginUser, getMe } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import styles from './LawyerAuthPage.module.css';

const DOMAINS = [
  { id: 'civil_law',          label: 'Civil Law' },
  { id: 'criminal_law',       label: 'Criminal Law' },
  { id: 'corporate_law',      label: 'Corporate Law' },
  { id: 'tax_law',            label: 'Tax Law' },
  { id: 'constitutional_law', label: 'Constitutional Law' },
  { id: 'family_law',         label: 'Family Law' },
  { id: 'property_law',       label: 'Property Law' },
  { id: 'labour_law',         label: 'Labour Law' },
];

const STEPS = ['Account Setup', 'Professional Details', 'Verification Docs'];

export default function LawyerAuthPage() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    fullName: '', username: '', email: '',
    password: '', confirm: '',
    barNumber: '', practiceDomains: [],
    yearsExp: '', bio: '',
  });
  const [errors, setErrors] = useState({});
  const [files, setFiles]   = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [createdToken, setCreatedToken] = useState(null);

  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const set = (field) => (e) =>
    setForm((p) => ({ ...p, [field]: e.target.value }));

  /* ---- Step validation ---- */
  const validateStep = () => {
    const errs = {};
    if (step === 0) {
      if (!form.fullName)  errs.fullName = 'Required';
      if (!form.username)  errs.username = 'Required';
      if (!form.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
        errs.email = 'Enter a valid email';
      if (form.password.length < 10)
        errs.password = 'Minimum 10 characters with caps, digit, and symbol';
      if (form.password !== form.confirm)
        errs.confirm = 'Passwords do not match';
    }
    if (step === 1) {
      if (!form.barNumber)  errs.barNumber = 'Required';
      if (!form.practiceDomains.length) errs.practiceDomains = 'Select at least one domain';
      if (!form.yearsExp || isNaN(form.yearsExp)) errs.yearsExp = 'Enter valid number';
      if (!form.bio || form.bio.length < 50) errs.bio = 'Provide at least 50 characters';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleNext = async () => {
    if (!validateStep()) return;
    if (step === 1) {
      // Register lawyer on step 1 completion
      setLoading(true);
      try {
        await registerLawyer(form);
        const { access_token } = await loginUser(form.username, form.password);
        setCreatedToken(access_token);
        setStep(2);
      } catch (err) {
        const msg = err.response?.data?.detail || 'Registration failed.';
        toast(typeof msg === 'string' ? msg : msg[0]?.msg, 'error');
      } finally {
        setLoading(false);
      }
    } else {
      setStep((s) => s + 1);
    }
  };

  const handleSubmit = async () => {
    if (!files.length) { toast('Please upload at least one document', 'error'); return; }
    setLoading(true);
    try {
      for (const file of files) {
        await uploadVerificationDoc(file, 'bar_council_card', createdToken);
      }
      const userData = await getMe();
      login(createdToken, userData);
      toast('Registration complete! Your account is under review.', 'success');
      navigate('/verification-hold');
    } catch {
      toast('Document upload failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const toggleDomain = (id) => {
    setForm((p) => ({
      ...p,
      practiceDomains: p.practiceDomains.includes(id)
        ? p.practiceDomains.filter((d) => d !== id)
        : [...p.practiceDomains, id],
    }));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = Array.from(e.dataTransfer.files).filter(
      (f) => f.size <= 10 * 1024 * 1024
    );
    setFiles((prev) => [...prev, ...dropped]);
  };

  const errText = (field) =>
    errors[field] ? <span className="form-error">{errors[field]}</span> : null;

  return (
    <div className={styles.page}>
      <div className="bg-orbs" />

      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <span className={styles.headerIcon}>⚖️</span>
          <h1 className={styles.headerTitle}>LexAI Lawyer Onboarding</h1>
          <p className={styles.headerSub}>Join India's verified advocate network</p>
        </div>

        {/* Stepper */}
        <div className={styles.stepper}>
          {STEPS.map((label, i) => (
            <React.Fragment key={label}>
              <div className={styles.stepItem}>
                <div className={`${styles.stepCircle} ${i < step ? styles.stepDone : i === step ? styles.stepActive : ''}`}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span className={`${styles.stepLabel} ${i === step ? styles.stepLabelActive : ''}`}>
                  {label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`${styles.stepLine} ${i < step ? styles.stepLineDone : ''}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Form Card */}
        <div className={styles.card}>
          {/* STEP 0 — Account Setup */}
          {step === 0 && (
            <div className={styles.formGrid}>
              <h2 className={styles.stepTitle}>Account Setup</h2>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="glass-input" placeholder="Ravi Sharma" value={form.fullName} onChange={set('fullName')} />
                {errText('fullName')}
              </div>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input className="glass-input" placeholder="advocate_sharma" value={form.username} onChange={set('username')} />
                {errText('username')}
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input className="glass-input" type="email" placeholder="sharma@lawfirm.com" value={form.email} onChange={set('email')} />
                {errText('email')}
              </div>
              <div className="form-group">
                <label className="form-label">Password (min 10 chars)</label>
                <input className="glass-input" type="password" placeholder="SecureAdvocate99!" value={form.password} onChange={set('password')} />
                {errText('password')}
              </div>
              <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input className="glass-input" type="password" placeholder="Repeat password" value={form.confirm} onChange={set('confirm')} />
                {errText('confirm')}
              </div>
            </div>
          )}

          {/* STEP 1 — Professional Details */}
          {step === 1 && (
            <div className={styles.formGrid}>
              <h2 className={styles.stepTitle}>Professional Details</h2>
              <div className="form-group">
                <label className="form-label">Bar Registration Number</label>
                <input className="glass-input" placeholder="BCI/2018/4567" value={form.barNumber} onChange={set('barNumber')} />
                {errText('barNumber')}
              </div>
              <div className="form-group">
                <label className="form-label">Practice Domains</label>
                <div className={styles.domainGrid}>
                  {DOMAINS.map((d) => (
                    <button
                      key={d.id}
                      type="button"
                      id={`domain-${d.id}`}
                      className={`${styles.domainChip} ${form.practiceDomains.includes(d.id) ? styles.domainChipActive : ''}`}
                      onClick={() => toggleDomain(d.id)}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
                {errText('practiceDomains')}
              </div>
              <div className="form-group">
                <label className="form-label">Years of Practice</label>
                <input className="glass-input" type="number" min="0" placeholder="8" value={form.yearsExp} onChange={set('yearsExp')} />
                {errText('yearsExp')}
              </div>
              <div className="form-group">
                <label className="form-label">Professional Bio (min 50 chars)</label>
                <textarea
                  className="glass-input"
                  rows={4}
                  maxLength={1000}
                  placeholder="Senior advocate specializing in..."
                  value={form.bio}
                  onChange={set('bio')}
                  style={{ resize: 'vertical', fontFamily: 'var(--font-body)' }}
                />
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', alignSelf: 'flex-end' }}>
                  {form.bio.length}/1000
                </span>
                {errText('bio')}
              </div>
            </div>
          )}

          {/* STEP 2 — Verification Documents */}
          {step === 2 && (
            <div className={styles.formGrid}>
              <h2 className={styles.stepTitle}>Verification Documents</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                Upload your Bar Council ID card and Certificate of Practice. Supported: PDF, PNG, JPG (max 10MB each).
              </p>

              <div
                id="doc-dropzone"
                className={`${styles.dropzone} ${dragOver ? styles.dropzoneActive : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => document.getElementById('doc-file-input').click()}
              >
                <input
                  id="doc-file-input"
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  multiple
                  style={{ display: 'none' }}
                  onChange={(e) => setFiles((prev) => [...prev, ...Array.from(e.target.files)])}
                />
                <span className={styles.dropzoneIcon}>📄</span>
                <span className={styles.dropzoneText}>
                  {dragOver ? 'Drop files here' : 'Drag & drop files or click to browse'}
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                  Bar Council ID, Certificate of Practice
                </span>
              </div>

              {files.length > 0 && (
                <div className={styles.fileList}>
                  {files.map((f, i) => (
                    <div key={i} className={styles.fileItem}>
                      <span>📎 {f.name}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                        {(f.size / 1024).toFixed(0)} KB
                      </span>
                      <button
                        type="button"
                        className={styles.removeFile}
                        onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          <div className={styles.navBtns}>
            {step > 0 && (
              <button className="btn btn-ghost" onClick={() => setStep((s) => s - 1)} disabled={loading}>
                ← Back
              </button>
            )}
            {step < 2 ? (
              <button
                id={`lawyer-next-step-${step}`}
                className="btn btn-amber"
                style={{ marginLeft: 'auto' }}
                onClick={handleNext}
                disabled={loading}
              >
                {loading ? <span className="animate-spin">◌</span> : 'Continue →'}
              </button>
            ) : (
              <button
                id="lawyer-submit"
                className="btn btn-amber"
                style={{ marginLeft: 'auto' }}
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? <span className="animate-spin">◌</span> : 'Submit for Review'}
              </button>
            )}
          </div>
        </div>

        <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '1.5rem' }}>
          Signing up as a client instead?{' '}
          <a href="/auth" style={{ color: 'var(--amber)' }}>Go to Client Auth →</a>
        </p>
      </div>
    </div>
  );
}
