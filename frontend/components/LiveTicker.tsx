
import React from 'react';
import { LiveEvent } from '../types';

interface LiveTickerProps {
  events: LiveEvent[];
}

export const LiveTicker: React.FC<LiveTickerProps> = ({ events }) => {
  // Tweak this to control scroll speed (seconds)
  const TICKER_SPEED_SECONDS = 100;

  return (
    <div className="w-full bg-slate-950/80 border-y border-slate-800 h-10 overflow-hidden flex items-center relative z-30">
      <div className="bg-sky-500 text-white text-[9px] font-black px-4 h-full flex items-center z-40 whitespace-nowrap tracking-tighter shadow-[5px_0_15px_rgba(0,0,0,0.5)]">
        LIVE_PULSE_FEED
      </div>
      <div className="flex-1 overflow-hidden relative h-full flex items-center fade-edge-x">
        <div
          className="ticker-scroll flex space-x-16 whitespace-nowrap pl-8"
          style={{ animationDuration: `${TICKER_SPEED_SECONDS}s` }}
        >
          {[...events, ...events].map((event, idx) => (
            <div key={`${event.id}-${idx}`} className="flex items-center space-x-3 text-[13px]">
              <span className="text-slate-500 font-mono text-[11px] font-medium tracking-tight">
                {event.timestamp.split(' ')[1]}
              </span>
              <span className="text-slate-100 font-semibold tracking-tight">{event.title}</span>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-slate-800 text-slate-400 border border-slate-700 uppercase">
                {event.source}
              </span>
              <span className="w-1 h-1 bg-slate-700 rounded-full mx-2"></span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
