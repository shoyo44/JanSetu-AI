import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles, Loader2, Trash2, File, Loader, AlertCircle, Zap, Search, FileText, Scale, ChevronDown, Landmark, Mic, MicOff, X, ArrowRightLeft, BookOpen, ShieldAlert } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useApp } from '../context/AppContext';
import { useToast } from '../components/Toast';

import './Chat.css';

const cleanContent = (content) => {
  if (!content) return "";
  let text = content.trim();
  
  // Strip markdown JSON code fence wrappers
  text = text.replace(/^```(?:json)?\s*/i, "");
  text = text.replace(/\s*```$/, "");
  text = text.trim();
  
  if (text.startsWith("{") && text.endsWith("}")) {
    try {
      const parsed = JSON.parse(text);
      if (parsed && parsed.answer) {
        return parsed.answer;
      }
    } catch (e) {}
  }
  
  try {
    const match = text.match(/"answer"\s*:\s*"([^"]*)$/);
    if (match && match[1]) {
      return match[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
    }
    
    const matchComplete = text.match(/"answer"\s*:\s*"([^"]*)"/);
    if (matchComplete && matchComplete[1]) {
      return matchComplete[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
    }
  } catch (e) {}
  
  return content;
};

const Chat = () => {
  const { 
    vertical, setVertical, documents, activeJobs, tenantId, apiBase, wsBase,
    temperature, topK, scoreFloor 
  } = useApp();
  const toast = useToast();
  const [expandedEvidence, setExpandedEvidence] = useState({});
  const inputRef = useRef(null);
  
  const toggleEvidence = (idx) => {
    setExpandedEvidence(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your JanSetu AI Intelligence Agent for the IndiaAI Fellowship. I can help you analyze Public Governance Gazettes, citizen welfare schemes, Supreme Court judgments, and statutory criminal concordance. What should we look into today?' }
  ]);
  const [dbHistoryEnabled, setDbHistoryEnabled] = useState(false);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // ── India AI: Speech-to-Text Voice Query State ─────────────────────────────
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // ── India AI: Statutory Concordance Quick Converter Modal State ────────────
  const [showConcordanceModal, setShowConcordanceModal] = useState(false);
  const [showAidModal, setShowAidModal] = useState(false);
  const [concordanceQuery, setConcordanceQuery] = useState('IPC 420');
  const [concordanceResults, setConcordanceResults] = useState([]);
  const [loadingConcordance, setLoadingConcordance] = useState(false);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-IN';
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setInput(transcript);
      };
      recognition.onerror = (event) => {
        console.warn("Speech recognition event error:", event.error);
        setIsListening(false);
      };
      recognition.onend = () => {
        setIsListening(false);
      };
      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      toast.warning("Voice Input", "Your browser does not support Speech Recognition. Use Google Chrome or MS Edge.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        toast.info("Microphone Active", "Speak your question in English or Hindi...");
      } catch (err) {
        console.warn("Speech start exception:", err);
      }
    }
  };

  const handleSearchConcordance = async (queryParam) => {
    const term = queryParam || concordanceQuery;
    if (!term || !term.trim()) return;
    try {
      setLoadingConcordance(true);
      const res = await fetch(`${apiBase}/statutory/concordance?query=${encodeURIComponent(term)}`);
      const data = await res.json();
      setConcordanceResults(data.concordances || []);
    } catch (err) {
      toast.error("Lookup Failed", err.message);
    } finally {
      setLoadingConcordance(false);
    }
  };

  // Keyboard shortcut: Ctrl+K to focus input
  useEffect(() => {
    const handleKey = (e) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  const scrollToBottom = () => {

    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Sync messages to localStorage (always runs as local fallback)
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_history_${vertical}`, JSON.stringify(messages));
    }
  }, [messages, vertical]);

  // Load chat history from MongoDB with LocalStorage fallback
  useEffect(() => {
    let active = true;
    const loadHistory = async () => {
      try {
        const res = await fetch(`${apiBase}/history?tenant_id=${tenantId}&vertical=${vertical}`);
        if (!res.ok) throw new Error("History DB offline");
        const data = await res.json();
        if (active) {
          if (data.messages && data.messages.length > 0) {
            setMessages(data.messages);
          } else {
            setMessages([
              { role: 'assistant', content: `Hello! I am your Aura AI Agent for the ${vertical} workspace. I can help you analyze documents, find compliance gaps, or summarize legal clauses. What should we look into today?` }
            ]);
          }
          setDbHistoryEnabled(true);
        }
      } catch (err) {
        console.warn("MongoDB Atlas History DB offline, using LocalStorage:", err);
        if (active) {
          setDbHistoryEnabled(false);
          const saved = localStorage.getItem(`chat_history_${vertical}`);
          if (saved) {
            try {
              setMessages(JSON.parse(saved));
            } catch (e) {
              console.error("Failed to load local history:", e);
            }
          } else {
            setMessages([
              { role: 'assistant', content: `Hello! I am your Aura AI Agent for the ${vertical} workspace. I can help you analyze documents, find compliance gaps, or summarize legal clauses. What should we look into today?` }
            ]);
          }
        }
      }
    };

    loadHistory();
    return () => { active = false; };
  }, [apiBase, tenantId, vertical]);

  // Filter documents and jobs matching current vertical
  const activeDocs = vertical === 'auto'
    ? documents
    : documents.filter(doc => doc.vertical === vertical);

  const ongoingJobs = vertical === 'auto'
    ? activeJobs.filter(job => job.status === 'pending' || job.status === 'running')
    : activeJobs.filter(job => job.vertical === vertical && (job.status === 'pending' || job.status === 'running'));

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const queryText = input;
    const userMessage = { role: 'user', content: queryText };
    setMessages(prev => [...prev, userMessage]);

    setInput('');
    setIsTyping(true);

    // Create a placeholder for the assistant response
    setMessages(prev => [...prev, { role: 'assistant', content: '', isStreaming: true }]);

    try {
      const socket = new WebSocket(`${wsBase}/ws/query`);
      
      socket.onopen = () => {
        socket.send(JSON.stringify({
          question: input,
          tenant_id: tenantId,
          vertical: vertical,
          use_hyde: true,
          temperature: temperature,
          top_k: topK,
          score_floor: scoreFloor
        }));
      };


      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'status') {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;
            newMessages[lastIdx] = {
              ...newMessages[lastIdx],
              statusText: data.data
            };
            return newMessages;
          });
        } else if (data.type === 'chunks') {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;
            newMessages[lastIdx] = {
              ...newMessages[lastIdx],
              evidence: data.data
            };
            return newMessages;
          });
        } else if (data.type === 'token') {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;
            newMessages[lastIdx] = {
              ...newMessages[lastIdx],
              content: newMessages[lastIdx].content + data.data
            };
            return newMessages;
          });


        } else if (data.type === 'done') {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;
            newMessages[lastIdx] = {
              ...newMessages[lastIdx],
              ...data.data,
              isStreaming: false
            };
            return newMessages;
          });
          socket.close();
          setIsTyping(false);

          // Sync user and assistant responses to MongoDB with the resolved vertical
          if (dbHistoryEnabled) {
            try {
              const resolvedVertical = data.data.vertical || vertical;
              const assistantContent = data.data.answer || data.data.content || '';
              
              // 1. Sync User Message
              fetch(`${apiBase}/history/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  tenant_id: tenantId,
                  vertical: resolvedVertical,
                  role: 'user',
                  content: queryText
                })
              }).catch(err => console.warn("Failed to sync user message:", err));

              // 2. Sync Assistant Message
              fetch(`${apiBase}/history/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  tenant_id: tenantId,
                  vertical: resolvedVertical,
                  role: 'assistant',
                  content: assistantContent,
                  evidence: data.data.evidence || [],
                  citations: data.data.citations || [],
                  paper_title: data.data.paper_title,
                  authors: data.data.authors || [],
                  abstract_summary: data.data.abstract_summary
                })
              }).catch(err => console.warn("Failed to sync assistant message:", err));
              
            } catch (err) {
              console.warn("Failed to sync conversation messages:", err);
            }
          }

        } else if (data.type === 'error') {
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1].content = "Error: " + data.data;
            newMessages[newMessages.length - 1].isStreaming = false;
            return newMessages;
          });
          socket.close();
          setIsTyping(false);
        }
      };

      socket.onerror = (err) => {
        console.error("WS Error:", err);
        toast.error("Connection Error", "Failed to connect to RAG server. Make sure backend is running.");
        setIsTyping(false);
      };

    } catch (error) {
      console.error("Chat Error:", error);
      toast.error("Execution Error", "An unexpected error occurred during pipeline startup.");
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-page-layout animate-fade-in">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-info">
            <h1>Agentic Workspace</h1>
            <p className="subtitle">Context-aware multi-vertical analysis</p>
          </div>
          <div className="chat-actions">
            <button className="clear-chat-btn" onClick={async () => {
              if (dbHistoryEnabled) {
                try {
                  const res = await fetch(`${apiBase}/history?tenant_id=${tenantId}&vertical=${vertical}`, {
                    method: 'DELETE'
                  });
                  if (res.ok) {
                    toast.success("Chat History Cleared", "MongoDB session logs have been purged.");
                  } else {
                    toast.warning("Local Reset Only", "Failed to purge database chat logs, but cleared locally.");
                  }
                } catch (err) {
                  console.warn("Failed to clear database history:", err);
                  toast.warning("Local Reset Only", "Failed to purge database chat logs, but cleared locally.");
                }
              } else {
                toast.info("Cleared Local Session", "Local storage message log has been reset.");
              }
              localStorage.removeItem(`chat_history_${vertical}`);
              setMessages([{ role: 'assistant', content: `Hello! I am your Aura AI Agent for the ${vertical} workspace. I can help you analyze documents, find compliance gaps, or summarize legal clauses. What should we look into today?` }]);
            }}>
              <Trash2 size={14} /> Clear Chat
            </button>
            <button
              type="button"
              className="clear-chat-btn hover-lift"
              style={{ borderColor: 'rgba(139,92,246,0.35)', color: '#c4b5fd' }}
              onClick={() => {
                setShowConcordanceModal(true);
                handleSearchConcordance(concordanceQuery || "IPC 420");
              }}
              title="Indian Criminal Laws Statutory Transition (July 1, 2024)"
            >
              <Scale size={14} /> ⚖️ IPC ⇄ BNS
            </button>
            <button
              type="button"
              className="clear-chat-btn hover-lift"
              style={{ borderColor: 'rgba(245,158,11,0.35)', color: '#fbbf24' }}
              onClick={() => setShowAidModal(true)}
              title="Official Citizen Helplines & NALSA Legal Aid"
            >
              <ShieldAlert size={14} /> 🛡️ Citizen Helplines
            </button>
            <div className="vertical-selector-chat">
              <Sparkles size={14} />
              <select value={vertical} onChange={(e) => setVertical(e.target.value)}>
                <option value="auto">🧠 Auto-Route (AI)</option>
                <option value="governance">🏛️ Public Governance & Welfare Schemes</option>
                <option value="judgment">⚖️ Court Judgments & Case Precedents</option>
                <option value="law">📜 Statutory Law & Concordance</option>
              </select>
            </div>
          </div>


        </div>

        <div className="chat-messages glass-panel">
          {/* Welcome Hero — shown only when single welcome message exists */}
          {messages.length === 1 && messages[0].role === 'assistant' && !isTyping && (
            <div className="welcome-hero">
              <div className="welcome-logo-ring">
                <Zap size={32} />
              </div>
              <h2 className="welcome-title">IndiaAI Sovereign Intelligence Workspace</h2>
              <p className="welcome-subtitle">Analyze Indian Public Policy Guidelines, Welfare Yojanas, and Supreme Court Case Law with grounded citations.</p>
              <div className="quick-prompts">
                {[
                  { icon: Landmark, text: "What are the eligibility criteria and required documents for PM-KISAN?" },
                  { icon: Scale, text: "What is the ratio decidendi regarding regular bail under Section 439 CrPC (BNSS 483)?" },
                  { icon: FileText, text: "தமிழில் விடை: சொத்து யாருக்கு விற்கப்பட்டது மற்றும் கிரையத் தொகை எவ்வளவு?" },
                  { icon: Scale, text: "What are the grounds for first-time undertrial release under BNSS Section 479?" },
                  { icon: Scale, text: "How to report cyber fraud on Helpline 1930 and file a Zero-FIR under BNSS §173?" },
                  { icon: Landmark, text: "What is the maximum security deposit allowed and eviction rules under the Model Tenancy Act?" },
                  { icon: FileText, text: "Can an elderly parent revoke a property gift deed under Section 23 of the Senior Citizens Act 2007?" },
                  { icon: Scale, text: "Translate IPC Section 420 (Cheating) to the new Bharatiya Nyaya Sanhita (BNS)." },
                  { icon: Landmark, text: "What are the secondary and tertiary hospitalization entitlements under Ayushman Bharat (PM-JAY)?" },
                ].map((prompt, i) => (
                  <button
                    key={i}
                    className="quick-prompt-pill hover-lift"
                    onClick={() => {
                      setInput(prompt.text);
                      setTimeout(() => {
                        const form = document.querySelector('.chat-input-area');
                        if (form) form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                      }, 50);
                    }}
                  >
                    <prompt.icon size={14} />
                    <span>{prompt.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="message-icon">
                {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
              </div>
              <div className="message-content">
                {/* Calibrated Abstention Banner */}
                {msg.role === 'assistant' && msg.abstained && (
                  <div className="abstention-banner" style={{
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    marginBottom: '10px',
                    fontSize: '0.85rem'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: '#ef4444' }}>
                      <AlertCircle size={16} />
                      <span>Calibrated Refusal Triggered (Anti-Hallucination Gate)</span>
                    </div>
                    {msg.abstention_reason && (
                      <p style={{ margin: '6px 0 0', color: 'var(--text-secondary, #94a3b8)', fontSize: '0.8rem' }}>
                        {msg.abstention_reason}
                      </p>
                    )}
                    {msg.nearest_topics?.length > 0 && (
                      <div style={{ marginTop: '8px', display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary, #64748b)' }}>Closest topics indexed:</span>
                        {msg.nearest_topics.map((topic, i) => (
                          <span key={i} style={{
                            fontSize: '0.75rem',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: 'rgba(255,255,255,0.06)',
                            border: '1px solid rgba(255,255,255,0.1)'
                          }}>
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Grounding & Verification Badge */}
                {msg.role === 'assistant' && msg.grounding_score !== undefined && msg.grounding_score !== null && (
                  <div className="grounding-badge" style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '3px 10px',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    marginBottom: '8px',
                    backgroundColor: msg.citation_verified ? 'rgba(34, 197, 94, 0.12)' : 'rgba(234, 179, 8, 0.12)',
                    border: `1px solid ${msg.citation_verified ? 'rgba(34, 197, 94, 0.3)' : 'rgba(234, 179, 8, 0.3)'}`,
                    color: msg.citation_verified ? '#22c55e' : '#eab308'
                  }}>
                    <Zap size={12} />
                    <span>
                      {msg.citation_verified ? 'Grounding Verified' : 'Partially Grounded'}: {Math.round(msg.grounding_score * 100)}%
                    </span>
                    {msg.unverified_claims?.length > 0 && (
                      <span style={{ opacity: 0.8, fontWeight: 400 }}>
                        ({msg.unverified_claims.length} unverified claim{msg.unverified_claims.length > 1 ? 's' : ''})
                      </span>
                    )}
                  </div>
                )}

                {/* Structured Judicial Card (for Indian Court Judgments) */}
                {msg.role === 'assistant' && (msg.case_title || msg.ratio_decidendi || msg.acts_cited?.length > 0) && (
                  <div className="metadata-card animate-slide-up" style={{ borderColor: 'rgba(139,92,246,0.35)', background: 'rgba(139,92,246,0.06)' }}>
                    <div className="metadata-label" style={{ color: '#8b5cf6' }}>⚖️ INDIAN JUDICIAL CASE INTELLIGENCE</div>
                    <h2 className="paper-title">{msg.case_title || "Court Judgment Analysis"}</h2>
                    {msg.court_name && (
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary, #94a3b8)', margin: '2px 0 6px' }}>
                        {msg.court_name} {msg.neutral_citation ? `• Citation: ${msg.neutral_citation}` : ''}
                      </p>
                    )}
                    {msg.acts_cited?.length > 0 && (
                      <div className="authors-list" style={{ marginTop: '6px' }}>
                        {msg.acts_cited.map((act, i) => (
                          <span key={i} className="author-tag" style={{ background: 'rgba(139,92,246,0.18)', color: '#c4b5fd', border: '1px solid rgba(139,92,246,0.3)' }}>
                            {act}
                          </span>
                        ))}
                      </div>
                    )}
                    {msg.ratio_decidendi && (
                      <div style={{ marginTop: '8px', padding: '8px 10px', borderRadius: '6px', background: 'rgba(255,255,255,0.04)', fontSize: '0.85rem' }}>
                        <strong style={{ color: '#a78bfa' }}>Ratio Decidendi: </strong>
                        <span>{msg.ratio_decidendi}</span>
                      </div>
                    )}
                    {msg.disposition && (
                      <p style={{ margin: '8px 0 0', fontSize: '0.8rem', fontWeight: 600, color: '#34d399' }}>
                        Disposition: {msg.disposition}
                      </p>
                    )}
                  </div>
                )}

                {/* Structured Citizen Welfare & Governance Card (India AI) */}
                {msg.role === 'assistant' && (msg.scheme_name || msg.jan_suvidha_summary || msg.eligibility_criteria?.length > 0) && (
                  <div className="metadata-card animate-slide-up" style={{ borderColor: 'rgba(14,165,233,0.35)', background: 'rgba(14,165,233,0.06)' }}>
                    <div className="metadata-label" style={{ color: '#0ea5e9' }}>🏛️ INDIA AI GOVERNANCE & CITIZEN WELFARE</div>
                    <h2 className="paper-title">{msg.scheme_name || "Public Policy / Scheme Intelligence"}</h2>
                    {msg.nodal_ministry && (
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary, #94a3b8)', margin: '2px 0 6px' }}>
                        {msg.nodal_ministry} {msg.gazette_reference ? `• Gazette Ref: ${msg.gazette_reference}` : ''}
                      </p>
                    )}
                    {msg.jan_suvidha_summary && (
                      <div style={{ marginTop: '8px', padding: '10px 12px', borderRadius: '6px', background: 'rgba(14,165,233,0.12)', borderLeft: '3px solid #0ea5e9', fontSize: '0.88rem' }}>
                        <strong style={{ color: '#38bdf8' }}>🇮🇳 Jan Suvidha Citizen Summary: </strong>
                        <p style={{ margin: '4px 0 0', lineHeight: 1.5, color: '#f1f5f9' }}>{msg.jan_suvidha_summary}</p>
                      </div>
                    )}
                    {msg.eligibility_criteria?.length > 0 && (
                      <div style={{ marginTop: '10px' }}>
                        <strong style={{ fontSize: '0.82rem', color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.5px' }}>✅ Eligibility Checklist:</strong>
                        <ul style={{ margin: '4px 0 8px 18px', padding: 0, fontSize: '0.85rem' }}>
                          {msg.eligibility_criteria.map((item, i) => (
                            <li key={i} style={{ marginBottom: '3px' }}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {msg.exclusion_criteria?.length > 0 && (
                      <div style={{ marginTop: '6px' }}>
                        <strong style={{ fontSize: '0.82rem', color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.5px' }}>❌ Exclusions / Non-Eligible:</strong>
                        <ul style={{ margin: '4px 0 8px 18px', padding: 0, fontSize: '0.85rem' }}>
                          {msg.exclusion_criteria.map((item, i) => (
                            <li key={i} style={{ marginBottom: '3px' }}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {msg.benefits?.length > 0 && (
                      <div style={{ marginTop: '6px' }}>
                        <strong style={{ fontSize: '0.82rem', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.5px' }}>💰 Entitlements & Benefits (DBT):</strong>
                        <ul style={{ margin: '4px 0 8px 18px', padding: 0, fontSize: '0.85rem' }}>
                          {msg.benefits.map((item, i) => (
                            <li key={i} style={{ marginBottom: '3px' }}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {msg.required_documents?.length > 0 && (
                      <div style={{ marginTop: '8px' }}>
                        <strong style={{ fontSize: '0.82rem', color: 'var(--text-secondary, #94a3b8)' }}>Mandatory Documents: </strong>
                        <div className="authors-list" style={{ marginTop: '4px' }}>
                          {msg.required_documents.map((doc, i) => (
                            <span key={i} className="author-tag" style={{ background: 'rgba(14,165,233,0.18)', color: '#38bdf8', border: '1px solid rgba(14,165,233,0.3)' }}>
                              {doc}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {msg.official_portal_or_helpline && (
                      <p style={{ margin: '10px 0 0', fontSize: '0.8rem', color: '#38bdf8', fontWeight: 600 }}>
                        Official Portal / Helpline: {msg.official_portal_or_helpline}
                      </p>
                    )}
                  </div>
                )}

                {/* Structured Metadata Card (for University/Academic) */}
                {msg.role === 'assistant' && (msg.paper_title || msg.authors?.length > 0) && (
                  <div className="metadata-card animate-slide-up">
                    <div className="metadata-label">DOCUMENT METADATA</div>
                    <h2 className="paper-title">{msg.paper_title || "Unknown Title"}</h2>
                    <div className="authors-list">
                      {msg.authors?.map((a, i) => <span key={i} className="author-tag">{a}</span>)}
                    </div>
                    {msg.abstract_summary && <p className="abstract-text">{msg.abstract_summary}</p>}
                  </div>
                )}

                {msg.role === 'assistant' && msg.evidence?.length > 0 && (
                  <div className="evidence-panel">
                    <button 
                      className="evidence-toggle"
                      onClick={() => toggleEvidence(idx)}
                    >
                      <Sparkles size={14} />
                      <span>Found {msg.evidence.length} evidence chunks</span>
                      <ChevronDown size={14} className={`arrow ${expandedEvidence[idx] ? 'open' : ''}`} />
                    </button>
                    
                    {expandedEvidence[idx] && (
                      <div className="evidence-list animate-fade-in">
                        {msg.evidence.map((ev, i) => (
                          <div key={i} className="evidence-card">
                            <div className="evidence-header">
                              <span className="source-tag">Source: {ev.doc_name || ev.metadata?.filename || 'Unknown Document'}</span>
                              <span className="score-tag">Score: {ev.score ? ev.score.toFixed(3) : 'N/A'}</span>
                            </div>
                            <p className="evidence-text">{ev.text || ev.content}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="answer-text markdown-body">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {cleanContent(msg.content)}
                  </ReactMarkdown>
                </div>

                {msg.citations?.length > 0 && (
                  <div className="citations" style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '10px' }}>
                    {msg.citations.map((c, i) => (
                      <span
                        key={i}
                        className="citation-tag hover-lift"
                        title={c.page ? `Referenced on Page ${c.page}` : 'Clause Citation'}
                        style={{
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '3px 8px',
                          borderRadius: '4px',
                          background: 'rgba(99, 102, 241, 0.12)',
                          border: '1px solid rgba(99, 102, 241, 0.3)',
                          color: '#818cf8',
                          fontSize: '0.75rem',
                          fontWeight: 600
                        }}
                        onClick={() => {
                          const pageNum = c.page || 1;
                          toast.info("Citation Ref", `Clause: ${c.clause || c.article || 'Ref'} • Document Page ${pageNum}`);
                        }}
                      >
                        <FileText size={12} />
                        <span>Clause {c.clause || c.article || 'Ref'}</span>
                        {c.page && <span style={{ opacity: 0.7 }}>• p.{c.page}</span>}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message-wrapper assistant">
              <div className="message-icon"><Bot size={20} /></div>
              <div className="message-content typing animate-pulse">
                <Loader2 className="spin text-accent" size={18} />
                <span>{messages[messages.length - 1]?.statusText || "Thinking..."}</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleSend}>
          <input 
            ref={inputRef}
            type="text" 
            placeholder="Ask about your documents (e.g., 'What is the liability cap in the vendor agreement?')"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
          />
          <button
            type="button"
            className="voice-input-btn hover-lift"
            onClick={toggleVoiceInput}
            title={isListening ? "Listening... Click to stop" : "Speak question in English or Hindi (Web Speech API)"}
            style={{
              background: isListening ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
              color: isListening ? '#ef4444' : '#94a3b8',
              border: isListening ? '1px solid #ef4444' : 'none',
              borderRadius: '8px',
              padding: '6px 8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '6px'
            }}
          >
            {isListening ? <MicOff size={18} className="animate-pulse" /> : <Mic size={18} />}
          </button>
          <button type="submit" className="send-button" disabled={isTyping || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
        <div style={{ textAlign: 'center', fontSize: '0.72rem', color: '#64748b', marginTop: '6px' }}>
          ⚖️ Official Helplines: NALSA Legal Aid <strong style={{color: '#94a3b8'}}>15100</strong> · Cyber Fraud <strong style={{color: '#94a3b8'}}>1930</strong> · PM-JAY <strong style={{color: '#94a3b8'}}>14555</strong> | Assistive Research Tool — Not Legal Advice
        </div>
      </div>

      <div className="chat-reference-panel glass-panel">
        <h3 className="reference-title">Reference Context</h3>
        <p className="reference-subtitle">Loaded knowledge sources for the <strong className="vertical-name-highlight">{vertical}</strong> workspace.</p>
        
        {ongoingJobs.length > 0 && (
          <div className="ref-jobs-list">
            {ongoingJobs.map(job => (
              <div key={job.id} className="ref-job-item">
                <Loader className="spin text-accent" size={14} />
                <div className="ref-job-details">
                  <span className="ref-job-name" title={job.name}>{job.name}</span>
                  <span className="ref-job-desc">Ingesting & indexing...</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeDocs.length === 0 && ongoingJobs.length === 0 ? (
          <div className="ref-empty-state">
            <AlertCircle size={24} className="text-tertiary" />
            <p className="empty-title">Workspace is empty</p>
            <p className="empty-desc">
              {vertical === 'auto' 
                ? "There are no documents uploaded in any workspace vertical yet."
                : `There are no documents uploaded in the ${vertical} vertical yet.`
              }
            </p>
            <p className="empty-action-hint">
              Go to the <strong>Document Vault</strong> to upload and index documents{vertical !== 'auto' && ` for the ${vertical} vertical`}.
            </p>
          </div>
        ) : (
          <div className="ref-docs-list">
            {activeDocs.map(doc => (
              <div key={doc.id} className="ref-doc-card">
                <File size={16} className="text-accent flex-shrink-0" />
                <div className="ref-doc-details">
                  <span className="ref-doc-name" title={doc.name}>{doc.name}</span>
                  <span className="ref-doc-meta">
                    <span className="badge-vertical-ref" style={{ 
                      fontSize: '0.62rem', 
                      fontWeight: '800', 
                      color: 'var(--accent-primary)',
                      marginRight: '0.35rem',
                      textTransform: 'uppercase'
                    }}>{doc.vertical}</span> • {doc.chunks_count} chunks
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── India AI: IPC ⇄ BNS Statutory Concordance Converter Modal ── */}
      {showConcordanceModal && (
        <div className="modal-overlay animate-fade-in" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(5px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '20px'
        }}>
          <div className="glass-panel animate-scale-up" style={{
            width: '100%', maxWidth: '640px', background: '#0f172a',
            border: '1px solid rgba(139,92,246,0.3)', borderRadius: '14px', padding: '24px',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.6)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Scale size={20} color="#8b5cf6" />
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc' }}>
                  Indian Criminal Law Statutory Concordance
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowConcordanceModal(false)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '0 0 14px', lineHeight: 1.5 }}>
              Instant cross-referencing between pre-2024 colonial criminal codes (IPC, CrPC, IEA) and the new Bharatiya criminal jurisprudence (BNS, BNSS, BSA enacted July 1, 2024).
            </p>

            {/* Search Input Bar */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
              <input
                type="text"
                placeholder="Enter section or offence (e.g. IPC 420, Section 302, CrPC 439, IEA 65B)"
                value={concordanceQuery}
                onChange={(e) => setConcordanceQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleSearchConcordance(); } }}
                style={{
                  flex: 1, padding: '9px 12px', borderRadius: '8px',
                  background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
                  color: '#fff', fontSize: '0.88rem'
                }}
              />
              <button
                type="button"
                className="hover-lift"
                onClick={() => handleSearchConcordance()}
                style={{
                  padding: '9px 16px', borderRadius: '8px', background: '#8b5cf6',
                  color: '#fff', border: 'none', fontWeight: 600, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: '6px'
                }}
              >
                {loadingConcordance ? <Loader size={15} className="spin" /> : <Search size={15} />}
                Search
              </button>
            </div>

            {/* Quick Presets */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
              <span style={{ fontSize: '0.73rem', color: '#64748b', alignSelf: 'center', marginRight: '4px' }}>Quick lookups:</span>
              {[
                { label: "IPC 420 (Cheating)", q: "IPC 420" },
                { label: "IPC 302 (Murder)", q: "IPC 302" },
                { label: "CrPC 439 (Bail)", q: "CrPC 439" },
                { label: "CrPC 154 (FIR)", q: "CrPC 154" },
                { label: "IEA 65B (Electronic Evidence)", q: "IEA 65B" },
              ].map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setConcordanceQuery(p.q);
                    handleSearchConcordance(p.q);
                  }}
                  style={{
                    padding: '3px 8px', borderRadius: '4px',
                    background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.3)',
                    color: '#c4b5fd', fontSize: '0.72rem', cursor: 'pointer'
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Results Container */}
            <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
              {concordanceResults.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#64748b', fontSize: '0.82rem', margin: '18px 0' }}>
                  No statutory concordance records found for "{concordanceQuery}". Try searching "IPC 420" or "CrPC 439".
                </p>
              ) : (
                concordanceResults.map((m, i) => (
                  <div key={i} style={{
                    padding: '10px 12px', borderRadius: '8px',
                    background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
                    marginBottom: '8px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#38bdf8' }}>
                        {m.source_act} Section {m.source_section}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#8b5cf6', fontSize: '0.82rem', fontWeight: 600 }}>
                        <ArrowRightLeft size={12} /> {m.target_act} Section {m.target_section}
                      </span>
                    </div>
                    <p style={{ margin: '0 0 3px', fontSize: '0.8rem', color: '#e2e8f0', fontWeight: 500 }}>
                      {m.title}
                    </p>
                    {m.punishment_or_note && (
                      <p style={{ margin: 0, fontSize: '0.73rem', color: '#94a3b8' }}>
                        ⚖️ Punishment/Provision: {m.punishment_or_note}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
      {/* ── Official Citizen Helplines & Legal Aid Modal ── */}
      {showAidModal && (
        <div className="concordance-modal-overlay animate-fade-in" onClick={() => setShowAidModal(false)}>
          <div className="concordance-modal-card glass-panel animate-scale-up" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '620px' }}>
            <div className="modal-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '12px', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldAlert size={20} color="#f59e0b" />
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc' }}>
                  National Citizen Helplines & Legal Aid Routing
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowAidModal(false)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.5, marginBottom: '14px' }}>
              JanSetu AI is an assistive document intelligence platform. If you require urgent, binding legal representation or official grievance redressal, connect directly with these certified public authorities:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#fbbf24', fontSize: '0.9rem' }}>National Legal Services Authority (NALSA)</strong>
                  <span style={{ background: '#f59e0b', color: '#000', padding: '2px 8px', borderRadius: '4px', fontWeight: 700, fontSize: '0.8rem' }}>15100 (24x7 Toll-Free)</span>
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: '#cbd5e1' }}>
                  Free legal representation, bail filing assistance for undertrials under BNSS §479, and legal aid clinics for women, scheduled castes, and marginal farmers under the Legal Services Authorities Act, 1987.
                </p>
              </div>

              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(56,189,248,0.08)', border: '1px solid rgba(56,189,248,0.25)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#38bdf8', fontSize: '0.9rem' }}>National Cyber Crime Helpline (I4C / MHA)</strong>
                  <span style={{ background: '#38bdf8', color: '#000', padding: '2px 8px', borderRadius: '4px', fontWeight: 700, fontSize: '0.8rem' }}>1930 (Golden Hour)</span>
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: '#cbd5e1' }}>
                  Immediate bank account freezing via CFCFRMS for UPI/banking fraud, Zero-FIR registration guidance under BNSS §173, and cyber cheating reports under BNS §318(4).
                </p>
              </div>

              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.25)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#4ade80', fontSize: '0.9rem' }}>Ayushman Bharat PM-JAY Grievance Redressal</strong>
                  <span style={{ background: '#22c55e', color: '#000', padding: '2px 8px', borderRadius: '4px', fontWeight: 700, fontSize: '0.8rem' }}>14555 (Toll-Free)</span>
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: '#cbd5e1' }}>
                  Hospital pre-authorization denial disputes, ₹5 Lakh cashless coverage verification, and empanelled hospital grievance escalation.
                </p>
              </div>
            </div>

            <div style={{ padding: '8px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.04)', fontSize: '0.74rem', color: '#94a3b8' }}>
              💡 <em>Pro-tip: Common Service Centers (CSCs) also operate the Department of Justice <strong>Tele-Law</strong> video consultation kiosk for grassroots legal advice at Gram Panchayats.</em>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
