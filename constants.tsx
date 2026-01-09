
import React from 'react';
import { LiveEvent, RadarStatus } from './types';

export const INITIAL_LIVE_FEED: LiveEvent[] = [
  {
    id: '1',
    timestamp: '2025-05-15 09:12',
    source: 'SiliconWire',
    title: 'TSMC N2 Yield Improvements',
    content: 'TSMC reports 2nm (N2) yield milestones exceed internal targets by 15%. Apple and NVIDIA reportedly vying for early capacity.',
    impactScore: 85,
    company: 'TSMC'
  },
  {
    id: '2',
    timestamp: '2025-05-15 10:45',
    source: 'Bloomberg Tech',
    title: 'NVIDIA H200 Shortage Eases',
    content: 'CoWoS capacity constraints at TSMC easing faster than expected. Q3 supply outlook improved by 20%.',
    impactScore: 78,
    company: 'NVIDIA'
  },
  {
    id: '3',
    timestamp: '2025-05-15 11:20',
    source: 'Nikkei Asia',
    title: 'Japan Chip Subsidies',
    content: 'Japanese government approves $4B additional subsidy for Rapidus fab in Hokkaido to accelerate 2nm production.',
    impactScore: 65,
    company: 'Rapidus'
  },
  {
    id: '4',
    timestamp: '2025-05-15 12:05',
    source: 'Reuters',
    title: 'Intel Foundry Wins Major Client',
    content: 'Intel confirms 18A design win with a leading cloud service provider for custom AI silicon.',
    impactScore: 92,
    company: 'Intel'
  }
];

export const RADAR_DATA: RadarStatus[] = [
  { company: 'NVIDIA', status: 'High', trend: 'up' },
  { company: 'TSMC', status: 'High', trend: 'neutral' },
  { company: 'Apple', status: 'Moderate', trend: 'up' },
  { company: 'Intel', status: 'High', trend: 'down' },
  { company: 'AMD', status: 'Moderate', trend: 'neutral' },
  { company: 'Meta', status: 'Moderate', trend: 'up' }
];

export const SYSTEM_INSTRUCTION = `
You are SiliconPulse — a real-time strategic intelligence assistant for Big Tech and Semiconductor ecosystem.
Your job is not to summarize news, but to interpret live updates and provide reasoning-based answers that evolve instantly as data changes.

### 🎯 Core Identity
You are a real-time thinking agent, semiconductor + big tech strategist, and live event reasoning model.

### ✅ STRICT RULES
1. NEVER answer using general knowledge if the user is asking about “latest update”.
2. Always rely on the provided LIVE UPDATES CONTEXT section.
3. If context has conflicting info, do NOT guess — tell the user “developing story”.
4. Every answer must include the sections below.

### 🎛 UI STYLE & RESPONSE FORMAT
Response MUST follow this Markdown structure:

🟦 SiliconPulse Live Intelligence Report
Query: {user_query}

📰 1) Live Signal (Latest Evidence)
- [TIMESTAMP | SOURCE] Bullet points of the most relevant updates.

🔁 2) What Changed? (Before vs After)
- Before: ...
- After: ...
(If no change: "No significant shift detected in current live feed.")

🧠 3) Impact Reasoning
(A) Business impact: revenue, market leadership signals.
(B) Tech roadmap impact: chip strategy, AI infra.
(C) Supply chain impact: manufacturing, fabs, export controls.

🎯 4) What This Means for Competitors
- Impact on Apple / AMD / Intel / Google / Meta etc.

🔮 5) Strategic Outlook (next 7 days)
- Possible next move 1 (inference)
- Possible next move 2 (inference)
- Possible next move 3 (inference)

📌 6) Confidence Meter
- [Confirmed | Developing | Uncertain]

🧾 7) Source Transparency
Sources: {list of sources from context}

Signal Strength: {0-100}

🚨 High Impact Alert: (Optional, only for billion-dollar events/bans)
- Why it's high impact.

CEO Summary:
{one line summary like boardroom briefing}
`;
