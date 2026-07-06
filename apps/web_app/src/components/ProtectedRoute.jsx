import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Protects routes by authentication state and optional role requirement.
 * @param {object} props
 * @param {'customer'|'lawyer'|null} props.role - Required role, or null for any authenticated user
 */
export default function ProtectedRoute({ children, role = null }) {
  const { isAuthenticated, isLawyer, isPendingVerification, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'var(--bg-base)',
      }}>
        <div style={{
          width: 40,
          height: 40,
          border: '3px solid var(--glass-border)',
          borderTopColor: 'var(--amber)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  if (role === 'lawyer' && !isLawyer) {
    return <Navigate to="/workspace" replace />;
  }

  if (role === 'customer' && isLawyer) {
    return <Navigate to="/feed" replace />;
  }

  // Lawyer pending verification — redirect to hold screen
  // (except if already on the hold screen)
  if (
    isPendingVerification &&
    location.pathname !== '/verification-hold'
  ) {
    return <Navigate to="/verification-hold" replace />;
  }

  return children;
}
