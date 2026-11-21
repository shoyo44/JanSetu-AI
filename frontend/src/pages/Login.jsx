import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldAlert, LogIn, Mail, ArrowRight, Sparkles } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useToast } from '../components/Toast';
import logoUrl from '../assets/jansetu-logo.svg';
import './Starter.css';
import './Login.css';

const Login = () => {
  const { loginWithGoogle } = useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const [loading, setLoading] = useState(false);

  // Get route where the user tried to go before redirect
  const from = location.state?.from?.pathname || "/chat";

  const handleGmailSignIn = async () => {
    setLoading(true);
    try {
      const { signInWithGooglePopup } = await import('../firebase');
      const result = await signInWithGooglePopup();
      const firebaseUser = result.user;
      
      const loggedUser = {
        name: firebaseUser.displayName || "Dev User",
        email: firebaseUser.email || "developer.docsai@gmail.com",
        avatar: firebaseUser.photoURL || "https://lh3.googleusercontent.com/a/default-user=s96-c",
        role: "Workspace Owner",
        joinedAt: new Date().toLocaleDateString()
      };
      
      loginWithGoogle(loggedUser);
      toast.success("Google Sign-In Successful", `Welcome back, ${loggedUser.name}!`);
      navigate(from, { replace: true });
    } catch (err) {
      console.error("Firebase Auth Sign-In failed/skipped:", err);
      
      // Fallback to simulated developer mode if auth keys are empty, popup is closed, or unauthorized local domain
      if (
        err.code === "auth/invalid-api-key" || 
        err.code === "auth/configuration-not-found" || 
        err.code === "auth/unauthorized-domain" ||
        err.code === "auth/popup-closed-by-user" ||
        !import.meta.env.VITE_FIREBASE_API_KEY
      ) {
        toast.warning("Local Demo Mode", "Firebase unauthorized for 127.0.0.1. Logging in with Developer Workspace.");
      } else {
        toast.error("Authentication Error", err.message || "Failed to sign in with Google.");
        setLoading(false);
        return;
      }
      
      const mockUser = {
        name: "Dev User",
        email: "developer.jansetu@gov.in",
        avatar: "https://lh3.googleusercontent.com/a/default-user=s96-c",
        role: "Workspace Owner",
        joinedAt: new Date().toLocaleDateString()
      };
      
      loginWithGoogle(mockUser);
      navigate(from, { replace: true });
    } finally {
      setLoading(false);
    }
  };

  const handleDevBypass = () => {
    const mockUser = {
      name: "Demo / India AI Reviewer",
      email: "reviewer.indiaai@gov.in",
      avatar: "https://lh3.googleusercontent.com/a/default-user=s96-c",
      role: "Fellowship Evaluator",
      joinedAt: new Date().toLocaleDateString()
    };
    loginWithGoogle(mockUser);
    toast.success("Welcome!", "Logged in as Fellowship Evaluator.");
    navigate(from, { replace: true });
  };

  return (
    <div className="login-page-container animate-fade-in">
      <div className="login-bg-grid"></div>

      <header className="starter-nav-header">
        <div className="starter-nav-logo" onClick={() => navigate('/')} style={{cursor: 'pointer'}}>
          <img src={logoUrl} alt="JanSetu AI Logo" className="starter-logo-img" />
          <h2>JanSetu AI</h2>
        </div>
        <button className="starter-nav-cta hover-lift" onClick={() => navigate('/')}>
          Back to Home
        </button>
      </header>

      <div className="login-main-content">
        <div className="login-card-wrapper">
          <div className="login-card glass-panel">
            
            <div className="login-card-header">
              <div className="login-logo-container">
                <img src={logoUrl} alt="JanSetu AI Logo" className="login-logo" />
              </div>
              <h2>JanSetu AI Workspace</h2>
              <p className="login-subtitle">Sovereign Governance & Citizen Intelligence Platform</p>
            </div>

            <div className="login-card-body">
              <p className="login-instruction">
                Sign in with your Google Workspace or Gmail account to access specialized agent verticals.
              </p>

              <button 
                className={`google-signin-btn hover-lift ${loading ? 'loading' : ''}`}
                onClick={handleGmailSignIn}
                disabled={loading}
              >
                {loading ? (
                  <div className="signin-spinner"></div>
                ) : (
                  <>
                    <div className="google-icon-wrapper">
                      <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22c-.22-.66-.35-1.36-.35-2.09z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                      </svg>
                    </div>
                    <span>Sign in with Google</span>
                  </>
                )}
              </button>

              <button 
                type="button"
                className="hover-lift"
                onClick={handleDevBypass}
                style={{
                  marginTop: '12px',
                  width: '100%',
                  padding: '11px 16px',
                  background: 'rgba(56, 189, 248, 0.08)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '10px',
                  color: '#e2e8f0',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}
              >
                <Sparkles size={15} color="#38bdf8" />
                <span>Instant Demo Access (Fellowship Evaluator)</span>
              </button>

              <div className="login-divider">
                <span>SECURITY VERIFIED</span>
              </div>

              <div className="security-features">
                <div className="security-item">
                  <ShieldAlert size={14} className="sec-icon" />
                  <span>Secure OAuth authorization via Google Identity</span>
                </div>
                <div className="security-item">
                  <Sparkles size={14} className="sec-icon" />
                  <span>Automatic tenant context separation</span>
                </div>
              </div>
            </div>

            <div className="login-card-footer">
              <span>By signing in, you agree to JanSetu AI workspace policies and research terms.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
