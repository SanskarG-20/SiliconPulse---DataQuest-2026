import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { WorkspacesPanel } from './WorkspacesPanel';

describe('WorkspacesPanel', () => {
  beforeEach(() => {
    global.fetch = vi.fn((url: string) => {
      if (String(url).includes('/workspaces')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ workspaces: [{ id: 'w1', name: 'Fab Team', invite_code: 'abc123' }] }) } as Response);
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) } as Response);
    }) as unknown as typeof fetch;
  });

  it('lists workspaces and detail', async () => {
    global.fetch = vi.fn((url: string) => {
      if (String(url).endsWith('/workspaces')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ workspaces: [{ id: 'w1', name: 'Fab Team', invite_code: 'abc123' }] }) } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ members: [{ user_id: 'u1', role: 'owner' }], watchlist: ['TSMC'], briefs: [{ id: 'b1', query_text: 'TSMC?' }] }),
      } as Response);
    }) as unknown as typeof fetch;
    render(<MemoryRouter><WorkspacesPanel /></MemoryRouter>);
    expect((await screen.findAllByText('Fab Team')).length).toBeGreaterThan(0);
    expect(await screen.findByText('TSMC')).toBeInTheDocument();
  });

  it('creates a workspace', async () => {
    global.fetch = vi.fn((url: string, init?: any) => {
      if (String(url).endsWith('/workspaces') && init?.method === 'POST') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ workspace: { id: 'w2', name: 'New Team' }, invite_code: 'def456' }) } as Response);
      }
      if (String(url).includes('/workspaces/w2')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ members: [], watchlist: [], briefs: [] }) } as Response);
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ workspaces: [{ id: 'w2', name: 'New Team', invite_code: 'def456' }] }) } as Response);
    }) as unknown as typeof fetch;
    render(<MemoryRouter><WorkspacesPanel /></MemoryRouter>);
    fireEvent.change(screen.getByPlaceholderText(/New team name/i), { target: { value: 'New Team' } });
    fireEvent.click(screen.getByRole('button', { name: /Create workspace/i }));
    await waitFor(() => expect(screen.getByText(/Invite code: def456/i)).toBeInTheDocument());
  });
});
