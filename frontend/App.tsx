import React, { useState, useEffect, useRef } from 'react';
import {
  Search, Terminal, Zap, Activity, Cpu, ShieldAlert,
  BarChart3, RefreshCw, Layers, TrendingUp, HelpCircle,
  Clock, CheckCircle2, AlertCircle, FileText, ExternalLink, X
} from 'lucide-react';
import { LiveTicker } from './components/LiveTicker';
import { CompanyRadar } from './components/CompanyRadar';
import { MarkdownRenderer } from './components/MarkdownRenderer';
import { StrategicInsightReport } from './components/StrategicInsightReport';
import { querySiliconPulse, injectSignal, fetchSignals, QueryResponse, formatEvidenceToContext, generateInsight, bootstrapSystem, fetchRecommendations, exportAnalysis, verifySources } from './api/siliconpulseApi';
import { INITIAL_LIVE_FEED } from './constants';
import { LiveEvent } from './types';

const App: React.FC = () => {
  const [liveFeed, setLiveFeed] = useState<LiveEvent[]>(INITIAL_LIVE_FEED);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [insight, setInsight] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState(new Date().toLocaleTimeString());
  const [recommendations, setRecommendations] = useState<any[]>([]);

  // Injection Modal State
  const [showInjectModal, setShowInjectModal] = useState(false);
  const [injectTitle, setInjectTitle] = useState('');
  const [injectContent, setInjectContent] = useState('');
  const [injectSource, setInjectSource] = useState('ManualInject');
  const [injectLoading, setInjectLoading] = useState(false);
  const [injectSuccess, setInjectSuccess] = useState(false);

  // Export & Verify State
  const [showExportModal, setShowExportModal] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [exportFormat, setExportFormat] = useState('md');
  const [verifiedSources, setVerifiedSources] = useState<any[]>([]);
  const [verifying, setVerifying] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log('✅ SiliconPulse App Loaded - Bootstrapping...');

    const init = async () => {
      // 1. Bootstrap System (Generate Fresh News)
      await bootstrapSystem();

      // 2. Refresh Signals
      refreshSignals();

      // 3. Fetch Recommendations
      fetchRecommendations().then(recs => {
        if (recs && recs.length > 0) {
          setRecommendations(recs);
        }
      });
    };

    init();

    // Auto-refresh signals every 5 seconds
    const interval = setInterval(refreshSignals, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [queryResult]);

  const refreshSignals = async () => {
    try {
      const signals = await fetchSignals();
      if (signals && signals.length > 0) {
        // Map API signals to LiveEvent format
        const mappedSignals: LiveEvent[] = signals.map((s: any, idx: number) => ({
          id: `api-${Date.now()}-${idx}`,
          timestamp: s.timestamp || new Date().toISOString(),
          source: s.source || 'Unknown',
          title: s.title,
          content: s.title, // Compact view uses title as content for now if content missing
          impactScore: 50, // Default score
          company: s.company || 'Unknown'
        }));
        setLiveFeed(prev => {
          // Merge new signals with existing ones, avoiding duplicates if possible
          // For simplicity, just prepending new ones or replacing could work.
          // Let's just use the API signals + initial feed for now
          return [...mappedSignals, ...INITIAL_LIVE_FEED].slice(0, 50);
        });
      }
    } catch (err) {
      console.error("Failed to refresh signals:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent | string) => {
    const finalQuery = typeof e === 'string' ? e : query;
    if (typeof e !== 'string') e.preventDefault();
    if (!finalQuery.trim() || loading) return;

    setLoading(true);
    setError(null);
    setQueryResult(null);
    setInsight(null);

    try {
      // 1. Get Evidence FIRST - show immediately
      const result = await querySiliconPulse(finalQuery);
      setQueryResult(result);
      setLoading(false); // Stop loading spinner immediately after evidence is shown

      // 2. Generate Insight ASYNCHRONOUSLY in background
      if (result.evidence.length > 0) {
        // Don't await - let it load in background
        const context = formatEvidenceToContext(result.evidence);
        generateInsight(finalQuery, context)
          .then(generatedInsight => {
            setInsight(generatedInsight);
          })
          .catch(err => {
            console.error("Insight generation failed:", err);
            setInsight("Insight generation unavailable. Evidence displayed above.");
          });
      } else {
        setInsight("No sufficient evidence found in the data stream to generate a specific insight.");
      }

      setQuery('');
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err.message || 'Intelligence failure. Connection to core reasoning lost.');
      setLoading(false);
    }
  };

  const handleInjectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!injectTitle.trim() || !injectContent.trim()) return;

    setInjectLoading(true);
    try {
      await injectSignal(injectTitle, injectContent, injectSource);
      setInjectSuccess(true);
      setInjectTitle('');
      setInjectContent('');
      setInjectSource('ManualInject');

      // Refresh signals and close modal after short delay
      await refreshSignals();
      setTimeout(() => {
        setInjectSuccess(false);
        setShowInjectModal(false);
      }, 1500);

      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Injection failed:", err);
      // Could set an error state for the modal here
    } finally {
      setInjectLoading(false);
    }
  };

  const handleExport = async () => {
    if (!queryResult || !insight) return;
    try {
      await exportAnalysis(
        queryResult.query,
        insight,
        queryResult.evidence,
        exportFormat
      );
      setShowExportModal(false);
    } catch (err) {
      console.error("Export failed:", err);
      alert("Export failed. See console for details.");
    }
  };

  const handleVerify = async () => {
    if (!queryResult) return;
    setVerifying(true);
    setShowVerifyModal(true);
    try {
      const data = await verifySources(queryResult.query);
      setVerifiedSources(data.sources);
    } catch (err) {
      console.error("Verification failed:", err);
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#020617] text-slate-200 relative">
      {/* INJECTION MODAL */}
      {showInjectModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-lg bg-[#020617] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden relative">
            <button
              onClick={() => setShowInjectModal(false)}
              className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>

            <div className="p-6 border-b border-slate-800/50">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-sky-500/10 rounded-lg text-sky-500">
                  <Zap size={20} />
                </div>
                <h3 className="text-lg font-black text-white uppercase tracking-tight">Inject Signal</h3>
              </div>
            </div>

            {injectSuccess ? (
              <div className="p-12 flex flex-col items-center justify-center text-center space-y-4">
                <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-500 mb-2">
                  <CheckCircle2 size={32} />
                </div>
                <h4 className="text-xl font-bold text-white">Signal Injected</h4>
                <p className="text-slate-400 text-sm">Data stream updated successfully.</p>
              </div>
            ) : (
              <form onSubmit={handleInjectSubmit} className="p-6 space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Title</label>
                  <input
                    type="text"
                    value={injectTitle}
                    onChange={(e) => setInjectTitle(e.target.value)}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 outline-none transition-all"
                    placeholder="e.g. TSMC Yield Report"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Source</label>
                  <input
                    type="text"
                    value={injectSource}
                    onChange={(e) => setInjectSource(e.target.value)}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 outline-none transition-all"
                    placeholder="e.g. ManualInject"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Content Payload</label>
                  <textarea
                    value={injectContent}
                    onChange={(e) => setInjectContent(e.target.value)}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-lg px-4 py-3 text-sm text-white focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 outline-none transition-all h-32 resize-none"
                    placeholder="Enter raw signal data..."
                    required
                  />
                </div>

                <div className="pt-4">
                  <button
                    type="submit"
                    disabled={injectLoading}
                    className="w-full py-3 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-black uppercase tracking-widest transition-all shadow-[0_0_15px_rgba(14,165,233,0.3)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {injectLoading ? (
                      <>
                        <RefreshCw size={14} className="animate-spin" />
                        <span>Injecting...</span>
                      </>
                    ) : (
                      <>
                        <Zap size={14} />
                        <span>Transmit Signal</span>
                      </>
                    )}

                    {/* EXPORT MODAL */}
                    {showExportModal && (
                      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                        <div className="w-full max-w-md bg-[#020617] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden relative">
                          <button onClick={() => setShowExportModal(false)} className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"><X size={20} /></button>
                          <div className="p-6 border-b border-slate-800/50">
                            <h3 className="text-lg font-black text-white uppercase tracking-tight flex items-center">
                              <BarChart3 size={20} className="mr-2 text-sky-500" /> Export Analysis
                            </h3>
                          </div>
                          <div className="p-6 space-y-4">
                            <div className="grid grid-cols-2 gap-3">
                              {['md', 'json', 'txt', 'pdf'].map(fmt => (
                                <button
                                  key={fmt}
                                  onClick={() => setExportFormat(fmt)}
                                  className={`p-3 rounded-lg border text-sm font-bold uppercase tracking-widest transition-all ${exportFormat === fmt
                                    ? 'bg-sky-500/20 border-sky-500 text-sky-400'
                                    : 'bg-slate-900 border-slate-800 text-slate-500 hover:border-slate-700'
                                    }`}
                                >
                                  .{fmt}
                                </button>
                              ))}
                            </div>
                            <button
                              onClick={handleExport}
                              className="w-full py-3 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-black uppercase tracking-widest transition-all shadow-[0_0_15px_rgba(14,165,233,0.3)] mt-4"
                            >
                              Download Report
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* VERIFY SOURCES MODAL */}
                    {showVerifyModal && (
                      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                        <div className="w-full max-w-2xl bg-[#020617] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden relative flex flex-col max-h-[80vh]">
                          <button onClick={() => setShowVerifyModal(false)} className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"><X size={20} /></button>
                          <div className="p-6 border-b border-slate-800/50 shrink-0">
                            <h3 className="text-lg font-black text-white uppercase tracking-tight flex items-center">
                              <HelpCircle size={20} className="mr-2 text-emerald-500" /> Source Verification
                            </h3>
                          </div>
                          <div className="p-6 overflow-y-auto custom-scrollbar">
                            {verifying ? (
                              <div className="flex flex-col items-center justify-center py-12 space-y-4">
                                <RefreshCw size={32} className="animate-spin text-emerald-500" />
                                <span className="text-sm font-mono text-slate-400 uppercase tracking-widest">Verifying Source Integrity...</span>
                              </div>
                            ) : (
                              <div className="space-y-3">
                                {verifiedSources.map((src, idx) => (
                                  <div key={idx} className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex items-start justify-between">
                                    <div className="flex-1 pr-4">
                                      <div className="flex items-center space-x-2 mb-1">
                                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-widest border ${src.trust_level === 'High' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
                                          src.trust_level === 'Medium' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                                            'bg-red-500/10 text-red-500 border-red-500/20'
                                          }`}>
                                          {src.trust_level} Trust
                                        </span>
                                        <span className="text-[10px] font-bold text-slate-500">{src.source}</span>
                                        <span className="text-[10px] text-slate-600">•</span>
                                        <span className="text-[10px] text-slate-600">{new Date(src.timestamp).toLocaleString()}</span>
                                      </div>
                                      <h4 className="text-sm font-bold text-slate-200 mb-1">{src.title}</h4>
                                      <p className="text-xs text-slate-500 italic">{src.reason}</p>
                                    </div>
                                    {src.url && (
                                      <a href={src.url} target="_blank" rel="noreferrer" className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
                                        <ExternalLink size={16} />
                                      </a>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* HEADER SECTION */}
      <header className="h-14 border-b border-slate-800/60 flex items-center justify-between px-6 bg-slate-950/40 backdrop-blur-xl z-50">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-sky-600 rounded flex items-center justify-center shadow-[0_0_15px_rgba(2,132,199,0.3)]">
              <Cpu size={18} className="text-white" />
            </div>
            <div className="leading-tight">
              <h1 className="text-sm font-black tracking-tighter uppercase text-white flex items-center">
                Silicon<span className="text-sky-500">Pulse</span>
                <span className="ml-2 px-1 py-0.5 bg-sky-500/10 text-sky-500 border border-sky-500/20 rounded-[4px] text-[8px] tracking-[0.1em]">OS_v4</span>
              </h1>
            </div>
          </div>
          <div className="h-4 w-[1px] bg-slate-800"></div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1.5 group cursor-help">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest group-hover:text-emerald-400 transition-colors">Nodes_Online</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <Activity size={12} className="text-sky-500" />
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Latency: 12ms</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowInjectModal(true)}
            className="flex items-center space-x-2 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 rounded-md text-[10px] font-black uppercase tracking-widest text-sky-400 border border-slate-800 transition-all active:scale-95"
          >
            <Zap size={12} />
            <span>Inject_Signal</span>
          </button>
        </div>
      </header>

      {/* LIVE SIGNALS ZONE */}
      <LiveTicker events={liveFeed} />

      {/* CORE LAYOUT GRID */}
      <main className="flex-1 flex overflow-hidden">

        {/* RADAR ZONE (SIDEBAR) */}
        <aside className="w-80 border-r border-slate-800/40 bg-slate-950/20 p-6 space-y-8 hidden xl:block overflow-y-auto custom-scrollbar">
          <CompanyRadar />

          <div className="space-y-4">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center">
              <Zap size={14} className="mr-2 text-amber-500" />
              High Priority Signals
            </h3>
            <div className="space-y-3">
              {liveFeed.filter(f => f.impactScore > 80).slice(0, 3).map(ev => (
                <div key={ev.id} className="glass p-3 rounded-xl border-slate-800/50 hover:border-sky-500/30 transition-all cursor-pointer group">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] font-mono text-sky-500">{ev.timestamp.split(' ')[1]}</span>
                    <span className="px-1.5 py-0.5 rounded-[4px] bg-red-500/10 text-red-500 text-[8px] font-black uppercase tracking-tighter border border-red-500/20">Critical</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-100 group-hover:text-sky-400 leading-tight transition-colors mb-1">{ev.title}</h4>
                  <div className="flex items-center text-[9px] text-slate-500 font-bold uppercase tracking-widest">
                    <span>{ev.company}</span>
                    <span className="mx-1.5 opacity-20">|</span>
                    <span>{ev.impactScore} IMPACT</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-sky-500/5 border border-sky-500/10">
            <div className="flex items-center space-x-2 mb-3">
              <div className="p-1.5 bg-sky-500/20 rounded-lg">
                <ShieldAlert size={14} className="text-sky-500" />
              </div>
              <span className="text-[10px] font-black text-sky-500 uppercase tracking-widest">Analyst Advisory</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium italic leading-relaxed">
              "Focus on TSMC N2 yield milestones. Early reports suggest Apple/NVIDIA bidding war for initial capacity. Cross-ref with GlobalFoundries delays."
            </p>
          </div>
        </aside>

        {/* QUERY & REPORT ZONE */}
        <section className="flex-1 flex flex-col bg-[#010409] relative">
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-10 custom-scrollbar">

            {/* INITIAL / IDLE STATE (QUICK QUERIES) */}
            {!queryResult && !loading && !error && (
              <div className="h-full flex flex-col justify-center max-w-4xl mx-auto space-y-12">
                <div className="space-y-4">
                  <div className="inline-flex items-center space-x-2 px-3 py-1 bg-sky-500/10 border border-sky-500/20 rounded-full text-sky-500 text-[10px] font-black uppercase tracking-widest animate-pulse">
                    <Layers size={12} />
                    <span>Ready for Intelligence Generation</span>
                  </div>
                  <h2 className="text-5xl font-black text-white tracking-tighter uppercase leading-none">
                    Strategic <br /> Intelligence <span className="text-sky-500">Node</span>
                  </h2>
                  <p className="text-slate-500 text-lg font-medium max-w-xl">
                    Monitor live supply chain signals, yield reports, and geopolitical shifts. Select a directive or enter a custom query.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(recommendations.length > 0 ? recommendations : [
                    { label: "NVIDIA-TSMC Pipeline", query: "Any new NVIDIA-TSMC contract today?", icon: Zap, color: "text-amber-400" },
                    { label: "Foundry Design Wins", query: "Status of Intel 18A design wins and foundry clients?", icon: CheckCircle2, color: "text-emerald-400" },
                    { label: "AI Infra Analysis", query: "What is the impact of Meta's new AI infra updates?", icon: Cpu, color: "text-sky-400" },
                    { label: "High Impact Summary", "query": "What are the top 3 high-impact events in last 2 hours?", icon: AlertCircle, color: "text-red-400" }
                  ]).map((item: any) => {
                    // Map string icon names to components if needed, or use defaults
                    const IconComponent = typeof item.icon === 'string'
                      ? (item.icon === 'Activity' ? Activity :
                        item.icon === 'Cpu' ? Cpu :
                          item.icon === 'Globe' ? ExternalLink :
                            item.icon === 'TrendingUp' ? TrendingUp :
                              item.icon === 'Zap' ? Zap :
                                item.icon === 'ShieldAlert' ? ShieldAlert :
                                  item.icon === 'BarChart3' ? BarChart3 :
                                    item.icon === 'Layers' ? Layers :
                                      item.icon === 'FileText' ? FileText :
                                        AlertCircle)
                      : item.icon;

                    return (
                      <button
                        key={item.label}
                        onClick={() => handleSubmit(item.query)}
                        className="glass glass-hover p-5 text-left rounded-2xl transition-all flex items-start space-x-4 group"
                      >
                        <div className={`p-3 bg-slate-900 rounded-xl group-hover:bg-slate-800 transition-colors ${item.color}`}>
                          <IconComponent size={20} />
                        </div>
                        <div className="flex-1">
                          <span className="text-xs font-black uppercase tracking-[0.1em] text-slate-500 mb-1 block group-hover:text-slate-300 transition-colors">{item.label}</span>
                          <p className="text-sm font-medium text-slate-300 group-hover:text-white leading-tight">{item.query}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ERROR STATE */}
            {error && (
              <div className="h-full flex flex-col items-center justify-center max-w-3xl mx-auto space-y-8 px-8">
                <div className="p-8 rounded-2xl bg-red-500/5 border border-red-500/20 w-full">
                  <div className="flex items-start space-x-4">
                    <AlertCircle size={32} className="text-red-500 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-xl font-black text-red-500 uppercase tracking-tight mb-2">Intelligence Synthesis Failed</h3>
                      <p className="text-slate-300 font-medium mb-4">{error}</p>

                      {error.includes("Backend offline") ? (
                        <button
                          onClick={async () => {
                            setError(null);
                            setLoading(true);
                            // Import dynamically to avoid circular dependency issues if any
                            const { checkBackendHealth } = await import('./api/siliconpulseApi');
                            const isOnline = await checkBackendHealth();
                            if (isOnline) {
                              setLoading(false);
                              // Retry the query if it was a query failure
                              if (query) handleSubmit(query);
                            } else {
                              setLoading(false);
                              setError("Backend still offline. Please ensure server is running on port 8000.");
                            }
                          }}
                          className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-xs font-black uppercase tracking-widest transition-all border border-red-500/30 flex items-center space-x-2"
                        >
                          <RefreshCw size={12} />
                          <span>Check Connection & Retry</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => setError(null)}
                          className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-xs font-black uppercase tracking-widest transition-all border border-red-500/30"
                        >
                          Dismiss
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="flex items-center space-x-2 px-6 py-3 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-black uppercase tracking-widest transition-all shadow-[0_0_15px_rgba(14,165,233,0.3)]"
                >
                  <RefreshCw size={14} />
                  <span>Return to Dashboard</span>
                </button>
              </div>
            )}

            {/* LOADING STATE */}
            {loading && (
              <div className="h-full flex flex-col items-center justify-center space-y-6">
                <div className="relative">
                  <div className="w-20 h-20 border-[3px] border-sky-500/10 border-t-sky-500 rounded-full animate-spin"></div>
                  <Activity className="absolute inset-0 m-auto text-sky-500 animate-pulse" size={32} />
                </div>
                <div className="text-center space-y-2">
                  <h3 className="text-sky-500 font-black text-xs uppercase tracking-[0.4em] animate-pulse">Synthesizing Signals</h3>
                  <p className="text-slate-500 text-[11px] font-mono tracking-widest uppercase">Cross-referencing global supply chain nodes...</p>
                </div>
              </div>
            )}

            {/* REPORT VIEW */}
            {queryResult && (
              <div className="pb-24 pt-4 animate-in fade-in slide-in-from-bottom-8 duration-700 ease-out">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tight mb-2">Intelligence Report</h2>
                    <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">Query: "{queryResult.query}"</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Signal Strength</div>
                      <div className="text-xl font-black text-sky-500">{queryResult.signal_strength}%</div>
                    </div>
                    <div className="w-12 h-12 rounded-full border-4 border-slate-800 flex items-center justify-center relative">
                      <svg className="absolute inset-0 transform -rotate-90 w-full h-full">
                        <circle cx="20" cy="20" r="18" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-slate-800" />
                        <circle cx="20" cy="20" r="18" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-sky-500" strokeDasharray={`${queryResult.signal_strength * 1.13} 113`} />
                      </svg>
                      <Activity size={16} className="text-sky-500" />
                    </div>
                  </div>
                </div>

                {/* INSIGHT SECTION */}
                {queryResult && queryResult.evidence.length > 0 && (
                  <div className="mb-8 p-6 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center space-x-2 mb-4">
                      <div className="p-1.5 bg-indigo-500/20 rounded-lg">
                        <Zap size={18} className="text-indigo-400" />
                      </div>
                      <h3 className="text-sm font-black text-indigo-400 uppercase tracking-widest">Strategic Insight</h3>
                    </div>
                    {insight ? (
                      <div className="max-w-none">
                        <StrategicInsightReport data={insight} />
                      </div>
                    ) : (
                      <div className="flex items-center space-x-3 text-slate-400">
                        <RefreshCw size={16} className="animate-spin" />
                        <span className="text-sm font-medium">Generating strategic insight...</span>
                      </div>
                    )}
                  </div>
                )}

                <div className="space-y-6">
                  {queryResult.evidence.length === 0 ? (
                    <div className="p-8 rounded-2xl bg-slate-900/50 border border-slate-800 text-center">
                      <ShieldAlert size={32} className="mx-auto text-slate-600 mb-4" />
                      <h3 className="text-lg font-bold text-slate-400 mb-2">No Direct Evidence Found</h3>
                      <p className="text-slate-500 text-sm">The current data stream does not contain specific signals matching your query parameters.</p>
                    </div>
                  ) : (
                    queryResult.evidence.map((item, idx) => (
                      <div key={idx} className="glass p-6 rounded-2xl border-slate-800/60 hover:border-sky-500/30 transition-all group">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="p-2 bg-slate-900 rounded-lg text-sky-500 group-hover:text-sky-400 transition-colors">
                              <FileText size={18} />
                            </div>
                            <div>
                              <h3 className="text-base font-bold text-slate-200 group-hover:text-white transition-colors">{item.title}</h3>
                              <div className="flex items-center space-x-2 text-[10px] font-black text-slate-500 uppercase tracking-widest mt-0.5">
                                <span>{item.source || 'Unknown Source'}</span>
                                <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                                <span>{item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}</span>
                              </div>
                            </div>
                          </div>
                          {item.company && (
                            <span className="px-2 py-1 rounded bg-slate-800 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                              {item.company}
                            </span>
                          )}
                        </div>
                        {item.snippet && item.snippet !== "..." && item.snippet.length >= 20 && (
                          <p className="text-sm text-slate-400 leading-relaxed pl-12 border-l-2 border-slate-800 group-hover:border-sky-500/30 transition-colors">
                            {item.snippet}
                          </p>
                        )}
                      </div>
                    ))
                  )}
                </div>

                <div className="mt-16 flex items-center justify-between p-6 glass rounded-2xl border-slate-800/40">
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setShowExportModal(true)}
                      className="flex items-center space-x-2 px-4 py-2 bg-sky-500 text-white rounded-lg text-xs font-black uppercase tracking-widest hover:bg-sky-400 transition-all shadow-[0_0_15px_rgba(14,165,233,0.3)]"
                    >
                      <BarChart3 size={14} />
                      <span>Export Analysis</span>
                    </button>
                    <button
                      onClick={handleVerify}
                      className="flex items-center space-x-2 px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs font-black uppercase tracking-widest hover:bg-slate-700 transition-all"
                    >
                      <HelpCircle size={14} />
                      <span>Verify Sources</span>
                    </button>
                  </div>
                  <div className="flex items-center space-x-3 text-[10px] font-mono text-slate-600">
                    <span className="uppercase tracking-widest">Last Updated: {queryResult.last_updated}</span>
                    <span className="w-1 h-1 bg-slate-800 rounded-full"></span>
                    <span className="uppercase tracking-widest">SID: SP-94-ALPHA</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* INPUT BAR (STICKY BOTTOM) */}
          <div className="p-8 bg-slate-950/60 backdrop-blur-2xl border-t border-slate-800/60 relative z-40">
            <div className="max-w-4xl mx-auto space-y-4">
              <form onSubmit={handleSubmit} className="relative group">
                <div className="absolute inset-0 -m-[1px] bg-gradient-to-r from-sky-500/40 via-indigo-500/40 to-sky-500/40 rounded-2xl opacity-0 group-focus-within:opacity-100 blur-[6px] transition-all duration-500"></div>
                <div className="relative flex items-center bg-slate-900 border border-slate-700/60 rounded-2xl overflow-hidden px-5 focus-within:border-sky-500/50 shadow-2xl transition-all">
                  <Terminal className="text-slate-500 mr-4" size={20} />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="ENTER COMMAND OR QUERY PULSE..."
                    className="flex-1 py-5 bg-transparent outline-none text-slate-100 placeholder-slate-600 font-mono text-sm tracking-tight"
                    disabled={loading}
                  />
                  <div className="flex items-center space-x-4">
                    <div className="hidden sm:flex items-center space-x-2 px-2 py-1 bg-slate-800/50 rounded-md border border-slate-700/50">
                      <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">ENTER</span>
                    </div>
                    <button
                      type="submit"
                      disabled={loading || !query.trim()}
                      className={`p-3 rounded-xl transition-all ${loading || !query.trim()
                        ? 'text-slate-600 bg-slate-800/50'
                        : 'text-white bg-sky-600 hover:bg-sky-500 shadow-[0_0_20px_rgba(14,165,233,0.4)] active:scale-95'
                        }`}
                    >
                      <Search size={22} />
                    </button>
                  </div>
                </div>
              </form>

              <div className="flex items-center justify-between px-2">
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <Clock size={12} className="text-slate-500" />
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Context Freshness: <span className="text-sky-500">{lastUpdate}</span></span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp size={12} className="text-emerald-500" />
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Signals Active: <span className="text-emerald-500">{liveFeed.length}</span></span>
                  </div>
                </div>
                <div className="flex items-center space-x-2 text-[10px] font-black text-slate-600 uppercase tracking-widest">
                  <span className="text-sky-500/60 font-mono">GEMINI_3_PRO_REASONING_ACTIVE</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
