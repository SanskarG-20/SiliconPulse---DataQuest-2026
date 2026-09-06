import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { TeamIntegrations } from './TeamIntegrations';

describe('TeamIntegrations', () => {
  beforeEach(() => {
    global.fetch = vi.fn((url: string) => {
      if (String(url).includes('/keys')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ keys: [] }) } as Response);
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ webhooks: [] }) } as Response);
    }) as unknown as typeof fetch;
  });

  it('renders keys and webhook sections', async () => {
    render(<TeamIntegrations />);
    await waitFor(() => expect(screen.getByText(/API KEYS FOR BOTS/i)).toBeInTheDocument());
    expect(screen.getByText(/TEAM CHANNEL FOR SPIKE ALERTS/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ci-bot/i)).toBeInTheDocument();
  });
});
