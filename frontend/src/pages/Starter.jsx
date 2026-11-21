import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Files, Activity, Clock, ShieldCheck, ArrowRight, Zap, Target, BookOpen, Layers } from 'lucide-react';
import { useApp } from '../context/AppContext';
import logoUrl from '../assets/jansetu-logo.svg';
import './Starter.css';

const Starter = () => {
  const { user, documents } = useApp();
  const navigate = useNavigate();

  const handleLaunch = () => {
    if (user) {
      navigate('/chat');
    } else {
      navigate('/login');
    }
  };

  const features = [
    {
      icon: MessageSquare,
      title: "Jan Suvidha Governance Intelligence",
      desc: "Automatically analyzes Central & State Gazettes and Welfare Yojanas (PM-KISAN, Ayushman Bharat, PMAY) to generate citizen eligibility checklists."
    },
    {
      icon: Files,
      title: "Nyaya Setu Statutory Concordance",
      desc: "Bidirectional statutory cross-referencing between colonial penal codes and modern 2024 criminal acts (IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA)."
    },
    {
      icon: Activity,
      title: "Supreme Court Case Law & Bail Ratio",
      desc: "Extracts ratio decidendi, Article 21 personal liberty doctrines, and bail precedents from Indian Supreme Court and High Court judgments."
    },
    {
      icon: Clock,
      title: "Sovereign Knowledge Graph & Auditing",
      desc: "Air-gapped graph store mapping government gazettes, case precedents, and statutory sections complying with DPDPA 2023 Section 16."
    }
  ];

  return (
    <div className="starter-page-container animate-fade-in">
      <div className="starter-mesh-grid"></div>

      <header className="starter-nav-header">
        <div className="starter-nav-logo">
          <img src={logoUrl} alt="JanSetu AI Logo" className="starter-logo-img" />
          <h2>JanSetu AI</h2>
        </div>
        <button className="starter-nav-cta hover-lift" onClick={handleLaunch}>
          {user ? "Enter Fellowship Workspace" : "Fellowship Demo Access"}
        </button>
      </header>

      <main className="starter-main-hero">
        <div className="starter-hero-content">
          <div className="starter-pill-badge">
            <Zap size={13} />
            <span>🇮🇳 IndiaAI Mission Fellowship Research Initiative</span>
          </div>
          <h1>
            Sovereign AI for Indian <br />
            <span>Public Governance & Justice</span>
          </h1>
          <p className="starter-hero-subtitle">
            Sovereign Multi-Vertical Agentic Knowledge Graph & RAG Platform delivering Jan Suvidha citizen welfare intelligence and statutory criminal law concordance (IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA).
          </p>

          <div className="starter-cta-group">
            <button className="starter-hero-btn-primary hover-lift" onClick={handleLaunch}>
              <span>Launch Fellowship Workspace</span>
              <ArrowRight size={16} />
            </button>
          </div>

          <div className="starter-hero-stats">
            <div className="stat-card">
              <h3>3 Benchmarks</h3>
              <span>PM-KISAN, SC Bail, PM-JAY</span>
            </div>
            <div className="stat-card">
              <h3>100% Sovereign</h3>
              <span>DPDPA Section 16 Compliant</span>
            </div>
            <div className="stat-card">
              <h3>&lt; 2.5s</h3>
              <span>Average Retrieval Latency</span>
            </div>
          </div>
        </div>

        <div className="starter-feature-section">
          <h2>Fellowship Core Capabilities</h2>
          <div className="features-grid">
            {features.map((f, i) => (
              <div key={i} className="feature-card glass-panel hover-lift">
                <div className="feature-card-icon">
                  <f.icon size={22} />
                </div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="starter-page-footer">
        <p>&copy; {new Date().getFullYear()} JanSetu AI (जनसेतु) — IndiaAI Fellowship Submission (Applicant: Dhanush S, Kalasalingam Academy of Research and Education).</p>
      </footer>
    </div>
  );
};

export default Starter;
