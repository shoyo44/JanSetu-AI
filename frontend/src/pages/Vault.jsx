import React, { useState, useRef } from 'react';
import {
  UploadCloud, File, AlertCircle, Loader, Trash2, Clock,
  CheckCircle2, XCircle, Sparkles, ChevronDown, ShieldCheck,
  BookOpen, Briefcase, Scale, Users, Tag, Target, FileText,
  ArrowRight, Info, RefreshCw, Gavel, ShieldAlert, Eye, Printer, ExternalLink, Check,
  Landmark,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useToast } from '../components/Toast';
import './Vault.css';

// ── Vertical metadata ──────────────────────────────────────────────────────────
const VERTICAL_META = {
  governance: {
    label: 'Public Governance & Welfare Schemes',
    icon: Landmark,
    color: '#0ea5e9',
    bg: 'rgba(14,165,233,0.12)',
    border: 'rgba(14,165,233,0.35)',
    desc: 'Government Gazettes, Ministry guidelines, Welfare Schemes (PM-KISAN, Ayushman Bharat), citizen eligibility',
  },
  judgment: {
    label: 'Court Judgments & Case Precedents',
    icon: Gavel,
    color: '#8b5cf6',
    bg: 'rgba(139,92,246,0.12)',
    border: 'rgba(139,92,246,0.35)',
    desc: 'Indian Supreme Court / High Court orders, judgments, ratio decidendi, bail jurisprudence',
  },
  law: {
    label: 'Statutory Law & Criminal Concordance',
    icon: Scale,
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.12)',
    border: 'rgba(245,158,11,0.35)',
    desc: 'Statutory enactments, IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA concordance, legal decrees',
  },
};

