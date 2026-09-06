import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CustomSources } from './CustomSources';

describe('CustomSources', () => {
  beforeEach(() => {
    global.fetch = vi.fn((url: string) => {
      if (String(url).endsWith('/rss')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ feeds: [{ id: 'f1', url: 'https://e.com/feed.xml', label: 'Semi Blog', enabled: true }] }) } as Response);
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) } as Response);
    }) as unknown as typeof fetch;
  });

  it('lists feeds and validates URL', async () => {
    render(<CustomSources />);
    expect(await screen.findByText('Semi Blog')).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText(/feed.xml/i), { target: { value: 'ftp://bad' } });
    fireEvent.click(screen.getByRole('button', { name: /^Add$/i }));
    expect(await screen.findByText(/must start with http/i)).toBeInTheDocument();
  });
});
