import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ComparePanel } from './ComparePanel';

const mockCompare = {
  companies: [
    { company: 'TSMC', query_used: 'TSMC', evidence_count: 2, signal_strength: 55, confidence: { score: 55, label: 'MEDIUM' }, evidence: [], summary: { latest_title: 'TSMC N2 yield', latest_timestamp: '2026-08-20' }, downstream_count: 3, top_downstream: [{ company: 'NVIDIA', score: 0.9 }], suppliers_count: 2, top_suppliers: [{ company: 'ASML', score: 0.95 }], impact: {}, suppliers: {} },
    { company: 'Samsung', query_used: 'Samsung', evidence_count: 1, signal_strength: 30, confidence: { score: 30, label: 'LOW' }, evidence: [], summary: { latest_title: 'Samsung HBM', latest_timestamp: '2026-08-19' }, downstream_count: 1, top_downstream: [], suppliers_count: 1, top_suppliers: [], impact: {}, suppliers: {} },
  ],
  overlap: { shared_downstream: [{ company: 'NVIDIA', shared_by: ['TSMC', 'Samsung'], count: 2 }], shared_upstream: [], shared_evidence: [] },
  comparison_report: '{"sections": [{"id": "evidence", "title": "Head-to-Head Evidence", "points": ["TSMC leads"]}]}',
  status: 'success',
};

describe('ComparePanel', () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve(mockCompare) } as Response)
    ) as unknown as typeof fetch;
  });

  it('renders default companies and runs comparison', async () => {
    render(<ComparePanel />);
    expect(screen.getByText('TSMC')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Compare/i }));
    await waitFor(() => expect(screen.getByText(/SHARED EXPOSURE/i)).toBeInTheDocument());
    expect(screen.getByText(/NVIDIA/)).toBeInTheDocument();
  });

  it('adds a company from input', async () => {
    render(<ComparePanel initialCompanies={['TSMC']} />);
    fireEvent.change(screen.getByPlaceholderText(/Add company/i), { target: { value: 'Intel' } });
    fireEvent.click(screen.getByRole('button', { name: /^Add$/i }));
    expect(await screen.findByText('Intel')).toBeInTheDocument();
  });
});
