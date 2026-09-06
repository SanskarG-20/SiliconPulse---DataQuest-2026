import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { TrendsPanel } from './TrendsPanel';

const mockTrends = {
  company: null,
  days: 30,
  total: 12,
  mean: 1.5,
  std: 1.2,
  daily: [
    { date: '2026-08-01', count: 1 },
    { date: '2026-08-02', count: 6 },
    { date: '2026-08-03', count: 2 },
  ],
  spikes: [{ date: '2026-08-02', count: 6, z: 2.4 }],
  by_company: [{ company: 'TSMC', count: 7 }],
  by_type: [],
};

describe('TrendsPanel', () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve(mockTrends) } as Response)
    ) as unknown as typeof fetch;
  });

  it('renders sparkline and spike badge', async () => {
    render(<TrendsPanel days={30} />);
    await waitFor(() => expect(screen.getByText(/SIGNAL TRENDS/i)).toBeInTheDocument());
    expect(await screen.findByText(/12 signals/i)).toBeInTheDocument();
    expect(screen.getByText(/1 spike/i)).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders spike date row', async () => {
    render(<TrendsPanel days={30} />);
    expect(await screen.findByText('2026-08-02')).toBeInTheDocument();
  });
});
