import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  ScalesIcon, MessageIcon, FolderIcon,
  BriefcaseIcon, UserIcon, LogOutIcon,
  GridIcon, ChevronDownIcon, SparkleIcon,
} from './Icons';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { user, isLawyer, logout } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();
  const [dropOpen, setDropOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close dropdown on route change
  useEffect(() => setDropOpen(false), [location]);

  const handleLogout = () => { logout(); navigate('/auth'); };

  const customerLinks = [
    { to: '/workspace', label: 'AI Workspace', icon: <SparkleIcon size={16} /> },
    { to: '/cases',     label: 'My Cases',     icon: <FolderIcon size={16} /> },
    { to: '/inbox',     label: 'Inbox',        icon: <MessageIcon size={16} /> },
  ];

  const lawyerLinks = [
    { to: '/feed',   label: 'Feed',           icon: <GridIcon size={16} /> },
    { to: '/cases',  label: 'Case Inquiries', icon: <BriefcaseIcon size={16} /> },
    { to: '/inbox',  label: 'Inbox',          icon: <MessageIcon size={16} /> },
  ];

  const links = isLawyer ? lawyerLinks : customerLinks;

  return (
    <nav className={`${styles.navbar} ${scrolled ? styles.navbarScrolled : ''}`}>
      {/* Brand */}
      <div
        className={styles.brand}
        onClick={() => navigate(isLawyer ? '/feed' : '/workspace')}
      >
        <div className={styles.brandIconWrap}>
          <ScalesIcon size={20} color="#FBBF24" />
          <div className={styles.brandIconGlow} />
        </div>
        <span className={styles.brandName}>LexAI</span>
        <span className={styles.brandTag}>Legal Intelligence</span>
      </div>

      {/* Nav links */}
      <div className={styles.links}>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              isActive
                ? `${styles.link} ${styles.linkActive}`
                : styles.link
            }
          >
            <span className={styles.linkIcon}>{l.icon}</span>
            {l.label}
            <span className={styles.linkUnderline} />
          </NavLink>
        ))}
      </div>

      {/* Right — Profile */}
      <div
        className={styles.profile}
        onClick={() => setDropOpen((v) => !v)}
      >
        <div className={styles.avatarWrap}>
          <div className={styles.avatar}>
            {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <div className={styles.avatarRing} />
        </div>
        <div className={styles.profileText}>
          <span className={styles.userName}>
            {user?.full_name?.split(' ')[0]}
          </span>
          <span className={styles.userRole}>
            {isLawyer ? 'Advocate' : 'Client'}
          </span>
        </div>
        <span className={`${styles.chevron} ${dropOpen ? styles.chevronOpen : ''}`}>
          <ChevronDownIcon size={14} color="var(--text-muted)" />
        </span>

        {dropOpen && (
          <div className={styles.dropdown}>
            <div className={styles.dropHeader}>
              <div className={styles.dropName}>{user?.full_name}</div>
              <div className={styles.dropRole}>
                {isLawyer ? '⚖️ Verified Advocate' : '👤 Client'}
              </div>
            </div>
            <hr style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '0.5rem 0' }} />
            <button className={styles.dropItem}>
              <UserIcon size={15} color="var(--text-secondary)" />
              My Profile
            </button>
            <button className={`${styles.dropItem} ${styles.dropItemDanger}`} onClick={handleLogout}>
              <LogOutIcon size={15} color="var(--red)" />
              Sign Out
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
