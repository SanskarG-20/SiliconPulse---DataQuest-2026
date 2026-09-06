import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { BriefComments } from './BriefComments';

vi.mock('@clerk/clerk-react', () => ({
  useAuth: () => ({ getToken: vi.fn().mockResolvedValue('t'), userId: 'user_123' }),
  SignedIn: ({ children }: any) => <>{children}</>,
  SignedOut: () => null,
}));

describe('BriefComments', () => {
  beforeEach(() => {
    global.fetch = vi.fn((url: string, init?: any) => {
      if (String(url).includes('/comments') && (!init || init.method === undefined || init.method === 'GET')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ comments: [{ id: 'c1', user_id: 'user_123', body: 'Check CoWoS capacity', created_at: '2026-09-06T12:00:00Z' }] }) } as Response);
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ comment: { id: 'c2', user_id: 'user_123', body: 'New note', created_at: '2026-09-06T12:01:00Z' } }) } as Response);
    }) as unknown as typeof fetch;
  });

  it('renders thread and posts a comment', async () => {
    render(<MemoryRouter><BriefComments briefId="b1" /></MemoryRouter>);
    expect(await screen.findByText('Check CoWoS capacity')).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText(/follow-up/i), { target: { value: 'New note' } });
    fireEvent.click(screen.getByRole('button', { name: /Post comment/i }));
    await waitFor(() => expect(screen.getByText('New note')).toBeInTheDocument());
  });

  it('shows empty state when no comments', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ comments: [] }) } as Response)
    ) as unknown as typeof fetch;
    render(<MemoryRouter><BriefComments briefId="b1" /></MemoryRouter>);
    expect(await screen.findByText(/No comments yet/i)).toBeInTheDocument();
  });
});
