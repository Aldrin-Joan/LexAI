import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';

import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import ProtectedRoute from './components/ProtectedRoute';
import ParticleCanvas from './components/ParticleCanvas';

import AuthPage          from './pages/AuthPage';
import LawyerAuthPage    from './pages/LawyerAuthPage';
import VerificationHold  from './pages/VerificationHold';
import ClientWorkspace   from './pages/ClientWorkspace';
import LawyerFeed        from './pages/LawyerFeed';
import InboxPage         from './pages/InboxPage';
import CasesPage         from './pages/CasesPage';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          {/* Live particle canvas — renders behind everything */}
          <ParticleCanvas />

          <Routes>
            {/* Public routes */}
            <Route path="/auth"        element={<AuthPage />} />
            <Route path="/lawyer-auth" element={<LawyerAuthPage />} />

            {/* Verification hold — authenticated lawyers only */}
            <Route
              path="/verification-hold"
              element={
                <ProtectedRoute role="lawyer">
                  <VerificationHold />
                </ProtectedRoute>
              }
            />

            {/* Client workspace */}
            <Route
              path="/workspace"
              element={
                <ProtectedRoute role="customer">
                  <ClientWorkspace />
                </ProtectedRoute>
              }
            />

            {/* Lawyer feed */}
            <Route
              path="/feed"
              element={
                <ProtectedRoute role="lawyer">
                  <LawyerFeed />
                </ProtectedRoute>
              }
            />

            {/* Shared authenticated routes */}
            <Route
              path="/inbox"
              element={
                <ProtectedRoute>
                  <InboxPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/cases"
              element={
                <ProtectedRoute>
                  <CasesPage />
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/auth" replace />} />
            <Route path="*" element={<Navigate to="/auth" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
