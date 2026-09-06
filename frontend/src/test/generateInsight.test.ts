import { describe, it, expect, vi, beforeEach } from 'vitest';
import { generateInsight } from '../../api/siliconpulseApi';

const jsonHeaders = () => new Headers({ 'content-type': 'application/json' });

describe('generateInsight error reporting', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('reports quota exhaustion specifically on 429', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: false, status: 429, headers: jsonHeaders() } as Response)
    ) as unknown as typeof fetch;
    const msg = await generateInsight('TSMC?', 'LIVE UPDATES CONTEXT:\n[x]');
    expect(msg).toContain('429');
    expect(msg).toMatch(/quota/i);
  });

  it('reports HTTP status on server errors', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: false, status: 500, headers: jsonHeaders() } as Response)
    ) as unknown as typeof fetch;
    const msg = await generateInsight('TSMC?', 'ctx');
    expect(msg).toContain('HTTP 500');
  });

  it('reports timeouts specifically on abort', async () => {
    global.fetch = vi.fn(() =>
      Promise.reject(new DOMException('The operation was aborted.', 'AbortError'))
    ) as unknown as typeof fetch;
    const msg = await generateInsight('TSMC?', 'ctx');
    expect(msg).toMatch(/timed out/i);
  });

  it('returns insight text on success', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        headers: jsonHeaders(),
        json: () => Promise.resolve({ insight: '{"sections": []}' }),
      } as unknown as Response)
    ) as unknown as typeof fetch;
    expect(await generateInsight('TSMC?', 'ctx')).toBe('{"sections": []}');
  });
});
