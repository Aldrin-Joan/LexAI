import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { onAuthStateChanged, signOut, signInWithEmailAndPassword } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { auth, db } from '../api/firebase';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Listen to Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setLoading(true);
      if (firebaseUser) {
        try {
          const tokenVal = await firebaseUser.getIdToken();
          setToken(tokenVal);
          const userDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
          if (userDoc.exists()) {
            setUser({
              id: firebaseUser.uid,
              uid: firebaseUser.uid,
              email: firebaseUser.email,
              ...userDoc.data(),
            });
          } else {
            // Auto-provision user document for third-party auth (Google)
            const autoProfile = {
              full_name: firebaseUser.displayName || firebaseUser.email.split('@')[0],
              username: firebaseUser.email.split('@')[0] + '_' + Math.random().toString(36).substr(2, 4),
              email: firebaseUser.email,
              is_lawyer: false,
              is_active: true,
              created_at: new Date().toISOString(),
            };
            await setDoc(doc(db, 'users', firebaseUser.uid), autoProfile);
            setUser({
              id: firebaseUser.uid,
              uid: firebaseUser.uid,
              email: firebaseUser.email,
              ...autoProfile,
            });
          }
        } catch (err) {
          console.error("Error restoring user session:", err);
          setUser({
            id: firebaseUser.uid,
            uid: firebaseUser.uid,
            email: firebaseUser.email,
          });
        }
      } else {
        setUser(null);
        setToken(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = useCallback(async (email, password) => {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    const tokenVal = await cred.user.getIdToken();
    setToken(tokenVal);
    const userDoc = await getDoc(doc(db, 'users', cred.user.uid));
    if (userDoc.exists()) {
      const fullProfile = {
        id: cred.user.uid,
        uid: cred.user.uid,
        email: cred.user.email,
        ...userDoc.data(),
      };
      setUser(fullProfile);
      return fullProfile;
    } else {
      const basicProfile = {
        id: cred.user.uid,
        uid: cred.user.uid,
        email: cred.user.email,
      };
      setUser(basicProfile);
      return basicProfile;
    }
  }, []);

  const logout = useCallback(async () => {
    await signOut(auth);
    setUser(null);
    setToken(null);
  }, []);

  const isAuthenticated = !!user;
  const isLawyer = user?.is_lawyer === true;
  const isVerified = user?.is_active === true;
  const isPendingVerification =
    isLawyer && user?.verification_status?.includes('pending');

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      logout,
      isAuthenticated,
      isLawyer,
      isVerified,
      isPendingVerification,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
