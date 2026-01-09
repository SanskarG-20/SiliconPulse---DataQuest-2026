
import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { RADAR_DATA } from '../constants';

export const CompanyRadar: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center">
          <span className="w-1.5 h-1.5 bg-sky-500 rounded-full mr-2 shadow-[0_0_8px_#0ea5e9]"></span>
          Company Radar
        </h3>
        <span className="text-[9px] font-mono text-slate-600">v4.0</span>
      </div>
      <div className="space-y-1">
        {RADAR_DATA.map((item) => (
          <div key={item.company} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-800/40 transition-colors cursor-default">
            <span className="text-sm font-medium text-slate-300">{item.company}</span>
            <div className="flex items-center space-x-3">
              <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter ${
                item.status === 'High' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                item.status === 'Moderate' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 
                'bg-slate-800 text-slate-500 border border-slate-700'
              }`}>
                {item.status}
              </span>
              <div className={`p-1 rounded ${
                item.trend === 'up' ? 'text-emerald-400 bg-emerald-400/10' : 
                item.trend === 'down' ? 'text-red-400 bg-red-400/10' : 
                'text-slate-500 bg-slate-800'
              }`}>
                {item.trend === 'up' ? <TrendingUp size={12} /> : 
                 item.trend === 'down' ? <TrendingDown size={12} /> : 
                 <Minus size={12} />}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
