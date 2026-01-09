
import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, Terminal, Zap, Activity, Cpu, ShieldAlert, 
  BarChart3, RefreshCw, Layers, TrendingUp, HelpCircle,
  Clock, CheckCircle2, AlertCircle
} from 'lucide-react';
import { LiveTicker } from './components/LiveTicker';
import { CompanyRadar } from './components/CompanyRadar';
import { MarkdownRenderer } from './components/MarkdownRenderer';
import { querySiliconPulse } from './services/gemini';
import { INITIAL_LIVE_FEED } from './constants';
import { LiveEvent } from './types';

const App: React.FC = () => {
  const [liveFeed, setLiveFeed] = useState<LiveEvent[]>(INITIAL_LIVE_FEED);
  const [query, setQuery] = useState('');
  const [report, setReport] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState(new Date().toLocaleTimeString());
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [report]);

  const handleSubmit = async (e: React.FormEvent | string) => {
    const finalQuery = typeof e === 'string' ? e : query;
    if (typeof e !== 'string') e.preventDefault();
    if (!finalQuery.trim() || loading) return;

    setLoading(true);
    setError(null);
    setReport(null);

    const contextStr = liveFeed.map(ev => `[${ev.timestamp} | ${ev.source}] ${ev.title}: ${ev.content}`).join('\n');

    try {
      const result = await querySiliconPulse(finalQuery, contextStr);
      setReport(result || 'No signals generated.');
      setQuery('');
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err.message || 'Intelligence failure. Connection to core reasoning lost.');
    } finally {
      setLoading(false);
    }
  };

  const addLiveSignal = () => {
    const newEvent: LiveEvent = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
      source: 'GlobalFoundries Insider',
      title: 'U.S. Fab Expansion Halted',
      content: 'Major equipment delay from ASML impacts Arizona fab timeline by 6 months. Operational date pushed to H2 2026.',
      impactScore: 88,
      company: 'GlobalFoundries'
    };
    setLiveFeed(prev => [newEvent, ...prev]);
    setLastUpdate(new Date().toLocaleTimeString());
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#020617] text-slate-200">
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
            onClick={addLiveSignal}
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
            {!report && !loading && !error && (
              <div className="h-full flex flex-col justify-center max-w-4xl mx-auto space-y-12">
                <div className="space-y-4">
                   <div className="inline-flex items-center space-x-2 px-3 py-1 bg-sky-500/10 border border-sky-500/20 rounded-full text-sky-500 text-[10px] font-black uppercase tracking-widest animate-pulse">
                      <Layers size={12} />
                      <span>Ready for Intelligence Generation</span>
                   </div>
                   <h2 className="text-5xl font-black text-white tracking-tighter uppercase leading-none">
                      Strategic <br/> Intelligence <span className="text-sky-500">Node</span>
                   </h2>
                   <p className="text-slate-500 text-lg font-medium max-w-xl">
                      Monitor live supply chain signals, yield reports, and geopolitical shifts. Select a directive or enter a custom query.
                   </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { label: "NVIDIA-TSMC Pipeline", query: "Any new NVIDIA-TSMC contract today?", icon: Zap, color: "text-amber-400" },
                    { label: "Foundry Design Wins", query: "Status of Intel 18A design wins and foundry clients?", icon: CheckCircle2, color: "text-emerald-400" },
                    { label: "AI Infra Analysis", query: "What is the impact of Meta's new AI infra updates?", icon: Cpu, color: "text-sky-400" },
                    { label: "High Impact Summary", query: "What are the top 3 high-impact events in last 2 hours?", icon: AlertCircle, color: "text-red-400" }
                  ].map(item => (
                    <button 
                      key={item.label}
                      onClick={() => handleSubmit(item.query)}
                      className="glass glass-hover p-5 text-left rounded-2xl transition-all flex items-start space-x-4 group"
                    >
                      <div className={`p-3 bg-slate-900 rounded-xl group-hover:bg-slate-800 transition-colors ${item.color}`}>
                        <item.icon size={20} />
                      </div>
                      <div className="flex-1">
                        <span className="text-xs font-black uppercase tracking-[0.1em] text-slate-500 mb-1 block group-hover:text-slate-300 transition-colors">{item.label}</span>
                        <p className="text-sm font-medium text-slate-300 group-hover:text-white leading-tight">{item.query}</p>
                      </div>
                    </button>
                  ))}
                </div>
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
            {report && (
              <div className="pb-24 pt-4 animate-in fade-in slide-in-from-bottom-8 duration-700 ease-out">
                <MarkdownRenderer content={report} />
                
                <div className="mt-16 flex items-center justify-between p-6 glass rounded-2xl border-slate-800/40">
                  <div className="flex space-x-3">
                    <button className="flex items-center space-x-2 px-4 py-2 bg-sky-500 text-white rounded-lg text-xs font-black uppercase tracking-widest hover:bg-sky-400 transition-all shadow-[0_0_15px_rgba(14,165,233,0.3)]">
                      <BarChart3 size={14} />
                      <span>Export Analysis</span>
                    </button>
                    <button className="flex items-center space-x-2 px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs font-black uppercase tracking-widest hover:bg-slate-700 transition-all">
                      <HelpCircle size={14} />
                      <span>Verify Sources</span>
                    </button>
                  </div>
                  <div className="flex items-center space-x-3 text-[10px] font-mono text-slate-600">
                    <span className="uppercase tracking-widest">TS: {Date.now()}</span>
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
                      className={`p-3 rounded-xl transition-all ${
                        loading || !query.trim() 
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