const CONFIDENCE_STYLE = {
  HIGH: { color: '#10b981', bg: 'rgba(16,185,129,0.12)', label: 'High confidence' },
  MEDIUM: { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', label: 'Medium confidence' },
  LOW: { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', label: 'Low confidence' },
};

// ── Detecting phases ───────────────────────────────────────────────────────────
const DETECT_PHASES = [
  { id: 0, label: 'Extracting text from document…' },
  { id: 1, label: 'Phase 1 — Summarising document…' },
  { id: 2, label: 'Phase 2 — Classifying document type…' },
];

// ── Component ─────────────────────────────────────────────────────────────────
const Vault = () => {
  const toast = useToast();
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  // Detection state
  const [detecting, setDetecting] = useState(false);
  const [detectPhase, setDetectPhase] = useState(0);
  const [detection, setDetection] = useState(null);
  const [confirmedVertical, setConfirmedVertical] = useState(null);
  const [showOverride, setShowOverride] = useState(false);
  const [showSummaryDetail, setShowSummaryDetail] = useState(false);

  const {
    vertical, setVertical,
    documents, loadingDocs, fetchDocuments,
    activeJobs, uploadDocument,
    tenantId, apiBase, user,
  } = useApp();

  // ── Phase 3: Human-in-the-Loop Red-Flag Review & Viewer State ──────────────
  const [selectedAuditDoc, setSelectedAuditDoc] = useState(null);
  const [auditReport, setAuditReport] = useState(null);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [actionNotes, setActionNotes] = useState({});
  const [selectedViewerDoc, setSelectedViewerDoc] = useState(null);
  const [viewerChunks, setViewerChunks] = useState([]);
  const [loadingViewer, setLoadingViewer] = useState(false);
  const [loadingBenchmark, setLoadingBenchmark] = useState(null);
  const [viewerSearch, setViewerSearch] = useState('');

  const openAuditWorkbench = async (doc) => {
    setSelectedAuditDoc(doc);
    setLoadingAudit(true);
    try {
      const res = await fetch(`${apiBase}/documents/${doc.id}/redflags?tenant_id=${tenantId}`);
      if (!res.ok) {
        if (res.status === 404) {
          toast.info("No Audit Report", "This document does not have a red-flag report generated yet.");
          setAuditReport(null);
          return;
        }
        throw new Error("Failed to load audit report");
      }
      const data = await res.json();
      setAuditReport(data);
    } catch (err) {
      toast.error("Error", err.message);
      setAuditReport(null);
    } finally {
      setLoadingAudit(false);
    }
  };

  const handleReviewAction = async (flagId, action) => {
    if (!selectedAuditDoc) return;
    try {
      const note = actionNotes[flagId] || "";
      const res = await fetch(`${apiBase}/documents/${selectedAuditDoc.id}/redflags/${flagId}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenantId,
          action: action,
          note: note,
          reviewer: user?.email || "Legal Counsel"
        })
      });
      if (!res.ok) throw new Error("Review submission failed");
      const data = await res.json();
      setAuditReport(data.report);
      toast.success("Review Applied", `Flag marked as ${action.replace('_', ' ').toUpperCase()}`);
    } catch (err) {
      toast.error("Review Error", err.message);
    }
  };

  const handleExportReport = (format = 'html') => {
    if (!selectedAuditDoc) return;
    const url = `${apiBase}/documents/${selectedAuditDoc.id}/export?tenant_id=${tenantId}&format=${format}`;
    window.open(url, '_blank');
  };

  const openDocViewer = async (doc) => {
    setSelectedViewerDoc(doc);
    setLoadingViewer(true);
    setViewerSearch('');
    try {
      const res = await fetch(`${apiBase}/documents/${doc.id}/chunks?tenant_id=${tenantId}`);
      if (!res.ok) throw new Error("Failed to load document chunks");
      const data = await res.json();
      setViewerChunks(data.chunks || []);
    } catch (err) {
      toast.error("Viewer Error", err.message);
      setViewerChunks([]);
    } finally {
      setLoadingViewer(false);
    }
  };

  const inputRef = useRef(null);
  const phaseTimer = useRef(null);

  // ── Phase ticker (cosmetic progress while waiting) ──────────────────────────
  const startPhaseTimer = () => {
    setDetectPhase(0);
    let phase = 0;
    phaseTimer.current = setInterval(() => {
      phase = Math.min(phase + 1, DETECT_PHASES.length - 1);
      setDetectPhase(phase);
    }, 2200);
  };
  const stopPhaseTimer = () => {
    clearInterval(phaseTimer.current);
    phaseTimer.current = null;
  };

  // ── Detect vertical via DocumentClassifierAgent backend ────────────────────
  const detectVertical = async (selectedFile) => {
    setDetecting(true);
    setDetection(null);
    setConfirmedVertical(null);
    setShowOverride(false);
    setShowSummaryDetail(false);
    startPhaseTimer();

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await fetch(
        `${apiBase}/detect-vertical?tenant_id=${tenantId}`,
        { method: 'POST', body: formData }
      );

      if (!res.ok) throw new Error(`Detection failed: ${res.statusText}`);
      const data = await res.json();
      setDetection(data);
      setConfirmedVertical(data.vertical);
      setVertical(data.vertical);
    } catch (err) {
      console.error('Auto-detect failed:', err);
      setDetection({
        vertical: vertical || 'governance',
        confidence: 'LOW',
        ai_suggestion: 'Could not reach the detection service. Please select the document type manually.',
        summary: {},
        meta: {},
      });
      setConfirmedVertical(vertical || 'governance');
    } finally {
      stopPhaseTimer();
      setDetecting(false);
    }
  };

  // ── India AI Fellowship 1-Click Benchmark Loader ─────────────────────────
  const handleLoadBenchmark = async (benchmarkId) => {
    try {
      setLoadingBenchmark(benchmarkId);
      const res = await fetch(`${apiBase}/benchmarks/load?benchmark_id=${benchmarkId}&tenant_id=${tenantId}`, {
        method: 'POST'
      });
      let data = {};
      try {
        data = await res.json();
      } catch (jsonErr) {
        const textErr = await res.text().catch(() => '');
        throw new Error(textErr || `Server returned HTTP ${res.status}`);
      }
      if (!res.ok) {
        throw new Error(data.detail || "Failed to load benchmark.");
      }
      toast.success("Benchmark Loaded!", `Successfully indexed: ${data.display_title || data.doc_name}`);
      fetchDocuments();
    } catch (err) {
      toast.error("Benchmark Load Error", err.message);
    } finally {
      setLoadingBenchmark(null);
    }
  };

  // ── File handling ──────────────────────────────────────────────────────────
  const handleFile = (selectedFile) => {
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    const supported = ['pdf', 'png', 'jpg', 'jpeg', 'txt', 'csv', 'docx'];
    if (!supported.includes(ext)) {
      setError('Unsupported file type. Supported: PDF, PNG, JPG, TXT, CSV, DOCX');
      return;
    }
    setFile(selectedFile);
    setError(null);
    detectVertical(selectedFile);
  };

  const handleDrag = (e) => {
    e.preventDefault(); e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files?.[0]) handleFile(e.target.files[0]);
  };

  // ── Override ───────────────────────────────────────────────────────────────
  // NOTE: Do NOT call setVertical here — it triggers an AppContext re-render
  // which re-applies animate-fade-in on the detection card, making it look like
  // the selection didn't register. confirmedVertical is the sole source of truth
  // for the ingest call; setVertical only needs to be set on final confirm.
  const handleOverride = (v) => {
    setConfirmedVertical(v);
    // Close dropdown after a brief delay so user sees the checkmark move
    setTimeout(() => setShowOverride(false), 300);
  };

  // ── Re-detect ──────────────────────────────────────────────────────────────
  const handleRedetect = () => {
    if (file) detectVertical(file);
  };

  // ── Ingest ─────────────────────────────────────────────────────────────────
  const onUpload = async () => {
    if (!file || !confirmedVertical) return;
    setUploading(true);
    setError(null);
    try {
      // Sync context vertical with confirmed choice right before upload
      setVertical(confirmedVertical);
      await uploadDocument(file, confirmedVertical);
      toast.success("Ingestion Started", `"${file.name}" is being processed in the background.`);
      setFile(null);
      setDetection(null);
      setConfirmedVertical(null);
      setShowSummaryDetail(false);
    } catch (err) {
      setError(err.message);
      toast.error("Upload Failed", err.message);
    } finally {
      setUploading(false);
    }
  };

  // ── Delete ─────────────────────────────────────────────────────────────────
  const handleDelete = async (docId) => {
    if (!window.confirm('Delete this document? All associated chunks and graph nodes will be removed.')) return;
    try {
      const res = await fetch(`${apiBase}/documents/${docId}?tenant_id=${tenantId}`, { method: 'DELETE' });
      if (res.ok) {
        toast.success("Document Purged", "Document and associated indexing nodes deleted.");
        fetchDocuments();
      } else {
        const data = await res.json().catch(() => ({}));
        const errMsg = `Delete failed: ${data.detail || res.statusText}`;
        setError(errMsg);
        toast.error("Deletion Failed", errMsg);
      }
    } catch (err) {
      const errMsg = `Delete failed: ${err.message}`;
      setError(errMsg);
      toast.error("Deletion Failed", errMsg);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('WARNING: This will delete ALL documents. This cannot be undone.')) return;
    try {
      await Promise.all(documents.map(doc =>
        fetch(`${apiBase}/documents/${doc.id}?tenant_id=${tenantId}`, { method: 'DELETE' })
      ));
      toast.success("Vault Cleared", "All documents purged successfully.");
      fetchDocuments();
    } catch (err) {
      setError(`Clear all failed: ${err.message}`);
      toast.error("Purge Failed", err.message);
    }
  };

  // ── Computed helpers ───────────────────────────────────────────────────────
  const activeMeta = VERTICAL_META[confirmedVertical] || VERTICAL_META.governance;
  const detectedMeta = detection ? (VERTICAL_META[detection.vertical] || VERTICAL_META.governance) : null;
  const confStyle = detection ? (CONFIDENCE_STYLE[detection.confidence] || CONFIDENCE_STYLE.MEDIUM) : null;
  const summary = detection?.summary || {};
  const altMeta = detection?.alternative_vertical
    ? (VERTICAL_META[detection.alternative_vertical] || null)
    : null;
  const ActiveIcon = activeMeta.icon;
  const isOverridden = detection && confirmedVertical !== detection.vertical;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="vault-container animate-fade-in">

      <div className="vault-header">
        <h1>Document Vault</h1>
        <p className="subtitle">
          Upload a document — JanSetu AI will automatically summarise and classify its type, then ask for your confirmation before indexing.
        </p>
      </div>

      <div className="vault-content">
        <div className="upload-section glass-panel">

          {/* ── India AI Fellowship 1-Click Benchmark Loader ── */}
          <div className="benchmark-bar animate-fade-in" style={{
            marginBottom: '18px',
            padding: '12px 14px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, rgba(14,165,233,0.08) 0%, rgba(139,92,246,0.08) 100%)',
            border: '1px solid rgba(14,165,233,0.25)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={15} color="#0ea5e9" />
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f8fafc', letterSpacing: '0.3px' }}>
                  🇮🇳 INDIA AI FELLOWSHIP BENCHMARK EVALUATION (1-CLICK LOAD)
                </span>
              </div>
              <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Reviewer Quick-Start</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: '#cbd5e1', margin: '0 0 8px', lineHeight: 1.4 }}>
              Click any official Government of India benchmark document below to instantly ingest, chunk, and index into the knowledge graph:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(14,165,233,0.18)', border: '1px solid rgba(14,165,233,0.4)', color: '#38bdf8',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('pm_kisan')}
              >
                {loadingBenchmark === 'pm_kisan' ? <Loader size={12} className="spin" /> : <Landmark size={12} />}
                🏛️ PM-KISAN Guidelines (Governance)
              </button>

              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(139,92,246,0.18)', border: '1px solid rgba(139,92,246,0.4)', color: '#c4b5fd',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('sc_judgment')}
              >
                {loadingBenchmark === 'sc_judgment' ? <Loader size={12} className="spin" /> : <Gavel size={12} />}
                ⚖️ Supreme Court Bail Ruling (Law &amp; Justice)
              </button>

              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(16,185,129,0.18)', border: '1px solid rgba(16,185,129,0.4)', color: '#6ee7b7',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('ayushman_bharat')}
              >
                {loadingBenchmark === 'ayushman_bharat' ? <Loader size={12} className="spin" /> : <ShieldCheck size={12} />}
                🏥 Ayushman Bharat PM-JAY Policy (Governance)
              </button>

              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(245,158,11,0.18)', border: '1px solid rgba(245,158,11,0.4)', color: '#fcd34d',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('tamil_pattiram')}
              >
                {loadingBenchmark === 'tamil_pattiram' ? <Loader size={12} className="spin" /> : <FileText size={12} />}
                📜 Tamil Land Deed / பத்திரம் (Land Governance)
              </button>

              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(239,68,68,0.18)', border: '1px solid rgba(239,68,68,0.4)', color: '#fca5a5',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('cyber_fir')}
              >
                {loadingBenchmark === 'cyber_fir' ? <Loader size={12} className="spin" /> : <ShieldAlert size={12} />}
                🛡️ Cyber Fraud & Zero-FIR Guide (Citizen Rights)
              </button>

              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(168,85,247,0.18)', border: '1px solid rgba(168,85,247,0.4)', color: '#d8b4fe',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('tenancy_act')}
              >
                {loadingBenchmark === 'tenancy_act' ? <Loader size={12} className="spin" /> : <Briefcase size={12} />}
                🏠 Model Tenancy & Rent Protection (Urban Housing)
              </button>

              <button
                type="button"
                className="hover-lift"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(236,72,153,0.18)', border: '1px solid rgba(236,72,153,0.4)', color: '#fbcfe8',
                  fontSize: '0.78rem', fontWeight: 500, cursor: 'pointer'
                }}
                disabled={loadingBenchmark !== null}
                onClick={() => handleLoadBenchmark('senior_citizen')}
              >
                {loadingBenchmark === 'senior_citizen' ? <Loader size={12} className="spin" /> : <Users size={12} />}
                👴 Senior Citizen Property Revocation (Elder Care)
              </button>
            </div>
          </div>

          {/* ── Drop zone ── */}
          {!file && (
            <div
              className={`dropzone ${dragActive ? 'active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => inputRef.current.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.docx"
                onChange={handleChange}
                style={{ display: 'none' }}
              />
              <UploadCloud size={48} className="dropzone-icon" />
              <h3>Drag &amp; Drop a file here</h3>
              <p>PDF, DOCX, TXT, CSV, PNG, JPG supported</p>
            </div>
          )}

          {/* ── Hidden input when file is selected (for "change file") ── */}
          {file && (
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.docx"
              onChange={handleChange}
              style={{ display: 'none' }}
            />
          )}

          {/* ── Detecting spinner ── */}
          {detecting && (
            <div className="detection-card detecting animate-fade-in">
              <div className="detection-spinner-row">
                <Loader size={20} className="spin" style={{ color: 'var(--accent-primary)' }} />
                <div className="detection-phases">
                  <span className="detection-analyzing-text">
                    {DETECT_PHASES[detectPhase].label}
                  </span>
                  <div className="phase-dots">
                    {DETECT_PHASES.map((p) => (
                      <span
                        key={p.id}
                        className={`phase-dot ${p.id <= detectPhase ? 'active' : ''}`}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="detection-file-name" style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>
                {file?.name}
              </div>
            </div>
          )}

          {/* ── Detection result card ── */}
          {!detecting && detection && file && (
            <div
              className="detection-card"
              style={{ borderColor: activeMeta.border, background: activeMeta.bg, transition: 'border-color 0.3s ease, background 0.3s ease' }}
            >
              {/* Header: AI badge + confidence */}
              <div className="detection-header">
                <div className="detection-ai-badge">
                  <Sparkles size={12} />
                  <span>AI Classified</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {isOverridden && (
                    <span className="override-chip">Manually overridden</span>
                  )}
                  <span
                    className="detection-confidence-badge"
                    style={{ color: confStyle.color, background: confStyle.bg }}
                  >
                    {confStyle.label}
                  </span>
                </div>
              </div>

              {/* Detected type */}
              <div className="detection-type-row">
                <div
                  className="detection-type-icon-wrap"
                  style={{ background: activeMeta.bg, borderColor: activeMeta.border }}
                >
                  <ActiveIcon size={24} style={{ color: activeMeta.color }} />
                </div>
                <div className="detection-type-info">
                  <span className="detection-type-label" style={{ color: activeMeta.color }}>
                    {activeMeta.label}
                  </span>
                  {summary.document_type && (
                    <span className="detection-doc-type-sub">
                      Detected as: <strong>{summary.document_type}</strong>
                    </span>
                  )}
                </div>
              </div>

              {/* AI Suggestion paragraph */}
              {detection.ai_suggestion && (
                <div className="ai-suggestion-block" style={{ borderLeftColor: activeMeta.color }}>
                  <div className="ai-suggestion-header">
                    <Sparkles size={13} style={{ color: activeMeta.color }} />
                    <span>AI Suggestion</span>
                  </div>
                  <p className="ai-suggestion-text">{detection.ai_suggestion}</p>
                </div>
              )}

              {/* Alternative vertical hint */}
              {altMeta && !isOverridden && (
                <div className="alt-vertical-hint">
                  <Info size={13} />
                  <span>
                    Could also be&nbsp;
                    <strong style={{ color: altMeta.color }}>{altMeta.label}</strong>
                    &nbsp;— use "Change type" below if needed.
                  </span>
                </div>
              )}

              {/* Document summary (collapsible) */}
              {(summary.main_topics?.length > 0 || summary.key_entities?.length > 0 || summary.intended_audience) && (
                <div className="summary-section">
                  <button
                    className="summary-toggle"
                    onClick={() => setShowSummaryDetail(v => !v)}
                  >
                    <FileText size={13} />
                    <span>Document Summary</span>
                    <ChevronDown
                      size={13}
                      style={{ transform: showSummaryDetail ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                    />
                  </button>

                  {showSummaryDetail && (
                    <div className="summary-detail animate-fade-in">
                      {summary.intended_audience && (
                        <div className="summary-row">
                          <Target size={12} className="summary-row-icon" />
                          <span className="summary-row-label">Audience:</span>
                          <span className="summary-row-value">{summary.intended_audience}</span>
                        </div>
                      )}
                      {summary.language_style && (
                        <div className="summary-row">
                          <FileText size={12} className="summary-row-icon" />
                          <span className="summary-row-label">Style:</span>
                          <span className="summary-row-value">{summary.language_style}</span>
                        </div>
                      )}
                      {summary.main_topics?.length > 0 && (
                        <div className="summary-row summary-row-wrap">
                          <Tag size={12} className="summary-row-icon" />
                          <span className="summary-row-label">Topics:</span>
                          <div className="summary-tags">
                            {summary.main_topics.map((t, i) => (
                              <span key={i} className="summary-tag" style={{ background: activeMeta.bg, color: activeMeta.color }}>
                                {t}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {summary.key_entities?.length > 0 && (
                        <div className="summary-row summary-row-wrap">
                          <Tag size={12} className="summary-row-icon" />
                          <span className="summary-row-label">Entities:</span>
                          <div className="summary-tags">
                            {summary.key_entities.slice(0, 8).map((e, i) => (
                              <span key={i} className="summary-tag entity-tag">
                                {e}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {summary.excerpt_highlights?.length > 0 && (
                        <div className="summary-excerpts">
                          <span className="summary-row-label">Key excerpts:</span>
                          {summary.excerpt_highlights.map((ex, i) => (
                            <blockquote key={i} className="summary-excerpt">"{ex}"</blockquote>
                          ))}
                        </div>
                      )}
                      {detection.meta?.pages_read != null && (
                        <div className="summary-meta-row">
                          <span>📄 {detection.meta.pages_read} page(s) read</span>
                          {detection.meta.chars_used > 0 && (
                            <span>· {detection.meta.chars_used.toLocaleString()} chars analysed</span>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* File info row */}
              <div className="detection-file-row">
                <File size={14} style={{ color: 'var(--text-tertiary)' }} />
                <span className="detection-file-name">{file.name}</span>
                <span className="detection-file-size">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>

              {/* Override picker */}
              <div className="detection-actions">
                <div className="override-wrapper">
                  <button
                    className="override-toggle"
                    onClick={() => setShowOverride(v => !v)}
                  >
                    <span>Not right? Change type</span>
                    <ChevronDown
                      size={13}
                      style={{ transform: showOverride ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                    />
                  </button>

                  {showOverride && (
                    <div className="override-dropdown animate-fade-in">
                      {Object.entries(VERTICAL_META).map(([key, meta]) => {
                        const Icon = meta.icon;
                        return (
                          <button
                            key={key}
                            className={`override-option ${confirmedVertical === key ? 'active' : ''}`}
                            onClick={() => handleOverride(key)}
                            style={confirmedVertical === key ? { background: meta.bg, borderColor: meta.border } : {}}
                          >
                            <Icon size={15} style={{ color: meta.color }} />
                            <div className="override-option-text">
                              <span className="override-option-label">{meta.label}</span>
                              <span className="override-option-desc">{meta.desc}</span>
                            </div>
                            {confirmedVertical === key && (
                              <CheckCircle2 size={13} style={{ color: meta.color, marginLeft: 'auto', flexShrink: 0 }} />
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* CTA row */}
                <div className="detection-cta-row">
                  <button
                    className="ghost-button"
                    title="Re-run detection"
                    onClick={handleRedetect}
                    disabled={detecting}
                  >
                    <RefreshCw size={14} />
                    Re-detect
                  </button>
                  <button
                    className="ghost-button"
                    onClick={() => { setFile(null); setDetection(null); setConfirmedVertical(null); inputRef.current.click(); }}
                  >
                    Change file
                  </button>
                  <button
                    className="primary-button confirm-ingest-btn hover-lift"
                    onClick={onUpload}
                    disabled={uploading}
                  >
                    {uploading
                      ? <><Loader className="spin" size={16} /> Processing…</>
                      : <><CheckCircle2 size={16} /> Confirm &amp; Ingest</>
                    }
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="alert error animate-fade-in">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {/* Ongoing ingestions */}
          {activeJobs.length > 0 && (
            <div className="ongoing-jobs-panel animate-fade-in">
              <h4 className="ongoing-title">Ongoing Ingestions</h4>
              <div className="ongoing-jobs-list">
                {activeJobs.map(job => (
                  <div key={job.id} className={`ongoing-job-card ${job.status}`}>
                    <div className="ongoing-job-header">
                      <div className="ongoing-job-title-row">
                        {job.status === 'pending' && <Clock size={16} className="text-tertiary" />}
                        {job.status === 'running' && <Loader size={16} className="spin text-accent" />}
                        {job.status === 'completed' && <CheckCircle2 size={16} className="text-success" />}
                        {job.status === 'failed' && <XCircle size={16} className="text-error" />}
                        <span className="job-name-text" title={job.name}>{job.name}</span>
                      </div>
                      <span className={`status-badge ${job.status}`}>{job.status}</span>
                    </div>
                    {job.status === 'running' && (
                      <div className="ongoing-job-progress">
                        <div className="progress-bar-fill running" />
                      </div>
                    )}
                    <div className="ongoing-job-footer">
                      <span className="job-vertical-tag">{job.vertical}</span>
                      {job.status === 'completed' && (
                        <span className="job-desc-success">Created {job.chunksCreated} chunks.</span>
                      )}
                      {job.status === 'failed' && (
                        <span className="job-desc-error" title={job.error}>Failed: {job.error}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Documents panel ── */}
        <div className="docs-section glass-panel">
          <div className="section-header-row">
            <h3>Your Documents</h3>
            {documents.length > 0 && (
              <button className="clear-all-btn" onClick={handleClearAll}>
                <Trash2 size={14} /> Clear All
              </button>
            )}
          </div>

          {loadingDocs ? (
            <div className="skeleton-list">
              {[1, 2, 3].map(i => (
                <div key={i} className="skeleton-item">
                  <div className="skeleton-icon" />
                  <div className="skeleton-details">
                    <div className="skeleton-title" />
                    <div className="skeleton-meta" />
                  </div>
                </div>
              ))}
            </div>
          ) : documents.length === 0 ? (
            <p className="empty-state">No documents found. Upload one to get started!</p>
          ) : (
            <div className="doc-list">
              {documents.map(doc => {
                const meta = VERTICAL_META[doc.vertical] || VERTICAL_META.governance;
                const Icon = meta.icon;
                return (
                  <div key={doc.id} className="doc-item animate-slide-up">
                    <div className="doc-icon" style={{ color: meta.color }}>
                      <Icon size={18} />
                    </div>
                    <div className="doc-details">
                      <span className="doc-name">{doc.name}</span>
                      <span className="doc-meta">
                        <span className="doc-vertical-pill" style={{ background: meta.bg, color: meta.color }}>
                          {meta.label}
                        </span>
                        &nbsp;•&nbsp;{doc.chunks_count} chunks
                      </span>
                    </div>
                    <div className="doc-item-actions" style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <button 
                        className="action-icon-btn hover-lift" 
                        title="View Document Chunks & Citations"
                        onClick={() => openDocViewer(doc)}
                        style={{ padding: '6px 8px', borderRadius: '6px', border: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem' }}
                      >
                        <Eye size={14} />
                        <span>View</span>
                      </button>

                      {['law', 'judgment'].includes(doc.vertical) && (
                        <button 
                          className="action-icon-btn hover-lift" 
                          title="Open Human-in-the-Loop Risk Audit Workbench"
                          onClick={() => openAuditWorkbench(doc)}
                          style={{ padding: '6px 8px', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.3)', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', fontWeight: 600 }}
                        >
                          <ShieldAlert size={14} />
                          <span>Audit</span>
                        </button>
                      )}

                      <button className="delete-btn" onClick={() => handleDelete(doc.id)} title="Delete Document">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── Phase 3: Human-in-the-Loop Audit Workbench Modal ──────────────────── */}
      {selectedAuditDoc && (
        <div className="modal-backdrop" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '20px'
        }}>
          <div className="glass-panel animate-slide-up" style={{
            background: 'var(--bg-secondary, #1e293b)', width: '100%', maxWidth: '900px',
            maxHeight: '90vh', borderRadius: '14px', border: '1px solid var(--border-subtle)',
            display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 20px 40px rgba(0,0,0,0.4)'
          }}>
            {/* Modal Header */}
            <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldAlert size={20} color="#ef4444" />
                  <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>Risk & Red-Flag Audit Workbench</h3>
                  {auditReport && (
                    <span style={{
                      padding: '2px 10px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 800,
                      background: auditReport.document_risk_level === 'HIGH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                      color: auditReport.document_risk_level === 'HIGH' ? '#ef4444' : '#f59e0b',
                      border: `1px solid ${auditReport.document_risk_level === 'HIGH' ? '#ef4444' : '#f59e0b'}`
                    }}>
                      {auditReport.document_risk_level} RESIDUAL RISK
                    </span>
                  )}
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Document: <strong>{selectedAuditDoc.name}</strong> • Tenant: <code>{tenantId}</code>
                </p>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  className="hover-lift"
                  onClick={() => handleExportReport('html')}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: 'var(--accent-primary, #6366f1)', color: '#fff', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 600 }}
                >
                  <Printer size={14} />
                  <span>Print / Save PDF Report</span>
                </button>
                <button
                  className="hover-lift"
                  onClick={() => handleExportReport('markdown')}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.08)', color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem' }}
                >
                  <ExternalLink size={14} />
                  <span>Markdown</span>
                </button>
                <button
                  onClick={() => { setSelectedAuditDoc(null); setAuditReport(null); }}
                  style={{ background: 'none', border: 'none', color: 'var(--text-tertiary)', fontSize: '1.4rem', cursor: 'pointer', marginLeft: '8px', lineHeight: 1 }}
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
              {loadingAudit ? (
                <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  <Loader className="spin" size={28} style={{ margin: '0 auto 12px' }} />
                  <p>Analyzing document risk nodes & human review trail...</p>
                </div>
              ) : !auditReport || !auditReport.red_flags || auditReport.red_flags.length === 0 ? (
                <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  <CheckCircle2 size={36} color="#10b981" style={{ margin: '0 auto 12px' }} />
                  <h4>No Active Red Flags Found</h4>
                  <p style={{ fontSize: '0.85rem' }}>This document passed the 10-point autonomous legal risk scan cleanly.</p>
                </div>
              ) : (
                <div>
                  {/* Progress Metrics Bar */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
                    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
                      <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>{auditReport.red_flags.length}</div>
                      <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-tertiary)', fontWeight: 700 }}>Total Flags</div>
                    </div>
                    <div style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
                      <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981' }}>
                        {auditReport.red_flags.filter(f => f.review_status === 'ACCEPTED').length}
                      </div>
                      <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#10b981', fontWeight: 700 }}>Accepted</div>
                    </div>
                    <div style={{ background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
                      <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ef4444' }}>
                        {auditReport.red_flags.filter(f => f.review_status === 'NEEDS_REMEDIATION').length}
                      </div>
                      <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#ef4444', fontWeight: 700 }}>Remediation</div>
                    </div>
                    <div style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
                      <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f59e0b' }}>
                        {auditReport.red_flags.filter(f => f.review_status === 'PENDING').length}
                      </div>
                      <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#f59e0b', fontWeight: 700 }}>Pending Review</div>
                    </div>
                  </div>

                  {/* List of Flags */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {auditReport.red_flags.map((flag, idx) => (
                      <div key={flag.id || idx} style={{
                        background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)',
                        borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <div>
                            <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginRight: '10px' }}>
                              {flag.type}
                            </span>
                            <span style={{
                              padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700,
                              background: flag.severity === 'HIGH' ? '#ef4444' : (flag.severity === 'MEDIUM' ? '#f59e0b' : '#10b981'),
                              color: '#fff'
                            }}>
                              {flag.severity}
                            </span>
                            <span style={{ marginLeft: '10px', fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                              Ref: <strong>{flag.clause_ref || `Page ${flag.page || '?'}`}</strong>
                            </span>
                          </div>
                          <span style={{
                            padding: '3px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700,
                            background: flag.review_status === 'ACCEPTED' ? 'rgba(16,185,129,0.15)' : (flag.review_status === 'DISMISSED' ? 'rgba(255,255,255,0.08)' : (flag.review_status === 'NEEDS_REMEDIATION' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)')),
                            color: flag.review_status === 'ACCEPTED' ? '#10b981' : (flag.review_status === 'DISMISSED' ? '#94a3b8' : (flag.review_status === 'NEEDS_REMEDIATION' ? '#ef4444' : '#f59e0b')),
                            border: `1px solid ${flag.review_status === 'ACCEPTED' ? 'rgba(16,185,129,0.3)' : (flag.review_status === 'DISMISSED' ? 'rgba(255,255,255,0.15)' : (flag.review_status === 'NEEDS_REMEDIATION' ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'))}`
                          }}>
                            {flag.review_status || 'PENDING'}
                          </span>
                        </div>

                        {flag.excerpt && (
                          <blockquote style={{
                            margin: '4px 0', padding: '8px 12px', background: 'rgba(0,0,0,0.2)',
                            borderLeft: '3px solid #6366f1', borderRadius: '4px', fontStyle: 'italic',
                            fontSize: '0.82rem', color: 'var(--text-secondary)'
                          }}>
                            "{flag.excerpt}"
                          </blockquote>
                        )}

                        <div style={{ fontSize: '0.82rem', color: 'var(--accent-primary, #818cf8)' }}>
                          <strong>Recommendation: </strong> {flag.recommendation || 'Standard legal renegotiation required.'}
                        </div>

                        {/* Interactive Reviewer Actions */}
                        <div style={{ marginTop: '6px', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <input
                              type="text"
                              placeholder="Add legal reviewer rationale/note..."
                              value={actionNotes[flag.id] !== undefined ? actionNotes[flag.id] : (flag.review_note || '')}
                              onChange={(e) => setActionNotes({ ...actionNotes, [flag.id]: e.target.value })}
                              style={{
                                flex: 1, padding: '6px 10px', borderRadius: '6px', background: 'rgba(0,0,0,0.2)',
                                border: '1px solid var(--border-subtle)', color: 'var(--text-primary)', fontSize: '0.8rem'
                              }}
                            />
                            <button
                              className="hover-lift"
                              onClick={() => handleReviewAction(flag.id, 'accept_risk')}
                              style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(16,185,129,0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.3)', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 700 }}
                            >
                              ✓ Accept
                            </button>
                            <button
                              className="hover-lift"
                              onClick={() => handleReviewAction(flag.id, 'dismiss')}
                              style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)', cursor: 'pointer', fontSize: '0.75rem' }}
                            >
                              ✕ Dismiss
                            </button>
                            <button
                              className="hover-lift"
                              onClick={() => handleReviewAction(flag.id, 'needs_remediation')}
                              style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.3)', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 700 }}
                            >
                              ⚠️ Remediate
                            </button>
                          </div>

                          {flag.reviewed_by && (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                              Stamped by <strong>{flag.reviewed_by}</strong> on {new Date(flag.reviewed_at).toLocaleString()}
                              {flag.review_note ? ` — "${flag.review_note}"` : ''}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Phase 3: Document Citation & Chunk Inspector Modal ───────────────── */}
      {selectedViewerDoc && (
        <div className="modal-backdrop" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '20px'
        }}>
          <div className="glass-panel animate-slide-up" style={{
            background: 'var(--bg-secondary, #1e293b)', width: '100%', maxWidth: '850px',
            maxHeight: '90vh', borderRadius: '14px', border: '1px solid var(--border-subtle)',
            display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 20px 40px rgba(0,0,0,0.4)'
          }}>
            <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Eye size={20} color="var(--accent-primary, #6366f1)" />
                  <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>Document Chunks & Citation Viewer</h3>
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {selectedViewerDoc.name} • {viewerChunks.length} indexed chunks
                </p>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  className="hover-lift"
                  onClick={() => window.open(`${apiBase}/documents/${selectedViewerDoc.id}/pdf`, '_blank')}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: 'var(--accent-primary, #6366f1)', color: '#fff', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 600 }}
                >
                  <ExternalLink size={14} />
                  <span>Open Full PDF</span>
                </button>
                <button
                  onClick={() => { setSelectedViewerDoc(null); setViewerChunks([]); }}
                  style={{ background: 'none', border: 'none', color: 'var(--text-tertiary)', fontSize: '1.4rem', cursor: 'pointer', marginLeft: '8px', lineHeight: 1 }}
                >
                  ✕
                </button>
              </div>
            </div>

            <div style={{ padding: '12px 24px', borderBottom: '1px solid var(--border-subtle)' }}>
              <input
                type="text"
                placeholder="Filter indexed chunks by clause, term, or keyword..."
                value={viewerSearch}
                onChange={(e) => setViewerSearch(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)', fontSize: '0.85rem' }}
              />
            </div>

            <div style={{ padding: '16px 24px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {loadingViewer ? (
                <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  <Loader className="spin" size={28} style={{ margin: '0 auto 12px' }} />
                  <p>Loading document knowledge chunks...</p>
                </div>
              ) : viewerChunks.length === 0 ? (
                <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '40px 0' }}>No chunks found for this document.</p>
              ) : (
                viewerChunks
                  .filter(c => !viewerSearch || c.text?.toLowerCase().includes(viewerSearch.toLowerCase()) || (c.clause_ref && c.clause_ref.toLowerCase().includes(viewerSearch.toLowerCase())))
                  .map((chunk, i) => (
                    <div key={chunk.id || i} style={{
                      background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-subtle)',
                      borderRadius: '8px', padding: '12px 14px'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                        <span style={{ fontWeight: 700, color: '#818cf8' }}>
                          Page {chunk.page || 1} {chunk.clause_ref ? `• ${chunk.clause_ref}` : (chunk.section ? `• ${chunk.section}` : '')}
                        </span>
                        <span>ID: <code>{chunk.id}</code></span>
                      </div>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                        {chunk.text}
                      </p>
                    </div>
                  ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Vault;
